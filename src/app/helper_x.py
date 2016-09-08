import math
from math import floor
import app
from app.constants import CELL_STEP

from app.polygon_data import all_polygons
from app.helper import get_angle_collision, polygon_cell




def get_polygon_info(polygon):
    xp = [p.x for p in polygon]
    yp = [p.y for p in polygon]
    edge = (min(xp), max(xp), min(yp), max(yp))
    return xp, yp, edge

all_polygons_edge = []
all_polygons_x = []
all_polygons_y = []
for idx, points in enumerate(all_polygons):
    xp, yp, edge = get_polygon_info(points)
    all_polygons_x.append(xp)
    all_polygons_y.append(yp)
    all_polygons_edge.append(edge)

all_polygons_edge = tuple(all_polygons_edge)


def resolve_line(p1, p2):
    if p2[0] == p1[0]:
        return None, None  # vertical
    K = (p2[1] - p1[1]) / (p2[0] - p1[0])
    B = p2[1] - K * p2[0]
    return K, B


def in_polygon_idx(x, y, idx):
    polygon_edge = all_polygons_edge[idx]
    if x < polygon_edge[0] or x > polygon_edge[1] or y < polygon_edge[2] or y > polygon_edge[3]:
        return False

    xp = all_polygons_x[idx]
    yp = all_polygons_y[idx]
    c = 0
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


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def get_polygon_idx_collision(x, y):
    for idx, polygon in enumerate(all_polygons):
        if in_polygon_idx(x, y, idx):
            return idx
    return False


#  from xlimb_helper import get_polygon_idx_collision
#  from xlimb_helper import resolve_line, get_polygon_idx_collision
#  from xlimb_helper import distance, get_polygon_idx_collision

def calculate_position(self):

    self.life_limit -= app.constants.FRAME_INTERVAL

    if self.able_to_make_tracing > -100:
        self.able_to_make_tracing += app.constants.FRAME_INTERVAL

    if self.current_speed.x == self.current_speed.y == 0:
        return

    candidat_position_x = self.current_position.x + self.current_speed.x*app.constants.FRAME_INTERVAL
    candidat_position_y = self.current_position.y - self.current_speed.y*app.constants.FRAME_INTERVAL

    self.approx_x = floor(candidat_position_x/CELL_STEP)
    self.approx_y = floor(candidat_position_y/CELL_STEP)

    try:
        if polygon_cell[self.approx_x][self.approx_y]:
            polygon_idx = get_polygon_idx_collision(candidat_position_x, candidat_position_y)
            if polygon_idx:
                polygon = all_polygons[polygon_idx]
            else:
                polygon = None
        else:
            polygon = None
    except IndexError:
        self.approx_x = self.approx_y = 0
        polygon = None

    if polygon and not self.ricochet:
        self.life_limit = -1
        return

    if polygon and self.ricochet:

        self.candidat_position.reinit(
            x=candidat_position_x,
            y=candidat_position_y,
        )

        angle = get_angle_collision(self, polygon)
        if angle is None:
            self.life_limit = -1  # выстрел прямо в скале
            return

        self.current_speed.reinit(
            length=self.current_speed.length,
            angle=angle*2 + self.current_speed.angle()
        )
        return

    self.current_position.reinit(
        x=candidat_position_x,
        y=candidat_position_y,
    )
