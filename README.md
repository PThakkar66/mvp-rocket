# MVP Rocket 🚀

**Two-part MVP acceleration toolkit**: from messy LLM output to strict types, and from codebase to defensible launch recommendation.

Zero dependencies — Python 3.10+ stdlib only.

---

## Part 1: JSON Repair & Schema Inference

### `repair_json.py`

Extracts and repairs malformed JSON from messy text (LLM output, scraped pages, logs).

```bash
# Repair broken JSON from an LLM
echo "{name: 'test', active: True, count: 0xFF, tags: ('a' 'b'), score: .95,}" \
  | python scripts/repair_json.py -

# Output: {"name": "test", "active": true, "count": 255, "tags": ["a", "b"], "score": 0.95}
```

#### What It Fixes

| Category | Examples |
|----------|----------|
| Markdown code fences | `` ```json ... ``` `` |
| Smart quotes | `"curly"` → `"straight"` |
| Comments | `//` line and `/* block */` |
| Single-quoted strings | `'hello'` → `"hello"` |
| Unquoted object keys | `{name: "val"}` → `{"name": "val"}` |
| Python/JS literals | `True`/`False`/`None`/`undefined`/`NaN`/`Infinity` |
| Trailing commas | `{"a": 1,}` and multiple commas |
| Truncated output | Unclosed strings, objects, arrays auto-closed |
| Hex/octal numbers | `0xFF` → `255`, `0o77` → `63` |
| Non-standard floats | `.5` → `0.5`, `5.` → `5.0` |
| Missing commas | `"a" "b"` → `"a", "b"` |
| Python tuples | `(1, 2, 3)` → `[1, 2, 3]` |
| UTF-8 BOM | Stripped automatically |

#### CLI

```bash
python scripts/repair_json.py raw.txt                  # repair → stdout
python scripts/repair_json.py raw.txt --compact         # minified
python scripts/repair_json.py raw.txt --indent 4        # 4-space indent
python scripts/repair_json.py raw.txt -o clean.json     # write to file
python scripts/repair_json.py raw.txt -i                # in-place
python scripts/repair_json.py raw.txt --check           # exit 0=valid, 1=needs repair
cat raw.txt | python scripts/repair_json.py -           # stdin
```

#### Library API

```python
import repair_json
data = repair_json.loads(messy_text)
data, stages = repair_json.repair(messy_text)
```

---

### `json_to_schema.py`

Analyzes sample JSON and generates strict type definitions.

```bash
python scripts/json_to_schema.py sample.json --name User                          # Zod (default)
python scripts/json_to_schema.py sample.json --name User --lang pydantic          # Pydantic v2
python scripts/json_to_schema.py sample.json --name User --lang jsonschema        # JSON Schema 2020-12
python scripts/json_to_schema.py sample.json --name User --lang typescript        # TypeScript interfaces
```

#### Features

- **Format detection**: UUID, email, URL, ISO date, ISO datetime
- **Enum inference**: low-cardinality strings → `z.enum()` / `Literal[...]`
- **Nullable handling**: `null + Type` → `.nullable()` / `Type | None`
- **Multi-sample merging**: feed multiple records to discover optional fields
- **Loose mode**: `.passthrough()` / `extra="allow"` / `additionalProperties`

#### The Full Pipeline

```bash
cat llm_output.txt | python scripts/repair_json.py - --compact \
  | python scripts/json_to_schema.py - --name Response
```

---

## Part 2: Release Auditor

Scans an MVP codebase for release blockers and produces a **GO / CONDITIONAL GO / NO-GO** recommendation.

### Operating Modes

| Mode | Behavior |
|------|----------|
| `audit-only` (default) | Inspect and report. No code changes. |
| `audit-and-fix` | Diagnose, fix, measure before/after, retest. |
| `verify-fixes` | Retest previous findings + regression check. |

### What It Covers

| Category | Examples |
|----------|----------|
| **Functional** | Auth, CRUD, forms, navigation, edge cases, integrations |
| **Performance** | Core Web Vitals, API latency, bundle size, memory, queries |
| **Security** | Secrets, auth, XSS, injection, CORS, headers, dependencies |
| **Accessibility** | Keyboard, focus, contrast, semantics, screen readers |
| **Cross-browser** | Chromium, Firefox, WebKit/Safari |
| **Responsive** | 320px → 1920px, overflow, layout shifts |
| **Reliability** | Failure handling, retries, idempotency, data consistency |
| **Usability** | First-time UX, error recovery, empty states |
| **Code Review** | Architecture, error handling, type safety, deployment |

### Audit Scripts

```bash
# Scan for hardcoded secrets (API keys, passwords, tokens)
python scripts/audit_secrets.py <directory> --json --gitignore

# Scan for TODO/FIXME/HACK comments with severity
python scripts/audit_todos.py <directory> --json --severity
```

### Reference Documents

- [`references/test-checklists.md`](references/test-checklists.md) — 200+ test items across 7 categories
- [`references/performance-methodology.md`](references/performance-methodology.md) — metrics, targets, root cause analysis
- [`references/severity-and-release-gates.md`](references/severity-and-release-gates.md) — severity definitions + GO/NO-GO criteria
- [`references/report-template.md`](references/report-template.md) — structured 18-section report template

---

## Testing

```bash
pip install pytest
python -m pytest tests/ -v          # 67 unit tests
python test_journeys.py             # 27 E2E journey tests
```

## License

MIT
