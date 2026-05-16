import unittest

from system_coach_maintenance_manager.followup_plans import (
    build_followup_request,
    derive_cosmic_display_layout_fix,
    parse_cosmic_displays,
)


COSMIC_OUTPUT = """
eDP-1 (enabled)
  Position: 1920,1536
  Scale: 150%
  Transform: normal
  Modes:
    1920x1080 @ 60.001 Hz (current)
DVI-I-1 (enabled)
  Make: Samsung Electric Company
  Model: C27F390
  Position: 3840,0
  Scale: 125%
  Transform: rotate90
  Modes:
    1920x1080 @ 60.000 Hz (current) (preferred)
DVI-I-2 (enabled)
  Model: C27F390
  Position: 1920,456
  Scale: 100%
  Transform: normal
  Modes:
    1920x1080 @ 60.000 Hz (current) (preferred)
DP-1 (enabled)
  Model: LG FHD
  Position: 0,456
  Scale: 100%
  Transform: normal
  Modes:
    1920x1080 @ 60.000 Hz (current) (preferred)
"""


class FollowupPlanTests(unittest.TestCase):
    def test_parse_cosmic_displays_extracts_layout(self):
        displays = parse_cosmic_displays(COSMIC_OUTPUT)

        self.assertEqual(len(displays), 4)
        self.assertEqual(displays[1]["name"], "DVI-I-1")
        self.assertEqual(displays[1]["x"], 3840)
        self.assertEqual(displays[1]["scale_percent"], 125)
        self.assertEqual(displays[1]["transform"], "rotate90")
        self.assertEqual(displays[1]["current_mode"]["width"], 1920)

    def test_derive_cosmic_display_layout_fix_targets_rotated_external_monitor(self):
        followup = derive_cosmic_display_layout_fix(COSMIC_OUTPUT)

        self.assertIsNotNone(followup)
        self.assertEqual(followup["family"], "display-layout-fix")
        self.assertEqual(followup["target_output"], "DVI-I-1")
        self.assertIn("position 3840,456", followup["request_text"])
        self.assertIn("scale 1.0 transform normal", followup["request_text"])
        self.assertIn("position 3840,0 scale 1.25 transform rotate90", followup["request_text"])

    def test_build_followup_request_for_display_dock_execution(self):
        followup = build_followup_request(
            {"family": "display-dock", "title": "Investigate display dock"},
            {
                "status": "completed",
                "commands": ["cosmic-randr list"],
                "output": COSMIC_OUTPUT,
            },
            {"model": "gemma4:latest"},
        )

        self.assertIsNotNone(followup)
        self.assertEqual(followup["reasoning"]["source"], "deterministic-followup")
        self.assertEqual(followup["reasoning"]["model"], "gemma4:latest")
        self.assertEqual(followup["reasoning"]["family"], "display-layout-fix")

    def test_non_evidence_result_does_not_create_followup(self):
        followup = build_followup_request(
            {"family": "cursor-size"},
            {"status": "completed", "output": COSMIC_OUTPUT},
        )

        self.assertIsNone(followup)

    def test_normal_matching_external_displays_do_not_create_fix(self):
        output = """
DVI-I-1 (enabled)
  Position: 3840,0
  Scale: 100%
  Transform: normal
  Modes:
    1920x1080 @ 60.000 Hz (current)
DVI-I-2 (enabled)
  Position: 1920,0
  Scale: 100%
  Transform: normal
  Modes:
    1920x1080 @ 60.000 Hz (current)
"""

        self.assertIsNone(derive_cosmic_display_layout_fix(output))


if __name__ == "__main__":
    unittest.main()
