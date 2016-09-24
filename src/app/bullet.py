import math
import random
import uuid
from math import floor, ceil

import app
from app.constants import CELL_STEP
from app.vector import Vector2D


class Bullet:
    def __init__(
            self, emitter, speed=650,
            ricochet=False, life_limit=4,
            health=-35, dispersion=0,
            able_to_make_tracing=False,  # seconds
            reverse_shot=False,
            center_shot=False,
            is_tracer=False,
            trace_speed=None,
            trace_dispersion=0,
            trace_life_limit=0,
            trace_health=-5,
            trace_count=0,
            trace_route=0,
            trace_ricochet=False,
            bullet_speed=None,
    ):
        self.ship_emitter = emitter.ship_emitter if is_tracer else emitter
        self.pk = uuid.uuid4().hex[0:4]
        self.current_polygon = None
        self.trace_speed = trace_speed
        self.trace_dispersion = trace_dispersion
        self.trace_life_limit = trace_life_limit
        self.trace_health = trace_health
        self.trace_count = trace_count
        self.trace_route = trace_route
        self.trace_ricochet = trace_ricochet
        self.bullet_speed = bullet_speed


        if is_tracer:
            bullet_route = random.random()*2*math.pi
        else:
            if dispersion:
                bullet_route = emitter.current_route + random.random()*dispersion - dispersion/2
            else:
                bullet_route = emitter.current_route

        start_position = emitter.position_abs(candidat=False)

        max_radius = 2 if is_tracer else emitter.demensions_max_radius
        self.current_route = 0

        if center_shot:
            self.current_position = Vector2D(x=start_position.x, y=start_position.y)
        elif reverse_shot:
            self.current_position = (
                Vector2D(x=start_position.x, y=start_position.y) -
                Vector2D(x=max_radius * math.cos(emitter.current_route), y=-max_radius*math.sin(emitter.current_route))
            )
        else:
            self.current_position = (
                Vector2D(x=start_position.x, y=start_position.y) +
                Vector2D(x=max_radius * math.cos(emitter.current_route), y=-max_radius*math.sin(emitter.current_route))
            )

        self.approx_x = floor(self.current_position.x/CELL_STEP)
        self.approx_y = floor(self.current_position.y/CELL_STEP)

        if is_tracer:
            if trace_speed is None:
                self.current_speed = Vector2D(length=speed, angle=bullet_route)
            else:
                if trace_route:
                    self.current_speed = Vector2D(length=trace_speed * random.random(), angle=bullet_route) + self.bullet_speed * trace_route
                else:
                    self.current_speed = Vector2D(length=trace_speed * random.random(), angle=bullet_route)
        else:
            if reverse_shot:
                self.current_speed = Vector2D(length=speed, angle=bullet_route + math.pi)
            else:
                self.current_speed = Vector2D(length=speed, angle=bullet_route)
                if emitter.current_speed and not center_shot:
                    self.current_speed += emitter.current_speed

        self.bullet_speed = self.current_speed

        self.candidat_position = Vector2D(x=0, y=0)
        self.ricochet = ricochet
        self.able_to_make_tracing = -able_to_make_tracing if able_to_make_tracing else -100000000
        self.life_limit = life_limit
        self.health = health
        self.fuel = 0
        self.bullet1 = 0
        self.bullet2 = 0

        if not self.health:
            self.size = 0
        else:
            self.size = 5 - (self.health/100) * 25

    @property
    def gun_kwargs(self):
        return {
            'rate_fire': abs(self.health/50) if self.health > -30 else abs(self.health/70),
            'ammo_count': ceil(abs(300/self.health)),
        }

    @property
    def short_data(self):
        return (self.current_position.x, self.current_position.y, self.size)

    def __str__(self):
        return 'B:(%s, %s)' % (self.current_position, self.life_limit)

    def position_abs(self, candidat=True):
        return self.candidat_position if candidat else self.current_position

    def make_tracer(self):

        trace_count_tmp = self.trace_count
        if self.able_to_make_tracing < 0:
            return []

        max_per_frame = (1/app.constants.FRAME_INTERVAL)

        bullets = []
        while (
            trace_count_tmp >= max_per_frame or
            random.random() < trace_count_tmp * app.constants.FRAME_INTERVAL
        ):
            bullets.append(
                Bullet(
                    self,
                    is_tracer=True,
                    ricochet=self.trace_ricochet,
                    speed=self.trace_speed,
                    health=self.trace_health,
                    dispersion=self.trace_dispersion,
                    life_limit=self.trace_life_limit,
                    trace_speed=self.trace_speed,
                    trace_dispersion=None,
                    bullet_speed=self.bullet_speed,
                    trace_route=self.trace_route,
                )
            )

            if trace_count_tmp >= max_per_frame:
                trace_count_tmp -= max_per_frame
            else:
                break
        return bullets

