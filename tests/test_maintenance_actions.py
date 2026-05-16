import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from system_coach_maintenance_manager.maintenance_actions import build_action_contract, execute_guarded_action


class MaintenanceActionsTests(unittest.TestCase):
    def _project_control(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "project-control.yaml"
        path.write_text(text, encoding="utf-8")
        return path

    def test_contract_blocks_execution_when_runner_flag_is_missing(self):
        control_path = self._project_control(
            "\n".join(
                [
                    "governance_level: 1",
                    "agent_controls:",
                    "  autonomy_level: A1",
                ]
            )
        )
        plan = {
            "id": "request-cursor-size-linux",
            "family": "cursor-size",
            "title": "Adjust Linux cursor size",
            "approval_required": True,
            "execution_enabled": False,
            "risk": "low",
            "reversible": True,
            "requires_privilege": False,
            "commands": ["gsettings set org.gnome.desktop.interface cursor-size 24"],
            "expected_effect": "Change the current user's pointer size.",
            "rollback": ["Restore the previous cursor size."],
        }

        contract = build_action_contract(plan, project_control_path=control_path)
        result = execute_guarded_action(contract, contract["confirmation_phrase"])

        self.assertTrue(contract["eligible_for_guarded_execution"])
        self.assertFalse(contract["execution_enabled"])
        self.assertEqual(result["status"], "blocked")
        self.assertIsNone(result["exit_code"])
        self.assertIn("action_runner_enabled", result["error"])

    def test_contract_marks_privileged_or_placeholder_plans_ineligible(self):
        control_path = self._project_control("governance_level: 1\nautonomy_level: A1\naction_runner_enabled: true\n")
        plan = {
            "id": "plan-failed-services",
            "finding_id": "failed-services",
            "title": "Inspect failed services",
            "approval_required": True,
            "execution_enabled": False,
            "risk": "low",
            "reversible": True,
            "requires_privilege": False,
            "commands": ["systemctl status <service-name>"],
            "expected_effect": "Inspect one service.",
            "rollback": [],
        }

        contract = build_action_contract(plan, project_control_path=control_path)

        self.assertFalse(contract["eligible_for_guarded_execution"])
        self.assertFalse(contract["execution_enabled"])
        self.assertTrue(any("placeholder" in reason for reason in contract["eligibility_notes"]))

    def test_enabled_low_risk_contract_executes_guarded_command(self):
        control_path = self._project_control("governance_level: 1\nautonomy_level: A1\naction_runner_enabled: true\n")
        plan = {
            "id": "request-cursor-size-linux",
            "family": "cursor-size",
            "title": "Adjust Linux cursor size",
            "approval_required": True,
            "execution_enabled": False,
            "risk": "low",
            "reversible": True,
            "requires_privilege": False,
            "commands": [
                "gsettings get org.gnome.desktop.interface cursor-size",
                "gsettings set org.gnome.desktop.interface cursor-size 24",
            ],
            "expected_effect": "Change the current user's pointer size.",
            "rollback": ["Restore the previous cursor size."],
        }

        contract = build_action_contract(plan, project_control_path=control_path)

        with patch(
            "system_coach_maintenance_manager.maintenance_actions.subprocess.run",
            return_value=CompletedProcess(args=[], returncode=0, stdout="ok\n", stderr=""),
        ) as run:
            result = execute_guarded_action(contract, "")

        self.assertTrue(contract["eligible_for_guarded_execution"])
        self.assertTrue(contract["execution_enabled"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(run.call_count, 2)

    def test_read_only_evidence_plan_executes_guarded_commands(self):
        control_path = self._project_control("governance_level: 1\nautonomy_level: A1\naction_runner_enabled: true\n")
        plan = {
            "id": "plan-journal-errors",
            "finding_id": "journal-errors",
            "title": "Group recent critical log errors",
            "approval_required": True,
            "execution_enabled": False,
            "risk": "low",
            "reversible": True,
            "requires_privilege": False,
            "commands": ["journalctl -p 3 -n 100 --no-pager"],
            "expected_effect": "Collect recent critical log lines.",
            "rollback": [],
        }

        contract = build_action_contract(plan, project_control_path=control_path)

        with patch(
            "system_coach_maintenance_manager.maintenance_actions.subprocess.run",
            return_value=CompletedProcess(args=[], returncode=0, stdout="log lines\n", stderr=""),
        ) as run:
            result = execute_guarded_action(contract, "")

        self.assertTrue(contract["eligible_for_guarded_execution"])
        self.assertTrue(contract["execution_enabled"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
