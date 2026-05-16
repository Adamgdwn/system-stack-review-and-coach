"""Local web server that exposes the System Coach browser GUI and JSON API."""

from __future__ import annotations

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import threading
import webbrowser

from .agents import build_agents
from .ai_engine import answer_question, reason_about_request
from .diagnostics import collect_diagnostics
from .maintenance_actions import build_action_contract, execute_guarded_action
from .maintenance_history import load_history, record_maintenance_report, record_request_plan
from .maintenance_history import record_action_result
from .maintenance_reporting import generate_maintenance_report
from .reporting import generate_report
from .request_evidence import collect_request_evidence
from .request_plans import prepare_request_plan
from .scanner import map_filesystem, suggest_roots


WEB_ROOT = Path(__file__).resolve().parent / "web"


def build_report() -> dict:
    results = [agent.run() for agent in build_agents()]
    return generate_report(results)


def build_maintenance_report() -> dict:
    report = generate_maintenance_report(collect_diagnostics())
    record_maintenance_report(report)
    return report


class SystemCoachHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/api/report":
            self._send_json(build_report())
            return
        if self.path == "/api/scan-options":
            self._send_json({"suggested_roots": suggest_roots()})
            return
        if self.path == "/api/maintenance":
            self._send_json(build_maintenance_report())
            return
        if self.path == "/api/history":
            self._send_json(load_history())
            return
        if self.path == "/health":
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path not in {"/api/map", "/api/request-plan", "/api/action-contract", "/api/action-run", "/api/ask"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON payload")
            return

        if self.path == "/api/request-plan":
            request_text = str(payload.get("request", ""))
            os_name = payload.get("os_name")
            desktop_hint = payload.get("desktop_hint")
            maintenance_report = payload.get("maintenance_report")
            evidence = collect_request_evidence(
                request_text,
                os_name=str(os_name) if os_name else None,
                desktop_hint=str(desktop_hint) if desktop_hint else None,
            )
            reasoning = reason_about_request(
                request_text,
                os_name=str(os_name) if os_name else None,
                desktop_hint=str(desktop_hint) if desktop_hint else None,
                maintenance_report=maintenance_report if isinstance(maintenance_report, dict) else None,
                request_evidence=evidence,
            )
            reasoning["request_evidence"] = evidence
            if not reasoning.get("ok"):
                reasoning = {
                    "source": "deterministic-fallback",
                    "model": None,
                    "family": None,
                    "ready": True,
                    "confidence": None,
                    "reasoning_summary": reasoning.get("reasoning_summary", ""),
                    "request_evidence": evidence,
                }
            plan = prepare_request_plan(
                request_text,
                os_name=str(os_name) if os_name else None,
                distribution_hint=str(desktop_hint) if desktop_hint else None,
                family_override=reasoning.get("family"),
                reasoning=reasoning,
            )
            record_request_plan(plan)
            self._send_json(plan)
            return

        if self.path == "/api/action-contract":
            plan = payload.get("plan")
            if not isinstance(plan, dict):
                self.send_error(HTTPStatus.BAD_REQUEST, "plan must be an object")
                return
            self._send_json(build_action_contract(plan))
            return

        if self.path == "/api/action-run":
            contract = payload.get("contract")
            if not isinstance(contract, dict):
                self.send_error(HTTPStatus.BAD_REQUEST, "contract must be an object")
                return
            result = execute_guarded_action(contract, str(payload.get("confirmation", "")))
            record_action_result(result)
            self._send_json(result)
            return

        if self.path == "/api/ask":
            question = str(payload.get("question", ""))
            response = answer_question(
                question,
                payload.get("report"),
                payload.get("system_map"),
                payload.get("maintenance_report"),
                payload.get("request_plan"),
            )
            self._send_json(response)
            return

        roots = payload.get("roots", [])
        if not isinstance(roots, list):
            self.send_error(HTTPStatus.BAD_REQUEST, "roots must be a list of paths")
            return

        report = map_filesystem([str(item) for item in roots])
        self._send_json(report)


def _find_open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def serve(host: str = "127.0.0.1", port: int | None = None, open_browser: bool = True) -> None:
    active_port = port or _find_open_port()
    server = ThreadingHTTPServer((host, active_port), SystemCoachHandler)
    url = f"http://{host}:{active_port}"

    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    print(f"System Coach and Maintenance Manager running at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
