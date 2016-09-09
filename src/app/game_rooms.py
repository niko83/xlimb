import json
import gc

import app
from app import constants
import datetime
from app.game_room import GameRoom
import logging
logger = logging.getLogger('xlimb.' + __name__)


_rooms = []
_palyers_queues = []


def get_room(pk):
    for room in _rooms:
        for client in room.clients:
            if client.pk == pk:
                return room, client
    return None, None


def restore_socket(client_pk, ws):

    room, client = get_room(client_pk)
    if client:
        client.ws = ws
        room.add_listenter(client, restore=True)
        return client

    return False


class _Queue:

    def __init__(self):
        self._queue = []
        self._loop = None

    def init_loop(self, loop):
        self._loop = loop

    def run(self):
        for idx, client in enumerate(self._queue):
            if client.ws.closed or client.is_assigned_to_room:
                del self._queue[idx]
                continue

            client.ws.send_str(json.dumps({
                'command': 'waiting',
                'data': {
                    'client_pk': client.pk,
                    'queue_position': idx+1,
                    'queue_size': self.count_q_players,
                }
            }))

    def _gc_collect(self):
        gc.collect()
        self._handler3 = self._loop.call_later(3600, self._gc_collect)

    def _run_stat(self):

        logger.info('[Q:%d, R:%d Bul:%d Bon:%d] fps:%d Traffic:%.1fMb Rooms:%s' % (
            self.count_q_players,
            self.count_active_players,
            sum(len(r.bullets) for r in _rooms),
            sum(len(r.bonuses) for r in _rooms),
            1/app.constants.FRAME_INTERVAL,
            app.game_room.SUMMARY_TRAFFIC / 1024/1024,
            ', '.join("[%s/%s/%s]" % r.get_stat() for r in _rooms),
        ))

        self._handler2 = self._loop.call_later(constants.INTERVAL_SUMMARY_STAT, self._run_stat)

    def _run(self):
        self.run()
        self._handler = self._loop.call_later(constants.INTERVAL_QUEUE_NOTIFICATION, self._run)

    def start(self):
        self._handler = self._loop.call_later(0, self._run)
        self._handler2 = self._loop.call_later(1, self._run_stat)
        self._handler3 = self._loop.call_later(20, self._gc_collect)

    @property
    def count_active_players(self):
        return sum(len(r.clients) for r in _rooms)

    @property
    def count_q_players(self):
        return len(self._queue)

    def push(self, client):
        self._queue.append(client)
        client.ws.send_str(json.dumps({
            'command': 'waiting',
            'data': {'client_pk': client.pk, 'queue': self.count_q_players}
        }))

    def pop(self):
        for cl in self._queue:
            if cl.is_assigned_to_room is False:
                cl.is_assigned_to_room = True
                return cl

queue = _Queue()


def get_free_room(loop, am_i_bot):

    if not _rooms:
        room = GameRoom(loop)
        _rooms.append(room)
        return room

    sorted_rooms = sorted(
        _rooms,
        key=lambda r:  (len(r.clients), r.clients_without_bots) if am_i_bot else (r.clients_without_bots, 0),
        reverse=True
    )

    if am_i_bot:
        len_players = len(sorted_rooms[-1].clients)
    else:
        len_players = sorted_rooms[-1].clients_without_bots

    if len_players >= constants.CLIENT_ROOM_LIMIT:
        if len(_rooms) < constants.ROOMS_BY_CORE:
            room = GameRoom(loop)
            _rooms.append(room)
            return room
        else:
            return None

    for room in sorted_rooms:
        if (len(room.clients) if am_i_bot else room.clients_without_bots) < constants.CLIENT_ROOM_LIMIT:
            return room
