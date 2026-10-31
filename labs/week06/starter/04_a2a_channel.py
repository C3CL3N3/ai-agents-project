"""A small A2A-style channel built for the Week 6 take-home.

This is a local teaching channel, not a certified A2A implementation. It
keeps the three ideas that matter here: capability discovery, task states,
and typed artifacts.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8972

AGENT_CARD = {
    "name": "translation-agent",
    "description": "Translates short administrative texts.",
    "url": f"http://127.0.0.1:{PORT}",
    "version": "1.0",
    "skills": [{
        "id": "translate",
        "name": "Translate a short text",
        "description": "Translates between French, German, and English.",
        "inputModes": ["text/plain"],
        "outputModes": ["text/plain"],
    }],
}

TRANSLATIONS = {
    "opening hours": "heures d'ouverture",
    "waste collection": "collecte des dechets",
}


class AgentHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/.well-known/agent.json":
            self.send_json(200, AGENT_CARD)
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        request = json.loads(self.rfile.read(length) or b"{}")
        task_id = request.get("taskId", "task-1")
        text = request.get("message", {}).get("parts", [{}])[0].get(
            "text", "")

        if "FAIL" in text:
            self.send_json(200, {
                "taskId": task_id,
                "state": "failed",
                "error": "translation is not available",
            })
            return
        if "SLOW" in text:
            time.sleep(5)
        if "EMPTY" in text:
            artifact = {"parts": [{"data": {"unsupported": True}}]}
        else:
            artifact = {"parts": [{
                "text": TRANSLATIONS.get(text.strip(), f"[fr] {text.strip()}")
            }]}
        self.send_json(200, {
            "taskId": task_id,
            "state": "completed",
            "artifact": artifact,
        })

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve() -> None:
    ThreadingHTTPServer(("127.0.0.1", PORT), AgentHandler).serve_forever()


def fetch_card() -> dict:
    with urllib.request.urlopen(
            f"http://127.0.0.1:{PORT}/.well-known/agent.json",
            timeout=5) as response:
        return json.loads(response.read())


def send_task(text: str, task_id: str, timeout: float = 3.0) -> dict:
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/",
        data=json.dumps({
            "taskId": task_id,
            "message": {"parts": [{"text": text}]},
        }).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def main() -> int:
    server = mp.Process(target=serve, daemon=True)
    server.start()
    time.sleep(0.5)
    try:
        card = fetch_card()
        skills = {skill["id"] for skill in card["skills"]}
        print("card:", card["name"], sorted(skills))
        if "translate" not in skills:
            raise RuntimeError("remote agent does not advertise translate")

        completed = send_task("opening hours", "task-1")
        print("completed:", completed)

        failed = send_task("FAIL please", "task-2")
        print("failed:", failed)

        try:
            send_task("SLOW please", "task-3", timeout=1.0)
        except (urllib.error.URLError, TimeoutError) as exc:
            print("timed out:", type(exc).__name__, "task id kept: task-3")

        no_text = send_task("EMPTY please", "task-4")
        parts = no_text["artifact"]["parts"]
        if not any("text" in part for part in parts):
            print("artifact mismatch:", parts)
        return 0
    finally:
        server.terminate()


if __name__ == "__main__":
    mp.set_start_method("spawn")
    raise SystemExit(main())
