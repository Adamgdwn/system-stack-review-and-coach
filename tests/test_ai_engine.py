import unittest

from stack_review_coach.ai_engine import build_context, choose_model


class AiEngineTests(unittest.TestCase):
    def test_choose_model_prefers_known_models(self):
        model = choose_model(["mistral", "qwen3:8b", "other"])
        self.assertEqual(model, "qwen3:8b")

    def test_build_context_includes_report_and_map(self):
        report = {
            "environment": {"os": "Linux", "shell": "/bin/bash"},
            "components": [
                {
                    "label": "Python",
                    "category": "language",
                    "version": "3.12.3",
                    "path": "/usr/bin/python3",
                }
            ],
            "summary": {"primary_stack_matches": [{"title": "Python App Stack", "confidence": "high", "summary": "ready", "coaching": "start with venv"}]},
            "recommendations": ["Use virtual environments."],
        }
        system_map = {
            "summary": {"roots_scanned": 1, "projects_detected": 2},
            "requested_roots": ["/home/tester"],
            "scans": [{"projects": [{"path": "/home/tester/demo", "types": ["Python project"]}]}],
            "config_findings": [{"label": "Git config", "path": "/home/tester/.gitconfig"}],
        }

        context = build_context(report, system_map)

        self.assertIn("Python", context)
        self.assertIn("/home/tester/demo", context)
        self.assertIn("Git config", context)


if __name__ == "__main__":
    unittest.main()
