"""Native GTK desktop shell for the stack coach."""

from __future__ import annotations

import json
import threading

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")

from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from .agents import build_agents
from .reporting import generate_report
from .scanner import map_filesystem, suggest_roots


def build_report() -> dict:
    results = [agent.run() for agent in build_agents()]
    return generate_report(results)


class StackCoachWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="System Stack Review and Coach")
        self.set_default_size(1220, 840)
        self.set_border_width(16)

        self.current_report: dict | None = None
        self.current_map: dict | None = None

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(root)

        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.pack_start(header, False, False, 0)

        title = Gtk.Label()
        title.set_markup("<span size='24000' weight='bold'>System Stack Review and Coach</span>")
        title.set_xalign(0)
        header.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(
            label=(
                "A local teaching tool for understanding your environment, installed tools, "
                "and selected folders without sending data anywhere else."
            )
        )
        subtitle.set_xalign(0)
        subtitle.set_line_wrap(True)
        header.pack_start(subtitle, False, False, 0)

        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        root.pack_start(action_row, False, False, 0)

        self.review_button = Gtk.Button(label="Run Local Review")
        self.review_button.connect("clicked", self.on_run_review)
        action_row.pack_start(self.review_button, False, False, 0)

        self.map_button = Gtk.Button(label="Scan Selected Roots")
        self.map_button.connect("clicked", self.on_run_map)
        action_row.pack_start(self.map_button, False, False, 0)

        self.share_button = Gtk.Button(label="Copy Share Summary")
        self.share_button.connect("clicked", self.on_copy_summary)
        action_row.pack_start(self.share_button, False, False, 0)

        self.status_label = Gtk.Label(label="Ready. Run a review to learn the environment.")
        self.status_label.set_xalign(0)
        root.pack_start(self.status_label, False, False, 0)

        content = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        root.pack_start(content, True, True, 0)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.add1(left)
        content.add2(right)
        content.set_position(540)

        self.summary_view = self._make_text_view()
        left.pack_start(self._frame("Summary", self.summary_view), True, True, 0)

        self.environment_view = self._make_text_view()
        left.pack_start(self._frame("Environment", self.environment_view), True, True, 0)

        self.learning_view = self._make_text_view()
        left.pack_start(self._frame("Learning Path", self.learning_view), True, True, 0)

        notebook = Gtk.Notebook()
        right.pack_start(notebook, True, True, 0)

        self.components_view = self._make_text_view()
        notebook.append_page(self._frame("Detected Components", self.components_view), Gtk.Label(label="Components"))

        self.stacks_view = self._make_text_view()
        notebook.append_page(self._frame("Stack Patterns And Tips", self.stacks_view), Gtk.Label(label="Stacks"))

        self.scan_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.scan_page.set_border_width(6)
        notebook.append_page(self.scan_page, Gtk.Label(label="Find And Map"))
        self._build_scan_page()

        self.command_view = self._make_text_view()
        notebook.append_page(self._frame("Command Log", self.command_view), Gtk.Label(label="Command Log"))

        self.show_all()
        self.on_run_review(None)

    def _make_text_view(self) -> Gtk.TextView:
        view = Gtk.TextView()
        view.set_editable(False)
        view.set_cursor_visible(False)
        view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        view.set_left_margin(10)
        view.set_right_margin(10)
        return view

    def _frame(self, title: str, widget: Gtk.Widget) -> Gtk.Frame:
        frame = Gtk.Frame(label=title)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(widget)
        frame.add(scroll)
        return frame

    def _build_scan_page(self) -> None:
        intro = Gtk.Label(
            label=(
                "Choose folders the app is allowed to inspect. Scans are opt-in and local-only. "
                "Use this to find projects, config files, and the general shape of the system."
            )
        )
        intro.set_xalign(0)
        intro.set_line_wrap(True)
        self.scan_page.pack_start(intro, False, False, 0)

        suggestions_label = Gtk.Label(label="Suggested roots")
        suggestions_label.set_xalign(0)
        self.scan_page.pack_start(suggestions_label, False, False, 0)

        self.roots_list = Gtk.ListBox()
        self.scan_page.pack_start(self.roots_list, False, False, 0)

        for root in suggest_roots():
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            check = Gtk.CheckButton(label=root["path"])
            check.set_active(root["path"] == GLib.get_home_dir())
            box.pack_start(check, True, True, 0)
            row.add(box)
            row.check = check
            self.roots_list.add(row)

        custom_label = Gtk.Label(label="Custom roots, one per line")
        custom_label.set_xalign(0)
        self.scan_page.pack_start(custom_label, False, False, 0)

        self.custom_roots_view = Gtk.TextView()
        self.custom_roots_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        custom_scroll = Gtk.ScrolledWindow()
        custom_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        custom_scroll.set_min_content_height(90)
        custom_scroll.add(self.custom_roots_view)
        self.scan_page.pack_start(custom_scroll, False, False, 0)

        self.map_results_view = self._make_text_view()
        self.scan_page.pack_start(self._frame("System Map", self.map_results_view), True, True, 0)

    def _set_text(self, view: Gtk.TextView, text: str) -> None:
        buffer_ = view.get_buffer()
        buffer_.set_text(text)

    def _set_status(self, text: str) -> None:
        self.status_label.set_text(text)

    def _selected_roots(self) -> list[str]:
        roots = []
        for row in self.roots_list.get_children():
            if getattr(row, "check", None) and row.check.get_active():
                roots.append(row.check.get_label())

        custom_buffer = self.custom_roots_view.get_buffer()
        custom_text = custom_buffer.get_text(custom_buffer.get_start_iter(), custom_buffer.get_end_iter(), True)
        for line in custom_text.splitlines():
            line = line.strip()
            if line:
                roots.append(line)

        deduped = []
        seen = set()
        for root in roots:
            if root not in seen:
                deduped.append(root)
                seen.add(root)
        return deduped

    def on_run_review(self, _button: Gtk.Button | None) -> None:
        self.review_button.set_sensitive(False)
        self._set_status("Running local review...")
        threading.Thread(target=self._run_review_worker, daemon=True).start()

    def _run_review_worker(self) -> None:
        try:
            report = build_report()
            GLib.idle_add(self._apply_report, report)
        except Exception as exc:
            GLib.idle_add(self._set_status, f"Review failed: {exc}")
            GLib.idle_add(self.review_button.set_sensitive, True)

    def _apply_report(self, report: dict) -> bool:
        self.current_report = report
        self._set_text(
            self.summary_view,
            "\n".join(
                [
                    f"Generated: {report['generated_at']}",
                    f"Installed components: {report['summary']['installed_component_count']}",
                    f"Category mix: {json.dumps(report['summary']['category_breakdown'], indent=2)}",
                    "",
                    "Recommendations:",
                    *[f"- {item}" for item in report["recommendations"]],
                ]
            ),
        )
        self._set_text(
            self.environment_view,
            "\n".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in report["environment"].items()),
        )
        self._set_text(self.learning_view, "\n".join(f"{index}. {step}" for index, step in enumerate(report["learning_path"], 1)))
        self._set_text(
            self.components_view,
            "\n\n".join(
                [
                    "\n".join(
                        [
                            f"{component['label']} [{component['category']}]",
                            f"Version: {component['version']}",
                            f"Path: {component['path']}",
                            component["role"],
                            f"Works well with: {', '.join(component['pairs_well_with']) or 'No built-in note yet'}",
                            f"Learning tip: {component['learning_tip']}",
                        ]
                    )
                    for component in report["components"]
                ]
            ),
        )
        self._set_text(
            self.stacks_view,
            "\n\n".join(
                [
                    f"{item['title']} ({item['confidence']} confidence)\n{item['summary']}\n{item['coaching']}"
                    for item in report["summary"]["primary_stack_matches"]
                ]
            )
            or "No strong stack pattern matched yet.",
        )
        self._set_text(
            self.command_view,
            "\n\n".join(
                f"{entry['command']}\nexit {entry['exit_code']} in {entry['duration_ms']}ms\n{entry['output'] or 'No output'}"
                for entry in report["command_log"]
            )
            or "No command log available.",
        )
        self._set_status("Review complete. Explore the desktop app panels to learn the environment.")
        self.review_button.set_sensitive(True)
        return False

    def on_run_map(self, _button: Gtk.Button | None) -> None:
        roots = self._selected_roots()
        if not roots:
            self._set_status("Select at least one root before scanning.")
            return
        self.map_button.set_sensitive(False)
        self._set_status("Scanning the selected roots locally...")
        threading.Thread(target=self._run_map_worker, args=(roots,), daemon=True).start()

    def _run_map_worker(self, roots: list[str]) -> None:
        try:
            system_map = map_filesystem(roots)
            GLib.idle_add(self._apply_map, system_map)
        except Exception as exc:
            GLib.idle_add(self._set_status, f"Filesystem map failed: {exc}")
            GLib.idle_add(self.map_button.set_sensitive, True)

    def _apply_map(self, system_map: dict) -> bool:
        self.current_map = system_map
        sections = [
            "Selected roots:",
            *[f"- {root}" for root in system_map["requested_roots"]],
            "",
            "Summary:",
            *[f"- {key.replace('_', ' ')}: {value}" for key, value in system_map["summary"].items()],
            "",
            "Teaching notes:",
            *[f"- {note}" for note in system_map["teaching_notes"]],
            "",
            "Config findings:",
        ]
        if system_map["config_findings"]:
            sections.extend(
                f"- {item['label']}: {item['path']} | {item['teaching']}" for item in system_map["config_findings"]
            )
        else:
            sections.append("- No common config markers found in the selected scope.")

        sections.append("")
        sections.append("Detected roots and projects:")
        for scan in system_map["scans"]:
            sections.append(f"- {scan['root']}")
            sections.append(
                f"  scanned {scan['summary']['entries_scanned']} entries, found {scan['summary']['projects_detected']} projects"
            )
            for project in scan["projects"][:10]:
                sections.append(f"  project: {project['path']} [{', '.join(project['types'])}]")
            if scan["permission_errors"]:
                sections.append(f"  permission limits: {', '.join(scan['permission_errors'][:5])}")

        self._set_text(self.map_results_view, "\n".join(sections))
        self._set_status("Filesystem map complete.")
        self.map_button.set_sensitive(True)
        return False

    def on_copy_summary(self, _button: Gtk.Button | None) -> None:
        if not self.current_report:
            self._set_status("Run a review before copying a share summary.")
            return

        lines = [
            "System Stack Review and Coach",
            "",
            f"Generated: {self.current_report['generated_at']}",
            f"Operating system: {self.current_report['environment'].get('os', 'Unknown')}",
            f"Shell: {self.current_report['environment'].get('shell', 'Unknown')}",
            f"Installed components: {self.current_report['summary']['installed_component_count']}",
            "Detected tools:",
            *[
                f"- {component['label']} ({component['category']})"
                for component in self.current_report["components"][:18]
            ],
        ]
        if self.current_map:
            lines.extend(
                [
                    "",
                    f"Roots scanned: {self.current_map['summary']['roots_scanned']}",
                    f"Projects detected: {self.current_map['summary']['projects_detected']}",
                    f"Configs detected: {self.current_map['summary']['configs_detected']}",
                ]
            )
        lines.extend(["", "Generated locally on this machine."])

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text("\n".join(lines), -1)
        self._set_status("Share summary copied to the clipboard.")


class StackCoachDesktopApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.stack.review.coach")

    def do_activate(self) -> None:  # noqa: N802
        window = self.props.active_window
        if not window:
            window = StackCoachWindow(self)
        window.present()


def run_desktop() -> None:
    app = StackCoachDesktopApp()
    app.run(None)
