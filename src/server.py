#!/usr/bin/env python
import gc
gc.disable()
gc.set_debug(gc.DEBUG_STATS)
from sys import argv

from aiohttp import web

from app import init_log
from app import game
from app.game_rooms import queue
init_log()

import logging
logger = logging.getLogger('xlimb.' + __name__)
logger.info('Server start: %s', argv)


app = web.Application()

queue.init_loop(app.loop)
queue.start()

async def game_room(request):
    logger.info("Start request: %s", request.transport.get_extra_info('peername'))

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.tp == web.MsgType.text:
            game.processing(app.loop, ws, msg.data)
        elif msg.tp == web.MsgType.binary:
            ws.send_bytes(msg.data)
        elif msg.tp == web.MsgType.close:
            break
    return ws

app.router.add_route('GET', '/ws/', game_room)
if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=argv[1])  # , shutdown_timeout=1)
