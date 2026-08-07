# MVP Rocket 🚀

**JSON Repair & Schema Inference — from messy LLM output to strict types in one pipeline.**

MVP Rocket provides two complementary Python utilities for handling real-world JSON:

1. **`repair_json.py`** — Extracts and repairs malformed JSON from messy text (LLM output, scraped pages, logs)
2. **`json_to_schema.py`** — Infers strict validation schemas from JSON samples

Zero dependencies — Python 3.10+ stdlib only.

---

## Quick Start

```bash
# Repair broken JSON from an LLM
echo "{name: 'test', active: True, count: 0xFF, tags: ('a' 'b'), score: .95,}" \
  | python scripts/repair_json.py -

# Output:
# {"name": "test", "active": true, "count": 255, "tags": ["a", "b"], "score": 0.95}

# Generate a Zod schema from a JSON sample
python scripts/json_to_schema.py sample.json --name User

# The full pipeline: repair → schema
cat llm_output.txt | python scripts/repair_json.py - --compact \
  | python scripts/json_to_schema.py - --name Response
```

---

## `repair_json.py`

Heuristically repairs common JSON failure modes **outside string literals**.

### What It Fixes

| Category | Examples |
|----------|----------|
| Markdown code fences | `` ```json ... ``` `` and surrounding prose |
| Smart quotes | `"curly"` → `"straight"` |
| Comments | `//` line and `/* block */` comments |
| Single-quoted strings | `'hello'` → `"hello"` |
| Unquoted object keys | `{name: "val"}` → `{"name": "val"}` |
| Python/JS literals | `True`/`False`/`None`/`undefined`/`NaN`/`Infinity`/`nil` (case-insensitive) |
| Trailing commas | `{"a": 1,}` and multiple commas `{"a": 1,,}` |
| Truncated output | Unclosed strings, objects, arrays auto-closed |
| Unescaped newlines | Literal `\n`/`\t`/`\r` inside strings |
| Hex/octal numbers | `0xFF` → `255`, `0o77` → `63` |
| Non-standard floats | `.5` → `0.5`, `5.` → `5.0`, `+5` → `5` |
| Missing commas | `"a" "b"` → `"a", "b"` |
| Python tuples | `(1, 2, 3)` → `[1, 2, 3]` |
| UTF-8 BOM | Stripped automatically |

### CLI

```bash
python scripts/repair_json.py raw.txt                  # repair → stdout
python scripts/repair_json.py raw.txt --compact         # minified
python scripts/repair_json.py raw.txt --indent 4        # 4-space indent
python scripts/repair_json.py raw.txt -o clean.json     # write to file
python scripts/repair_json.py raw.txt -i                # in-place
python scripts/repair_json.py raw.txt --check           # exit 0=valid, 1=needs repair
python scripts/repair_json.py raw.txt -e latin-1        # specify encoding
cat raw.txt | python scripts/repair_json.py -           # stdin
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | stdout | Write to file |
| `-e`, `--encoding` | `utf-8-sig` | Input encoding |
| `--indent` | `2` | Indentation (0 = compact) |
| `--compact` | off | Alias for `--indent 0` |
| `--check` | off | Validation mode, no output |
| `-i`, `--in-place` | off | Overwrite input file |
| `--quiet` | off | Suppress diagnostics |

### Library API

```python
import repair_json

data = repair_json.loads(messy_text)                   # parse or raise
data, stages = repair_json.repair(messy_text)           # parse + list of applied repairs
```

---

## `json_to_schema.py`

Analyzes sample JSON and generates strict type definitions.

### Output Targets

| `--lang` | Output | Use Case |
|----------|--------|----------|
| `zod` *(default)* | Zod schema + TS type | TypeScript/Node.js |
| `pydantic` | Pydantic v2 models | Python APIs |
| `jsonschema` | JSON Schema 2020-12 | OpenAPI, cross-language |
| `typescript` | Raw TS interfaces | TS without Zod |

### Features

- **Format detection**: UUID, email, URL, ISO date, ISO datetime
- **Enum inference**: Low-cardinality strings → `z.enum()` / `Literal[...]` (configurable threshold)
- **Nullable handling**: `null + Type` → `.nullable()` / `Type | None`
- **Union types**: Heterogeneous values → `z.union([...])`
- **Multi-sample merging**: Feed multiple records to discover optional fields
- **Loose mode**: `.passthrough()` / `extra="allow"` / `additionalProperties`

### CLI

```bash
python scripts/json_to_schema.py sample.json --name User
python scripts/json_to_schema.py sample.json --lang pydantic --name User
python scripts/json_to_schema.py sample.json --lang jsonschema --name User
python scripts/json_to_schema.py sample.json --lang typescript --name User

# Model array items
python scripts/json_to_schema.py records.json --root-array-item --name Record

# Merge multiple files
python scripts/json_to_schema.py s1.json s2.json --merge --name Response

# Control enum threshold
python scripts/json_to_schema.py data.json --enums 5

# Disable enums & format detection
python scripts/json_to_schema.py data.json --enums 0 --no-formats

# Write to file
python scripts/json_to_schema.py sample.json -o schema.ts
```

| Flag | Default | Description |
|------|---------|-------------|
| `--lang` | `zod` | `zod`, `pydantic`, `jsonschema`, `typescript` |
| `--name` | `Root` | Root schema name |
| `--root-array-item` | off | Model array element, not array |
| `--no-formats` | off | Skip format detection |
| `--loose` | off | Allow unknown keys |
| `-o`, `--output` | stdout | Write to file |
| `--enums` | `10` | Enum threshold (0 = disabled) |
| `--max-array-samples` | all | Cap sampling |
| `--merge` | off | Merge multiple inputs |

> **Naming tip**: For Zod, `Schema` is auto-appended. Use `--name User` (not `--name UserSchema`).

---

## License

MIT
