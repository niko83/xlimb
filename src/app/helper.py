import math
import os
import pickle

from bitarray import bitarray

from my_module import (
    distance,
    in_polygon as in_polygon_idx,
    resolve_line,
    get_polygon_idx_collision
)

from app.constants import MAP_SIZE_APPROX, CELL_STEP, ROOT_DIR
from app.polygon_data import all_polygons
from app.vector import Vector2D


def in_polygon_info(x, y, polygon_info):

    polygon_edge = polygon_info[2]

    if x < polygon_edge[0] or x > polygon_edge[1] or y < polygon_edge[2] or y > polygon_edge[3]:
        return False

    return _in_polygon(x, y, polygon_info[0], polygon_info[1])

def _in_polygon(x, y, xp, yp):
    c=0
    for i in range(len(xp)):
        if (
            (
                (yp[i]<=y<yp[i-1]) or (yp[i-1]<=y<yp[i])
            ) and (
                x > (xp[i-1]-xp[i]) * (y-yp[i]) / (yp[i-1]-yp[i]) + xp[i]
            )
        ):
            c = 1 - c

    return c % 2 == 1

def get_intersection_angle(p1, p2, p3, p4):
    K1, B1 = resolve_line((p1.x, p1.y), (p2.x, p2.y))
    K2, B2 = resolve_line((p3.x, p3.y), (p4.x, p4.y))

    if K1 == K2:
        return None
    if K1 is None and B1 is None:
        x = p1.x
    elif K2 is None and B2 is None:
        x = p3.x
    else:
        x = (B2 - B1)/(K1 - K2)
    if (p1.x<=x<=p2.x) or (p2.x<=x<=p1.x):  # has intersection

        nil_vector_ship = (p2 - p1)
        nil_vector_polygon1= (p4 - p3).angle()
        if nil_vector_polygon1 >= math.pi:
            nil_vector_polygon1 -= math.pi

        angle_intersection = nil_vector_ship.angle() - nil_vector_polygon1
        while angle_intersection > math.pi/2:
            angle_intersection -= math.pi

        return angle_intersection

    return None


def get_angle_collision(object2d, polygon):

    prev_point = object2d.current_position
    next_point = object2d.candidat_position

    for idx, _ in enumerate(polygon):
        angle = get_intersection_angle(prev_point, next_point, polygon[idx], polygon[idx-1])
        if angle is not None:
            return angle




def dump_edge():
    for polygon in all_polygons:
        print(
            '{%d, %d, %d, %d};' % (
                min(p.x for p in polygon),
                max(p.x for p in polygon),
                min(p.y for p in polygon),
                max(p.y for p in polygon)
            )
        )


def get_polygon_info(polygon):
    xp = [p.x for p in polygon]
    yp = [p.y for p in polygon]
    edge = (min(xp), max(xp), min(yp), max(yp))
    return xp, yp, edge



polygon_cell = []
def _calculate_polygon_cell():
    for x in range(MAP_SIZE_APPROX[0] + 1):
        polygon_cell.append([])
        class _FakeObject2D:
            def __init__(self, x, y):
                self.candidat_position = Vector2D(x=x, y=y)

        for y in range(MAP_SIZE_APPROX[1] + 1):
            cell = [
                _FakeObject2D(x=x*CELL_STEP, y=y*CELL_STEP),
                _FakeObject2D(x=x*CELL_STEP, y=(y+1)*CELL_STEP),
                _FakeObject2D(x=(x+1)*CELL_STEP, y=y*CELL_STEP),
                _FakeObject2D(x=(x+1)*CELL_STEP, y=(y+1)*CELL_STEP),
            ]

            for cell_point in cell:
                if get_polygon_idx_collision(cell_point.candidat_position.x, cell_point.candidat_position.y):
                    polygon_cell[x].append(True)
                    break
            else:
                polygon_cell[x].append(False)

        polygon_cell[x] = bitarray(polygon_cell[x])


_calculate_polygon_cell()
if ROOT_DIR:
    with open(os.path.join(ROOT_DIR, 'cache_map.pickle'), 'wb') as f:
        pickle.dump(polygon_cell, f)
