# Deployment Guide

## Environments

- `dev`: Local execution from the repository with `PYTHONPATH=src python3 -m stack_review_coach`
- `staging`: Desktop-launch validation on a representative workstation
- `prod`: Internal workstation use through the installed desktop entry

Because this is a local internal tool, staging and prod differ mainly by installation path and user validation.

## Deployment Steps

1. Validate the code locally with tests and compile checks.
2. Install or update the desktop launcher with `bash launchers/install-desktop-entry.sh`.
3. Ensure Ollama is running with at least one supported local model if AI coaching is expected.
4. Start the application from the launcher or CLI.
5. Confirm that the native window opens and the review report renders.

## Rollback

1. Remove the installed desktop files:
   - `~/.local/share/applications/system-stack-review-and-coach.desktop`
   - `~/Desktop/System Stack Review and Coach.desktop`
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
  - confirm the Ask The Coach tab answers a question through the local model when available
  - confirm the command log shows local probe execution
