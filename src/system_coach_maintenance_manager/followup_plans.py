"""Turn executed evidence into the next guarded request plan."""

from __future__ import annotations

from collections import Counter
import re
from typing import Any


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
DISPLAY_HEADER_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.:-]+)\s+\(enabled\)")
POSITION_RE = re.compile(r"Position:\s*(-?\d+),(-?\d+)")
SCALE_RE = re.compile(r"Scale:\s*(\d+(?:\.\d+)?)%")
TRANSFORM_RE = re.compile(r"Transform:\s*([A-Za-z0-9]+)")
MODEL_RE = re.compile(r"Model:\s*(.*)")
CURRENT_MODE_RE = re.compile(r"(\d+)\s*x\s*(\d+)\s*@\s*([\d.]+)\s*Hz.*\(current\)")


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _scale_percent_to_ratio(value: float) -> str:
    ratio = value / 100
    return f"{ratio:.2f}".rstrip("0").rstrip(".")


def _refresh_value(value: str) -> str:
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return str(int(number))
    return f"{number:.3f}".rstrip("0").rstrip(".")


def parse_cosmic_displays(output: str) -> list[dict[str, Any]]:
    """Parse the stable parts of `cosmic-randr list` output."""

    displays: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in _strip_ansi(output).splitlines():
        line = raw_line.rstrip()
        header = DISPLAY_HEADER_RE.match(line.strip())
        if header:
            current = {"name": header.group("name"), "current_mode": None}
            displays.append(current)
            continue
        if not current:
            continue

        stripped = line.strip()
        if match := MODEL_RE.match(stripped):
            model = match.group(1).strip()
            if model:
                current["model"] = model
        elif match := POSITION_RE.match(stripped):
            current["x"] = int(match.group(1))
            current["y"] = int(match.group(2))
        elif match := SCALE_RE.match(stripped):
            current["scale_percent"] = float(match.group(1))
        elif match := TRANSFORM_RE.match(stripped):
            current["transform"] = match.group(1)
        elif match := CURRENT_MODE_RE.search(stripped):
            current["current_mode"] = {
                "width": int(match.group(1)),
                "height": int(match.group(2)),
                "refresh": _refresh_value(match.group(3)),
            }
    return displays


def _choose_affected_display(displays: list[dict[str, Any]]) -> dict[str, Any] | None:
    rotated = [item for item in displays if item.get("transform") and item.get("transform") != "normal"]
    if rotated:
        return sorted(rotated, key=lambda item: item.get("x", 0), reverse=True)[0]
    external = [item for item in displays if not item.get("name", "").startswith("eDP-")]
    if not external:
        return None
    scales = [
        item.get("scale_percent")
        for item in external
        if item.get("scale_percent") is not None and item.get("transform", "normal") == "normal"
    ]
    if not scales:
        return None
    common_scale = Counter(scales).most_common(1)[0][0]
    scaled = [item for item in external if item.get("scale_percent") is not None and item.get("scale_percent") != common_scale]
    if scaled:
        return sorted(scaled, key=lambda item: item.get("x", 0), reverse=True)[0]
    return None


def _common_external_y(displays: list[dict[str, Any]], affected: dict[str, Any]) -> int | None:
    external_y = [
        item["y"]
        for item in displays
        if item is not affected
        and not item.get("name", "").startswith("eDP-")
        and item.get("transform", "normal") == "normal"
        and "y" in item
    ]
    if not external_y:
        return affected.get("y")
    return Counter(external_y).most_common(1)[0][0]


def derive_cosmic_display_layout_fix(output: str) -> dict[str, Any] | None:
    """Create an executable COSMIC layout fix from display evidence."""

    displays = parse_cosmic_displays(output)
    affected = _choose_affected_display(displays)
    if not affected or not affected.get("current_mode"):
        return None
    if not {"x", "y", "scale_percent", "transform"} <= affected.keys():
        return None

    mode = affected["current_mode"]
    target_y = _common_external_y(displays, affected)
    if target_y is None:
        return None

    old_scale = _scale_percent_to_ratio(float(affected["scale_percent"]))
    request_text = (
        "Apply COSMIC display layout fix. "
        f"Output {affected['name']}. "
        f"Set mode {mode['width']}x{mode['height']} refresh {mode['refresh']} "
        f"position {affected['x']},{target_y} scale 1.0 transform normal. "
        f"Rollback mode {mode['width']}x{mode['height']} refresh {mode['refresh']} "
        f"position {affected['x']},{affected['y']} scale {old_scale} transform {affected['transform']}."
    )
    model = affected.get("model")
    summary = (
        f"{affected['name']}"
        + (f" ({model})" if model else "")
        + f" is using transform {affected['transform']} at {int(affected['scale_percent'])}% scale. "
        f"The proposed fix sets it back to normal rotation, 100% scale, and aligns it at y={target_y}."
    )
    return {
        "family": "display-layout-fix",
        "request_text": request_text,
        "summary": summary,
        "target_output": affected["name"],
    }


def build_followup_request(plan: dict, result: dict, analysis: dict | None = None) -> dict[str, Any] | None:
    """Return the next request to prepare after a successful evidence action."""

    if result.get("status") != "completed":
        return None
    family = plan.get("family")
    if family == "display-dock":
        followup = derive_cosmic_display_layout_fix(str(result.get("output", "")))
        if not followup:
            return None
        followup["reasoning"] = {
            "source": "deterministic-followup",
            "model": (analysis or {}).get("model"),
            "family": followup["family"],
            "ready": True,
            "confidence": 0.9,
            "reasoning_summary": followup["summary"],
            "request_evidence": {
                "scopes": ["display-dock", "display-layout-fix"],
                "commands": [{"command": command, "output": ""} for command in result.get("commands", [])],
            },
        }
        return followup
    return None
