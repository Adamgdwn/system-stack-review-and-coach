"""Permission-based filesystem mapper for local environment discovery."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import os


PROJECT_MARKERS = {
    "Python project": ["pyproject.toml", "requirements.txt", "setup.py"],
    "Node project": ["package.json"],
    "Rust project": ["Cargo.toml"],
    "Go project": ["go.mod"],
    "Dockerized project": ["Dockerfile", "compose.yaml", "docker-compose.yml"],
    "Git repository": [".git"],
}

CONFIG_MARKERS = {
    "Shell config": [".bashrc", ".zshrc", ".profile"],
    "Git config": [".gitconfig"],
    "SSH config": [".ssh/config"],
    "Docker config": [".docker/config.json"],
    "VS Code settings": [".config/Code/User/settings.json"],
    "Cursor settings": [".config/Cursor/User/settings.json"],
}

SKIP_DIRS = {
    ".cache",
    ".local/share/Trash",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}


def _safe_resolve(path_text: str) -> Path:
    return Path(path_text).expanduser().resolve()


def suggest_roots() -> list[dict]:
    home = Path.home()
    candidates = [
        home,
        home / "code",
        home / "projects",
        home / "Desktop",
        Path("/etc"),
        Path("/usr/local/bin"),
    ]
    suggestions = []
    seen = set()
    for candidate in candidates:
        if not candidate.exists():
            continue
        resolved = str(candidate.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        suggestions.append(
            {
                "path": resolved,
                "label": candidate.name or resolved,
                "kind": "directory" if candidate.is_dir() else "file",
            }
        )
    return suggestions


def _match_project_markers(path: Path) -> list[str]:
    matches = []
    names = {entry.name for entry in path.iterdir()}
    for label, markers in PROJECT_MARKERS.items():
        if any(marker in names for marker in markers):
            matches.append(label)
    return matches


def _detect_config(home: Path) -> list[dict]:
    findings = []
    for label, markers in CONFIG_MARKERS.items():
        for marker in markers:
            target = home / marker
            if target.exists():
                findings.append(
                    {
                        "label": label,
                        "path": str(target),
                        "teaching": f"{label} helps shape how one part of your command-line or editor environment behaves.",
                    }
                )
    return findings


def _scan_root(root: Path, *, max_depth: int = 4, max_entries: int = 6000) -> dict:
    root = root.resolve()
    counters = Counter()
    discovered_projects = []
    interesting_directories = []
    permission_errors = []
    visited = 0

    def walk(current: Path, depth: int) -> None:
        nonlocal visited
        if visited >= max_entries or depth > max_depth:
            return
        visited += 1

        if current.name in SKIP_DIRS:
            return

        try:
            if current.is_dir():
                if depth <= 1:
                    interesting_directories.append(str(current))
                counters["directories"] += 1
                matches = _match_project_markers(current)
                if matches:
                    discovered_projects.append(
                        {
                            "path": str(current),
                            "types": matches,
                            "teaching": "This folder contains marker files that usually define how the project is built or run.",
                        }
                    )
                if depth == max_depth:
                    return
                for child in sorted(current.iterdir(), key=lambda item: item.name.lower())[:250]:
                    walk(child, depth + 1)
            else:
                counters["files"] += 1
        except PermissionError:
            permission_errors.append(str(current))
        except OSError:
            permission_errors.append(str(current))

    walk(root, 0)

    return {
        "root": str(root),
        "summary": {
            "directories": counters["directories"],
            "files": counters["files"],
            "projects_detected": len(discovered_projects),
            "permission_errors": len(permission_errors),
            "entries_scanned": visited,
        },
        "interesting_directories": interesting_directories[:18],
        "projects": discovered_projects[:36],
        "permission_errors": permission_errors[:20],
    }


def map_filesystem(roots: list[str]) -> dict:
    home = Path.home()
    requested = []
    seen = set()
    for root_text in roots:
        if not root_text.strip():
            continue
        resolved = _safe_resolve(root_text)
        if not resolved.exists():
            continue
        marker = str(resolved)
        if marker in seen:
            continue
        seen.add(marker)
        requested.append(resolved)

    scans = [_scan_root(root) for root in requested]
    total_projects = sum(scan["summary"]["projects_detected"] for scan in scans)
    total_permission_errors = sum(scan["summary"]["permission_errors"] for scan in scans)
    total_entries_scanned = sum(scan["summary"]["entries_scanned"] for scan in scans)

    config_findings = _detect_config(home)
    teaching_notes = [
        "Filesystem mapping is opt-in. The app only scans the roots you choose.",
        "Project markers like `package.json`, `pyproject.toml`, and `Cargo.toml` are often the quickest clues to how a folder works.",
        "Configuration files explain how your shell, Git, editors, and Docker behave on this machine.",
    ]

    return {
        "requested_roots": [str(root) for root in requested],
        "summary": {
            "roots_scanned": len(scans),
            "projects_detected": total_projects,
            "permission_errors": total_permission_errors,
            "entries_scanned": total_entries_scanned,
            "configs_detected": len(config_findings),
        },
        "scans": scans,
        "config_findings": config_findings,
        "teaching_notes": teaching_notes,
    }
