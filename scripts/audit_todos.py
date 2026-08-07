"""Scan for TODO/FIXME/HACK/XXX/TEMP comments in a codebase.

Outputs findings grouped by category with severity classification.
Zero dependencies — Python 3.10+ stdlib only.
"""

import os
import re
import sys
import json
import fnmatch
import argparse
from typing import Any

TODO_PATTERNS: dict[str, dict[str, str]] = {
    'HACK': {'regex': r'\bHACK\b', 'severity': 'high'},
    'FIXME': {'regex': r'\bFIXME\b', 'severity': 'high'},
    'TODO': {'regex': r'\bTODO\b', 'severity': 'medium'},
    'XXX': {'regex': r'\bXXX\b', 'severity': 'low'},
    'TEMP': {'regex': r'\bTEMP\b', 'severity': 'low'}
}

# Max file size to scan (50 MB)
MAX_FILE_SIZE: int = 50 * 1024 * 1024


def load_gitignore(directory: str) -> list[re.Pattern[str]]:
    """Load .gitignore patterns and compile them using fnmatch."""
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns: list[re.Pattern[str]] = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Use fnmatch.translate for correct glob-to-regex conversion
                        regex = fnmatch.translate(line)
                        try:
                            patterns.append(re.compile(regex))
                        except re.error:
                            pass  # Skip malformed patterns
        except OSError:
            pass  # Skip unreadable .gitignore
    return patterns


def is_ignored(path: str, ignore_patterns: list[re.Pattern[str]]) -> bool:
    """Check if a path matches any ignore pattern."""
    basename = os.path.basename(path)
    for pattern in ignore_patterns:
        if pattern.search(path) or pattern.search(basename):
            return True
    if '.git' in path.split(os.sep) or 'node_modules' in path or '__pycache__' in path:
        return True
    return False


def _is_binary(file_path: str) -> bool:
    """Quick binary file detection via null-byte check."""
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(8192)
            return b'\0' in sample
    except OSError:
        return True


def scan_directory(directory: str, ignore_patterns: list[re.Pattern[str]]) -> list[dict[str, Any]]:
    """Scan a directory recursively for TODO-style comments."""
    findings: list[dict[str, Any]] = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignore_patterns)]

        for file in files:
            file_path = os.path.join(root, file)
            if is_ignored(file_path, ignore_patterns):
                continue

            # Skip binary files and oversized files
            if _is_binary(file_path):
                continue
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):  # Stream line-by-line
                        for cat, info in TODO_PATTERNS.items():
                            if re.search(info['regex'], line, re.IGNORECASE):
                                findings.append({
                                    "file": file_path,
                                    "line": i + 1,
                                    "category": cat,
                                    "severity": info['severity'],
                                    "context": line.strip()
                                })
            except (UnicodeDecodeError, PermissionError, OSError):
                pass  # Skip unreadable files

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit for TODOs and FIXMEs")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--severity", action="store_true", help="Include severity in output")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any findings")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        return 1

    ignore_patterns = load_gitignore(args.directory)
    findings = scan_directory(args.directory, ignore_patterns)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for finding in findings:
            sev_str = f" [{finding['severity'].upper()}]" if args.severity else ""
            print(f"[{finding['category']}]{sev_str} {finding['file']}:{finding['line']} - {finding['context']}")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(130)
