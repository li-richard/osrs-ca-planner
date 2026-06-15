#!/usr/bin/env python3
"""
Launcher for the OSRS Combat Achievements planner.

Serves the app on http://localhost:8765 AND proxies the WikiSync lookup
server-side, which sidesteps the browser CORS / Cloudflare problem you hit
when opening the .html file directly.

Run:   python3 serve.py
Then open the URL it prints (it tries to open your browser automatically).
Stop with Ctrl-C.
"""
import http.server, socketserver, urllib.request, urllib.error, urllib.parse, json, sys, os, webbrowser, threading

PORT = int(os.environ.get("PORT", "8765"))
APP_FILE = "osrs-combat-achievements.html"
UA = "osrs-ca-planner/1.0 (local; +https://oldschool.runescape.wiki)"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("  " + (fmt % args) + "\n")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" :
            self.path = "/" + APP_FILE
            return super().do_GET()
        if parsed.path == "/api/wikisync":
            return self.proxy_wikisync(urllib.parse.parse_qs(parsed.query))
        return super().do_GET()

    def proxy_wikisync(self, q):
        name = (q.get("name") or [""])[0].strip()
        profile = (q.get("profile") or ["STANDARD"])[0].strip() or "STANDARD"
        if not name:
            return self._json(400, {"error": "Missing name."})
        target = "https://sync.runescape.wiki/runelite/player/%s/%s" % (
            urllib.parse.quote(name), urllib.parse.quote(profile))
        req = urllib.request.Request(target, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
                return self._raw(r.status, body)
        except urllib.error.HTTPError as e:
            # pass upstream status + body through (e.g. 400 NO_USER_DATA)
            return self._raw(e.code, e.read())
        except Exception as e:
            return self._json(502, {"error": "Proxy could not reach WikiSync: %s" % e})

    def _raw(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status, obj):
        self._raw(status, json.dumps(obj).encode())

def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = "http://localhost:%d/" % PORT
        print("\n  OSRS CA planner running at  %s" % url)
        print("  (live WikiSync lookup is proxied through this server)")
        print("  Press Ctrl-C to stop.\n")
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Stopped.")

if __name__ == "__main__":
    main()
