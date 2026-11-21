"""Phone remote: use FreeClipping from a phone on the same Wi-Fi.

The heavy work (recording, speech, rendering) always happens on the PC. The phone is a remote control and viewer:
paste a live link, watch the chat-hype meter, press "clip the last 20 s", and play / save the clips.

Safety rules (this opens the tool to your home network, so they are strict):
  * It is OFF unless FreeClipping is started with NEONCLIPPING_LAN=1.
    Without it the server only listens on 127.0.0.1 and nothing here is reachable.
  * Anything that is not the PC itself needs a 6-digit PIN (shown only on the PC, stored in data/phone.json). After 5 wrong
    tries an address is locked for 10 minutes. A correct PIN gives an HttpOnly cookie.
  * Even with the PIN a phone can only use the live, library, make, status, clips, feedback and creators routes. Uploads,
    file-based tools, the queue and every /phone route stay PC-only.
"""
import hmac
import hashlib
import json
import os
import secrets
import socket
import time
from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

LOCAL = ('127.0.0.1', '::1', 'localhost')
ALLOW = ('/m', '/manifest.webmanifest', '/phone-icon.svg', '/icon-192.png', '/icon-512.png', '/icon-maskable.png',
         '/live', '/live-active', '/library', '/media', '/text', '/make', '/status',
         '/clips', '/feedback', '/creators', '/healthz', '/assets')
MAX_TRIES, LOCK_SECONDS = 5, 600
COOKIE = 'nc_phone'


def is_local(host):
    return host in LOCAL or str(host).startswith('127.')


def allowed(path):
    return any(path == p or path.startswith(p + '/') for p in ALLOW)


def lan_enabled():
    return os.environ.get('NEONCLIPPING_LAN') == '1'


def lan_ips():
    """Private IPv4 addresses of this PC (what a phone on the same Wi-Fi would type)."""
    found = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))                 # no packet is sent; it only picks the outgoing interface
        found.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            found.append(info[4][0])
    except OSError:
        pass
    out = []
    for ip in found:
        parts = ip.split('.')
        private = ip.startswith(('10.', '192.168.')) or (ip.startswith('172.') and len(parts) > 1 and 16 <= int(parts[1]) <= 31)
        if private and ip not in out:
            out.append(ip)
    return out


def attach(app, data, root):
    store = Path(data) / 'phone.json'
    fails = {}          # ip -> [count, first_time]

    def load():
        try:
            j = json.loads(store.read_text(encoding='utf-8'))
            if isinstance(j, dict) and j.get('pin') and j.get('salt'):
                return j
        except (OSError, ValueError):
            pass
        return new_pin()

    def new_pin():
        j = {'pin': f'{secrets.randbelow(10**6):06d}', 'salt': secrets.token_hex(16)}
        tmp = store.with_suffix('.tmp')
        tmp.write_text(json.dumps(j), encoding='utf-8')
        tmp.replace(store)
        return j

    def token(j):
        return hmac.new(j['salt'].encode(), j['pin'].encode(), hashlib.sha256).hexdigest()

    def authed(request):
        got = request.cookies.get(COOKIE, '')
        return bool(got) and hmac.compare_digest(got, token(load()))

    def port_of(request):
        return os.environ.get('NEONCLIPPING_PORT') or str(request.url.port or 8770)

    @app.middleware('http')
    async def gate(request: Request, call_next):
        host = request.client.host if request.client else ''
        if is_local(host):
            return await call_next(request)
        path = request.url.path
        if not lan_enabled():
            return JSONResponse({'detail': 'Phone access is off on this computer.'}, status_code=403)
        if path in ('/m', '/m/login', '/manifest.webmanifest', '/phone-icon.svg', '/icon-192.png', '/icon-512.png', '/icon-maskable.png'):
            return await call_next(request)                 # the page itself and the PIN form carry no data
        if not allowed(path) or path.startswith('/phone'):
            return JSONResponse({'detail': 'This is only available on the PC.'}, status_code=403)
        if not authed(request):
            return JSONResponse({'detail': 'Enter the PIN shown on the PC.'}, status_code=401)
        return await call_next(request)

    @app.get('/m')
    def mobile_page():
        return HTMLResponse((Path(root) / 'mobile.html').read_text(encoding='utf-8'))

    @app.post('/m/login')
    def login(b: dict, request: Request):
        ip = request.client.host if request.client else '?'
        count, first = fails.get(ip, [0, time.time()])
        if count >= MAX_TRIES and time.time() - first < LOCK_SECONDS:
            raise HTTPException(429, 'Too many wrong PINs. Try again in a few minutes.')
        if time.time() - first >= LOCK_SECONDS:
            count, first = 0, time.time()
        j = load()
        if not hmac.compare_digest(str(b.get('pin', '')).strip(), j['pin']):
            fails[ip] = [count + 1, first]
            raise HTTPException(401, 'Wrong PIN.')
        fails.pop(ip, None)
        resp = JSONResponse({'ok': True})
        resp.set_cookie(COOKIE, token(j), httponly=True, samesite='lax', max_age=30 * 24 * 3600)
        return resp

    @app.get('/phone/status')
    def status(request: Request):
        host = request.client.host if request.client else ''
        if not is_local(host):
            raise HTTPException(403, 'This is only available on the PC.')
        port = port_of(request)
        on = lan_enabled()
        return {'enabled': on, 'port': port, 'urls': [f'http://{ip}:{port}/m' for ip in lan_ips()] if on else [], 'pin': load()['pin'] if on else None}

    @app.post('/phone/newpin')
    def newpin(request: Request):
        host = request.client.host if request.client else ''
        if not is_local(host):
            raise HTTPException(403, 'This is only available on the PC.')
        return {'pin': new_pin()['pin']}

    @app.get('/manifest.webmanifest')
    def manifest():
        return JSONResponse({'name': 'FreeClipping', 'short_name': 'FreeClipping', 'start_url': '/m', 'scope': '/', 'display': 'standalone',
                             'background_color': '#07090e', 'theme_color': '#07090e',
                             'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
                                       {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
                                       {'src': '/icon-maskable.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]},
                            media_type='application/manifest+json')

    def icon_file(name):
        # 3D app icons - icons/app-icon-*.png are generated by tools/build_icons.py from the master art
        path = root / 'icons' / name
        if not path.exists():
            raise HTTPException(404, 'Icon not installed')
        return FileResponse(path, media_type='image/png')

    @app.get('/phone-icon.svg')
    def icon():
        # kept for backwards compatibility - the .svg URL now serves the real 3D icon
        return icon_file('app-icon-512.png')

    @app.get('/icon-192.png')
    def icon_192():
        return icon_file('app-icon-192.png')

    @app.get('/icon-512.png')
    def icon_512():
        return icon_file('app-icon-512.png')

    @app.get('/icon-maskable.png')
    def icon_maskable():
        return icon_file('app-icon-maskable-512.png')
