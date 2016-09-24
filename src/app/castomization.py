from random import randint, random

from app.bonus import Bonus
from app.bullet import Bullet
from app.ship import Ship
from app.vector import Vector2D


class Ship10(Ship):
    def __init__(self, name, wearpon1, wearpon2, *args, **kwargs):
        self.demensions = [
            Vector2D(x=-7, y=30),
            Vector2D(x=7, y=30),
            Vector2D(x=32, y=10),
            Vector2D(x=12, y=-30),
            Vector2D(x=-12, y=-30),
            Vector2D(x=-32, y=10),
        ]

        # Bot ship
        super(Ship10, self).__init__(
            name=name,
            bullet1_cls=map_weapon1[wearpon1],
            bullet2_cls=map_weapon2[wearpon2],
            ship_type=10,
            *args, **kwargs,
        )
        self.rotation_speed = 3
        self.weight = 0.8
        self.health = 80
        self.engine.power = 800


class Ship20(Ship):
    def __init__(self, name, wearpon1, wearpon2, *args, **kwargs):
        self.demensions = [
            Vector2D(x=-7, y=30),
            Vector2D(x=7, y=30),
            Vector2D(x=32, y=-5),
            Vector2D(x=12, y=-30),
            Vector2D(x=-12, y=-30),
            Vector2D(x=-32, y=-5),
        ]

        super(Ship20, self).__init__(
            name=name,
            bullet1_cls=map_weapon1[wearpon1],
            bullet2_cls=map_weapon2[wearpon2],
            ship_type=20,
            *args, **kwargs,
        )
        self.rotation_speed = 1.12 * 4
        self.weight = 0.70
        self.health = 80
        self.engine.power = self.engine.power * 0.80


class Ship30(Ship):
    def __init__(self, name, wearpon1, wearpon2, *args, **kwargs):
        self.demensions = [
            Vector2D(x=-7, y=30),
            Vector2D(x=7, y=30),
            Vector2D(x=45, y=5),
            Vector2D(x=12, y=-30),
            Vector2D(x=-12, y=-30),
            Vector2D(x=-45, y=5),
        ]
        super(Ship30, self).__init__(
            name=name,
            bullet1_cls=map_weapon1[wearpon1],
            bullet2_cls=map_weapon2[wearpon2],
            ship_type=30,
            *args,
            **kwargs,
        )
        self.health = 170
        self.weight = 1.3
        self.rotation_speed = 0.9*4
        self.engine.power = self.engine.power * 1.10


class Ship11(Ship10):  # No Bot
    def __init__(self, *args, **kwargs):
        super(Ship11, self).__init__(*args, **kwargs)
        self.ship_type = 11
        self.rotation_speed = 4
        self.weight = 1
        self.health = 100
        self.engine.power = 1000


class Ship12(Ship10):  # Bot
    def __init__(self, *args, **kwargs):
        super(Ship12, self).__init__(*args, **kwargs)
        self.ship_type = 12


class Ship21(Ship20):
    def __init__(self, *args, **kwargs):
        super(Ship21, self).__init__(*args, **kwargs)
        self.ship_type = 21


class Ship22(Ship20):
    def __init__(self, *args, **kwargs):
        super(Ship22, self).__init__(*args, **kwargs)
        self.ship_type = 22


class Ship31(Ship30):
    def __init__(self, *args, **kwargs):
        super(Ship31, self).__init__(*args, **kwargs)
        self.ship_type = 31


class Ship32(Ship30):
    def __init__(self, *args, **kwargs):
        super(Ship32, self).__init__(*args, **kwargs)
        self.ship_type = 32


class W11(Bullet):
    def __init__(self, emitter):
        super(W11, self).__init__(
            emitter,
            speed=300,
            ricochet=True,
            life_limit=2,
            health=-2,
            dispersion=0.7,

            able_to_make_tracing=0.1,
            trace_life_limit=0.3,
            trace_health=-2,
            trace_count=5,
            trace_speed=50,
            trace_route=0.5,
        )


class W12(Bullet):
    def __init__(self, emitter):
        super(W12, self).__init__(
            emitter,
            speed=600,
            ricochet=True,
            life_limit=2,
            health=-2,
            dispersion=0.2
        )


class W13(Bullet):
    def __init__(self, emitter):
        super(W13, self).__init__(
            emitter,
            speed=600,
            ricochet=True,
            life_limit=2,
            health=-2,
            dispersion=0
        )


class W21(Bullet):
    def __init__(self, emitter):
        super(W21, self).__init__(
            emitter,
            speed=550,
            ricochet=True, life_limit=2,
            health=-20, dispersion=0.2,
            able_to_make_tracing=0.2,
            trace_speed=0,
            trace_dispersion=0,
            trace_life_limit=4,
            trace_health=-10,
            trace_count=30,
        )


class W22(Bullet):
    def __init__(self, emitter):
        super(W22, self).__init__(
            emitter,
            speed=50,
            ricochet=True,
            life_limit=6,
            health=-100,
            dispersion=0,
            reverse_shot=True,
            able_to_make_tracing=0.01,
            trace_life_limit=1,
            trace_health=-8,
            trace_count=100,
            trace_speed=250,
            trace_ricochet=True,
        )


class W23(Bullet):
    def __init__(self, emitter):
        super(W23, self).__init__(
            emitter,
            speed=700,
            ricochet=False, life_limit=4,
            health=-49, dispersion=0,
            able_to_make_tracing=0.3,
            trace_life_limit=2.0,
            trace_health=-5,
            trace_count=40,
            trace_speed=80,
            trace_route=0.3,
            trace_ricochet=True,
        )


class SmokeBullet(Bullet):
    def __init__(self, emitter, explode_speed=0):
        import math
        super(SmokeBullet, self).__init__(
            emitter,
            speed=randint(30, int(explode_speed+30)) if explode_speed else randint(30, 60),
            life_limit=random() * 0.6,
            health=0,

            dispersion=2*math.pi,
            center_shot=True,
            able_to_make_tracing=False,
            trace_life_limit=0.3,
            trace_health=0,
            trace_count=1,
            trace_speed=180,
        )


class ArtifactBullet(Bullet):
    def __init__(self, emitter):
        super(ArtifactBullet, self).__init__(
            emitter,
            speed=800,
            life_limit=0.6,
            health=-1, is_tracer=True,
            able_to_make_tracing=False
        )


class FuelBonusSmall(Bonus):
    def __init__(self, **kwargs):
        super(FuelBonusSmall, self).__init__(
            fuel=15, **kwargs
        )
        self.type = 100  # 'small_fuel'


class HealthBonusSmall(Bonus):
    def __init__(self, **kwargs):
        super(HealthBonusSmall, self).__init__(
            health=15, **kwargs
        )
        self.type = 200  # 'small_health'


class HealthBonusMedium(Bonus):
    def __init__(self, **kwargs):
        super(HealthBonusMedium, self).__init__(
            health=50, **kwargs
        )
        self.type = 220  # 'medium_health'


class HealthBonusMega(Bonus):
    def __init__(self, **kwargs):
        super(HealthBonusMega, self).__init__(
            health=100, **kwargs
        )
        self.type = 250  # 'mega_health'


class Bullet1BonusSmall(Bonus):
    def __init__(self, **kwargs):
        super(Bullet1BonusSmall, self).__init__(
            bullet1=25, **kwargs
        )
        self.type = 300  # 'small_ammo'


class Bullet2BonusSmall(Bonus):
    def __init__(self, **kwargs):
        super(Bullet2BonusSmall, self).__init__(
            bullet2=2, **kwargs
        )
        self.type = 400  # 'small_roket'

bonus_type_to_str = {
    100: 'small_fuel',
    200: 'small_health',
    220: 'medium_health',
    250: 'mega_health',
    300: 'small_ammo',
    400: 'small_roket',
}

map_weapon1 = {
    1: W11,
    2: W12,
    3: W13,
}
map_weapon2 = {
    1: W21,
    2: W22,
    3: W23,
}
ship_type_to_ship = {
    10: Ship10,
    11: Ship11,
    12: Ship12,
    20: Ship20,
    21: Ship21,
    22: Ship22,
    30: Ship30,
    31: Ship31,
    32: Ship32,
}
