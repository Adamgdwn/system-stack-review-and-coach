# AI Bootstrap Rules

## Purpose
This repository must be workable by Claude, Codex, and local coding agents
using the same operating rules.

## Change rules
- Prefer editing existing files over creating duplicate replacements.
- Keep changes small and reversible.
- Do not rename or move core files unless explicitly instructed.
- Explain new dependencies before adding them.
- Update docs when behavior, interfaces, or architecture change.

## Governance
- Run the governance preflight before making substantial changes:
  `bash scripts/governance-preflight.sh`
- Review `project-control.yaml` for risk tier and required controls.
- Record deviations as exceptions rather than ignoring them.

## Commands
- Install: `bash launchers/install-desktop-entry.sh`
- Dev:     `PYTHONPATH=src python3 -m stack_review_coach`
- Lint:    `python3 -m compileall src tests`
- Build:   `python3 -m compileall src`
- Test:    `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

## Document control
- Architecture decisions go in `docs/`
- If code behavior changes, update the nearest controlled document in the same task

## Completion standard
A task is not complete until relevant validation is run or a blocker is clearly stated.
