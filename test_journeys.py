#!/usr/bin/env python3
"""End-to-end integration tests for mvp-rocket critical user journeys.

Tests the full pipeline that a user would actually exercise:
1. Repair broken JSON from various sources
2. Generate schemas in all 4 output formats
3. Pipeline: repair -> schema
4. CLI flags (--check, --in-place, --output, --merge)
5. Library API (repair_json.loads, repair_json.repair)
6. Edge cases that would hit users in production
"""

import json
import os
import sys
import subprocess
import tempfile

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")
REPAIR = os.path.join(SCRIPTS_DIR, "repair_json.py")
SCHEMA = os.path.join(SCRIPTS_DIR, "json_to_schema.py")

passed = 0
failed = 0
skipped = 0

def test(name, condition, details=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}")
        if details:
            print(f"     → {details}")

def skip(name, reason):
    global skipped
    skipped += 1
    print(f"  ⏭️  {name} — SKIPPED: {reason}")

def run(cmd, stdin_data=None):
    r = subprocess.run(
        cmd, input=stdin_data, capture_output=True, text=True, timeout=30
    )
    return r

# ============================================================
print("\n🔧 Journey 1: Repairing Broken JSON")
print("=" * 50)

# 1a. LLM output with code fences
r = run([sys.executable, REPAIR, "-"], '```json\n{"name": "test"}\n```')
test("Markdown fences stripped", r.returncode == 0 and '"name"' in r.stdout)

# 1b. Python dict output
r = run([sys.executable, REPAIR, "-"], "{'key': True, 'val': None}")
data = json.loads(r.stdout) if r.returncode == 0 else None
test("Python dict (single quotes + True/None)", data == {"key": True, "val": None})

# 1c. Messy LLM output with multiple issues
messy = '{name: "test", active: True, count: 0xFF, tags: ("a" "b"), score: .95,}'
r = run([sys.executable, REPAIR, "-"], messy)
data = json.loads(r.stdout) if r.returncode == 0 else None
test("Multi-issue repair (7 stages)", 
     data == {"name": "test", "active": True, "count": 255, "tags": ["a", "b"], "score": 0.95},
     f"Got: {data}")

# 1d. Truncated JSON
r = run([sys.executable, REPAIR, "-"], '{"users": [{"name": "Alice"')
data = json.loads(r.stdout) if r.returncode == 0 else None
test("Truncated JSON auto-closed", data == {"users": [{"name": "Alice"}]}, f"Got: {data}")

# 1e. JSON with comments
r = run([sys.executable, REPAIR, "-"], '{\n  // API config\n  "url": "https://api.test.com",\n  /* timeout */ "timeout": 30\n}')
data = json.loads(r.stdout) if r.returncode == 0 else None
test("Comments stripped", data == {"url": "https://api.test.com", "timeout": 30})

# 1f. Already valid JSON (no repair needed)
r = run([sys.executable, REPAIR, "-"], '{"valid": true}')
test("Valid JSON passes through", r.returncode == 0 and "repaired via" not in r.stderr)

# ============================================================
print("\n📐 Journey 2: Schema Generation (All 4 Formats)")
print("=" * 50)

sample = '{"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Alice", "age": 30, "active": true, "email": "alice@test.com", "joined": "2024-01-15"}'

# 2a. Zod
r = run([sys.executable, SCHEMA, "-", "--name", "User", "--enums", "0"], sample)
test("Zod schema generated", 
     r.returncode == 0 and "z.object" in r.stdout and "UserSchema" in r.stdout)

# 2b. Pydantic
r = run([sys.executable, SCHEMA, "-", "--name", "User", "--lang", "pydantic", "--enums", "0"], sample)
test("Pydantic model generated",
     r.returncode == 0 and "BaseModel" in r.stdout and "class User" in r.stdout)

# 2c. JSON Schema
r = run([sys.executable, SCHEMA, "-", "--name", "User", "--lang", "jsonschema", "--enums", "0"], sample)
out = json.loads(r.stdout) if r.returncode == 0 else None
test("JSON Schema generated",
     out and "$schema" in out and "properties" in out and out["title"] == "User")

# 2d. TypeScript
r = run([sys.executable, SCHEMA, "-", "--name", "User", "--lang", "typescript", "--enums", "0"], sample)
test("TypeScript interface generated",
     r.returncode == 0 and "export interface" in r.stdout and "string" in r.stdout)

# 2e. Format detection
r = run([sys.executable, SCHEMA, "-", "--name", "User", "--lang", "jsonschema", "--enums", "0"], sample)
out = json.loads(r.stdout) if r.returncode == 0 else None
props = out.get("properties", {}) if out else {}
test("UUID format detected", props.get("id", {}).get("format") == "uuid", f"Got: {props.get('id')}")
test("Email format detected", props.get("email", {}).get("format") == "email", f"Got: {props.get('email')}")
test("Date format detected", props.get("joined", {}).get("format") == "date", f"Got: {props.get('joined')}")

# ============================================================
print("\n🔗 Journey 3: Full Pipeline (Repair → Schema)")
print("=" * 50)

messy_api = "```json\n{name: 'Alice', age: 30, role: 'admin', active: True}\n```"

# Step 1: Repair
r1 = run([sys.executable, REPAIR, "-", "--compact"], messy_api)
test("Pipeline step 1: repair", r1.returncode == 0)

# Step 2: Schema from repaired output
if r1.returncode == 0:
    r2 = run([sys.executable, SCHEMA, "-", "--name", "User", "--enums", "0"], r1.stdout)
    test("Pipeline step 2: schema from repaired JSON",
         r2.returncode == 0 and "z.object" in r2.stdout)
else:
    skip("Pipeline step 2", "Step 1 failed")

# ============================================================
print("\n⚙️  Journey 4: CLI Flags")
print("=" * 50)

# 4a. --check on valid JSON
r = run([sys.executable, REPAIR, "-", "--check"], '{"valid": true}')
test("--check returns 0 for valid JSON", r.returncode == 0 and r.stdout == "")

# 4b. --check on broken JSON
r = run([sys.executable, REPAIR, "-", "--check"], "{name: 'test'}")
test("--check returns 1 for repairable JSON", r.returncode == 1)

# 4c. --compact
r = run([sys.executable, REPAIR, "-", "--compact"], '{"a":    1,   "b":  2}')
test("--compact output", r.returncode == 0 and r.stdout.strip() == '{"a":1,"b":2}')

# 4d. --indent 4
r = run([sys.executable, REPAIR, "-", "--indent", "4"], '{"a": 1}')
test("--indent 4", r.returncode == 0 and "    " in r.stdout)

# 4e. --output to file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    tmpout = f.name
try:
    r = run([sys.executable, REPAIR, "-", "-o", tmpout], '{"a": 1}')
    with open(tmpout) as f:
        content = f.read()
    test("--output writes to file", '"a"' in content)
finally:
    os.unlink(tmpout)

# 4f. --in-place
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write("{name: 'test'}")
    tmpfile = f.name
try:
    r = run([sys.executable, REPAIR, tmpfile, "-i"])
    with open(tmpfile) as f:
        content = json.loads(f.read())
    test("--in-place repairs file", content == {"name": "test"})
finally:
    os.unlink(tmpfile)

# 4g. Schema --output to file
with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
    tmpschema = f.name
try:
    r = run([sys.executable, SCHEMA, "-", "--name", "T", "-o", tmpschema, "--enums", "0"], '{"x": 1}')
    with open(tmpschema) as f:
        content = f.read()
    test("Schema --output writes to file", "z.object" in content)
finally:
    os.unlink(tmpschema)

# 4h. Schema --merge with multiple files
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1, \
     tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
    json.dump({"a": 1, "b": "hello"}, f1); tmp1 = f1.name
    json.dump({"a": 2, "c": True}, f2); tmp2 = f2.name
try:
    r = run([sys.executable, SCHEMA, tmp1, tmp2, "--merge", "--name", "Merged", "--lang", "jsonschema", "--enums", "0"])
    out = json.loads(r.stdout) if r.returncode == 0 else None
    props = out.get("properties", {}) if out else {}
    test("--merge combines schemas", "a" in props and "b" in props and "c" in props, f"Got props: {list(props.keys())}")
finally:
    os.unlink(tmp1); os.unlink(tmp2)

# ============================================================
print("\n📚 Journey 5: Library API")
print("=" * 50)

sys.path.insert(0, SCRIPTS_DIR)
import repair_json

# 5a. loads()
data = repair_json.loads("{name: 'test', active: True}")
test("repair_json.loads() works", data == {"name": "test", "active": True})

# 5b. repair() returns stages
data, stages = repair_json.repair("{name: 'test'}")
test("repair() returns applied stages", len(stages) > 0 and isinstance(stages, list))

# 5c. loads() on valid JSON
data = repair_json.loads('{"valid": true}')
test("loads() on valid JSON (no repair)", data == {"valid": True})

# 5d. loads() raises on garbage
try:
    repair_json.loads("not json at all !!!")
    test("loads() raises on garbage", False, "Should have raised")
except json.JSONDecodeError:
    test("loads() raises JSONDecodeError on garbage", True)

# ============================================================
print("\n🌐 Journey 6: Browser Testing")
print("=" * 50)
skip("Chrome testing", "mvp-rocket is a CLI/library tool with no web UI")
skip("Firefox testing", "mvp-rocket is a CLI/library tool with no web UI")
skip("Safari testing", "mvp-rocket is a CLI/library tool with no web UI")
skip("Edge testing", "mvp-rocket is a CLI/library tool with no web UI")

# ============================================================
print("\n" + "=" * 50)
total = passed + failed + skipped
print(f"\n📊 Results: {passed} passed, {failed} failed, {skipped} skipped ({total} total)")
if failed == 0:
    print("🎉 All critical user journeys passed!")
else:
    print(f"⚠️  {failed} journey(s) need attention")
    sys.exit(1)
