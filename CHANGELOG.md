# Changelog

All notable changes to MVP Rocket are documented in this file.

## [1.1.0] — 2026-08-07

### Added — Release Auditor
- `scripts/audit_secrets.py` — Scan for hardcoded secrets (API keys, passwords, tokens, private keys) with regex matching and redacted output
- `scripts/audit_todos.py` — Scan for TODO/FIXME/HACK/XXX/TEMP comments with severity classification
- `references/test-checklists.md` — 200+ checklist items across functional, visual, security, accessibility, reliability categories
- `references/performance-methodology.md` — Performance budget, metrics catalog, testing conditions, root cause analysis
- `references/severity-and-release-gates.md` — Blocker/Critical/High/Medium/Low definitions with GO/CONDITIONAL GO/NO-GO criteria
- `references/report-template.md` — Structured 18-section report template with findings and performance tables

### Changed
- `SKILL.md` — Combined JSON repair/schema + release auditor into unified skill
- `README.md` — Merged documentation for both capabilities

## [1.0.1] — 2026-08-07

### Fixed
- Hardened error messages: removed verbose exception details that could leak system paths
- Narrowed broad `except Exception` to specific exception types
- Fixed `-Infinity` regex in `fix_literals` (word boundary didn't match `-` prefix)
- Added `_strict_loads` to reject NaN/Infinity so repair stages can convert them to null

## [1.0.0] — 2026-08-07

### Added — JSON Repair & Schema Inference
- `scripts/repair_json.py` — 12 repair stages, 8 CLI flags, library API (`loads()`, `repair()`)
- `scripts/json_to_schema.py` — 4 output targets (Zod, Pydantic, JSON Schema, TypeScript), enum inference, format detection, multi-file merging
- `SKILL.md` — Skill documentation
- `README.md` — GitHub-facing docs
- `LICENSE` — MIT
- `tests/` — 67 pytest unit tests
- `test_journeys.py` — 27 E2E integration tests
