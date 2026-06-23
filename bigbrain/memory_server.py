# bigbrain/memory_server.py

import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from memory_store import save_memory, search_memory, format_memories


HOST = "127.0.0.1"
PORT = 7010


class MemoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        if not body:
            return {}

        return json.loads(body)

    def do_POST(self):
        try:
            data = self._read_json()

            if self.path == "/save":
                text = data.get("text", "").strip()
                memory_type = data.get("memory_type", "general")

                if not text:
                    self._send_json({
                        "ok": False,
                        "error": "No text provided."
                    }, status=400)
                    return

                result = save_memory(text, memory_type=memory_type)

                self._send_json({
                    "ok": True,
                    "result": result
                })
                return

            if self.path == "/search":
                query = data.get("query", "").strip()
                n_results = int(data.get("n_results", 5))

                if not query:
                    self._send_json({
                        "ok": True,
                        "result": "No relevant long-term memories.",
                        "raw": []
                    })
                    return

                memories = search_memory(query, n_results=n_results)
                formatted = format_memories(memories)

                self._send_json({
                    "ok": True,
                    "result": formatted,
                    "raw": memories
                })
                return

            self._send_json({
                "ok": False,
                "error": f"Unknown path: {self.path}"
            }, status=404)

        except Exception as e:
            self._send_json({
                "ok": False,
                "error": str(e)
            }, status=500)

    def log_message(self, format, *args):
        return


def main():
    print(f"Memory server online at http://{HOST}:{PORT}")
    print("Loading memory system once and keeping it alive.")

    server = ThreadingHTTPServer((HOST, PORT), MemoryHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()