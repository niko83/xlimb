#!/usr/bin/env python

import sys
import os
import pickle
import websocket
import random
import json
import struct
import threading
from sys import argv
from time import sleep
import math
from functools import partial
import copy
from app.constants import CELL_STEP, ROOT_DIR

from app.vector import Vector2D
from itertools import cycle


path = [
    {'id': 1, 'x': 748, 'y': 340},
    {'id': 2, 'x': 391, 'y': 682},
    {'id': 3, 'x': 695, 'y': 1326},
    {'id': 4, 'x': 1521, 'y': 1379},
    {'id': 5, 'x': 2759, 'y': 1352},
    {'id': 6, 'x': 2884, 'y': 899},
    {'id': 7, 'x': 2933, 'y': 358},
    {'id': 8, 'x': 2079, 'y': 383},
]

help_path = [
    [
        {'id': 1, 'x': 2362, 'y': 702},
        {'id': 2, 'x': 2079, 'y': 383},
    ],
    [
        {'id': 1, 'x': 1109, 'y': 877},
        {'id': 2, 'x': 567, 'y': 917},
    ],
    [
        {'id': 1, 'x': 1584, 'y': 952},
        {'id': 2, 'x': 1815, 'y': 974},
        {'id': 3, 'x': 2551, 'y': 1032},
        {'id': 3, 'x': 2781, 'y': 1041},
    ],
    [
        {'id': 1, 'x': 259, 'y': 229},
        {'id': 2, 'x': 478, 'y': 340},
    ],
    [
        {'id': 1, 'x': 193, 'y': 304},
        {'id': 2, 'x': 260, 'y': 559},
    ],
]

#  path = [
    #  {'id': 1, 'x': 250, 'y': 250},
    #  {'id': 2, 'x': 900, 'y': 550},
    #  {'id': 3, 'x': 900, 'y': 250},
    #  {'id': 4, 'x': 250, 'y': 550},
#  ]
#  help_path = []


def get_directions_correction(my_obj, obj, prev_point=None):
    angle_to_obj = Vector2D(
        x=obj['x'] - my_obj['x'],
        y=my_obj['y'] - obj['y'],
    ).angle()

    if prev_point:
        if (
            int(my_obj['x']) == int(prev_point['x']) and
            int(my_obj['y']) == int(prev_point['y'])
        ):
            print ('Stop %s' % random.random())


        #  angle_speed = Vector2D(
            #  x=my_obj['x'] - prev_point['x'],
            #  y=prev_point['y'] - my_obj['y']
        #  ).angle()

        #  if angle_speed > math.pi:
            #  angle_speed -= (math.pi * 2)
        #  if angle_speed < -math.pi:
            #  angle_speed += (math.pi * 2)

    if my_obj['angle'] > math.pi:
        my_obj['angle'] -= (math.pi * 2)
    if my_obj['angle'] < -math.pi:
        my_obj['angle'] += (math.pi * 2)

    if angle_to_obj > math.pi:
        angle_to_obj -= (math.pi * 2)
    if angle_to_obj < -math.pi:
        angle_to_obj += (math.pi * 2)

    angle_diff = angle_to_obj - my_obj['angle']
    #  if prev_point and my_obj['angle'] and abs(angle_speed-my_obj['angle'])/my_obj['angle'] < math.pi / 2:
        #  angle_diff = angle_to_obj - angle_speed*0.2 - my_obj['angle']
    #  else:

    abs_angle_diff = abs(angle_diff)

    if not(15 <= math.degrees(abs_angle_diff) <= 360-15):
        return '0', abs_angle_diff

    if angle_diff < math.pi/180*3:
        if abs_angle_diff <= math.pi:
            return '1', abs_angle_diff
        else:
            return '-1', abs_angle_diff
    elif angle_diff > math.pi/180*3:
        if abs_angle_diff <= math.pi:
            return '-1', abs_angle_diff
        else:
            return '1', abs_angle_diff


def bot_control(ws, viewport_data):
    last_msg = None

    bot_path = None
    prev_point = None

    while True:
        sleep(0.1)

        v_data = copy.deepcopy(viewport_data)
        try:
            v_data['my_obj']['x']
            v_data['my_obj']['client_pk']
            v_data['my_obj']['ship_pk']
        except KeyError:
            bot_path, nearest_point = None, None
            sleep(1)
            continue

        msg = {
            'client_pk': v_data['my_obj']['client_pk'],
            'ship_pk': v_data['my_obj']['ship_pk'],
            'gas': 0,
            'direction': 0,
            'weapon1': 0,
            'weapon2': 0,
        }

        if prev_point:
            speed = Vector2D(
                x= v_data['my_obj']['x'] - prev_point['x'],
                y= prev_point['y'] - v_data['my_obj']['y']
            ).length
        else:
            speed = 0

        if not v_data['ships']:
            msg['weapon1'] = 0
            msg['weapon1'] = 0

        if not v_data['bonuses']:
            msg['gas'] = 0

        if _ship_attack(v_data, msg):
            bot_path, nearest_point = None, None
        elif _grab_bonus(v_data, speed, msg):
            bot_path, nearest_point = None, None
        else:
            if not bot_path:
                bot_path, nearest_point, is_main_path = get_bot_path(v_data['my_obj'])

            if not bot_path:
                msg['gas'] = 1
                continue

            limit = 100 if is_main_path else 50

            if sort_by_distance(v_data['my_obj'], nearest_point) < limit:
                try:
                    nearest_point = bot_path.__next__()
                except StopIteration:
                    local_path = copy.deepcopy(path)
                    sort_dst = partial(sort_by_distance, v_data['my_obj'])
                    local_path.sort(key=sort_dst)
                    nearest_point = local_path[0]

                    bot_path = cycle(path)
                    for i in bot_path:
                        if i == nearest_point:
                            break

            msg['direction'], angle = get_directions_correction(v_data['my_obj'], nearest_point)
            msg['gas'] = _gas(speed, v_data['my_obj'], nearest_point, is_main_path, angle=angle)

            if _has_world_collision(v_data['my_obj'], nearest_point):
                bot_path, nearest_point = None, None
                pass
            else:
                pass


        candidat_msg = '{client_pk}:cursor_pos:{ship_pk}!{gas}!{direction}!{weapon1}!{weapon2}'.format(**msg)
        if candidat_msg != last_msg:
            ws.send(candidat_msg)
            last_msg = candidat_msg

        prev_point = copy.deepcopy(v_data['my_obj'])


def get_bot_path(my_obj):
    nearest_dist = sys.maxsize
    nearest_path = None
    for candidat_path in [path] + help_path:
        local_path = copy.deepcopy(candidat_path)
        sort_dst = partial(sort_by_distance, my_obj)
        local_path.sort(key=sort_dst)
        for nearest_point_candidat in local_path:
            if _has_world_collision(nearest_point_candidat, my_obj):
                continue

            dist = sort_by_distance(my_obj, nearest_point_candidat)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_path = candidat_path
                nearest_point = nearest_point_candidat

    if not nearest_path:
        return None, None, None

    if nearest_path == path:
        bot_path = cycle(path)
        is_main_path = True
        for i in bot_path:
            if i == nearest_point:
                break
    else:
        bot_path = nearest_path.__iter__()
        is_main_path = False
        for i in bot_path:
            if i == nearest_point:
                break

    return bot_path, nearest_point, is_main_path


def sort_by_distance(my_obj, a):
    return math.sqrt((my_obj['x'] - a['x'])**2 + (my_obj['y'] - a['y'])**2)


def _gas(speed, my_obj, point, is_main_path=True, angle=None):

    if angle >= math.radians(20):
        return  0

    dist = sort_by_distance(my_obj, point)
    if 30 < dist < 90:
        return 1
    if not dist:
        return 1
    if is_main_path and (speed / dist) < 0.090:
        return 1
    if not is_main_path and (speed / dist) < 0.090:
        return 1
    return 0

def startBot():
    ws = websocket.WebSocket()
    ws.connect('ws://127.0.0.1:8080/ws/')
    #  ws.connect('ws://www.xlimb.ru/ws/')

    viewport_data = {}

    t = threading.Thread(target=bot_control, args=(ws, viewport_data))
    t.start()

    name = random.choice([
        'Joe',
        'Boris',
        'Alex',
        'Katrin',
        'Ivan',
        'Sonya',
        'Leo',
        'Lucas',
        'Luke',
        'James',
        'Eva',
    ])

    while True:
        sleep(1)
        ws.send(':join:{client_pk}:{weapon1}:{weapon2}:{name}:{ship_type}'.format(
            client_pk=None,
            weapon1=random.randint(1, 3),
            weapon2=random.choice([1, 3]),
            name=name,
            ship_type=random.choice([10, 12]),
        ))

        while True:
            try:
                data = ws.recv()
            except Exception as e:
                print('Bot failed', e)
                return

            if type(data) == bytes or data.startswith('plain'):
                continue

            data = json.loads(data)

            if data.get('command') == 'start_game':
                client_pk = data['data'].get('client_pk')
                ship_pk = data['data'].get('ship_pk')
                print('+', end="", flush=True)
                break

            if data.get('command') == 'waiting':
                #  print('.', end="", flush=True)
                continue
            print(data)

        viewport_data['ships'] = []
        viewport_data['bonuses'] = []
        viewport_data['my_obj'] = {
            'ship_pk': ship_pk,
            'client_pk': client_pk,
        }

        is_alive = True
        while is_alive:
            data = ws.recv()

            if type(data) == str and data.startswith('plainviewport'):
                data = data.split('!')
                viewport_data['my_obj']['health'] = int(data[2])
                viewport_data['my_obj']['fuel'] = int(data[3])
                viewport_data['my_obj']['ammo'] = int(data[4])
                viewport_data['my_obj']['roket'] = int(data[5])
                continue

            try:
                json_data = json.loads(data)
            except:
                json_data = None

            if json_data and json_data['command'] == 'socket_closed':
                #  print('%s-%s ' % (
                    #  json_data['data']['dead_reason'],
                    #  json_data['data']['lifetime']
                #  ), end="\n", flush=True)
                break

            if type(data) != bytes:
                continue

            data = struct.unpack('h' * int(len(data) / 2), data)
            if data[0] not in [20, 30]:
                continue

            if data[0] == 30:
                tmp_ships = []
                data = data[4:]
                while data:
                    if 's_%s' % data[0] == ship_pk:
                        viewport_data['my_obj']['x'] = data[2]
                        viewport_data['my_obj']['y'] = data[3]
                        viewport_data['my_obj']['angle'] = (data[4]/100) % (math.pi * 2)
                    elif data[5] == -1:  # is alive
                        tmp_ships.append({
                            'x': data[2],
                            'y': data[3],
                        })
                    data = data[9:]
                viewport_data['ships'] = tmp_ships
            elif data[0] == 20:
                tmp_bonuses = []
                data = data[3:]
                while data:
                    tmp_bonuses.append({
                        'x': data[0],
                        'y': data[1],
                        'type': data[2],
                    })
                    data = data[3:]
                viewport_data['bonuses'] = tmp_bonuses

with open(os.path.join(ROOT_DIR, 'cache_map.pickle'), 'rb') as f:
    _polygon_cell = pickle.load(f)


def is_nearest_point(approx_x, approx_y, start_approx, end_approx):

    if (
        (approx_x == start_approx[0] and approx_y == start_approx[1]) or
        (approx_x == end_approx[0] and approx_y == end_approx[1])
    ):
        return True
    return False


    if (
        approx_x in (start_approx[0]-1,  start_approx[0],  start_approx[0]+1) and
        approx_y in (start_approx[1]-1,  start_approx[1],  start_approx[1]+1)
    ):
            return True
    if (
        approx_x in (end_approx[0]-1,  end_approx[0],  end_approx[0]+1) and
        approx_y in (end_approx[1]-1,  end_approx[1],  end_approx[1]+1)
    ):
            return True
    return False


def _has_world_collision(obj1, obj2):
    K, B = resolve_line(obj1, obj2)

    x1, y1 = obj1['x'], obj1['y']
    x2, y2 = obj2['x'], obj2['y']

    test_delta = 10
    test_x = x1 + test_delta
    test_y = K * test_x + B
    test_distance = math.sqrt((test_y - y1)**2 + (test_x - x1)**2)
    delta_x = test_delta * (CELL_STEP / test_distance)
    mult = 1 if x2 >= x1 else -1

    x = x1 + delta_x * mult
    y = K * x + B
    approx_x = math.floor(x/CELL_STEP)
    approx_y = math.floor(y/CELL_STEP)
    counter = 0

    start_approx = (math.floor(x1/CELL_STEP), math.floor(y1/CELL_STEP))
    end_approx = (math.floor(x2/CELL_STEP), math.floor(y2/CELL_STEP))

    while (
        min(start_approx[0], end_approx[0]) <= approx_x <= max(start_approx[0], end_approx[0])
        and min(start_approx[1], end_approx[1]) <= approx_y <= max(start_approx[1], end_approx[1])
    ):
        if is_nearest_point(approx_x, approx_y, start_approx, end_approx):
            x = x1 + counter * delta_x * mult
            y = K * x + B
            counter += 1

            approx_x = math.floor(x/CELL_STEP)
            approx_y = math.floor(y/CELL_STEP)
            continue

        try:
            collision = _polygon_cell[approx_x][approx_y]
        except:
            print ('??')
            collision = False

        x = x1 + counter * delta_x * mult
        y = K * x + B
        counter += 1

        approx_x = math.floor(x/CELL_STEP)
        approx_y = math.floor(y/CELL_STEP)

        if collision:
            return True
    return False


def resolve_line(p1, p2):
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    if x2 == x1:
        return 10000, 0  # @FIXME
    K = (y2-y1)/(x2-x1)
    B = (y1*(x2-x1) - x1*(y2-y1)) / (x2 - x1)
    return K, B

def _grab_bonus(viewport_data, speed, msg):

    if not viewport_data['bonuses']:
        return False

    sort_dst = partial(sort_by_distance, viewport_data['my_obj'])
    viewport_data['bonuses'].sort(key=sort_dst)
    for bonus in viewport_data['bonuses']:
        if _has_world_collision(bonus, viewport_data['my_obj']):
            continue

        #  print('bonus', viewport_data['my_obj']['x'], viewport_data['my_obj']['y'] , bonus['x'], bonus['y'], '----%s'% random.random())

        msg['direction'], angle = get_directions_correction(viewport_data['my_obj'], bonus)
        msg['gas'] = _gas(speed, viewport_data['my_obj'], bonus, angle=angle)
        return True
    return False

def _ship_attack(viewport_data, msg):
    if not viewport_data['ships'] or viewport_data['my_obj'].get('ammo', 0) <= 0:
        return False

    sort_dst = partial(sort_by_distance, viewport_data['my_obj'])
    viewport_data['ships'].sort(key=sort_dst)

    for ship in viewport_data['ships']:
        if _has_world_collision(ship, viewport_data['my_obj']):
            continue

        msg['direction'], angle = get_directions_correction(viewport_data['my_obj'], ship)
        if angle < math.pi/180 * 20:
            msg['weapon1'] = 1
        #  if angle < math.pi/180 * 40:
            #  msg['weapon2'] = 1
        msg['gas'] = 1 if random.randint(0, 3) > 2 else 0
        return True
    return False


if __name__ == '__main__':
    for i in range(int(argv[1])):
        t = threading.Thread(target=startBot)
        t.start()
        sleep(0.1)
