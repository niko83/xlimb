#!/usr/bin/env python
from sys import argv

from aiohttp import web

from app import game
from app.game_rooms import queue


app = web.Application()

queue.init_loop(app.loop)
queue.start()

async def game_room(request):
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
