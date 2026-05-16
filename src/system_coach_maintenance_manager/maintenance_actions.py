"""Approved-action contracts and guarded command execution."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import re
import shlex
import subprocess


DEFAULT_TIMEOUT_SECONDS = 30
CONTRACT_VERSION = "approved-action-contract-v1"
MAX_OUTPUT_BYTES = 20000
LOW_RISK_FAMILIES = {
    "cursor-size",
    "display-brightness",
    "display-dock",
    "display-night-light",
    "display-refresh-rate",
    "display-scaling",
    "audio-routing",
    "failed-services",
    "journal-errors",
    "network-basics",
}
ALLOWED_EXECUTABLES = {
    "brightnessctl",
    "cat",
    "cmd",
    "cosmic-randr",
    "cosmic-settings",
    "eventvwr.msc",
    "gsettings",
    "ip",
    "ipconfig",
    "journalctl",
    "kcmshell5",
    "kcmshell6",
    "kscreen-doctor",
    "lspci",
    "lsusb",
    "pactl",
    "powershell",
    "pwsh",
    "resolvectl",
    "route",
    "systemctl",
    "wevtutil",
    "xfconf-query",
    "xrandr",
}
READ_ONLY_VERBS = {"get", "info", "list", "query"}
MUTATING_VERBS = {"set"}


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "action"


def load_runner_controls(project_control_path: Path | None = None) -> dict:
    """Read the small subset of project controls needed by the runner gate."""

    path = project_control_path or Path.cwd() / "project-control.yaml"
    controls = {
        "governance_level": None,
        "autonomy_level": None,
        "action_runner_enabled": False,
        "source": str(path),
    }
    if not path.exists():
        controls["gate_reason"] = "project-control.yaml was not found, so action execution is disabled."
        return controls

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("governance_level:"):
            raw_value = stripped.split(":", 1)[1].strip()
            try:
                controls["governance_level"] = int(raw_value)
            except ValueError:
                controls["governance_level"] = None
        elif stripped.startswith("autonomy_level:"):
            controls["autonomy_level"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("action_runner_enabled:"):
            raw_value = stripped.split(":", 1)[1].strip().lower()
            controls["action_runner_enabled"] = raw_value in {"true", "yes", "1"}
    return controls


def _has_placeholder(command: str) -> bool:
    return "<" in command or ">" in command


def _candidate_assessment(plan: dict) -> dict:
    commands = plan.get("commands", [])
    family = plan.get("family", plan.get("finding_id", "maintenance"))
    reasons = []
    if not plan.get("approval_required", True):
        reasons.append("plan does not require approval")
    if plan.get("risk") != "low":
        reasons.append("plan risk is not low")
    if not plan.get("reversible"):
        reasons.append("plan is not marked reversible")
    if plan.get("requires_privilege"):
        reasons.append("plan requires privilege")
    if family not in LOW_RISK_FAMILIES:
        reasons.append("plan family is not in the low-risk guarded catalog")
    if not commands:
        reasons.append("plan has no exact command preview")
    if any(_has_placeholder(command) for command in commands):
        reasons.append("plan contains placeholder command text")
    for command in commands:
        allowed, reason = _command_allowed(command, family)
        if not allowed:
            reasons.append(reason or f"command is not allowed: {command}")
    return {
        "eligible": not reasons,
        "reasons": reasons,
        "family": family,
    }


def _execution_gate(controls: dict, assessment: dict) -> dict:
    reasons = []
    governance_level = controls.get("governance_level")
    autonomy_level = controls.get("autonomy_level")
    if governance_level != 1:
        reasons.append("guarded execution currently requires governance level 1 approval controls")
    if autonomy_level != "A1":
        reasons.append("guarded execution currently requires A1 user-approved autonomy")
    if not controls.get("action_runner_enabled"):
        reasons.append("action_runner_enabled is not set in project controls")
    if not assessment["eligible"]:
        reasons.extend(assessment["reasons"])
    return {
        "allowed": not reasons,
        "reasons": reasons,
    }


def _split_command(command: str) -> list[str]:
    return shlex.split(command, posix=os.name != "nt")


def _command_allowed(command: str, family: str) -> tuple[bool, str | None]:
    try:
        parts = _split_command(command)
    except ValueError as exc:
        return False, f"command could not be parsed safely: {exc}"
    if not parts:
        return False, "empty command"
    executable = Path(parts[0]).name.lower()
    if executable not in ALLOWED_EXECUTABLES:
        return False, f"executable {parts[0]} is not in the guarded catalog"
    if executable in {"gsettings", "xfconf-query"}:
        if not any(verb in parts for verb in READ_ONLY_VERBS | MUTATING_VERBS) and "-s" not in parts:
            return False, f"{executable} command does not declare an allowed read or set operation"
    if executable in {"cmd", "powershell", "pwsh"} and family not in {"cursor-size", "display-dock", "journal-errors", "network-basics"}:
        return False, f"{executable} execution is only enabled for guarded settings or read-only evidence plans"
    return True, None


def build_action_contract(plan: dict, project_control_path: Path | None = None) -> dict:
    """Build the immutable preview contract for a plan."""

    controls = load_runner_controls(project_control_path)
    assessment = _candidate_assessment(plan)
    gate = _execution_gate(controls, assessment)
    action_id = f"action-{_slug(plan.get('id', plan.get('title', 'plan')))}"
    return {
        "contract_version": CONTRACT_VERSION,
        "id": action_id,
        "plan_id": plan.get("id"),
        "plan_title": plan.get("title"),
        "family": assessment["family"],
        "status": "blocked",
        "eligible_for_guarded_execution": assessment["eligible"],
        "eligibility_notes": assessment["reasons"],
        "approval_required": True,
        "confirmation_phrase": f"APPROVE {action_id}",
        "execution_enabled": gate["allowed"],
        "execution_gate": gate,
        "command_preview": list(plan.get("commands", [])),
        "expected_effect": plan.get("expected_effect", ""),
        "requires_privilege": bool(plan.get("requires_privilege")),
        "reversible": bool(plan.get("reversible")),
        "risk": plan.get("risk", "unknown"),
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "output_capture": {
            "stdout": True,
            "stderr": True,
            "max_bytes": MAX_OUTPUT_BYTES,
        },
        "post_check": _post_check_for_plan(plan),
        "rollback": list(plan.get("rollback", [])),
        "created_at": _now(),
    }


def _post_check_for_plan(plan: dict) -> list[str]:
    family = plan.get("family", "")
    if family == "cursor-size":
        return ["Read the current cursor size setting again.", "Confirm normal apps render the pointer as expected."]
    if family.startswith("display-"):
        return ["Confirm the target display uses the intended setting.", "Confirm text and windows are usable."]
    if family == "audio-routing":
        return ["Play test audio or record a short microphone test.", "Confirm the expected device is selected."]
    return ["Rerun the relevant diagnostic or request review before considering the action complete."]


def build_action_contracts(plans: list[dict], project_control_path: Path | None = None) -> list[dict]:
    return [build_action_contract(plan, project_control_path=project_control_path) for plan in plans]


def attach_action_contract(plan: dict, project_control_path: Path | None = None) -> dict:
    contract = build_action_contract(plan, project_control_path=project_control_path)
    plan["action_contract"] = contract
    plan["execution_enabled"] = contract["execution_enabled"]
    return plan


def execute_guarded_action(contract: dict, confirmation_text: str) -> dict:
    """Execute a gated low-risk action contract."""

    started_at = _now()

    if not contract.get("execution_enabled"):
        return {
            "action_id": contract.get("id"),
            "plan_id": contract.get("plan_id"),
            "status": "blocked",
            "started_at": started_at,
            "finished_at": _now(),
            "execution_enabled": False,
            "exit_code": None,
            "commands": contract.get("command_preview", []),
            "output": "",
            "error": "; ".join(contract.get("execution_gate", {}).get("reasons", [])),
            "post_check": contract.get("post_check", []),
            "rollback": contract.get("rollback", []),
        }

    outputs = []
    commands = contract.get("command_preview", [])
    family = contract.get("family", "")
    for command in commands:
        allowed, reason = _command_allowed(command, family)
        if not allowed:
            return {
                "action_id": contract.get("id"),
                "plan_id": contract.get("plan_id"),
                "status": "blocked",
                "started_at": started_at,
                "finished_at": _now(),
                "execution_enabled": True,
                "exit_code": None,
                "commands": commands,
                "output": "\n".join(outputs),
                "error": reason or "command is not allowed",
                "post_check": contract.get("post_check", []),
                "rollback": contract.get("rollback", []),
            }
        try:
            completed = subprocess.run(
                _split_command(command),
                capture_output=True,
                check=False,
                text=True,
                timeout=int(contract.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "action_id": contract.get("id"),
                "plan_id": contract.get("plan_id"),
                "status": "failed",
                "started_at": started_at,
                "finished_at": _now(),
                "execution_enabled": True,
                "exit_code": None,
                "commands": commands,
                "output": "\n".join(outputs),
                "error": str(exc),
                "post_check": contract.get("post_check", []),
                "rollback": contract.get("rollback", []),
            }
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
        if output:
            outputs.append(f"$ {command}\n{output[:MAX_OUTPUT_BYTES]}")
        if completed.returncode != 0:
            return {
                "action_id": contract.get("id"),
                "plan_id": contract.get("plan_id"),
                "status": "failed",
                "started_at": started_at,
                "finished_at": _now(),
                "execution_enabled": True,
                "exit_code": completed.returncode,
                "commands": commands,
                "output": "\n".join(outputs),
                "error": f"command failed: {command}",
                "post_check": contract.get("post_check", []),
                "rollback": contract.get("rollback", []),
            }

    return {
        "action_id": contract.get("id"),
        "plan_id": contract.get("plan_id"),
        "status": "completed",
        "started_at": started_at,
        "finished_at": _now(),
        "execution_enabled": True,
        "exit_code": 0,
        "commands": commands,
        "output": "\n".join(outputs),
        "error": "",
        "post_check": contract.get("post_check", []),
        "rollback": contract.get("rollback", []),
    }
