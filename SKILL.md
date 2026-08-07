---
name: mvp-rocket
description: A toolset for handling messy JSON from LLMs and APIs. Repairs malformed JSON payloads and infers Zod, Pydantic, JSON Schema, or TypeScript type definitions from sample data. Use when you receive broken JSON, need to generate validation schemas, or want to speed up MVP data pipeline setup.
---

# MVP Rocket: JSON Repair & Schema Inference

## Overview

MVP Rocket provides two complementary utilities that form a pipeline for handling real-world JSON:

1. **`repair_json.py`** — Extracts and repairs malformed JSON from messy text (LLM output, scraped pages, logs)
2. **`json_to_schema.py`** — Infers strict validation schemas from JSON samples (Zod, Pydantic, JSON Schema, TypeScript)

## Quick Start: The Pipeline

The most powerful pattern is piping repair into schema generation:

```bash
# LLM spits out broken JSON → repair it → generate a Zod schema
cat llm_output.txt | python scripts/repair_json.py - --compact | python scripts/json_to_schema.py - --name Response

# Repair an API response, then generate Pydantic models
python scripts/repair_json.py api_dump.txt -o clean.json
python scripts/json_to_schema.py clean.json --lang pydantic --name User
```

---

## Capability 1: Repairing JSON (`repair_json.py`)

Heuristically repairs common JSON failure modes **outside string literals**.

### What It Fixes

| Category | Examples |
|----------|----------|
| Markdown code fences | ` ```json ... ``` ` and surrounding prose |
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

### CLI Usage

```bash
python scripts/repair_json.py raw.txt                       # repair → stdout (2-space indent)
python scripts/repair_json.py raw.txt --compact              # minified output
python scripts/repair_json.py raw.txt --indent 4             # 4-space indent
python scripts/repair_json.py raw.txt -o clean.json          # write to file
python scripts/repair_json.py raw.txt -i                     # repair in place
python scripts/repair_json.py raw.txt --check                # exit 0=valid, 1=needed repair
python scripts/repair_json.py raw.txt --quiet                # suppress stderr diagnostics
python scripts/repair_json.py raw.txt -e latin-1             # specify input encoding
cat raw.txt | python scripts/repair_json.py -                # stdin
python scripts/repair_json.py raw.txt --quiet --compact      # silent + compact (for pipelines)
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `input` | *(required)* | Path to file, or `-` for stdin |
| `-o`, `--output` | stdout | Write output to file |
| `-e`, `--encoding` | `utf-8-sig` | Input file encoding |
| `--indent` | `2` | Indentation level (0 = compact) |
| `--compact` | off | Minified output (same as `--indent 0`) |
| `--check` | off | Validation mode — no output, exit code only |
| `-i`, `--in-place` | off | Overwrite input file with repaired output |
| `--quiet` | off | Suppress stderr diagnostics |

### Library API

```python
import repair_json

# Quick parse — returns parsed object or raises JSONDecodeError
data = repair_json.loads(messy_text)

# Detailed — returns (parsed_object, list_of_applied_stages)
data, stages = repair_json.repair(messy_text)
```

---

## Capability 2: Inferring Schemas (`json_to_schema.py`)

Analyzes sample JSON and generates strict type definitions.

### Output Targets

| `--lang` | Output | Use Case |
|----------|--------|----------|
| `zod` *(default)* | Zod schema + TypeScript type | TypeScript/Node.js validation |
| `pydantic` | Pydantic v2 BaseModel classes | Python API validation |
| `jsonschema` | JSON Schema (Draft 2020-12) | OpenAPI docs, cross-language |
| `typescript` | Raw TypeScript `interface`/`type` | TS projects without Zod dependency |

### Features

- **Format detection**: UUID, email, URL, ISO date, ISO datetime
- **Enum inference**: Low-cardinality string fields auto-detected as `z.enum()` / `Literal[...]` (threshold: 10 by default)
- **Nullable handling**: `null + Type` → `.nullable()` / `Type | None`
- **Union types**: Heterogeneous values → `z.union([...])` / `X | Y`
- **Multi-sample merging**: Feed multiple records to discover optional fields
- **Loose mode**: `.passthrough()` / `extra="allow"` / `additionalProperties`
- **Recursion safety**: Depth-limited to 50 levels

### CLI Usage

```bash
# Generate Zod schema
python scripts/json_to_schema.py sample.json --name User

# Generate Pydantic models
python scripts/json_to_schema.py sample.json --lang pydantic --name User

# Generate JSON Schema
python scripts/json_to_schema.py sample.json --lang jsonschema --name User

# Generate TypeScript interfaces
python scripts/json_to_schema.py sample.json --lang typescript --name User

# Model array items (infer element schema from array of records)
python scripts/json_to_schema.py records.json --root-array-item --name Record

# Merge multiple sample files into one schema
python scripts/json_to_schema.py sample1.json sample2.json --merge --name Response

# Disable format detection
python scripts/json_to_schema.py data.json --no-formats

# Control enum detection threshold
python scripts/json_to_schema.py data.json --root-array-item --enums 5

# Cap array sampling for large files
python scripts/json_to_schema.py huge.json --max-array-samples 100

# Write to file
python scripts/json_to_schema.py sample.json -o schema.ts

# Loose mode (allow unknown keys)
python scripts/json_to_schema.py sample.json --loose

# stdin
cat payload.json | python scripts/json_to_schema.py - --name Payload
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `inputs` | *(required)* | One or more JSON file paths, or `-` for stdin |
| `--lang` | `zod` | Output target: `zod`, `pydantic`, `jsonschema`, `typescript` |
| `--name` | `Root` | Root schema/model name |
| `--root-array-item` | off | Model the array item, not the array itself |
| `--no-formats` | off | Skip string format detection |
| `--loose` | off | Allow unknown keys in output schema |
| `-o`, `--output` | stdout | Write output to file |
| `--enums` | `10` | Max unique values to detect as enum (0 = disabled) |
| `--max-array-samples` | all | Cap array elements sampled |
| `--merge` | off | Required when passing multiple input files |

> **Naming note**: `--name` is used as the root identifier. For Zod, `Schema` is automatically appended (e.g., `--name User` → `UserSchema`). Don't pass `--name UserSchema` or you'll get `UserSchemaSchema`.

---

## Resources

- `scripts/repair_json.py`: JSON repair utility (CLI + library)
- `scripts/json_to_schema.py`: Schema inference utility
