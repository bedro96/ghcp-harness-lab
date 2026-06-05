# RETRO — mdtodo

**Date:** 2026-06-05  
**Branch:** main  
**Commits:** 9 (skeleton → full implementation)  
**Tests:** 42 passing (0 failures)

---

## What Was Built

A single-module Python CLI (`mdtodo.py`) that manages a markdown checkbox todo file. Three commands: `add`, `list`, `done`. Invoked as `python3 -m mdtodo`.

---

## What Went Well

- **Superpowers workflow paid off.** Running brainstorming → writing-plans → subagent-driven-development in order produced a clean, well-specified design before any code was written. The DESIGN.md and PLAN.md with full code meant subagents had everything they needed to implement tasks without guessing.

- **TDD discipline held.** Every task followed write-failing-test → implement → verify-passing. The 42 tests cover unit, integration, and end-to-end layers, making the code highly verifiable.

- **Layered architecture made testing easy.** Separating `parse`/`serialize` (pure text), `load_file`/`save_file` (I/O), and `cmd_*` (business logic) meant each layer could be tested independently without filesystem dependencies.

- **Two-stage review (spec then quality) caught issues early.** The spec reviewer on Task 2 noted the implementation used `split('\n')` vs the plan's `splitlines()` — a deviation that was functionally harmless but good to flag.

- **Final code reviewer flagged a false positive.** The reviewer claimed `python3 -m mdtodo` requires `__main__.py` — which is incorrect for a single `.py` module. Pushing back with evidence (42 passing e2e tests) was the right call.

---

## What Could Be Improved

- **`parse()` uses `split('\n')` instead of `splitlines()`** — the plan specified `splitlines()` which is more robust (handles `\r\n` on Windows). This was noted in review but not fixed. A one-line change.

- **No validation for empty `add` text** — `mdtodo add ""` creates a blank todo. The spec doesn't prohibit it, but adding a guard would improve UX.

- **Missing edge-case tests in `main()`** — `mdtodo add` (no text), `mdtodo done` (no N), `mdtodo list extra` all exit with usage errors but aren't explicitly tested. Low priority since the behavior is correct.

---

## Design Decisions

| Decision | Rationale |
|---|---|
| Parse → mutate → serialize (Option B) | Cleanest separation; enables pure-function testing of commands |
| `TodoItem` / `RawLine` dataclasses | Typed, immutable-friendly, no overhead |
| `ValueError` for invalid N | Clean signal from business logic to CLI layer |
| File auto-create on any command | User-friendly; avoids requiring manual file setup |
| 42 tests across 4 layers | Belt-and-suspenders: unit tests catch logic bugs; e2e tests catch integration issues |

---

## Completion Checklist

- [x] All BRIEF.md scenarios pass as unit tests
- [x] README written (≤ 30 lines)
- [x] DESIGN.md filled in
- [x] PLAN.md filled in
- [x] RETRO.md filled in (this file)
