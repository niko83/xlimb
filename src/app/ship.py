import logging
import random
from datetime import datetime
from math import floor, pi

import app
from app.constants import MU, G, G_DIVE, MAP_SIZE, CELL_STEP, DeadReason
from app.engine import Engine
from app.gun import Gun
from app.helper import in_polygon_info, distance, get_polygon_idx_collision, get_polygon_info,  get_angle_collision, polygon_cell
from app.polygon_data import all_polygons
from app.vector import Vector2D


logger = logging.getLogger('ship.' + __name__)

now = datetime.now
_pi2 = pi * 2
_pi_2 = pi/2

gravity = Vector2D(angle=pi*3/2, length=G)
gravity_dive = Vector2D(angle=pi*3/2, length=G_DIVE)

_smoke_interval = 0.020


class _Control:
    def __init__(self):
        self.accelerator = 0
        self.vector = 0
        self.shot = 0
        self.shot2 = 0


class Ship(object):

    def __init__(self, name, bullet1_cls, bullet2_cls, ship_type=None):
        self.ship_type = ship_type
        self.tilt_angle = 0
        self.weight = 1
        self.health = 100
        self.immortality = int(3 / app.constants.FRAME_INTERVAL)
        self.engine = Engine()
        self.damage = 0
        self.kills = 0
        self.name = name[:15] or 'Anonymous'
        self._acc = Vector2D(x=0, y=0)
        self.dead_step = -1
        # dead_step
        # -1 : life
        # 0 : in dive
        # >0 impolisum and fire
        # 0..5 implosiom
        # >80 close socket

        self.pk = None
        self.candidat_position = Vector2D(x=0, y=0)
        self.current_speed = Vector2D(x=0, y=0)
        self.current_route = _pi_2
        self.control = _Control()
        self.a_sum = Vector2D(x=0, y=0)

        self.demensions_info = [
            (p.length, p.angle()-_pi_2) for p in self.demensions
        ]
        self.demensions_max_radius = max(d.y for d in self.demensions)

        while True:
            self.candidat_position = Vector2D(
                x=random.random()*MAP_SIZE[0],
                y=random.random()*MAP_SIZE[1]
            )
            if not get_polygon_idx_collision(self.candidat_position.x, self.candidat_position.y):
                self.current_position = self.candidat_position
                self.candidat_position = Vector2D(x=0, y=0)
                break
        self.current_polygon = [
            Vector2D(
                length=p_length,
                angle=p_angle - self.current_route,
            ) + self.current_position for p_length, p_angle in self.demensions_info
        ]
        self.current_polygon_info = get_polygon_info(self.current_polygon)

        self.gun1 = Gun(**bullet1_cls(self).gun_kwargs)
        self.bullet1_cls = bullet1_cls

        self.gun2 = Gun(**bullet2_cls(self).gun_kwargs)
        self.bullet2_cls = bullet2_cls

        from app.castomization import SmokeBullet
        self.smoke_cls = SmokeBullet
        self.smoke_interval = _smoke_interval
        self.lifetime = None
        self.starttime = None

        self.dead_reason = None

    def __str__(self):
        return 'Ship: %s' % self.pk

    def set_pk(self, pk):
        self.pk = 's_%s' % pk
        self._pk_short = pk
        self.starttime = now()

    @property
    def short_data(self):
        return (
            self._pk_short,
            self.tilt_angle,
            self.current_position.x,
            self.current_position.y,
            (self.current_route % (_pi2)) * 100,
            self.dead_step,
            self.ship_type,
        )

    @property
    def is_dead(self):
        return self.dead_step > 80

    def mark_as_dead(self, reason='', to_dive=None):
        if reason:
            self.dead_reason = reason
            if not self.lifetime:
                self.lifetime = int((now() - self.starttime).total_seconds())
        if self.dead_step == -1 and to_dive is True:
            self.dead_step = 0
        elif self.dead_step == -1 and to_dive is False:
            self.dead_step = 1

    def has_ramping(self, another_ship):

        if self is another_ship:
            return []

        if self.dead_step > 0 or another_ship.dead_step > 0:
            return []

        if distance(
            (self.current_position.x, self.current_position.y),
            (another_ship.current_position.x, another_ship.current_position.y)
        ) > 40:
            return []

        i = 0
        while distance(
            (self.current_position.x, self.current_position.y),
            (another_ship.current_position.x, another_ship.current_position.y)
        ) <= 40:
            i += 1
            if i > 1:
                #  print('WARNING %s...%s' % (
                    #  i,
                    #  distance(
                        #  (self.current_position.x, self.current_position.y),
                        #  (another_ship.current_position.x, another_ship.current_position.y)
                    #  )
                #  ))
                if i > 5:
                    damage = min(self.health, another_ship.health)
                    self.health -= damage
                    another_ship.health -= damage
                    if self.health <= 0:
                        self.mark_as_dead(DeadReason.WORLD_COLLISION_BIRTH)
                    if another_ship.health <= 0:
                        another_ship.mark_as_dead(DeadReason.WORLD_COLLISION_BIRTH)

                    logger.debug('world_collision_birth one shid destroyed')

                    return []

            tmp_speed = self.current_speed*app.constants.FRAME_INTERVAL
            self.current_position.x -= tmp_speed.x
            self.current_position.y += tmp_speed.y

            tmp_speed = another_ship.current_speed*app.constants.FRAME_INTERVAL
            another_ship.current_position.x -= tmp_speed.x
            another_ship.current_position.y += tmp_speed.y

        u1 = self.current_speed
        m1 = self.weight

        u2 = another_ship.current_speed
        m2 = another_ship.weight

        m_sum = m1+m2
        self.current_speed = (u1*(m1-m2) + u2*2*m2) / m_sum
        another_ship.current_speed = (u2*(m2-m1) + u1*2*m1) / m_sum

        if self.immortality:
            ramping_energy = 0
        else:
            ramping_energy = (u2 - u1).length / 6

        damage_to_one = min(m2 / m_sum * ramping_energy, self.health)
        self.health -= damage_to_one
        another_ship.damage += damage_to_one

        damage_to_second = min(m1 / m_sum * ramping_energy, another_ship.health)
        another_ship.health -= damage_to_second
        self.damage += damage_to_second

        logger.debug(
            '%s (%s) %d....%s (%s) %d',
            self.ship_type, m1, damage_to_one,
            another_ship.ship_type, m2, damage_to_second
        )

        from app.castomization import (
            HealthBonusMedium, FuelBonusSmall, Bullet2BonusSmall, Bullet1BonusSmall
        )

        bonuses = []
        if self.health <= 0:
            self.mark_as_dead(reason=DeadReason.RAMPING, to_dive=False)
            bonuses += [
                HealthBonusMedium(emitter=self, start_position=self.current_position),
                FuelBonusSmall(emitter=self, start_position=self.current_position),
                Bullet1BonusSmall(emitter=self, start_position=self.current_position),
                Bullet2BonusSmall(emitter=self, start_position=self.current_position),
            ]

        an_ship = another_ship
        if an_ship.health <= 0:
            an_ship.mark_as_dead(reason=DeadReason.RAMPING, to_dive=False)
            bonuses += [
                HealthBonusMedium(emitter=an_ship, start_position=an_ship.current_position),
                FuelBonusSmall(emitter=an_ship, start_position=an_ship.current_position),
                Bullet1BonusSmall(emitter=an_ship, start_position=an_ship.current_position),
                Bullet2BonusSmall(emitter=an_ship, start_position=an_ship.current_position),
            ]

        return bonuses

    def has_hit(self, object2d):

        if (
            self.health <= 0 or  # i am dead
            object2d.life_limit <= 0 or  # object is dead
            object2d.health == 0  # object is smoke
        ):
            return []

        for point in (object2d.current_polygon or [object2d.current_position]):
            if in_polygon_info(
                    point.x,
                    point.y,
                    polygon_info=self.current_polygon_info
            ):
                break
        else:
            return []

        damage = 0 if self.immortality else object2d.health

        health_before = self.health
        self.health += damage
        self.engine.fuel_amount += object2d.fuel

        self.gun1.ammo_count += object2d.bullet1
        self.gun2.ammo_count += object2d.bullet2

        if object2d.current_speed:
            self.current_speed += (object2d.current_speed * (-object2d.health/50 * 0.35))

        object2d.life_limit = -1

        if damage < 0:

            if self == object2d.ship_emitter:
                if self.health <= 0 and health_before > 0:
                    self.mark_as_dead(reason=DeadReason.SUICIDE)
            else:
                if self.health > 0:
                    if object2d.ship_emitter:
                        object2d.ship_emitter.damage += -damage
                elif health_before > 0:
                    if object2d.ship_emitter:
                        object2d.ship_emitter.damage += health_before
                        object2d.ship_emitter.kills += 1
                        self.mark_as_dead(reason=DeadReason.KILL)
                    from app.castomization import (
                        HealthBonusMedium, FuelBonusSmall, Bullet2BonusSmall, Bullet1BonusSmall
                    )
                    return [
                        HealthBonusMedium(emitter=self, start_position=self.current_position),
                        FuelBonusSmall(emitter=self, start_position=self.current_position),
                        Bullet1BonusSmall(emitter=self, start_position=self.current_position),
                        Bullet2BonusSmall(emitter=self, start_position=self.current_position),
                    ]

        return []

    def make_smoke(self, bullets):

        if self.dead_step >= 5:
            return

        self.smoke_interval -= app.constants.FRAME_INTERVAL
        if self.smoke_interval > 0:
            return
        else:
            self.smoke_interval = _smoke_interval

        if self.dead_step == -1:  # a little health

            if (self.health-20)/100 < random.random() * (0.5 - 0.2):
                bullets.append(self.smoke_cls(self))
            if self.health < 20:
                bullets.append(self.smoke_cls(self))
            #  elif self.health < 40:
                #  bullets.append(self.smoke_cls(self))
        elif self.dead_step == 0:  # in dive
            bullets += [self.smoke_cls(self), self.smoke_cls(self), self.smoke_cls(self)]
        elif self.dead_step < 5:  # impolisum
            bullets += [self.smoke_cls(self, self.current_speed.length) for i in range(1, 10)]

    def make_shot(self, bullets):

        if self.dead_step > 0:
            return

        if self.control.shot and self.gun1.is_ready:
            self.gun1.shot()
            bullets.append(self.bullet1_cls(self))

        if self.control.shot2 and self.gun2.is_ready:
            self.gun2.shot()
            bullets.append(self.bullet2_cls(self))

    def _dive(self):

        if self.dead_step > 0:
            self.dead_step += 20 * app.constants.FRAME_INTERVAL
            return

        a_friction = self.current_speed * (-MU) / 2
        self.current_route -= 4 * app.constants.FRAME_INTERVAL * self.control.vector
        self.a_sum = (gravity_dive + a_friction)
        self.current_speed += self.a_sum * app.constants.FRAME_INTERVAL

        sum_vector = self.current_speed*app.constants.FRAME_INTERVAL + (self.a_sum/2) * app.constants.FRAME_INTERVAL**2
        self.candidat_position.x = self.current_position.x + sum_vector.x
        self.candidat_position.y = self.current_position.y - sum_vector.y

        polygon_idx = get_polygon_idx_collision(self.candidat_position.x, self.candidat_position.y)
        if polygon_idx:
            polygon = all_polygons[polygon_idx]
        else:
            polygon = None

        if polygon:
            if self.dead_step == 0:
                self.mark_as_dead(to_dive=False)
            self.dead_step += 20 * app.constants.FRAME_INTERVAL  # start implosim and fire
            return

        self.current_position.reinit(
            x=self.candidat_position.x,
            y=self.candidat_position.y,
        )

        for idx, (p_length, p_angle) in enumerate(self.demensions_info):
            self.current_polygon[idx].reinit(
                length=p_length,
                angle=p_angle - self.current_route,
            )
            self.current_polygon[idx] += self.current_position

        self.current_polygon_info = get_polygon_info(self.current_polygon)

    def calculate_position(self):

        if self.immortality:
            self.immortality -= 1

        if self.health <= 0:
            if self.dead_step == -1:
                self.mark_as_dead(to_dive=True)
            return self._dive()

        a_friction = self.current_speed * (-MU)

        tilt_angle_speed = 7 * self.rotation_speed * app.constants.FRAME_INTERVAL
        if self.control.vector:
            if self.control.vector > 0 and self.tilt_angle < 9:
                self.tilt_angle += tilt_angle_speed
            elif self.control.vector < 0 and self.tilt_angle > -9:
                self.tilt_angle -= tilt_angle_speed
        else:
            if self.tilt_angle > 0:
                self.tilt_angle -= tilt_angle_speed
            elif self.tilt_angle < 0:
                self.tilt_angle += tilt_angle_speed

        self.current_route -= self.rotation_speed * app.constants.FRAME_INTERVAL * self.control.vector

        if self.control.accelerator:
            power = self.engine.power if self.engine.is_ready else 200
            self._acc.reinit(
                angle=self.current_route,
                length=power / self.weight,
            )
            self.engine.acceleration()
            self.a_sum.reinit(
                x=self._acc.x + gravity.x + a_friction.x,
                y=self._acc.y + gravity.y + a_friction.y,
            )
        else:
            self.a_sum.reinit(
                x=gravity.x + a_friction.x,
                y=gravity.y + a_friction.y,
            )
        self.a_sum *= app.constants.FRAME_INTERVAL
        self.current_speed += self.a_sum

        sum_vector = self.current_speed*app.constants.FRAME_INTERVAL + (self.a_sum/2) * app.constants.FRAME_INTERVAL**2
        self.candidat_position.x = self.current_position.x + sum_vector.x
        self.candidat_position.y = self.current_position.y - sum_vector.y

        round_x = floor(self.candidat_position.x/CELL_STEP)
        round_y = floor(self.candidat_position.y/CELL_STEP)
        try:
            has_world_collision = polygon_cell[round_x][round_y]
        except:
            has_world_collision = True

        if has_world_collision:
            polygon_idx = get_polygon_idx_collision(self.candidat_position.x, self.candidat_position.y)
            if polygon_idx:
                polygon = all_polygons[polygon_idx]
            else:
                polygon = None
        else:
            polygon = None

        if polygon:
            angle = get_angle_collision(self, polygon) or _pi_2

            self.current_speed.reinit(
                length=self.current_speed.length * 0.3,
                angle=angle*2 + self.current_speed.angle()
            )

            self.health -= 100 * app.constants.FRAME_INTERVAL  # polygon dead
            if self.health <= 0:
                self.mark_as_dead(DeadReason.WORLD_COLLISION)
            self.current_polygon = [
                Vector2D(
                    length=p_length,
                    angle=p_angle - self.current_route,
                ) + self.current_position for p_length, p_angle in self.demensions_info
            ]
            self.current_polygon_info = get_polygon_info(self.current_polygon)

            return
        self.current_position.reinit(
            x=self.candidat_position.x,
            y=self.candidat_position.y,
        )
        #  self.approx_x = floor(self.current_position.x/CELL_STEP)
        #  self.approx_y = floor(self.current_position.y/CELL_STEP)

        self.current_polygon = [
            Vector2D(
                length=p_length,
                angle=p_angle - self.current_route,
            ) + self.current_position for p_length, p_angle in self.demensions_info
        ]
        self.current_polygon_info = get_polygon_info(self.current_polygon)

    def position_abs(self, candidat=True):
        if candidat:
            return self.candidat_position
        else:
            return self.current_position
