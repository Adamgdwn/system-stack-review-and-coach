"""Approved-action contract and guarded execution scaffolding.

The current governance level keeps execution disabled. This module defines the
contract shape and records blocked attempts so future execution work has a
strong interface without silently changing the machine today.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
import re


DEFAULT_TIMEOUT_SECONDS = 30
CONTRACT_VERSION = "approved-action-contract-v1"
LOW_RISK_FAMILIES = {
    "cursor-size",
    "display-brightness",
    "display-night-light",
    "display-refresh-rate",
    "display-scaling",
    "audio-routing",
}


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
    return {
        "eligible": not reasons,
        "reasons": reasons,
        "family": family,
    }


def _execution_gate(controls: dict, assessment: dict) -> dict:
    reasons = []
    governance_level = controls.get("governance_level")
    autonomy_level = controls.get("autonomy_level")
    if governance_level is None or governance_level < 2:
        reasons.append("governance reassessment is required before guarded action execution")
    if autonomy_level in {None, "A1"}:
        reasons.append("current autonomy level does not allow action execution")
    if not controls.get("action_runner_enabled"):
        reasons.append("action_runner_enabled is not set in project controls")
    if not assessment["eligible"]:
        reasons.extend(assessment["reasons"])
    return {
        "allowed": False,
        "reasons": reasons or ["execution is disabled by default"],
    }


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
            "max_bytes": 20000,
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
    plan["action_contract"] = build_action_contract(plan, project_control_path=project_control_path)
    return plan


def execute_guarded_action(contract: dict, confirmation_text: str) -> dict:
    """Return an action result without executing when the contract is gated off."""

    if not contract.get("execution_enabled"):
        return {
            "action_id": contract.get("id"),
            "plan_id": contract.get("plan_id"),
            "status": "blocked",
            "started_at": _now(),
            "finished_at": _now(),
            "execution_enabled": False,
            "exit_code": None,
            "commands": contract.get("command_preview", []),
            "output": "",
            "error": "; ".join(contract.get("execution_gate", {}).get("reasons", [])),
            "post_check": contract.get("post_check", []),
            "rollback": contract.get("rollback", []),
        }

    expected = contract.get("confirmation_phrase")
    if confirmation_text.strip() != expected:
        return {
            "action_id": contract.get("id"),
            "plan_id": contract.get("plan_id"),
            "status": "rejected",
            "started_at": _now(),
            "finished_at": _now(),
            "execution_enabled": True,
            "exit_code": None,
            "commands": contract.get("command_preview", []),
            "output": "",
            "error": "confirmation phrase did not match",
            "post_check": contract.get("post_check", []),
            "rollback": contract.get("rollback", []),
        }

    return {
        "action_id": contract.get("id"),
        "plan_id": contract.get("plan_id"),
        "status": "not_implemented",
        "started_at": _now(),
        "finished_at": _now(),
        "execution_enabled": False,
        "exit_code": None,
        "commands": contract.get("command_preview", []),
        "output": "",
        "error": "subprocess execution is intentionally not implemented until governance is reassessed",
        "post_check": contract.get("post_check", []),
        "rollback": contract.get("rollback", []),
    }
