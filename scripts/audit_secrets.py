import os
import re
import sys
import json
import argparse

SECRET_PATTERNS = {
    'AWS Access Key': r'(?i)AKIA[0-9A-Z]{16}',
    'AWS Secret Key': r'(?i)(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])',
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'Stripe API Key': r'(?i)sk_(live|test)_[0-9a-zA-Z]{24}',
    'Generic API Key': r'(?i)(api_key|apikey|secret)[\s\=:\'"]+[0-9a-zA-Z\-_]{16,}',
    'Generic Password': r'(?i)(password|passwd)[\s\=:\'"]+[^"\'\s]{8,}',
    'Bearer Token': r'(?i)bearer[\s]+[a-zA-Z0-9\-\._\~\+\/]+',
    'JWT Token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
}

def redact_secret(secret):
    if len(secret) <= 8:
        return '***'
    return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]

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

def scan_directory(directory, use_gitignore=True):
    ignore_patterns = load_gitignore(directory) if use_gitignore else []
    findings = []
    
    for root, dirs, files in os.walk(directory):
        # Filter directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if is_ignored(file_path, ignore_patterns):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
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
            except UnicodeDecodeError:
                pass # Skip binary files
                
    return findings

def main():
    parser = argparse.ArgumentParser(description="Audit for secrets in code")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--gitignore", action="store_true", help="Respect .gitignore")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()
    
    findings = scan_directory(args.directory, args.gitignore)
    
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for finding in findings:
            print(f"[{finding['pattern']}] {finding['file']}:{finding['line']} - {finding['match']}")

if __name__ == "__main__":
    main()
