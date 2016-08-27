import json
import websocket
import time
import sys

collection = []
for i in range(int(sys.argv[1])):
    time.sleep(0.1)
    ws = websocket.WebSocket()
    ws.connect('ws://www.xlimb.loc/ws/')
    ws.send(':join::3:3:test_bot_%s:20' % i)

    collection.append(ws)
    print(i, end='-', flush=True)

print('')
print('geting')

while True:
    print('.', end='', flush=True)
    for ws in collection:
        ws.recv()



time.sleep(500)
