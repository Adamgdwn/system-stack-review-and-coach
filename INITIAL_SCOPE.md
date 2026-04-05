# Initial Scope — System Stack Review and Coach

Generated: 2026-04-05

## Classification

| Field          | Value |
|----------------|-------|
| Project name   | System Stack Review and Coach |
| Slug / dir     | system-stack-review-and-coach |
| Type           | internal-tool |
| Risk tier      | medium |
| Stack          | not specified |
| Primary model  | codex |
| Location       | /home/adamgoodwin/code/Applications/system-stack-review-and-coach |

## Build approach

Primary builder: **codex**

## Scope brief

**Problem:** New users don't always know what has been installed on their system, so we should build a summary and guide that lets the user learn as much as they need.

**User / consumer:** New to intermediate coders and system owners

**MVP:** Functional tool that identifies and coaches users on teh stack, the environments, a few tips and tricks, etc. through a clear GUI

## First session checklist

- [ ] Fill in commands in `AI_BOOTSTRAP.md`
- [ ] Confirm risk tier in `project-control.yaml`
- [ ] Add first ADR if architecture decisions were made at intake
- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`
