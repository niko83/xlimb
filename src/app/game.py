from app.castomization import ship_type_to_ship
from app.constants import DEBUG
from app.game_room import Client

import logging

logger = logging.getLogger('xlimb.' + __name__)


def _join(loop, ws, data):
    from app.game_rooms import get_free_room, queue, restore_socket
    data = data.split(':')

    try:
        client_pk = data[0]
        weapon1 = int(data[1])
        weapon2 = int(data[2])
        name = data[3].replace('"', '').replace("'", '').replace('\\', '')  # @FIXME
        ship_type = int(data[4])
    except Exception:
        logger.warning('wrong input data %s', data)
        if DEBUG:
            raise
        return

    if client_pk and restore_socket(client_pk, ws):
        lggger.info('Restore socket for client_pk: %s', client_pk)
        return

    ship = ship_type_to_ship[ship_type](name, weapon1, weapon2)
    room = get_free_room(loop)

    if room:
        room.add_listenter(Client(ws, ship, is_assigned_to_room=True))
    else:
        queue.push(Client(ws, ship, is_assigned_to_room=False))


def processing(loop, ws, msg_str):
    if ":" in msg_str:
        client_pk, command, data = msg_str.split(':', 2)
    else:
        command = None
        data = None

    if command == 'join':
        _join(loop, ws, data)
    elif command == 'cursor_pos':
        ship_pk, accelerator, vector, shot, shot2 = data.split('!')
        from app.game_rooms import get_room
        room, _ = get_room(client_pk)

        if room:
            room.set_controls(ship_pk, int(accelerator), int(vector), int(shot), int(shot2))
    else:
        logger.warning('Not handled message: "%s"', msg_str)
        return
