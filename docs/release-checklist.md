# Release Checklist

Use this checklist before sharing a build with another machine or user.

## Governance

- Run `bash scripts/governance-preflight.sh`.
- Confirm `project-control.yaml` still reflects the current governance level and autonomy level.
- Review `docs/risks/risk-register.md` when adding new diagnostics, request families, history fields, or execution support.
- Confirm all machine-changing actions remain disabled unless governance has been reassessed.

## Automated Validation

- Run `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`.
- Run `python3 -m compileall src tests`.
- Run `git diff --check`.

## Linux Native Smoke Test

- Launch with `PYTHONPATH=src python3 -m system_coach_maintenance_manager`.
- Confirm the GTK window opens.
- Run Local Review.
- Run Maintenance Diagnostics.
- Prepare a Request Desk plan.
- Confirm Approval Queue shows exact commands, risk, reversibility, privilege, and execution disabled.
- Confirm each queued plan shows an action-runner contract and gate reason.
- Refresh History and confirm the local JSONL path is visible.
- Ask Coach a short question when Ollama is available.
- Resize the window below and above the responsive breakpoint.

## Browser Fallback Smoke Test

- Launch with `PYTHONPATH=src python3 -m system_coach_maintenance_manager --browser --no-browser`.
- Open the printed local URL.
- Confirm `/health` returns `ok`.
- Run Local Review.
- Run Maintenance Diagnostics.
- Prepare a Request Desk plan.
- Confirm Approval Queue and History update.
- Confirm `/api/action-run` returns a blocked result for the current governance level.
- Ask Coach a short question when Ollama is available.

## Windows Browser Mode Smoke Test

- Launch from PowerShell with `$env:PYTHONPATH="src"; python -m system_coach_maintenance_manager --browser --no-browser`.
- Open the printed local URL.
- Confirm local review, Request Desk, Approval Queue, History, and Coach Chat render.
- Confirm action contracts are visible and execution remains disabled.
- Confirm missing Windows diagnostic commands produce readable warnings instead of crashes.

## Packaging

- Confirm `pyproject.toml` includes `src/system_coach_maintenance_manager/web` package data.
- Confirm editable install inside a virtual environment exposes `system-coach`.
- Confirm `system-coach` launches the same CLI as `python -m system_coach_maintenance_manager`.
- Confirm docs mention platform-specific setup paths and Ollama model tags.
