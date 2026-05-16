# Deployment Guide

## Environments

- `dev`: Local execution from the repository with `PYTHONPATH=src python3 -m system_coach_maintenance_manager`
- `staging`: Desktop-launch validation on a representative workstation
- `prod`: Internal workstation use through the installed desktop entry

Because this is a local internal tool, staging and prod differ mainly by installation path and user validation.

## Deployment Steps

1. Validate the code locally with tests and compile checks.
2. Choose the target interface:
   - Linux native GTK: `PYTHONPATH=src python3 -m system_coach_maintenance_manager`
   - Browser fallback: `PYTHONPATH=src python3 -m system_coach_maintenance_manager --browser`
   - Windows browser mode: `$env:PYTHONPATH="src"; python -m system_coach_maintenance_manager --browser`
3. Install or update the desktop launcher on Linux with `bash launchers/install-desktop-entry.sh` when native mode is desired.
4. Optionally install in a virtual environment with `python3 -m venv .venv`, `. .venv/bin/activate`, and `python -m pip install -e .` to expose the `system-coach` console command.
5. Ensure Ollama is running with at least one supported local model if AI coaching is expected.
6. Start the application from the launcher or CLI.
7. Confirm that the selected interface opens and the review report renders.

## Rollback

1. Remove the installed desktop files:
   - `~/.local/share/applications/system-coach-maintenance-manager.desktop`
   - `~/Desktop/System Coach and Maintenance Manager.desktop`
2. Revert the repository to the previous known-good version.
3. Reinstall the launcher from that version if needed.

## Validation

- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 -m compileall src tests`
- Manual smoke test:
  - launch the app
  - confirm the desktop window opens
  - resize the window narrower and wider and confirm the main panels adapt instead of becoming cramped
  - confirm the local AI status line reports Ollama health clearly
  - confirm the environment snapshot and component cards populate
  - confirm scan suggestions appear and an opt-in root scan returns project/config findings
  - confirm the Request Desk prepares a plan and the Approval Queue shows exact commands plus guarded execution state
  - confirm the History view shows the JSONL path and changed-since-last summary
  - confirm the Chat tab answers a question through the local model when available
  - confirm the command log shows local probe execution

## Platform Guides

- `docs/setup-linux.md`
- `docs/setup-windows-browser.md`
- `docs/release-checklist.md`
