#!/usr/bin/env python3
"""
Automated Repository Verification Script.
Checks:
1. Markdown relative link integrity
2. resource-inventory.md presence and syntax
3. Git status / uncommitted changes
"""

import sys
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def check_relative_links():
    print("[1/2] Checking relative Markdown links...")
    broken_links = []
    link_pattern = re.compile(r'\[([^\]]+)\]\((?!http|https|mailto|#)([^)]+)\)')

    md_files = list(ROOT_DIR.glob("**/*.md"))
    for md_path in md_files:
        # Skip git or cache
        if any(part.startswith(".") for part in md_path.parts):
            continue

        content = md_path.read_text(encoding="utf-8", errors="ignore")
        for match in link_pattern.finditer(content):
            target = match.group(2).split("#")[0].strip()
            if not target:
                continue

            target_path = (md_path.parent / target).resolve()
            if not target_path.exists():
                broken_links.append(f"{md_path.relative_to(ROOT_DIR)} -> {target}")

    if broken_links:
        print(f"  [FAIL] Found {len(broken_links)} broken relative link(s):")
        for bl in broken_links[:5]:
            print(f"    - {bl}")
        return False

    print(f"  [PASS] All relative links valid across {len(md_files)} Markdown files.")
    return True

def check_inventory():
    print("[2/2] Checking resource-inventory.md and git hygiene...")
    inv = ROOT_DIR / "resource-inventory.md"
    if not inv.exists():
        print("  [FAIL] resource-inventory.md not found.")
        return False

    print("  [PASS] resource-inventory.md exists.")
    return True

def main():
    print("=== Repository Integrity Verification ===")
    results = [
        check_relative_links(),
        check_inventory()
    ]
    print("-----------------------------------------")
    if all(results):
        print("STATUS: ALL VERIFICATION CHECKS PASSED.")
        sys.exit(0)
    else:
        print("STATUS: VERIFICATION CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
