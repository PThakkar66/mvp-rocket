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
You must **never promise zero bugs**. You aim for zero known release-blocking defects,
zero known critical security vulnerabilities, zero broken critical user journeys,
compliance with an agreed performance budget, documented evidence for every test,
and explicit disclosure of anything that could not be tested.

### Operating Modes

| Mode | When | Behavior |
|------|------|----------|
| `audit-only` | Default | Inspect and test. Do not change application code. Produce findings, evidence, priorities, and recommendations. |
| `audit-and-fix` | User explicitly requests fixes | Test, diagnose, implement safe fixes, and retest. Do not modify unrelated code or perform major dependency upgrades without approval. |
| `verify-fixes` | Re-checking previous issues | Retest specific issues. Confirm fixed or still failing. Run targeted regression around affected areas. Report new regressions. |

### Safety Boundaries

You MUST:
- Prefer local, preview, test, or staging environments
- Treat production as read-only unless the user explicitly authorizes specific tests
- Never run load, stress, destructive, payment, email, SMS, deletion, migration, or data-corruption tests against production without explicit authorization
- Never submit real purchases or use real customer information
- Use test accounts and synthetic test data
- Redact passwords, access tokens, API keys, cookies, personal information, payment data, and secrets from reports
- Avoid deleting or overwriting user data
- Preserve existing uncommitted code changes
- Avoid unrelated refactoring
- Stop and explain the blocker when testing requires credentials, permissions, external coordination, or potentially destructive action
- Distinguish application failures from test-environment or test-script failures
- Do not silently change lockfiles, upgrade dependencies, or install global software

### Audit Workflow

#### Phase 1: Discovery

1. **Detect product type**: web app, API, backend service, mobile-responsive web app, multi-service product, desktop app, mobile app, browser extension, or other.
2. **Inspect materials**: source repo, README, setup instructions, product requirements, user stories, acceptance criteria, architecture, routes/endpoints, database schema and migrations, existing tests, CI config, deployment config, monitoring and logging config.
3. **Detect stack**: languages, frameworks, package manager, build/test commands, runtime versions, database, external services, auth system, user roles/permissions, integrations (payment, email, file-upload, AI, analytics), supported browsers/devices, existing performance targets or SLOs.
4. **Identify critical user journeys** before testing: registration, login/logout, password recovery, onboarding, CRUD on primary object, search/filter/sort, checkout/subscription, file upload, form submission, invitation/collaboration, role/permission changes, saving/retrieving data, error recovery, cancellation/account deletion.
5. **Ask only for missing information that materially blocks testing.** Ask no more than three short questions at once.
6. **When requirements are incomplete**, state reasonable assumptions and continue with safe tests.

#### Phase 2: Test Plan

Create a risk-based test matrix before running tests. For each test track:
Test ID, Product area, User journey, Preconditions, Test steps, Expected result, Actual result, Environment, Browser/device, Status, Severity if failed, Evidence, Retest status.

Prioritize in this order:
1. Revenue, authentication, security, and data-loss risks
2. Critical user journeys
3. Performance and reliability
4. High-traffic features
5. Cross-browser and responsive behavior
6. Accessibility and usability
7. Secondary and edge-case behavior

#### Phase 3: Execute Tests

Run tests across these categories. See [references/test-checklists.md](references/test-checklists.md) for detailed checklists.

| Category | What's Tested |
|----------|--------------|
| Functional | Auth, CRUD, forms, navigation, edge cases, integrations. Test happy paths, failure paths, boundary conditions, recovery paths. |
| Visual & Responsive | 6 viewport widths (320px–1920px+), overflow, layout shifts, mobile keyboard, zoom. |
| Cross-browser | Chromium, Firefox, WebKit/Safari. Clearly state when a browser could not be tested. |
| Performance | Core Web Vitals, API latency, bundle size, memory, queries. See [references/performance-methodology.md](references/performance-methodology.md). |
| Load/Spike/Endurance | Only against authorized non-production environments. Establish expected load, stop conditions, protected endpoints first. |
| Security | Secrets, auth, XSS, injection, CORS, headers, dependencies. Safe review without destructive exploitation. |
| Accessibility | Automated checks plus manual keyboard and interaction checks. Do not claim compliance based only on automation. |
| Reliability | Failure scenarios, retries, idempotency, transaction correctness, recovery, health checks, rollback. |
| Usability | First-time UX, primary action clarity, consistent terminology, destructive action confirmations, error messages, empty states, duplicate prevention. Separate defects from suggestions. |
| Code Review | Architecture, business logic, error handling, validation, auth, database access, transactions, async/concurrency, retries, caching, logging, migrations, rollback readiness, type safety, dependency health. Do not equate lint warnings with user-facing defects. |
| Automated | Use the repo's existing commands first. Run: dependency install, type check, lint, format, unit/integration/E2E tests, build, production build, static analysis, dependency audit, accessibility automation, bundle analysis. |

#### Phase 4: Fixing (audit-and-fix mode only)

Follow this workflow for each fix:
1. Reproduce the defect
2. Record baseline measurement
3. Identify the root cause
4. Select the smallest safe fix
5. Preserve existing behavior outside the affected area
6. Implement the fix
7. Run the targeted test
8. Run surrounding regression tests
9. Repeat the original measurement
10. Compare before-and-after results
11. Report files changed and remaining risks

For performance fixes, always report: baseline measurement, suspected bottleneck, change made, post-fix measurement, percentage improvement (when meaningful), testing conditions, possible tradeoffs. Never report a fix based solely on code inspection.

#### Phase 5: Report

Produce the final report using the template in [references/report-template.md](references/report-template.md).
Apply the severity definitions and release gates from [references/severity-and-release-gates.md](references/severity-and-release-gates.md).

### Audit Scripts

```bash
# Scan for hardcoded secrets
python scripts/audit_secrets.py <directory> --json --gitignore

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

Do not inflate severity. Explain the concrete user and business impact.

### Key Principles

- Do not hide inconclusive results. Mark them as `NOT TESTED`, `BLOCKED`, or `INCONCLUSIVE`.
- Do not equate a lint warning with a user-facing defect. Classify by actual risk.
- Do not claim accessibility compliance based only on automated scanning.
- Do not claim the product is bug-free. The goal is to eliminate known release-blocking defects.

### Reference Documents

- [references/test-checklists.md](references/test-checklists.md) — 200+ checklist items
- [references/performance-methodology.md](references/performance-methodology.md) — metrics, targets, root cause analysis
- [references/severity-and-release-gates.md](references/severity-and-release-gates.md) — GO/NO-GO criteria
- [references/report-template.md](references/report-template.md) — structured report template

