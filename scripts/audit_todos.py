import os
import re
import json
import argparse

TODO_PATTERNS = {
    'HACK': {'regex': r'\bHACK\b', 'severity': 'high'},
    'FIXME': {'regex': r'\bFIXME\b', 'severity': 'high'},
    'TODO': {'regex': r'\bTODO\b', 'severity': 'medium'},
    'XXX': {'regex': r'\bXXX\b', 'severity': 'low'},
    'TEMP': {'regex': r'\bTEMP\b', 'severity': 'low'}
}

def load_gitignore(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line.replace('*', '.*'))
    return patterns

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if re.search(pattern, path):
            return True
    if '.git' in path or 'node_modules' in path or '__pycache__' in path:
        return True
    return False

def scan_directory(directory, ignore_patterns):
    findings = []
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if is_ignored(file_path, ignore_patterns):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        for cat, info in TODO_PATTERNS.items():
                            if re.search(info['regex'], line, re.IGNORECASE):
                                findings.append({
                                    "file": file_path,
                                    "line": i + 1,
                                    "category": cat,
                                    "severity": info['severity'],
                                    "context": line.strip()
                                })
            except UnicodeDecodeError:
                pass
                
    return findings

def main():
    parser = argparse.ArgumentParser(description="Audit for TODOs and FIXMEs")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--severity", action="store_true", help="Include severity in output")
    args = parser.parse_args()
    
    ignore_patterns = load_gitignore(args.directory)
    findings = scan_directory(args.directory, ignore_patterns)
    
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for finding in findings:
            sev_str = f" [{finding['severity'].upper()}]" if args.severity else ""
            print(f"[{finding['category']}]{sev_str} {finding['file']}:{finding['line']} - {finding['context']}")

if __name__ == "__main__":
    main()
