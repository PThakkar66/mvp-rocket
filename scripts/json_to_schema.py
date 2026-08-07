#!/usr/bin/env python3
"""Infer a validation schema from sample JSON.

Turns a real API/webhook/LLM payload into a Zod schema (TypeScript), Pydantic v2 model (Python), 
JSON Schema, or raw TypeScript interfaces, so boundaries get validated without hand-writing
types from a payload you already have.

Usage:
    python json_to_schema.py sample.json                    # Zod (default)
    python json_to_schema.py sample.json --lang pydantic
    python json_to_schema.py sample.json --lang jsonschema
    python json_to_schema.py sample.json --lang typescript
    cat payload.json | python json_to_schema.py -           # stdin
    python json_to_schema.py sample.json --name User --root-array-item
    python json_to_schema.py f1.json f2.json --merge

Options:
    --lang {zod,pydantic,jsonschema,typescript}   Output target. Default: zod.
    --name NAME             Root schema/model name. Default: Root.
    --root-array-item       If top level is an array, model the ITEM, not the array.
    --no-formats            Skip string format detection (email/uuid/url/datetime/date).
    --loose                 Emit .passthrough() (zod) / extra="allow" (pydantic) / additionalProperties (jsonschema)
    -o, --output            Write to a file instead of stdout.
    --enums, --enum-threshold Threshold for enum generation (default: 10).
    --max-array-samples     Max array elements to sample.
    --merge                 Merge multiple input files.

Notes:
    Inference reflects the SAMPLE, not the contract. Fields absent from every
    sampled record cannot be discovered. Widen with real production payloads
    before trusting the output.
"""

import argparse
import builtins
import json
import keyword
import re
import sys
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------- type model

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")
UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL = re.compile(r"^https?://\S+$")

RESERVED_PY = set(keyword.kwlist) | set(dir(builtins))


@dataclass
class Config:
    formats: bool = True
    max_samples: int = 0
    enum_threshold: int = 10


def detect_format(s: str, enabled: bool) -> str | None:
    if not enabled or not s:
        return None
    if UUID.match(s):
        return "uuid"
    if EMAIL.match(s):
        return "email"
    if URL.match(s):
        return "url"
    if ISO_DATE.match(s):
        return "date"
    if ISO_DT.match(s):
        return "datetime"
    return None


def infer(value: Any, config: Config, depth: int = 0) -> dict:
    if depth > 50:
        if depth == 51:
            print("warning: recursion depth exceeded 50 during inference", file=sys.stderr)
        return {"kind": "unknown"}

    if value is None:
        return {"kind": "null"}
    if isinstance(value, bool):
        return {"kind": "bool"}
    if isinstance(value, int):
        return {"kind": "int"}
    if isinstance(value, float):
        return {"kind": "float"}
    if isinstance(value, str):
        fmt = detect_format(value, config.formats)
        node = {"kind": "string", "format": fmt}
        if config.enum_threshold > 0:
            node["values"] = {value}
        return node
    if isinstance(value, list):
        item = None
        for i, el in enumerate(value):
            if config.max_samples > 0 and i >= config.max_samples:
                break
            node = infer(el, config, depth + 1)
            item = node if item is None else merge(item, node, config, depth + 1)
        return {"kind": "array", "item": item}
    if isinstance(value, dict):
        props = {k: infer(v, config, depth + 1) for k, v in value.items()}
        return {"kind": "object", "props": props, "required": set(props.keys())}
    return {"kind": "unknown"}


def merge(a: dict, b: dict, config: Config, depth: int = 0) -> dict:
    """Combine two inferred nodes into one that accepts both."""
    if depth > 50:
        return {"kind": "unknown"}

    if a == b:
        return a
    ka, kb = a["kind"], b["kind"]

    # null + X  ->  X, marked nullable
    if ka == "null" and kb != "null":
        out = dict(b)
        out["nullable"] = True
        return out
    if kb == "null" and ka != "null":
        out = dict(a)
        out["nullable"] = True
        return out

    nullable = a.get("nullable") or b.get("nullable")

    def finish(node: dict) -> dict:
        if nullable:
            node = dict(node)
            node["nullable"] = True
        return node

    # numeric widening
    if {ka, kb} <= {"int", "float"}:
        return finish({"kind": "float" if "float" in (ka, kb) else "int"})

    if ka == "string" and kb == "string":
        fmt = a.get("format") if a.get("format") == b.get("format") else None
        node = {"kind": "string", "format": fmt}
        if config.enum_threshold > 0:
            av = a.get("values", set())
            bv = b.get("values", set())
            if av is not None and bv is not None:
                merged_v = av | bv
                if len(merged_v) <= config.enum_threshold:
                    node["values"] = merged_v
                else:
                    node["values"] = None
            else:
                node["values"] = None
        return finish(node)

    if ka == "array" and kb == "array":
        ia, ib = a.get("item"), b.get("item")
        item = ib if ia is None else (ia if ib is None else merge(ia, ib, config, depth + 1))
        return finish({"kind": "array", "item": item})

    if ka == "object" and kb == "object":
        props: dict[str, dict] = {}
        # Preserve first-seen key order so codegen output is stable across runs.
        ordered = list(a["props"]) + [k for k in b["props"] if k not in a["props"]]
        for key in ordered:
            if key in a["props"] and key in b["props"]:
                props[key] = merge(a["props"][key], b["props"][key], config, depth + 1)
            else:
                props[key] = a["props"].get(key) or b["props"][key]
        # required only where present in BOTH samples
        required = set(a["required"]) & set(b["required"])
        return finish({"kind": "object", "props": props, "required": required})

    if ka == kb:
        return finish({"kind": ka})

    # genuinely different -> union
    opts: list[dict] = []
    for node_it in (a, b):
        for o in node_it["options"] if node_it["kind"] == "union" else [node_it]:
            if o not in opts:
                opts.append(o)
    return finish({"kind": "union", "options": opts})


def finalize(node: dict):
    """Post-process nodes before emitting."""
    if node["kind"] == "string" and node.get("values") is not None:
        node["enum_values"] = sorted(list(node["values"]))
        del node["values"]
    elif node["kind"] == "array" and node.get("item"):
        finalize(node["item"])
    elif node["kind"] == "object":
        for child in node["props"].values():
            finalize(child)
    elif node["kind"] == "union":
        for opt in node["options"]:
            finalize(opt)


# ------------------------------------------------------------------ emitters
def pascal(name: str) -> str:
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Field"


def to_snake_case(name: str) -> str:
    name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    return re.sub(r'[^a-zA-Z0-9]+', '_', name).strip('_').lower() or "field"


SAFE_KEY = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


def zod_key(k: str) -> str:
    return k if SAFE_KEY.match(k) else json.dumps(k)


ZOD_FORMATS = {
    "uuid": "z.string().uuid()",
    "email": "z.string().email()",
    "url": "z.string().url()",
    "datetime": "z.string().datetime({ offset: true })",
    "date": "z.string().date()",
}


def to_zod(node: dict, indent: int, loose: bool, depth: int = 0) -> str:
    if depth > 50:
        return "z.unknown()"

    pad = "  " * indent
    kind = node["kind"]

    if kind == "object":
        if not node["props"]:
            base = "z.record(z.unknown())"
        else:
            lines = ["z.object({"]
            for key, child in node["props"].items():
                optional = "" if key in node["required"] else ".optional()"
                lines.append(f"{pad}  {zod_key(key)}: {to_zod(child, indent + 1, loose, depth + 1)}{optional},")
            lines.append(pad + "})")
            base = "\n".join(lines)
            if loose:
                base += ".passthrough()"
    elif kind == "array":
        inner = to_zod(node["item"], indent, loose, depth + 1) if node.get("item") else "z.unknown()"
        base = f"z.array({inner})"
    elif kind == "union":
        opts = ", ".join(to_zod(o, indent, loose, depth + 1) for o in node["options"])
        base = f"z.union([{opts}])"
    elif kind == "string":
        if "enum_values" in node:
            if len(node["enum_values"]) == 1:
                base = f"z.literal({json.dumps(node['enum_values'][0])})"
            else:
                opts = ", ".join(json.dumps(v) for v in node["enum_values"])
                base = f"z.enum([{opts}])"
        else:
            base = ZOD_FORMATS.get(node.get("format") or "", "z.string()")
    elif kind == "int":
        base = "z.number().int()"
    elif kind == "float":
        base = "z.number()"
    elif kind == "bool":
        base = "z.boolean()"
    elif kind == "null":
        base = "z.null()"
    else:
        base = "z.unknown()"

    if node.get("nullable") and kind != "null":
        base += ".nullable()"
    return base


def emit_zod(root: dict, name: str, loose: bool) -> str:
    schema = pascal(name) + "Schema"
    return (
        'import { z } from "zod";\n\n'
        f"export const {schema} = {to_zod(root, 0, loose)};\n\n"
        f"export type {pascal(name)} = z.infer<typeof {schema}>;\n"
    )


PY_SCALARS = {"int": "int", "float": "float", "bool": "bool", "string": "str",
              "null": "None", "unknown": "Any"}
PY_FORMATS = {"uuid": "UUID", "email": "EmailStr", "url": "HttpUrl", "datetime": "datetime", "date": "date"}


def to_pydantic(node: dict, name: str, models: list[str], seen: set[str], loose: bool, depth: int = 0) -> str:
    """Return the annotation for `node`, appending nested models to `models`."""
    if depth > 50:
        return "Any"

    kind = node["kind"]

    if kind == "object":
        if not node["props"]:
            ann = "dict[str, Any]"
        else:
            base_cls = pascal(name)
            if len(base_cls) > 30:
                base_cls = base_cls[-30:]
            cls = base_cls
            idx = 1
            while cls in seen:
                idx += 1
                cls = f"{base_cls}{idx}"
            seen.add(cls)

            body = [f"class {cls}(BaseModel):"]
            if loose:
                body.append('    model_config = ConfigDict(extra="allow")')
            for key, child in node["props"].items():
                ann_child = to_pydantic(child, f"{cls}_{key}", models, seen, loose, depth + 1)
                
                field = to_snake_case(key)
                if field in RESERVED_PY or field[0].isdigit() or not SAFE_KEY.match(field):
                    field = f"_{field}" if not field[0].isdigit() else f"field_{field}"
                    if field in RESERVED_PY:
                        field = f"{field}_field"
                        
                alias = "" if field == key else f' = Field(alias="{key}")'
                if key not in node["required"]:
                    if not ann_child.endswith("None"):
                        ann_child = f"{ann_child} | None"
                    alias = (f' = Field(default=None, alias="{key}")' if field != key else " = None")
                body.append(f"    {field}: {ann_child}{alias}")
            models.append("\n".join(body))
            ann = cls
    elif kind == "array":
        inner = to_pydantic(node["item"], name + "Item", models, seen, loose, depth + 1) if node.get("item") else "Any"
        ann = f"list[{inner}]"
    elif kind == "union":
        ann = " | ".join(to_pydantic(o, f"{name}{i}", models, seen, loose, depth + 1) for i, o in enumerate(node["options"]))
    elif kind == "string":
        if "enum_values" in node:
            vals = ", ".join(f'"{v}"' for v in node["enum_values"])
            ann = f"Literal[{vals}]"
        else:
            ann = PY_FORMATS.get(node.get("format", ""), "str")
    else:
        ann = PY_SCALARS.get(kind, "Any")

    if node.get("nullable") and kind != "null" and not ann.endswith("None"):
        ann = f"{ann} | None"
    return ann


def emit_pydantic(root: dict, name: str, loose: bool) -> str:
    models: list[str] = []
    seen = set()
    ann = to_pydantic(root, name, models, seen, loose)
    body = "\n\n\n".join(models)
    if not models:
        body = f"{pascal(name)} = {ann}"

    # Import only what the generated body actually references.
    stdlib, third = [], []
    dt_imports = []
    if re.search(r"\bdatetime\b", body):
        dt_imports.append("datetime")
    if re.search(r"\bdate\b", body) and not re.search(r"def date\b", body):  # simplistic heuristic
        dt_imports.append("date")
    if dt_imports:
        stdlib.append(f"from datetime import {', '.join(sorted(set(dt_imports)))}")

    if re.search(r"\bAny\b", body):
        stdlib.append("from typing import Any")
    if re.search(r"\bLiteral\b", body):
        stdlib.append("from typing import Literal")
    if re.search(r"\bUUID\b", body):
        stdlib.append("from uuid import UUID")

    pyd = []
    if models:
        pyd.append("BaseModel")
    for sym in ("ConfigDict", "EmailStr", "Field", "HttpUrl"):
        if re.search(rf"\b{sym}\b", body):
            pyd.append(sym)
    
    if pyd:
        third.append("from pydantic import " + ", ".join(sorted(set(pyd))))

    parts = ["from __future__ import annotations", ""]
    if stdlib:
        parts += stdlib + [""]
    if third:
        parts += third + [""]
    header = "\n".join(parts) + ("\n" if parts[-1] else "")

    note = ""
    if "EmailStr" in body:
        note = "# EmailStr requires: pip install 'pydantic[email]'\n"
    return header + note + body.rstrip() + "\n"


def emit_jsonschema(root: dict, name: str, loose: bool) -> str:
    def to_js(node: dict, depth: int) -> dict:
        if depth > 50:
            return {}

        kind = node["kind"]
        res = {}

        if kind == "object":
            res["type"] = "object"
            if node["props"]:
                res["properties"] = {k: to_js(v, depth + 1) for k, v in node["props"].items()}
                if node["required"]:
                    res["required"] = sorted(list(node["required"]))
            if loose:
                res["additionalProperties"] = True
        elif kind == "array":
            res["type"] = "array"
            res["items"] = to_js(node["item"], depth + 1) if node.get("item") else {}
        elif kind == "union":
            res["anyOf"] = [to_js(o, depth + 1) for o in node["options"]]
        elif kind == "string":
            res["type"] = "string"
            if "enum_values" in node:
                res["enum"] = node["enum_values"]
            elif node.get("format"):
                res["format"] = "date-time" if node["format"] == "datetime" else node["format"]
        elif kind == "int":
            res["type"] = "integer"
        elif kind == "float":
            res["type"] = "number"
        elif kind == "bool":
            res["type"] = "boolean"
        elif kind == "null":
            res["type"] = "null"

        if node.get("nullable") and kind != "null":
            if "type" in res:
                if isinstance(res["type"], str):
                    res["type"] = [res["type"], "null"]
                elif isinstance(res["type"], list):
                    res["type"].append("null")
            elif "anyOf" in res:
                res["anyOf"].append({"type": "null"})
        return res

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": pascal(name),
        **to_js(root, 0)
    }
    return json.dumps(schema, indent=2) + "\n"


def emit_typescript(root: dict, name: str, loose: bool) -> str:
    interfaces: list[str] = []
    seen = set()

    def to_ts(node: dict, tname: str, depth: int) -> str:
        if depth > 50:
            return "any"

        kind = node["kind"]
        if kind == "object":
            if not node["props"]:
                ts = "Record<string, any>"
            else:
                base_cls = pascal(tname)
                if len(base_cls) > 30:
                    base_cls = base_cls[-30:]
                cls = base_cls
                idx = 1
                while cls in seen:
                    idx += 1
                    cls = f"{base_cls}{idx}"
                seen.add(cls)

                lines = [f"export interface {cls} {{"]
                for key, child in node["props"].items():
                    child_ts = to_ts(child, f"{cls}_{key}", depth + 1)
                    opt = "?" if key not in node["required"] else ""
                    safe_k = key if SAFE_KEY.match(key) else json.dumps(key)
                    lines.append(f"  {safe_k}{opt}: {child_ts};")

                if loose:
                    lines.append("  [key: string]: any;")

                lines.append("}")
                interfaces.append("\n".join(lines))
                ts = cls
        elif kind == "array":
            inner = to_ts(node["item"], tname + "Item", depth + 1) if node.get("item") else "any"
            if " " in inner or "|" in inner:
                ts = f"({inner})[]"
            else:
                ts = f"{inner}[]"
        elif kind == "union":
            ts = " | ".join(to_ts(o, f"{tname}{i}", depth + 1) for i, o in enumerate(node["options"]))
        elif kind == "string":
            if "enum_values" in node:
                ts = " | ".join(json.dumps(v) for v in node["enum_values"])
            else:
                ts = "string"
        elif kind in ("int", "float"):
            ts = "number"
        elif kind == "bool":
            ts = "boolean"
        elif kind == "null":
            ts = "null"
        else:
            ts = "any"

        if node.get("nullable") and kind != "null":
            if not ts.endswith(" | null"):
                if " | " in ts and not ts.startswith("("):
                    ts = f"({ts}) | null"
                else:
                    ts = f"{ts} | null"
        return ts

    root_ts = to_ts(root, name, 0)
    
    if root["kind"] != "object":
        interfaces.append(f"export type {pascal(name)} = {root_ts};")

    return "\n\n".join(interfaces) + "\n"


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Infer a Zod, Pydantic, JSON Schema, or TypeScript schema from sample JSON.")
    ap.add_argument("inputs", nargs="+", help="Path(s) to JSON files, or '-' for stdin")
    ap.add_argument("--lang", choices=["zod", "pydantic", "jsonschema", "typescript"], default="zod")
    ap.add_argument("--name", default="Root")
    ap.add_argument("--root-array-item", action="store_true",
                    help="Model the array ITEM when the top level is an array")
    ap.add_argument("--no-formats", action="store_true")
    ap.add_argument("--loose", action="store_true")
    ap.add_argument("-o", "--output", help="Write output to file instead of stdout")
    ap.add_argument("--enums", "--enum-threshold", dest="enum_threshold", type=int, default=10,
                    help="Max unique values to emit as enum/Literal (default: 10)")
    ap.add_argument("--max-array-samples", type=int, default=0,
                    help="Max number of array elements to sample")
    ap.add_argument("--merge", action="store_true", help="Merge multiple input files")
    args = ap.parse_args()

    if len(args.inputs) > 1 and not args.merge:
        print("error: multiple input files provided but --merge was not specified.", file=sys.stderr)
        return 1

    config = Config(formats=not args.no_formats,
                    max_samples=args.max_array_samples,
                    enum_threshold=args.enum_threshold)
    root = None

    for inp in args.inputs:
        try:
            raw = sys.stdin.read() if inp == "-" else open(inp, encoding="utf-8").read()
            data = json.loads(raw)
        except Exception as exc:
            print(f"error: failed to read or parse input from '{inp}' ({exc}).", file=sys.stderr)
            print("hint: ensure file exists and contains valid JSON.", file=sys.stderr)
            return 1

        if args.root_array_item and isinstance(data, list):
            if not data:
                print(f"warning: --root-array-item given but array in '{inp}' is empty.", file=sys.stderr)
                continue
            for i, el in enumerate(data):
                if config.max_samples > 0 and i >= config.max_samples:
                    break
                n = infer(el, config)
                root = n if root is None else merge(root, n, config)
        else:
            n = infer(data, config)
            root = n if root is None else merge(root, n, config)

    if root is None:
        print("error: no data to infer from.", file=sys.stderr)
        return 1

    finalize(root)

    if args.lang == "zod":
        out = emit_zod(root, args.name, args.loose)
    elif args.lang == "pydantic":
        out = emit_pydantic(root, args.name, args.loose)
    elif args.lang == "jsonschema":
        out = emit_jsonschema(root, args.name, args.loose)
    else:
        out = emit_typescript(root, args.name, args.loose)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out)
        except Exception as exc:
            print(f"error: failed to write to '{args.output}' ({exc}).", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
