# Runbook

## Purpose

This system teaches users about their local development environment through a native desktop window. In normal operation it starts the GTK application, runs bounded local probe agents, and displays explanations for detected tools.

It can also perform an opt-in filesystem map for user-selected roots to explain project folders, repositories, and configuration files in plain language.

## Alerts And Failures

Likely failure conditions:

- Python is unavailable or below the required version.
- The desktop window does not open or crashes at startup.
- A probe command hangs or is missing.
- A filesystem map root is too large, slow, or permission-limited.
- The desktop launcher points to an outdated repository path.

First response:

1. Run `bash launchers/run-stack-coach.sh`.
2. If the desktop shell still fails, try `PYTHONPATH=src python3 -m stack_review_coach --browser` as a fallback.
3. Check the command log in the UI to see which probe failed or timed out.
4. Reduce filesystem scan scope to one or two specific roots if mapping is slow.

## Dependencies

- `python3`
- GTK 3 via `python3-gi`
- The files under `src/stack_review_coach/web/`
- Optional local tools being probed, such as `git`, `node`, `docker`, and `gh`
- Read access for any folders the user chooses to map

## Recovery

- If the desktop shell does not load, retry from a terminal to surface runtime errors and use browser fallback mode if needed.
- If desktop launching fails, rerun `bash launchers/install-desktop-entry.sh`.
- If a specific tool is reported incorrectly, run its version command directly in a shell and compare the output.
- If filesystem mapping feels too broad, clear the selected roots and rerun with only the directories you want to inspect.

## Escalation

Escalate to the project owner or technical lead when:

- the local launcher repeatedly fails on multiple machines
- a probe command causes unexpected side effects
- governance requirements or exception handling need review
