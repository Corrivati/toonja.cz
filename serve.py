"""Local preview: `python3 serve.py`, then open http://localhost:8000

Serves the site the same way GitHub Pages / Netlify / Cloudflare Pages do:
/o-mne -> o-mne.html, /blog/ -> blog/index.html, unknown paths -> 404.html.
No dependencies beyond Python 3.
"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        local = self.translate_path(path)
        if not os.path.exists(local) and os.path.exists(local + ".html"):
            self.path = path + ".html"
        elif not os.path.exists(local):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(ROOT, "404.html"), "rb") as f:
                self.wfile.write(f.read())
            return None
        return super().send_head()


if __name__ == "__main__":
    print(f"Preview on http://localhost:{PORT}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
