# Linux Setup Guide

## Ubuntu And Debian

Install system dependencies:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 git
```

Optional AI coaching:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:latest
```

Run from the repository:

```bash
PYTHONPATH=src python3 -m stack_review_coach
```

Optional editable install with the console command:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
stack-review-coach
```

Install the desktop launcher:

```bash
bash launchers/install-desktop-entry.sh
```

Browser fallback:

```bash
PYTHONPATH=src python3 -m stack_review_coach --browser
```

## Fedora

Install system dependencies:

```bash
sudo dnf install python3 python3-gobject gtk3 git
```

Run:

```bash
PYTHONPATH=src python3 -m stack_review_coach
```

## Arch Linux

Install system dependencies:

```bash
sudo pacman -S python python-gobject gtk3 git
```

Run:

```bash
PYTHONPATH=src python -m stack_review_coach
```

## Local History

Maintenance diagnostics and Request Desk plans are written to `history/maintenance-history.jsonl` by default. To move the archive:

```bash
export STACK_COACH_HISTORY_DIR="$HOME/.local/share/system-stack-review-and-coach/history"
```

## Validation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m compileall src tests
bash scripts/governance-preflight.sh
```
