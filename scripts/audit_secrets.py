"""Scan for hardcoded secrets in a codebase.

Detects API keys, passwords, tokens, and private keys.
Redacts matches in output. Zero dependencies — Python 3.10+ stdlib only.
"""

import os
import re
import sys
import json
import fnmatch
import argparse
from typing import Any

SECRET_PATTERNS: dict[str, str] = {
    'AWS Access Key': r'(?i)AKIA[0-9A-Z]{16}',
    'AWS Secret Key': r'(?i)(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])',
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'Stripe API Key': r'(?i)sk_(live|test)_[0-9a-zA-Z]{24}',
    'Generic API Key': r'(?i)(api_key|apikey|secret)[\s\=:\'\"]+[0-9a-zA-Z\-_]{16,}',
    'Generic Password': r'(?i)(password|passwd)[\s\=:\'\"]+[^\"\'\\s]{8,}',
    'Bearer Token': r'(?i)bearer[\s]+[a-zA-Z0-9\-\._\~\+\/]+',
    'JWT Token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
}

# Max file size to scan (50 MB)
MAX_FILE_SIZE: int = 50 * 1024 * 1024


def redact_secret(secret: str) -> str:
    """Redact a secret value, showing only first 4 and last 4 characters."""
    if len(secret) <= 8:
        return '***'
    return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]


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


def scan_directory(directory: str, use_gitignore: bool = True) -> list[dict[str, Any]]:
    """Scan a directory recursively for hardcoded secrets."""
    ignore_patterns = load_gitignore(directory) if use_gitignore else []
    findings: list[dict[str, Any]] = []

    for root, dirs, files in os.walk(directory):
        # Filter directories
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
                        for pattern_name, pattern_regex in SECRET_PATTERNS.items():
                            matches = re.finditer(pattern_regex, line)
                            for match in matches:
                                secret_value = match.group(0)
                                findings.append({
                                    "file": file_path,
                                    "line": i + 1,
                                    "pattern": pattern_name,
                                    "match": redact_secret(secret_value)
                                })
            except (UnicodeDecodeError, PermissionError, OSError):
                pass  # Skip unreadable files

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit for secrets in code")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--gitignore", action="store_true", help="Respect .gitignore")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any findings")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        return 1

    findings = scan_directory(args.directory, args.gitignore)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for finding in findings:
            print(f"[{finding['pattern']}] {finding['file']}:{finding['line']} - {finding['match']}")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(130)
