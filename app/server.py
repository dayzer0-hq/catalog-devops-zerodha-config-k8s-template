"""Zerodha console service. Reads every setting from the environment and reports them.

It reports them so you can PROVE a ConfigMap and a Secret actually reached the pod — a
manifest that looks right and a pod that received the values are different claims.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

NON_SENSITIVE = ["ENVIRONMENT", "MARKET_OPEN_IST", "MAX_WATCHLIST_SIZE", "FEATURE_BASKET_ORDERS"]
SENSITIVE = ["DATABASE_URL", "BROKER_API_SECRET"]


def settings():
    out = {k: os.environ.get(k, "<unset>") for k in NON_SENSITIVE}
    # Sensitive values are reported as present/absent and NEVER echoed. A debug endpoint that
    # prints a secret is how a Secret ends up in a log aggregator.
    for k in SENSITIVE:
        out[k] = "<set>" if os.environ.get(k) else "<unset>"
    return out


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"{self.command} {self.path}", flush=True)
        path = self.path.split("?")[0]
        if path in ("/settings", "/"):
            body, code = json.dumps(settings()).encode(), 200
        elif path == "/healthz":
            body, code = json.dumps({"alive": True}).encode(), 200
        else:
            body, code = json.dumps({"error": "not found"}).encode(), 404
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"zerodha console listening on {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
