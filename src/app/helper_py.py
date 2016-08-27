import math

from app.polygon_data import all_polygons

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

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_polygon_idx_collision(x, y):
    for idx, polygon in enumerate(all_polygons):
        if in_polygon_idx(x, y, idx):
            return idx
    return False
