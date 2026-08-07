#!/usr/bin/env python3
"""Extract and repair JSON from messy real-world text.

Handles the failure modes that break `json.loads` / `JSON.parse` on output from
LLMs, scrapers, logs, and loosely-specified APIs:

  - markdown code fences and surrounding prose
  - trailing commas
  - single-quoted strings and unquoted object keys
  - Python literals (True / False / None) and NaN / Infinity
  - // and /* */ comments
  - smart quotes from copy-pasted text
  - truncated output (unclosed strings, objects, arrays)

Usage:
    python repair_json.py raw.txt
    cat raw.txt | python repair_json.py -
    python repair_json.py raw.txt --compact
    python repair_json.py raw.txt --quiet     # exit 1 on failure, no diagnostics

Exit codes: 0 = valid JSON on stdout, 1 = unrecoverable.

Repairs are heuristic and applied outside string literals only. When this is
patching over a recurring upstream bug, fix the producer; use this at the
boundary, then validate the result with a real schema.
"""

import argparse
import json
import re
import sys

FENCE = re.compile(r"```(?:json5?|javascript|js)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def strip_fences(text: str) -> str:
    blocks = FENCE.findall(text)
    if blocks:
        # Prefer the longest fenced block that looks like JSON.
        cands = [b.strip() for b in blocks if b.strip().startswith(("{", "[", "/"))]
        if cands:
            return max(cands, key=len)
        return max(blocks, key=len).strip()
    return text


def extract_span(text: str) -> str:
    """Return the outermost {...} or [...] span, tolerating truncation."""
    starts = [i for i, c in enumerate(text) if c in "{["]
    if not starts:
        return text.strip()
    
    # Prefer the first bracket that starts a valid-looking JSON structure
    valid_starts = []
    for i in starts:
        if i > 0 and text[i-1].isalnum():
            continue
        if text[i] == '{':
            if re.match(r'\{\s*["\'}]', text[i:]):
                valid_starts.append(i)
        else:
            if re.match(r'\[\s*["\'{\[0-9a-zA-Z-]', text[i:]):
                valid_starts.append(i)
                
    start = valid_starts[0] if valid_starts else starts[0]

    depth = 0
    in_str = False
    quote = ""
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
            continue
        if c in "\"'":
            in_str = True
            quote = c
        elif c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]  # truncated — close_open() will finish it


def _split_strings(s: str):
    """Yield (is_string, chunk) so repairs never touch string contents."""
    out = []
    start = 0
    in_str = False
    quote = ""
    esc = False
    for i, c in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                out.append((True, s[start:i+1]))
                start = i + 1
                in_str = False
            continue
        if c in "\"'":
            if i > start:
                out.append((False, s[start:i]))
            start = i
            in_str = True
            quote = c
            continue
    if start < len(s):
        out.append((in_str, s[start:]))
    return out


def normalize_quotes(s: str) -> str:
    return (s.replace("“", '"').replace("”", '"')
             .replace("‘", "'").replace("’", "'"))


def strip_comments(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if is_str:
            parts.append(chunk)
        else:
            chunk = re.sub(r"//[^\n]*", "", chunk)
            chunk = re.sub(r"/\*.*?\*/", "", chunk, flags=re.DOTALL)
            parts.append(chunk)
    return "".join(parts)


def requote(s: str) -> str:
    """Convert single-quoted strings to double-quoted, escaping inner quotes."""
    parts = []
    for is_str, chunk in _split_strings(s):
        if is_str and chunk.startswith("'") and chunk.endswith("'") and len(chunk) >= 2:
            inner = chunk[1:-1].replace('\\"', '"').replace("\\'", "'")
            # Only escape backslashes that aren't already part of valid JSON escape sequences
            inner = re.sub(r'\\(?![\\/bfnrt"]|u[0-9a-fA-F]{4})', r'\\\\', inner)
            inner = inner.replace('"', '\\"')
            parts.append(f'"{inner}"')
        else:
            parts.append(chunk)
    return "".join(parts)


def fix_unescaped_newlines(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if is_str:
            chunk = chunk.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
        parts.append(chunk)
    return "".join(parts)


def fix_literals(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = re.sub(r"\bTrue\b", "true", chunk)
            chunk = re.sub(r"\bFalse\b", "false", chunk)
            chunk = re.sub(r"\b(None|undefined)\b", "null", chunk)
            chunk = re.sub(r"-?\b(NaN|Infinity)\b", "null", chunk)
        parts.append(chunk)
    return "".join(parts)


def fix_case_literals(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = re.sub(r"(?i)\b(True)\b", "true", chunk)
            chunk = re.sub(r"(?i)\b(False)\b", "false", chunk)
            chunk = re.sub(r"(?i)\b(None|undefined|nil|null)\b", "null", chunk)
            chunk = re.sub(r"(?i)-?\b(NaN|Infinity)\b", "null", chunk)
        parts.append(chunk)
    return "".join(parts)


def fix_hex_numbers(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = re.sub(r'\b0[xX][0-9a-fA-F]+\b', lambda m: str(int(m.group(0), 16)), chunk)
            chunk = re.sub(r'\b0[oO][0-7]+\b', lambda m: str(int(m.group(0), 8)), chunk)
        parts.append(chunk)
    return "".join(parts)


def fix_nonstd_floats(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = re.sub(r'(?<![0-9])\.[0-9]+', lambda m: '0' + m.group(0), chunk)
            chunk = re.sub(r'[0-9]+\.(?![0-9])', lambda m: m.group(0) + '0', chunk)
            chunk = re.sub(r'(?<![0-9eEa-zA-Z])\+[0-9]+(\.[0-9]+)?', lambda m: m.group(0)[1:], chunk)
        parts.append(chunk)
    return "".join(parts)


def fix_python_tuples(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = chunk.replace('(', '[').replace(')', ']')
        parts.append(chunk)
    return "".join(parts)


def quote_keys(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        if not is_str:
            chunk = re.sub(r"([{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*)(\s*:)", r'\1"\2"\3', chunk)
        parts.append(chunk)
    return "".join(parts)


def _get_string_spans(s: str) -> list[tuple[int, int]]:
    spans = []
    idx = 0
    for is_str, chunk in _split_strings(s):
        if is_str:
            spans.append((idx, idx + len(chunk)))
        idx += len(chunk)
    return spans


def _is_in_string(idx: int, spans: list[tuple[int, int]]) -> bool:
    for start, end in spans:
        if start <= idx < end:
            return True
    return False


def fix_missing_commas(s: str) -> str:
    spans = _get_string_spans(s)
    def repl(m):
        if _is_in_string(m.start(), spans):
            return m.group(0)
        return "," + m.group(0)
    return re.sub(r'(?<=[}\]0-9a-zA-Z_"\'])\s+(?=[{\[0-9a-zA-Z_"\'-])', repl, s)


def drop_trailing_commas(s: str) -> str:
    parts = []
    for is_str, chunk in _split_strings(s):
        parts.append(chunk if is_str else re.sub(r",+(\s*[}\]])", r"\1", chunk))
    return "".join(parts)


def close_open(s: str) -> str:
    """Close a truncated payload: finish the open string, then unwind the stack."""
    stack = []
    in_str = False
    esc = False
    quote = ""
    for c in s:
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
            continue
        if c in "\"'":
            in_str = True
            quote = c
        elif c in "{[":
            stack.append(c)
        elif c in "}]" and stack:
            stack.pop()

    if in_str:
        s += quote
    if in_str or stack:
        # A truncated payload often ends mid-token; drop a dangling key/comma.
        s = re.sub(r",\s*$", "", s)
        s = re.sub(r'["\'][A-Za-z0-9_$ -]*["\']\s*:\s*$', "", s)
        s = re.sub(r",\s*$", "", s)
    for opener in reversed(stack):
        s += "}" if opener == "{" else "]"
    return s


STAGES = [
    ("strip comments", strip_comments),
    ("convert single quotes", requote),
    ("fix unescaped newlines", fix_unescaped_newlines),
    ("normalize literals", fix_literals),
    ("normalize case literals", fix_case_literals),
    ("fix hex numbers", fix_hex_numbers),
    ("fix nonstandard floats", fix_nonstd_floats),
    ("fix python tuples", fix_python_tuples),
    ("quote bare keys", quote_keys),
    ("fix missing commas", fix_missing_commas),
    ("drop trailing commas", drop_trailing_commas),
    ("close truncated structures", close_open),
]


def loads(s: str) -> object:
    """Convenience function that wraps repair() and returns just the parsed object."""
    return repair(s)[0]


def _strict_loads(s: str) -> object:
    """json.loads that rejects NaN/Infinity (Python accepts them by default)."""
    def _reject(c):
        raise json.JSONDecodeError(f"Non-standard constant: {c}", s, 0)
    return json.loads(s, parse_constant=_reject)


def repair(text: str) -> tuple[object, list[str]]:
    """Return (parsed, applied_stages). Raises json.JSONDecodeError if unrecoverable."""
    applied: list[str] = []
    
    if text.startswith("\ufeff"):
        text = text[1:]
        
    try:
        return _strict_loads(text), applied
    except json.JSONDecodeError:
        pass
        
    candidate = normalize_quotes(text)
    candidate = extract_span(strip_fences(candidate))
    
    try:
        return _strict_loads(candidate), applied
    except json.JSONDecodeError:
        pass

    for label, fn in STAGES:
        next_cand = fn(candidate)
        if next_cand != candidate:
            candidate = next_cand
            applied.append(label)
            try:
                return _strict_loads(candidate), applied
            except json.JSONDecodeError:
                continue
    
    return _strict_loads(candidate), applied



def main() -> int:
    ap = argparse.ArgumentParser(description="Extract and repair JSON from messy text.")
    ap.add_argument("input", help="Path to a text file, or '-' for stdin")
    ap.add_argument("-o", "--output", help="Write output to file instead of stdout")
    ap.add_argument("-e", "--encoding", default="utf-8-sig", help="Input file encoding (default: utf-8-sig)")
    ap.add_argument("--indent", type=int, default=2, help="Indentation level (default: 2, 0 for compact)")
    ap.add_argument("--compact", action="store_true", help="Minified output (same as --indent 0)")
    ap.add_argument("--check", action="store_true", help="Exit 0 if valid JSON, 1 if repair needed. No output.")
    ap.add_argument("-i", "--in-place", action="store_true", help="Repair file in place")
    ap.add_argument("--quiet", action="store_true", help="Suppress stderr diagnostics")
    args = ap.parse_args()

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(args.input, encoding=args.encoding) as f:
                raw = f.read()
        except (FileNotFoundError, PermissionError) as e:
            if not args.quiet:
                print(f"error: could not read file '{args.input}'", file=sys.stderr)
            return 1

    try:
        data, applied = repair(raw)
    except json.JSONDecodeError as exc:
        if not args.quiet:
            print(f"error: input is not recoverable JSON.", file=sys.stderr)
        return 1
        
    if args.check:
        if applied:
            return 1
        return 0

    if applied and not args.quiet:
        print(f"repaired via: {', '.join(applied)}", file=sys.stderr)

    indent = 0 if args.compact else args.indent
    
    out_file = sys.stdout
    if args.in_place and args.input != "-":
        args.output = args.input
        
    if args.output:
        try:
            out_file = open(args.output, "w", encoding="utf-8")
        except (OSError, PermissionError) as e:
            if not args.quiet:
                print(f"error: could not open output file.", file=sys.stderr)
            return 1

    try:
        if indent == 0:
            json.dump(data, out_file, separators=(",", ":"), ensure_ascii=False)
        else:
            json.dump(data, out_file, indent=indent, ensure_ascii=False)
        out_file.write("\n")
    except BrokenPipeError:
        pass
    finally:
        if out_file is not sys.stdout:
            out_file.close()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
