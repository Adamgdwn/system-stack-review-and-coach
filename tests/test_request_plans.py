import unittest

from system_coach_maintenance_manager.request_plans import format_request_plan, prepare_request_plan


class RequestPlanTests(unittest.TestCase):
    def assert_approval_preview(self, plan):
        self.assertTrue(plan["approval_required"])
        self.assertFalse(plan["execution_enabled"])
        self.assertIn("family", plan)
        self.assertIn("action_contract", plan)
        self.assertFalse(plan["action_contract"]["execution_enabled"])

    def test_prepare_linux_cursor_plan_is_approval_required(self):
        plan = prepare_request_plan(
            "My cursor size seems odd. Make it smaller.",
            os_name="Linux",
            distribution_hint="GNOME",
        )

        self.assertEqual(plan["id"], "request-cursor-size-linux")
        self.assert_approval_preview(plan)
        self.assertFalse(plan["requires_privilege"])
        self.assertTrue(any("gsettings set" in command for command in plan["commands"]))
        self.assertIn("GNOME", plan["summary"])

    def test_prepare_kde_cursor_plan_prefers_kde_settings(self):
        plan = prepare_request_plan("Make my pointer bigger", os_name="Linux", distribution_hint="KDE Plasma")

        self.assertEqual(plan["id"], "request-cursor-size-linux")
        self.assertTrue(any("kcmshell" in command for command in plan["commands"]))
        self.assertFalse(any("gsettings set" in command for command in plan["commands"]))

    def test_prepare_cosmic_cursor_plan_uses_cosmic_settings(self):
        plan = prepare_request_plan("Make my cursor larger", os_name="Linux", distribution_hint="COSMIC")

        self.assertEqual(plan["id"], "request-cursor-size-linux")
        self.assertEqual(plan["commands"], ["cosmic-settings"])

    def test_prepare_windows_cursor_plan_opens_settings(self):
        plan = prepare_request_plan("Make my pointer bigger", os_name="Windows")

        self.assertEqual(plan["id"], "request-cursor-size-windows")
        self.assert_approval_preview(plan)
        self.assertTrue(any("ms-settings:easeofaccess-mousepointer" in command for command in plan["commands"]))

    def test_prepare_display_scaling_plan(self):
        plan = prepare_request_plan("Make the display scaling bigger", os_name="Windows")

        self.assertEqual(plan["family"], "display-scaling")
        self.assert_approval_preview(plan)
        self.assertTrue(any("ms-settings:display" in command for command in plan["commands"]))

    def test_prepare_brightness_plan(self):
        plan = prepare_request_plan("Lower the screen brightness", os_name="Linux")

        self.assertEqual(plan["family"], "display-brightness")
        self.assert_approval_preview(plan)
        self.assertIn("brightnessctl info", plan["commands"])

    def test_prepare_night_light_plan(self):
        plan = prepare_request_plan("Turn on night light", os_name="Windows")

        self.assertEqual(plan["family"], "display-night-light")
        self.assert_approval_preview(plan)
        self.assertIn("start ms-settings:nightlight", plan["commands"])

    def test_prepare_refresh_rate_plan(self):
        plan = prepare_request_plan("Check my monitor refresh rate", os_name="Linux")

        self.assertEqual(plan["family"], "display-refresh-rate")
        self.assert_approval_preview(plan)
        self.assertIn("xrandr --query", plan["commands"])

    def test_prepare_audio_plan(self):
        plan = prepare_request_plan("Switch my microphone input", os_name="Linux")

        self.assertEqual(plan["family"], "audio-routing")
        self.assert_approval_preview(plan)
        self.assertTrue(any("pactl list short sources" in command for command in plan["commands"]))

    def test_prepare_network_dns_plan(self):
        plan = prepare_request_plan("DNS seems broken on my internet", os_name="Windows")

        self.assertEqual(plan["family"], "network-dns")
        self.assert_approval_preview(plan)
        self.assertIn("ipconfig /all", plan["commands"])

    def test_prepare_package_update_plan(self):
        plan = prepare_request_plan("Repair package updates", os_name="Linux")

        self.assertEqual(plan["family"], "package-updates")
        self.assert_approval_preview(plan)
        self.assertTrue(plan["requires_privilege"])
        self.assertIn("apt-get check", plan["commands"])

    def test_prepare_docker_cleanup_plan(self):
        plan = prepare_request_plan("Clean up Docker containers and images", os_name="Linux")

        self.assertEqual(plan["family"], "docker-cleanup")
        self.assert_approval_preview(plan)
        self.assertIn("docker system df", plan["commands"])
        self.assertFalse(any("prune" in command for command in plan["commands"]))

    def test_prepare_startup_apps_plan(self):
        plan = prepare_request_plan("Review startup apps", os_name="Windows")

        self.assertEqual(plan["family"], "startup-apps")
        self.assert_approval_preview(plan)
        self.assertTrue(any("startupapps" in command for command in plan["commands"]))

    def test_prepare_slow_computer_plan(self):
        plan = prepare_request_plan("My computer feels slow and laggy", os_name="Linux")

        self.assertEqual(plan["family"], "slow-computer")
        self.assert_approval_preview(plan)
        self.assertIn("free -h", plan["commands"])

    def test_unknown_request_needs_triage(self):
        plan = prepare_request_plan("Tune the blue sparkle thing", os_name="Linux")
        formatted = format_request_plan(plan)

        self.assertEqual(plan["id"], "request-needs-triage")
        self.assert_approval_preview(plan)
        self.assertIn("No commands prepared yet", formatted)

    def test_supported_family_on_unknown_platform_triages_without_commands(self):
        plan = prepare_request_plan("Fix my DNS", os_name="Haiku")

        self.assertEqual(plan["id"], "request-network-dns-triage")
        self.assertEqual(plan["commands"], [])
        self.assertIn("unsupported", plan["expected_effect"])


if __name__ == "__main__":
    unittest.main()
