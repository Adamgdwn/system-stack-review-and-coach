import tempfile
import unittest
from pathlib import Path

from system_coach_maintenance_manager.maintenance_history import (
    format_history,
    load_history,
    record_approval_decision,
    record_maintenance_report,
    record_request_plan,
)


class MaintenanceHistoryTests(unittest.TestCase):
    def test_records_reports_plans_and_decisions_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            report = {
                "generated_at": "2026-05-16T12:00:00",
                "summary": {
                    "finding_count": 2,
                    "severity_counts": {"info": 2},
                    "approval_required_count": 0,
                    "execution_enabled": False,
                },
                "findings": [],
                "action_plans": [],
            }
            plan = {
                "title": "Plan network troubleshooting",
                "family": "network-dns",
                "platform": "Linux",
                "risk": "low",
                "approval_required": True,
                "execution_enabled": False,
                "requires_privilege": False,
            }

            record_maintenance_report(report, base_dir=base_dir)
            record_request_plan(plan, base_dir=base_dir)
            record_approval_decision({"decision": "deferred", "plan_id": "plan-1"}, base_dir=base_dir)

            history = load_history(base_dir=base_dir)
            formatted = format_history(history)

        self.assertEqual(history["summary"]["record_count"], 3)
        self.assertEqual(history["summary"]["kind_counts"]["maintenance_report"], 1)
        self.assertEqual(history["summary"]["kind_counts"]["request_plan"], 1)
        self.assertIn("no critical or warning findings", history["known_good_lessons"][0])
        self.assertIn("Not enough maintenance history", history["changed_since_last"][0])
        self.assertIn("network-dns", formatted)

    def test_history_summarizes_changes_between_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            first = {
                "summary": {
                    "finding_count": 1,
                    "severity_counts": {"info": 1},
                    "approval_required_count": 0,
                    "execution_enabled": False,
                },
                "findings": [
                    {"id": "memory-pressure", "title": "Memory Pressure", "severity": "info", "status": "pass", "summary": "ok"}
                ],
            }
            second = {
                "summary": {
                    "finding_count": 2,
                    "severity_counts": {"info": 1, "warning": 1},
                    "approval_required_count": 1,
                    "execution_enabled": False,
                },
                "findings": [
                    {"id": "memory-pressure", "title": "Memory Pressure", "severity": "info", "status": "pass", "summary": "ok"},
                    {"id": "network-basics", "title": "Network Basics", "severity": "warning", "status": "warn", "summary": "dns issue"},
                ],
            }

            record_maintenance_report(first, base_dir=base_dir)
            record_maintenance_report(second, base_dir=base_dir)
            history = load_history(base_dir=base_dir)

        self.assertTrue(any("Network Basics" in change for change in history["changed_since_last"]))


if __name__ == "__main__":
    unittest.main()
