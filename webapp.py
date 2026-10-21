"""Local web interface for Conjecture Forge / ForgeLang (stdlib HTTP server)."""
from __future__ import annotations

import os
import html
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
# Support running directly from a source checkout without an editable install.
sys.path.insert(0, str(BASE_DIR / "src"))

from conjecture_forge.certificate import write_certificate
from conjecture_forge.forgelang import ForgeLangError, parse_forgelang, to_conjecture
from conjecture_forge.generator import estimate_total_graphs
from conjecture_forge.minimize import minimize_counterexample
from conjecture_forge.search import search_conjecture

EXAMPLE = '''conjecture "Minimum Degree Hamiltonicity":
    V(G in SimpleGraphs:
        (connected(G) & min_degree(G) >= 2) => hamiltonian(G)
    )'''


def run_check(data: dict) -> tuple[int, dict]:
    """Validate and search one API request; separated for straightforward tests."""
    source = data.get("source", "")
    if not isinstance(source, str) or not source.strip():
        return 400, {"status": "INVALID_FORMULA", "error": "Enter a ForgeLang conjecture first."}
    try:
        max_vertices = int(data.get("max_vertices", 5))
        max_graphs = int(data.get("max_graphs", 100000))
    except (TypeError, ValueError):
        return 400, {"status": "INVALID_SETTINGS", "error": "Search limits must be whole numbers."}
    if not 1 <= max_vertices <= 7:
        return 400, {"status": "INVALID_SETTINGS", "error": "Maximum vertices must be between 1 and 7."}
    if not 1 <= max_graphs <= 250000:
        return 400, {"status": "INVALID_SETTINGS", "error": "Maximum graphs must be between 1 and 250,000."}

    try:
        parsed = parse_forgelang(source)
        conjecture = to_conjecture(parsed)
        total_graphs = estimate_total_graphs(max_vertices, 1)
        result = search_conjecture(conjecture, max_vertices=max_vertices, min_vertices=1, max_graphs=max_graphs)
        response = {
            "conjecture_name": parsed.name,
            "statement": parsed.statement,
            "graphs_examined": result.graphs_examined,
            "elapsed_seconds": round(result.elapsed_seconds, 4),
            "max_vertices": max_vertices,
            "max_graphs": max_graphs,
            "theoretical_graph_count": total_graphs,
        }
        if not result.found:
            complete = result.graphs_examined >= total_graphs
            response.update({
                "status": "NO_COUNTEREXAMPLE_WITHIN_BOUND",
                "message": ("No counterexample was found in the explored search. This is not a proof."
                            if complete else "No counterexample was found before the search limit. This is not a proof."),
                "search_complete": complete,
            })
            return 200, response

        graph = minimize_counterexample(result.counterexample, conjecture)
        response.update({
            "status": "COUNTEREXAMPLE_FOUND",
            "message": "A graph satisfying the search domain makes the conjecture false.",
            "search_complete": False,
            "graph": {"n": graph.n, "edges": [list(edge) for edge in sorted(graph.edges)], "degrees": list(graph.degrees())},
            "formula_value": bool(conjecture.conclusion(graph)),
        })
        output_dir = BASE_DIR / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        write_certificate(graph, conjecture, output_dir / "web-counterexample.json")
        response["certificate"] = "output/web-counterexample.json"
        return 200, response
    except ForgeLangError as exc:
        return 400, {"status": "INVALID_FORMULA", "error": str(exc)}
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        return 400, {"status": "INVALID_FORMULA", "error": str(exc)}


class ForgeLangHandler(BaseHTTPRequestHandler):
    server_version = "ForgeLangLocal/0.1"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802 - stdlib handler method name
        path = urlparse(self.path).path
        if path == "/":
            try:
                template = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
                page = template.replace("{{ example }}", html.escape(EXAMPLE))
                self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            except OSError:
                self._send(500, b"Web interface files are missing.", "text/plain; charset=utf-8")
            return
        if path == "/api/examples":
            items = []
            for file_path in sorted((BASE_DIR / "examples").glob("*.forge")):
                try:
                    items.append({"name": file_path.stem.replace("_", " ").title(),
                                  "filename": file_path.name,
                                  "source": file_path.read_text(encoding="utf-8")})
                except OSError:
                    continue
            self._send_json(200, items)
            return
        if path.startswith("/static/"):
            filename = path.removeprefix("/static/")
            if filename not in {"style.css", "app.js"}:
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            asset = BASE_DIR / "static" / filename
            try:
                content = asset.read_bytes()
            except OSError:
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            self._send(200, content, mimetypes.guess_type(filename)[0] + "; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):  # noqa: N802 - stdlib handler method name
        if urlparse(self.path).path != "/api/check":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1_000_000:
                self._send_json(413, {"status": "INVALID_REQUEST", "error": "Request body must be between 1 byte and 1 MB."})
                return
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Request body must be a JSON object.")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send_json(400, {"status": "INVALID_REQUEST", "error": f"Invalid JSON request: {exc}"})
            return
        status, response = run_check(data)
        self._send_json(status, response)

    def log_message(self, format, *args):  # keep local console quiet
        return


def main():
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))

    server = ThreadingHTTPServer((host, port), ForgeLangHandler)
    print(f"ForgeLang web interface running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ForgeLang web interface...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
