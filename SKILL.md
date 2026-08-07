---
name: mvp-rocket
description: >
  MVP acceleration toolkit with two capabilities: (1) JSON repair and schema
  inference — repair broken JSON from LLMs, APIs, and scraped data, then generate
  strict type definitions in Zod, Pydantic, JSON Schema, or TypeScript.
  (2) Release auditing — scan an MVP codebase for release blockers and produce a
  structured GO, CONDITIONAL GO, or NO-GO recommendation covering functional
  testing, performance measurement, security review, accessibility, cross-browser
  checks, reliability, usability, code review, and automated checks. Use when the
  user asks to repair JSON, generate schemas/types from JSON, audit an MVP, test
  before launch, check launch readiness, find performance problems, test user
  journeys, make the app faster, perform QA, check production readiness, run
  regression tests, diagnose slowness, find and fix bugs, stress-test, or check
  Core Web Vitals and API response times.
---

# MVP Rocket

Two-part MVP acceleration toolkit:

1. **JSON Repair & Schema Inference** — from messy LLM output to strict types
2. **Release Auditor** — from codebase to defensible launch recommendation

---

## Part 1: JSON Repair & Schema Inference

### repair_json.py

Extracts and repairs malformed JSON from messy text (LLM output, scraped pages, logs).

```bash
# Repair broken JSON
echo "{name: 'test', active: True, count: 0xFF}" | python scripts/repair_json.py -

# Library API
import repair_json
data = repair_json.loads(messy_text)
```

**Fixes**: markdown fences, smart quotes, single quotes, comments, unquoted keys,
Python/JS literals, trailing commas, truncated output, hex/octal numbers,
non-standard floats, Python tuples, missing commas, BOM.

**CLI flags**: `--output`, `--encoding`, `--indent`, `--compact`, `--check`, `--in-place`, `--quiet`

### json_to_schema.py

Infers strict validation schemas from JSON samples.

```bash
# Generate Zod schema
python scripts/json_to_schema.py sample.json --name User

# Generate Pydantic model
python scripts/json_to_schema.py sample.json --name User --lang pydantic
```

**Output targets**: `zod` (default), `pydantic`, `jsonschema`, `typescript`

**Features**: format detection (UUID, email, URL, date, datetime), enum inference,
nullable/union handling, multi-sample merging, loose mode.

**CLI flags**: `--lang`, `--name`, `--root-array-item`, `--no-formats`, `--loose`,
`--output`, `--enums`, `--max-array-samples`, `--merge`

### Pipeline

```bash
cat llm_output.txt | python scripts/repair_json.py - --compact \
  | python scripts/json_to_schema.py - --name Response
```

---

## Part 2: Release Auditor

Scans an MVP codebase end to end and produces a release readiness report.

### Operating Modes

| Mode | When | Behavior |
|------|------|----------|
| `audit-only` | Default | Inspect and test. Do not change application code. |
| `audit-and-fix` | User explicitly requests fixes | Diagnose, fix, measure before/after, retest. |
| `verify-fixes` | Re-checking previous issues | Retest specific issues + regression check. |

### Safety Boundaries

- Prefer local/staging/test environments
- Treat production as read-only unless explicitly authorized
- Never run destructive tests without explicit authorization
- Redact all secrets and personal data from reports
- Preserve uncommitted code changes

### Audit Workflow

1. **Discovery** — detect product type, stack, critical user journeys
2. **Test Plan** — risk-based test matrix prioritized by severity
3. **Execute** — functional, visual, cross-browser, performance, security, accessibility, reliability, usability, code review, automated checks
4. **Fix** (audit-and-fix only) — reproduce, baseline, fix, measure, compare
5. **Report** — structured report with GO/CONDITIONAL GO/NO-GO verdict

### Audit Categories

| Category | What's Tested |
|----------|--------------|
| Functional | Auth, CRUD, forms, navigation, edge cases, integrations |
| Visual & Responsive | 6 viewport widths, overflow, layout shifts, mobile keyboard |
| Cross-browser | Chromium, Firefox, WebKit/Safari |
| Performance | Core Web Vitals, API latency, bundle size, memory, queries |
| Security | Secrets, auth, XSS, injection, CORS, headers, dependencies |
| Accessibility | Keyboard, focus, contrast, semantics, screen readers |
| Reliability | Failure handling, retries, idempotency, data consistency |
| Usability | First-time UX, error recovery, empty states, confirmations |
| Code Review | Architecture, error handling, type safety, deployment readiness |
| Automated | Existing test suite, lint, type check, build, dependency audit |

### Audit Scripts

```bash
# Scan for hardcoded secrets
python scripts/audit_secrets.py <directory> --json

# Scan for TODO/FIXME/HACK tags
python scripts/audit_todos.py <directory> --json --severity
```

### Severity Definitions

See [references/severity-and-release-gates.md](references/severity-and-release-gates.md)

| Level | Meaning |
|-------|---------|
| Blocker | Prevents launch or makes product unusable |
| Critical | Major security, privacy, financial, or data-integrity risk |
| High | Seriously affects important feature, limited workaround exists |
| Medium | Affects secondary journey or subset of users |
| Low | Minor visual or polish issue |

### Report Output

See [references/report-template.md](references/report-template.md)

Produces: executive summary, verdict, performance budget vs measured, findings by severity, security/accessibility/cross-browser results, areas not tested, recommended actions, release checklist.

### Reference Documents

- [references/test-checklists.md](references/test-checklists.md) — 200+ checklist items
- [references/performance-methodology.md](references/performance-methodology.md) — metrics, targets, root cause analysis
- [references/severity-and-release-gates.md](references/severity-and-release-gates.md) — GO/NO-GO criteria
- [references/report-template.md](references/report-template.md) — structured report template
