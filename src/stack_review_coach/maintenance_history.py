"""Local history archive for maintenance diagnostics and request plans."""

from __future__ import annotations

from collections import Counter
import datetime as dt
import json
import os
from pathlib import Path
import uuid


HISTORY_FILE_NAME = "maintenance-history.jsonl"


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def history_dir() -> Path:
    configured = os.environ.get("STACK_COACH_HISTORY_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.cwd() / "history"


def history_path(base_dir: Path | None = None) -> Path:
    return (base_dir or history_dir()) / HISTORY_FILE_NAME


def _new_record_id(recorded_at: str) -> str:
    safe_timestamp = recorded_at.replace(":", "").replace("-", "").replace("T", "-")
    return f"{safe_timestamp}-{uuid.uuid4().hex[:8]}"


def _maintenance_summary(report: dict) -> dict:
    summary = report.get("summary", {})
    return {
        "finding_count": summary.get("finding_count", 0),
        "severity_counts": summary.get("severity_counts", {}),
        "approval_required_count": summary.get("approval_required_count", 0),
        "execution_enabled": summary.get("execution_enabled", False),
    }


def _request_plan_summary(plan: dict) -> dict:
    return {
        "title": plan.get("title", "Request plan"),
        "family": plan.get("family", "unknown"),
        "platform": plan.get("platform", "Unknown"),
        "risk": plan.get("risk", "unknown"),
        "approval_required": plan.get("approval_required", True),
        "execution_enabled": plan.get("execution_enabled", False),
        "requires_privilege": plan.get("requires_privilege", False),
    }


def _approval_decision_summary(decision: dict) -> dict:
    return {
        "decision": decision.get("decision", "unknown"),
        "plan_id": decision.get("plan_id"),
        "plan_title": decision.get("plan_title"),
        "reason": decision.get("reason", ""),
    }


def _action_result_summary(result: dict) -> dict:
    return {
        "action_id": result.get("action_id"),
        "plan_id": result.get("plan_id"),
        "status": result.get("status", "unknown"),
        "exit_code": result.get("exit_code"),
        "execution_enabled": result.get("execution_enabled", False),
    }


def _summary_for(kind: str, payload: dict) -> dict:
    if kind == "maintenance_report":
        return _maintenance_summary(payload)
    if kind == "request_plan":
        return _request_plan_summary(payload)
    if kind == "approval_decision":
        return _approval_decision_summary(payload)
    if kind == "action_result":
        return _action_result_summary(payload)
    return {"kind": kind}


def append_history_record(kind: str, payload: dict, base_dir: Path | None = None) -> dict:
    """Append a local-only history record and return the stored record."""

    recorded_at = _now()
    record = {
        "id": _new_record_id(recorded_at),
        "recorded_at": recorded_at,
        "kind": kind,
        "summary": _summary_for(kind, payload),
        "payload": payload,
    }
    path = history_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def record_maintenance_report(report: dict, base_dir: Path | None = None) -> dict:
    return append_history_record("maintenance_report", report, base_dir=base_dir)


def record_request_plan(plan: dict, base_dir: Path | None = None) -> dict:
    return append_history_record("request_plan", plan, base_dir=base_dir)


def record_approval_decision(decision: dict, base_dir: Path | None = None) -> dict:
    return append_history_record("approval_decision", decision, base_dir=base_dir)


def record_action_result(result: dict, base_dir: Path | None = None) -> dict:
    return append_history_record("action_result", result, base_dir=base_dir)


def _read_records(base_dir: Path | None = None) -> list[dict]:
    path = history_path(base_dir)
    if not path.exists():
        return []

    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append(
                    {
                        "id": "corrupt-history-line",
                        "recorded_at": None,
                        "kind": "history_error",
                        "summary": {"error": "A history record could not be parsed."},
                        "payload": {"raw": line[:500]},
                    }
                )
    return records


def _known_good_lessons(records: list[dict]) -> list[str]:
    lessons = []
    for record in reversed(records):
        if record.get("kind") != "maintenance_report":
            continue
        payload = record.get("payload", {})
        severity_counts = payload.get("summary", {}).get("severity_counts", {})
        if not severity_counts.get("critical") and not severity_counts.get("warning"):
            lessons.append(
                f"{record.get('recorded_at')}: maintenance diagnostics had no critical or warning findings."
            )
            break
    return lessons


def _latest_maintenance_reports(records: list[dict], limit: int = 2) -> list[dict]:
    reports = [record for record in records if record.get("kind") == "maintenance_report"]
    return reports[-limit:]


def _finding_signature(finding: dict) -> str:
    return "|".join(
        [
            str(finding.get("id", "unknown")),
            str(finding.get("severity", "unknown")),
            str(finding.get("status", "unknown")),
            str(finding.get("summary", "")),
        ]
    )


def _changed_since_last(records: list[dict]) -> list[str]:
    latest = _latest_maintenance_reports(records)
    if len(latest) < 2:
        return ["Not enough maintenance history yet to compare diagnostic runs."]

    previous, current = latest
    previous_payload = previous.get("payload", {})
    current_payload = current.get("payload", {})
    previous_findings = {_finding_signature(finding): finding for finding in previous_payload.get("findings", [])}
    current_findings = {_finding_signature(finding): finding for finding in current_payload.get("findings", [])}
    previous_keys = set(previous_findings)
    current_keys = set(current_findings)

    new_findings = [current_findings[key]["title"] for key in sorted(current_keys - previous_keys)]
    resolved_findings = [previous_findings[key]["title"] for key in sorted(previous_keys - current_keys)]
    current_summary = current_payload.get("summary", {})
    previous_summary = previous_payload.get("summary", {})

    changes = [
        f"Compared {previous.get('recorded_at')} to {current.get('recorded_at')}.",
        (
            "Warnings/critical counts changed from "
            f"{previous_summary.get('severity_counts', {})} to {current_summary.get('severity_counts', {})}."
        ),
    ]
    if new_findings:
        changes.append(f"New or changed findings: {', '.join(new_findings[:8])}.")
    if resolved_findings:
        changes.append(f"Resolved or changed findings: {', '.join(resolved_findings[:8])}.")
    if not new_findings and not resolved_findings:
        changes.append("No finding-level changes were detected between the two latest diagnostic snapshots.")
    return changes


def load_history(limit: int = 25, base_dir: Path | None = None) -> dict:
    records = _read_records(base_dir)
    recent = list(reversed(records))[:limit]
    counts = Counter(record.get("kind", "unknown") for record in records)
    return {
        "path": str(history_path(base_dir)),
        "summary": {
            "record_count": len(records),
            "kind_counts": dict(counts),
        },
        "known_good_lessons": _known_good_lessons(records),
        "changed_since_last": _changed_since_last(records),
        "records": recent,
    }


def format_history(history: dict) -> str:
    lines = [
        f"History path: {history['path']}",
        f"Records: {history['summary']['record_count']}",
        f"Kind counts: {json.dumps(history['summary']['kind_counts'], indent=2)}",
        "",
        "Known-good lessons:",
    ]
    lessons = history.get("known_good_lessons", [])
    lines.extend(f"- {lesson}" for lesson in lessons)
    if not lessons:
        lines.append("- No evidence-backed known-good lessons yet.")

    lines.extend(["", "Changed since last diagnostic run:"])
    lines.extend(f"- {change}" for change in history.get("changed_since_last", []))

    lines.extend(["", "Recent records:"])
    for record in history.get("records", []):
        lines.extend(
            [
                f"- {record.get('recorded_at')} | {record.get('kind')} | {record.get('id')}",
                f"  {json.dumps(record.get('summary', {}), sort_keys=True)}",
            ]
        )
    if not history.get("records"):
        lines.append("- No history records yet.")
    return "\n".join(lines)
