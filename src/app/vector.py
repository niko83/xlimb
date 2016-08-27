import math


class Vector2D:
    def __init__(self, x=None, y=None, angle=None, length=None):
        if x is None:
            self.x = math.cos(angle) * length
            self.y = math.sin(angle) * length
        else:
            self.x = x
            self.y = y

    def reinit(self, x=None, y=None, angle=None, length=None):
        if x is None:
            self.x = math.cos(angle) * length
            self.y = math.sin(angle) * length
        else:
            self.x = x
            self.y = y

    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def angle(self):
        if self.x == 0:
            if self.y == 0:
                return 0
            elif self.y > 0:
                return math.pi/2
            else:
                return math.pi * 3 / 2
        angle = abs(math.atan(self.y / self.x))
        if self.x < 0:
            if self.y < 0:
                return math.pi + angle
            else:
                return math.pi - angle
        else:
            if self.y < 0:
                return 2 * math.pi - angle
            else:
                return angle

    def __repr__(self):
        return 'Vector2D({}, {}, {})'.format(self.x, self.y, self.angle())

    def __str__(self):
        return 'Vector(%.1f, %.1f, %.1f)' % (
            self.x, self.y, math.degrees(self.angle())
        )

    def __mul__(self, scalar):
        return Vector2D(self.x*scalar, self.y*scalar)

    def __truediv__(self, scalar):
        return Vector2D(self.x/scalar, self.y/scalar)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self


    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return self.x != 0 or self.y != 0

    def __neg__(self):
        return Vector2D(-self.x, -self.y)
