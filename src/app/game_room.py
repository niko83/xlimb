import json
import random
import struct
import uuid
from datetime import datetime, timedelta
from math import floor

import numpy

import app
from app.castomization import (
    HealthBonusMega, HealthBonusSmall, HealthBonusMedium,
    Bullet1BonusSmall, Bullet2BonusSmall, FuelBonusSmall
)
from app.constants import VIEWPORT_SIZE, MAP_SIZE, MAP_SIZE_APPROX, CELL_STEP, CLIENT_TIMEOUT, CLIENT_ROOM_LIMIT
from app.vector import Vector2D


now = datetime.now

regenerate_bonus = 20

SUMMARY_TRAFFIC = 0


def _up_summary_trafic(mb):
    global SUMMARY_TRAFFIC
    SUMMARY_TRAFFIC += mb


def _get_point_map(points):
    point_map = numpy.zeros(MAP_SIZE_APPROX, dtype=object)
    for b in points:
        try:
            if point_map[b.approx_x][b.approx_y]:
                point_map[b.approx_x][b.approx_y][0].append(b)
                point_map[b.approx_x][b.approx_y][1].extend(b.short_data)
            else:
                point_map[b.approx_x][b.approx_y] = ([b], list(b.short_data))
        except IndexError:
            logger.warning('Not found point map [%s, %s]', b.approx_x, b.approx_y)

    return point_map


class Client:
    def __init__(self, ws=None, ship=None, is_assigned_to_room=False):
        self.is_assigned_to_room = is_assigned_to_room
        self.last_use = now()
        self.pk = uuid.uuid4().hex[0:8]
        self.ws = ws
        self.ship = ship
        self.centor_vector = Vector2D(x=VIEWPORT_SIZE[0]/2, y=VIEWPORT_SIZE[1]/2)
        self.background_position = Vector2D(x=0, y=0)
        self.sum_damage = 0
        self._observer_position = Vector2D(
            x=random.randint(int(VIEWPORT_SIZE[0]/2), int(MAP_SIZE[0] - VIEWPORT_SIZE[0]/2)),
            y=random.randint(int(VIEWPORT_SIZE[1]/2), int(MAP_SIZE[1] - VIEWPORT_SIZE[1]/2)),
        )
        self._observer_position_delta = [[1, -1], [0.5, -0.5], ]
        self.extra_viewport = None

    def set_last_use(self, time=None):
        self.last_use = time or now()

    def __str__(self):
        return '[Client: %s %s %s]' % (self.pk, self.is_assigned_to_room, self.ship)

    @property
    def is_alive(self):
        return bool(self.ship)

    def calculate_viewport_edge(self):

        if self.is_alive:
            current_position = self.ship.current_position

        self.background_position = -current_position + self.centor_vector

        self.extra_viewport = [
            -self.background_position.x-30,
            -self.background_position.x+VIEWPORT_SIZE[0]+30,
            -self.background_position.y-30,
            -self.background_position.y+VIEWPORT_SIZE[1]+30,
        ]


class GameRoom(object):
    def __init__(self, loop):
        self._name = 'room_name_%s' % uuid.uuid4().hex[0:4]
        self._loop = loop
        self.pk = uuid.uuid4().hex[0:4]
        self.clients = []
        self.has_started = False
        self.bullets = []
        self.bonuses = []
        self.start_run = now()
        self.all_ships = []

    def get_stat(self):
        return (len(self.clients), len(self.bullets), len(self.bonuses))

    @property
    def clients_without_bots(self):
        return len(list(True for c in self.clients if not c.ship.name.startswith('Bot ')))

    def _run_regenerate_bonuses(self):

        for i in range(5):

            random_matrix = (
                (20, HealthBonusSmall),
                (15, Bullet1BonusSmall),
                (15, Bullet2BonusSmall),
                (15, FuelBonusSmall),
                (8, HealthBonusMedium),
                (4, HealthBonusMega),
            )
            sum_chance = sum(m[0] for m in random_matrix)
            bonus_cls = None
            while not bonus_cls:
                for chance, bonus_cls_candidat in random_matrix:
                    if random.randint(0, sum_chance) < chance:
                        bonus_cls = bonus_cls_candidat
                        break

            bonus = bonus_cls(dispersion=False, life_limit=regenerate_bonus-10 + random.random()*20)
            self.bonuses.append(bonus)

        self._handler3 = self._loop.call_later(regenerate_bonus/2, self._run_regenerate_bonuses)

    def add_listenter(self, client, restore=False):
        if not restore:
            self.clients.append(client)

            pk = random.randint(1, 2**15-1)
            i = 0
            while pk in [s.pk for s in self.all_ships] and i < 100:
                pk = random.randint(1, 2**15-1)
                i += 1

            client.ship.set_pk(pk)
            self.all_ships.append(client.ship)

        client.ws.send_str(json.dumps({
            'command': 'start_game',
            'data': {
                'ship_pk': client.ship.pk,
                'client_pk': client.pk,
            }
        }))
        self.start()

    def set_controls(self, ship_pk, accelerator, vector, shot, shot2):
        for client in self.clients:
            if client.ship and client.ship.pk == ship_pk:
                client.ship.control.accelerator = accelerator
                client.ship.control.vector = vector
                client.ship.control.shot = shot
                client.ship.control.shot2 = shot2
                client.set_last_use(self.start_run)
                break

    def _run(self):
        self.run()
        self._handler = self._loop.call_later(0.001, self._run)

    def _run_ship_infos(self):
        global_msg = []
        if self.all_ships:
            for sh in sorted(self.all_ships, key=lambda x: (x.kills * 100) + x.damage, reverse=True):
                global_msg.append('ship_infos:%s!%s!%d!%d' % ('%s' % sh.pk, sh.name, sh.damage, sh.kills))
                #  global_msg.append('ship_infos:%s!%s!%d!%d' % ('%s' % sh.pk, sh.name, 999, 12)) #sh.damage, sh.kills))
        else:
            global_msg.append('ship_infos:')

        if global_msg:
            msg = 'plain' + '|'.join(global_msg)

            for idx, client in enumerate(self.clients):
                #  if client.is_observer:
                    #  continue
                if self.start_run - client.last_use > timedelta(seconds=CLIENT_TIMEOUT):
                    if not client.ws.closed:
                        client.ws.send_str(json.dumps({
                            'command': 'socket_closed',
                            'data': {
                                'dead_reason': 'timeout',
                                'lifetime': -1,
                            }
                        }))
                        client.ws.close()
                        if client.ship:
                            client.ship.health = -1
                    del self.clients[idx]
                    continue

                if client.ws.closed:
                    continue

                _up_summary_trafic(len(msg))
                client.ws.send_str(msg)

        self._handler2 = self._loop.call_later(1, self._run_ship_infos)

    def has_ship_intersection(self, point_map, ship):
        x = [p.x for p in ship.current_polygon]
        y = [p.y for p in ship.current_polygon]
        slices = [
            floor(min(x)/CELL_STEP), floor(max(x)/CELL_STEP) + 1,
            floor(min(y)/CELL_STEP), floor(max(y)/CELL_STEP) + 1,
        ]
        bullet_candidate = []
        slice_points = point_map[slices[0]:slices[1], slices[2]:slices[3]].flat
        for points_collections, _ in filter(None, slice_points):
            bullet_candidate += points_collections
        return bullet_candidate

    def run(self):
        try:
            for ship in self.all_ships:
                ship.calculate_position()
                ship.make_shot(self.bullets)
                ship.gun1.refresh()
                ship.gun2.refresh()
                ship.make_smoke(self.bullets)

            tracer_bullets = []

            #  FI = app.constants.FRAME_INTERVAL
            for idx, bullet in enumerate(self.bullets):
                if bullet.life_limit < 0:
                    self.bullets.pop(idx)
                    continue
                bullet.calculate_position()
                #  calculate_position(FI, bullet)
                tracer_bullets += bullet.make_tracer()

            self.bullets += tracer_bullets

            self.bullet_map = _get_point_map(self.bullets)
            for ship in self.all_ships:
                for bullet in self.has_ship_intersection(self.bullet_map, ship):
                    self.bonuses += ship.has_hit(bullet)

            for idx, bonus in enumerate(self.bonuses):
                if bonus.life_limit < 0:
                    self.bonuses.pop(idx)
                    if bonus.life_limit == -1000:  # selfdestroy
                        self.bullets += bonus.make_artifacts()
                    continue
                bonus.calculate_position()

            for ship in self.all_ships:
                for bonus in self.bonuses:
                    ship.has_hit(bonus)

            for idx, sh in enumerate(self.all_ships):
                if sh.is_dead:
                    for cl_idx, cl in enumerate(self.clients):
                        if cl.ship and cl.ship.pk == sh.pk:
                            if not cl.ws.closed:
                                cl.ws.send_str(json.dumps({
                                    'command': 'socket_closed',
                                    'data': {
                                        'dead_reason':  sh.dead_reason,
                                        'lifetime': sh.lifetime,
                                    }
                                }))
                            self.clients.pop(cl_idx)
                            break
                    self.all_ships.pop(idx)

            _now = now()
            app.constants.FRAME_INTERVAL = (_now - self.start_run).total_seconds() * 0.75
            self.start_run = _now

            processed_ramping = []
            for ship in self.all_ships:
                for another_ship in self.all_ships:
                    if (ship, another_ship) not in processed_ramping:
                        self.bonuses += ship.has_ramping(another_ship)
                        processed_ramping += [(ship, another_ship), (another_ship, ship)]

            for idx, client in enumerate(self.clients):

                if self.start_run - client.last_use > timedelta(seconds=CLIENT_TIMEOUT):
                    if not client.ws.closed:
                        client.ws.send_str(json.dumps({
                            'command': 'socket_closed',
                            'data': {
                                'dead_reason': 'timeout',
                                'lifetime': -1,
                            }
                        }))
                        client.ws.close()
                        if client.ship:
                            client.ship.health = -1
                    del self.clients[idx]
                    continue

            if len(self.clients) < CLIENT_ROOM_LIMIT:
                from app.game_rooms import queue
                client = queue.pop()
                if client:
                    self.add_listenter(client)
        except RuntimeError as e:
            logger.exception('Unhandled exception')

    def _bullet_bonuses_processing(self, client):

        if not client.extra_viewport:
            return [], [], []

        if client.ship.immortality:
            slices = [0, MAP_SIZE_APPROX[0], 0, MAP_SIZE_APPROX[1]]
        else:
            slices = [
                max(0, floor(client.extra_viewport[0]/CELL_STEP)), min(MAP_SIZE_APPROX[0], floor(client.extra_viewport[1]/CELL_STEP)),
                max(0, floor(client.extra_viewport[2]/CELL_STEP)), min(MAP_SIZE_APPROX[1], floor(client.extra_viewport[3]/CELL_STEP))
            ]

        # Bullets
        bin_data = []
        slice_bullet = self.bullet_map[slices[0]:slices[1], slices[2]:slices[3]].flat
        for _, points_collections in filter(None, slice_bullet):
            bin_data += points_collections

        bonuses_bin_data = []
        for b in self.bonuses:
            if (
                (client.extra_viewport[0] <= b.current_position.x <= client.extra_viewport[1]) and
                (client.extra_viewport[2] <= b.current_position.y <= client.extra_viewport[3])
            ):
                bonuses_bin_data.extend(b.short_data)

        ships_bin_data = []
        for s in self.all_ships:
            if (
                (client.extra_viewport[0] <= s.current_position.x <= client.extra_viewport[1]) and
                (client.extra_viewport[2] <= s.current_position.y <= client.extra_viewport[3])
            ):
                ships_bin_data.extend(s.short_data)

        return bin_data, bonuses_bin_data, ships_bin_data

    def _client_processing(self):
        for client in self.clients:

            if client.ws.closed:
                continue

            client.calculate_viewport_edge()

            bckg_x = int(client.background_position.x)
            bckg_y = int(client.background_position.y)

            global_msg = ['viewport:%d!%d!%d!%d!%d!%d' % (
                bckg_x, bckg_y,
                client.ship.health if client.ship else 0,
                client.ship.engine.fuel_amount if client.ship else 0,
                client.ship.gun1.ammo_count if client.ship else 0,
                client.ship.gun2.ammo_count if client.ship else 0,
            )]

            bin_data_bullets, bin_data_bonuses, bin_data_ships = self._bullet_bonuses_processing(
                client
            )

            client.ws.send_bytes(struct.pack('h'*(len(bin_data_bullets)+3), 10, bckg_x, bckg_y, *map(int, bin_data_bullets)))
            client.ws.send_bytes(struct.pack('h'*(len(bin_data_bonuses)+3), 20, bckg_x, bckg_y, *map(int, bin_data_bonuses)))
            client.ws.send_bytes(struct.pack('h'*(len(bin_data_ships)+3), 30, bckg_x, bckg_y, *map(int, bin_data_ships)))

            """
            #  polygon_msg = []
            #  for polygon in maps.all_polygons:
                #  points = []
                #  for point in polygon:
                    #  points += [
                        #  '%d' % (point.x + bckg_x),
                        #  '%d' % (point.y + bckg_y),
                    #  ]
                #  global_msg.append('polygon:' + '!'.join(points))

            #  for sh in self.all_ships:
                #  points = []
                #  for point in sh.current_polygon:
                    #  points += [
                        #  '%d' % (point.x + bckg_x),
                        #  '%d' % (point.y + bckg_y),
                    #  ]
                #  global_msg.append('polygon:' + '!'.join(points))
            """

            msg = 'plain' + '|'.join(global_msg)

            _up_summary_trafic(len(msg))

            client.ws.send_str(msg)

        self._handler4 = self._loop.call_later(0.02, self._client_processing)

    def start(self):
        if self.has_started:
            return
        self.has_started = True
        self._handler = self._loop.call_later(0, self._run)
        self._handler2 = self._loop.call_later(0, self._run_ship_infos)
        self._handler3 = self._loop.call_later(0, self._run_regenerate_bonuses)
        self._handler4 = self._loop.call_later(0, self._client_processing)

    def stop(self):
        self._handler.cancel()
