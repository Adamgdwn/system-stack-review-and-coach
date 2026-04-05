import tempfile
from pathlib import Path
import unittest

from stack_review_coach.scanner import map_filesystem


class ScannerTests(unittest.TestCase):
    def test_map_filesystem_detects_project_markers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "demo-app"
            project.mkdir()
            (project / "package.json").write_text('{"name":"demo"}', encoding="utf-8")
            (project / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")

            result = map_filesystem([str(root)])

        self.assertEqual(result["summary"]["roots_scanned"], 1)
        self.assertGreaterEqual(result["summary"]["projects_detected"], 1)
        self.assertTrue(any(scan["projects"] for scan in result["scans"]))


if __name__ == "__main__":
    unittest.main()
