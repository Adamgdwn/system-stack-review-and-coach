import tempfile
import unittest
from pathlib import Path

from system_coach_maintenance_manager.maintenance_actions import build_action_contract, execute_guarded_action


class MaintenanceActionsTests(unittest.TestCase):
    def _project_control(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "project-control.yaml"
        path.write_text(text, encoding="utf-8")
        return path

    def test_contract_blocks_execution_at_governance_level_one(self):
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
        self.assertIn("governance reassessment", result["error"])

    def test_contract_marks_privileged_or_placeholder_plans_ineligible(self):
        control_path = self._project_control("governance_level: 3\nautonomy_level: A2\naction_runner_enabled: true\n")
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


if __name__ == "__main__":
    unittest.main()
