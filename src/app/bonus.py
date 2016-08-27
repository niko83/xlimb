import math
import random

import app
from app.constants import MAP_SIZE, MU
from app.vector import Vector2D


class Bonus:
    def __init__(
            self, emitter=None, health=1, fuel=0, bullet1=0, bullet2=0,
            dispersion=True, start_position=None,
            life_limit=30,
    ):
        self.type = 0
        self.damage = 0  # interface consist
        self.kills = 0  # interface consist
        self.current_route = 0  # interface consist
        self.pk = random.randint(1, 30000)
        self.ship_emitter = emitter
        if dispersion:
            bonus_route = random.random()*2*math.pi
        else:
            bonus_route = 0

        self._demensions = [
            Vector2D(x=-15, y=15),
            Vector2D(x=15, y=15),
            Vector2D(x=15, y=-15),
            Vector2D(x=-15, y=-15),
        ]
        self.demensions_info = [
            (p.length, p.angle()-math.pi/2) for p in self._demensions
        ]
        self.demensions_max_radius = max(d.y for d in self._demensions)

        if start_position:
            self.current_position = Vector2D(
                x=start_position.x,
                y=start_position.y,
            )
            self.candidat_position = Vector2D(x=0, y=0)
        else:
            while True:
                self.candidat_position = Vector2D(
                    x=random.random() * MAP_SIZE[0],
                    y=random.random() * MAP_SIZE[1],
                )
                if not app.helper.get_polygon_idx_collision(self.candidat_position.x, self.candidat_position.y):
                    self.current_position = self.candidat_position
                    break

        self.current_polygon = [
            Vector2D(
                length=p_length,
                angle=p_angle,
            ) + self.current_position for p_length, p_angle in self.demensions_info
        ]

        if dispersion:
            self.current_speed = Vector2D(length=60, angle=bonus_route)
        else:
            self.current_speed = None

        self.life_limit = life_limit
        self.health = health
        self.fuel = fuel
        self.bullet1 = bullet1
        self.bullet2 = bullet2

    def __str__(self):
        from app.castomization import bonus_type_to_str
        return 'Bonus:(%s, %.3f, %s)' % (
            self.current_position,
            self.life_limit,
            bonus_type_to_str.get(self.type, self.type)
        )

    def make_artifacts(self):
        from app.castomization import ArtifactBullet
        return [ArtifactBullet(self) for _ in range(15)]

    def position_abs(self, candidat=True):
        return self.candidat_position if candidat else self.current_position

    @property
    def short_data(self):
        return (self.current_position.x, self.current_position.y, self.type)

    def calculate_position(self):
        FI = app.constants.FRAME_INTERVAL
        self.life_limit -= FI
        if self.life_limit < 0:
            self.life_limit = -1000  # selfdestroy
            return

        if not self.current_speed:
            return

        a_sum = self.current_speed * (-MU)
        self.current_speed += a_sum * FI
        sum_vector = self.current_speed*FI + (a_sum/2) * FI**2
        self.candidat_position.reinit(
            self.current_position.x + sum_vector.x,
            self.current_position.y - sum_vector.y
        )

        if app.helper.get_polygon_idx_collision(self.candidat_position.x, self.candidat_position.y):
            self.life_limit = -1
            return

        self.current_position.reinit(
            x=self.candidat_position.x,
            y=self.candidat_position.y,
        )

        if self.current_speed.length < 2:
            self.current_speed = None

        self.current_polygon = [
            Vector2D(
                length=p_length,
                angle=p_angle,
            ) + self.current_position for p_length, p_angle in self.demensions_info
        ]
