#!/usr/bin/env python3
import argparse
import http.client
import http.server
import os
import socketserver
import sys
import urllib.parse


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    api_host = "127.0.0.1"
    api_port = 7860
    web_root = "/root/G0DM0D3"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=self.web_root, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        if self.path.startswith("/v1/"):
            self._proxy_request()
            return
        self.send_response(204)
        self.send_header("Allow", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/v1/"):
            self._proxy_request()
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/v1/"):
            self._proxy_request()
            return
        self.send_error(405, "Method not allowed")

    def do_HEAD(self):
        if self.path.startswith("/v1/"):
            self._proxy_request()
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_HEAD()

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt % args))
        sys.stdout.flush()

    def _proxy_request(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        if parsed.query:
            path = f"{path}?{parsed.query}"

        body = None
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))

        conn = http.client.HTTPConnection(self.api_host, self.api_port, timeout=120)
        headers = {}
        for key, value in self.headers.items():
            if key.lower() in {"host", "connection"}:
                continue
            headers[key] = value
        headers["Host"] = f"{self.api_host}:{self.api_port}"

        try:
            conn.request(self.command, path, body=body, headers=headers)
            upstream = conn.getresponse()
            self.send_response(upstream.status, upstream.reason)

            for key, value in upstream.getheaders():
                lower = key.lower()
                if lower in {"transfer-encoding", "connection", "server", "date"}:
                    continue
                self.send_header(key, value)
            self.end_headers()

            while True:
                chunk = upstream.read(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except Exception as exc:
            self.send_error(502, f"Upstream API error: {exc}")
        finally:
            conn.close()


def main():
  parser = argparse.ArgumentParser(description="Serve G0DM0D3 static UI with /v1 proxy.")
  parser.add_argument("--root", required=True, help="Path to the G0DM0D3 web root")
  parser.add_argument("--port", type=int, default=3000, help="Port to serve the UI on")
  parser.add_argument("--api-port", type=int, default=7860, help="Local API port")
  args = parser.parse_args()

  ProxyHandler.web_root = os.path.abspath(args.root)
  ProxyHandler.api_port = args.api_port

  class ThreadingServer(http.server.ThreadingHTTPServer):
      daemon_threads = True

  with ThreadingServer(("127.0.0.1", args.port), ProxyHandler) as httpd:
      print(f"G0DM0D3 web proxy listening on http://127.0.0.1:{args.port}", flush=True)
      httpd.serve_forever()


if __name__ == "__main__":
    main()
