import asyncio
import json
import os
import random
import re
import string
import pathlib

from aiohttp import web, WSMsgType

ROOT = pathlib.Path(__file__).parent
INDEX_FILE = ROOT / "static" / "index.html"

# room_code -> {'members': [WebSocketResponse, ...] (join order, index 0 = host),
#               'spectators': [WebSocketResponse, ...], 'capacity': int, 'rankedMode': str|None}
# capacity is fixed by whoever creates the room. For plain online (rankedMode is
# None): 2 = 1v1, 4 = 2v2, team assignment is index%2. For ranked-with-friends
# (rankedMode set): capacity = how many *humans* share team 0 (2 for rankedDuos,
# 3 for rankedTrios) — the rest of the battle royale is bots the host simulates.
# Spectators are extra sockets that receive every 'game' broadcast for the room but
# never count toward capacity and are never relayed as a source of truth themselves.
# Either way the server stays a dumb relay; it only remembers rankedMode so it can
# hand it back to whoever joins (the creator already knows what they asked for).
rooms = {}
DEFAULT_CAPACITY = 2
VALID_CAPACITIES = (2, 3, 4)
CUSTOM_CODE_RE = re.compile(r'^[A-Z0-9]{3,10}$')


def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


async def index(request):
    return web.FileResponse(INDEX_FILE)


async def ws_handler(request):
    ws = web.WebSocketResponse(heartbeat=25)
    await ws.prepare(request)
    ws.room = None
    ws.is_spectator = False

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
            except ValueError:
                continue
            t = data.get('type')

            if t == 'create':
                capacity = data.get('capacity', DEFAULT_CAPACITY)
                if capacity not in VALID_CAPACITIES:
                    capacity = DEFAULT_CAPACITY
                ranked_mode = data.get('rankedMode')
                if ranked_mode not in ('rankedDuos', 'rankedTrios'):
                    ranked_mode = None
                custom_code = (data.get('customCode') or '').strip().upper()
                if custom_code:
                    if not CUSTOM_CODE_RE.match(custom_code):
                        await ws.send_str(json.dumps({'type': 'codeInvalid'}))
                        continue
                    if custom_code in rooms:
                        await ws.send_str(json.dumps({'type': 'codeTaken'}))
                        continue
                    code = custom_code
                else:
                    code = gen_code()
                    while code in rooms:
                        code = gen_code()
                rooms[code] = {'members': [ws], 'spectators': [], 'capacity': capacity, 'rankedMode': ranked_mode}
                ws.room = code
                await ws.send_str(json.dumps({
                    'type': 'created', 'room': code, 'capacity': capacity, 'rankedMode': ranked_mode,
                }))

            elif t == 'join':
                code = (data.get('room') or '').strip().upper()[:10]
                entry = rooms.get(code)
                if entry is None:
                    await ws.send_str(json.dumps({'type': 'notfound'}))
                elif len(entry['members']) >= entry['capacity']:
                    await ws.send_str(json.dumps({'type': 'full'}))
                else:
                    members = entry['members']
                    members.append(ws)
                    ws.room = code
                    await ws.send_str(json.dumps({
                        'type': 'joined', 'room': code, 'capacity': entry['capacity'],
                        'rankedMode': entry.get('rankedMode'), 'waiting': len(members) < entry['capacity'],
                    }))
                    if len(members) == entry['capacity']:
                        for i, peer in enumerate(members):
                            await peer.send_str(json.dumps({
                                'type': 'ready', 'you': i, 'capacity': entry['capacity'],
                                'rankedMode': entry.get('rankedMode'),
                            }))

            elif t == 'spectate':
                code = (data.get('room') or '').strip().upper()[:10]
                entry = rooms.get(code)
                if entry is None:
                    await ws.send_str(json.dumps({'type': 'notfound'}))
                else:
                    entry['spectators'].append(ws)
                    ws.room = code
                    ws.is_spectator = True
                    await ws.send_str(json.dumps({
                        'type': 'spectating', 'room': code, 'capacity': entry['capacity'],
                        'rankedMode': entry.get('rankedMode'),
                    }))

            elif t == 'game':
                if ws.is_spectator:
                    continue
                entry = rooms.get(ws.room)
                if entry:
                    for peer in entry['members']:
                        if peer is not ws and not peer.closed:
                            await peer.send_str(msg.data)
                    for peer in entry['spectators']:
                        if not peer.closed:
                            await peer.send_str(msg.data)

        elif msg.type == WSMsgType.ERROR:
            break

    entry = rooms.get(ws.room)
    if entry is not None:
        if ws.is_spectator:
            if ws in entry['spectators']:
                entry['spectators'].remove(ws)
        else:
            members = entry['members']
            if ws in members:
                members.remove(ws)
            for peer in members:
                if not peer.closed:
                    await peer.send_str(json.dumps({'type': 'peerLeft'}))
            for peer in entry['spectators']:
                if not peer.closed:
                    await peer.send_str(json.dumps({'type': 'peerLeft'}))
            if not members:
                rooms.pop(ws.room, None)

    return ws


app = web.Application()
app.router.add_get('/ws', ws_handler)
app.router.add_get('/', index)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Axel's Royale escuchando en http://0.0.0.0:{port}")
    web.run_app(app, host='0.0.0.0', port=port)
