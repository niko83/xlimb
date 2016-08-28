from math import floor
import os
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')


TEST_BOT = False
DEBUG = True

ROOMS_BY_CORE, CLIENT_ROOM_LIMIT = 6, 4
INTERVAL_QUEUE_NOTIFICATION = 1

if TEST_BOT:
    MAP_SIZE = (1200, 800)
    VIEWPORT_SIZE = (1077, 662)
    #  MAP_SIZE = (3371, 1889)
    #  VIEWPORT_SIZE = (1077, 662)
    G = 45
    GAME_SPEED = 1.3
else:
    G = 45
    MAP_SIZE = (3371, 1889)
    VIEWPORT_SIZE = (1077, 662)
    GAME_SPEED = 1.3
CELL_STEP = 60
CLIENT_TIMEOUT = 600  # seconds

MAP_SIZE_APPROX = (floor(MAP_SIZE[0]/CELL_STEP)+1, floor(MAP_SIZE[1]/CELL_STEP)+1)

G_DIVE = 645
MU = 1.2
FRAME_INTERVAL = 0.015


class DeadReason:
    KILL = 'kill'
    SUICIDE = 'suicide'
    WORLD_COLLISION = 'world_collision'
    WORLD_COLLISION_BIRTH = 'world_collision_birth'
    RAMPING = 'ramping'
