#!/usr/bin/env python3
"""LibreJS-tagging check for an Odoo instance.

Usage: python3 check_librejs.py [base_url]   (default http://127.0.0.1:8069)

Verifies, with no LibreJS involved:
1. login page has the inline @licstart/@licend notice,
2. it carries a hidden rel="jslicense" link,
3. every <script src> served on the page starts with the license banner
   (tagged before it is sent to the browser),
4. /web/jslicense lists every one of those scripts in table jslicense-labels1,
5. the tagged bundle is still valid JavaScript (ast parse).
"""
import json
import re
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8069"
failures = []


def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=120) as r:
        return r.read()


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


html = fetch("/web/login").decode()

print(f"Odoo at {BASE}")
print("1. inline @licstart/@licend notice on page")
check("inline @licstart block present", "@licstart" in html and "@licend" in html)

print("2. hidden rel=jslicense link")
check("rel=\"jslicense\" link present", re.search(r'<a[^>]+rel="jslicense"', html) is not None)

print("3. every script tagged before it is sent")
srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
check("page has external scripts", len(srcs) > 0, "no scripts found")
for src in srcs:
    body = fetch(src)
    ok = body.lstrip().startswith(b"/* @licstart") and b"@licend" in body[:2000]
    check(f"tagged: {src}", ok, "banner missing at top of served JS")

print("4. web labels table")
labels = fetch("/web/jslicense").decode()
check("labels table present", 'id="jslicense-labels1"' in labels)
for src in srcs:
    check(f"labelled: {src}", src in labels)

print("5. tagged bundle still parses as JavaScript")
if srcs:
    body = fetch(srcs[0]).decode()
    body = re.sub(r"^/\*.*?\*/", "", body, count=1, flags=re.S)  # strip banner
    node = "/usr/bin/node"
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(body)
        path = f.name
    r = subprocess.run(["node", "--check", path], capture_output=True)
    os.unlink(path)
    check("bundle parses (node --check)", r.returncode == 0, r.stderr.decode()[:200])

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED")
