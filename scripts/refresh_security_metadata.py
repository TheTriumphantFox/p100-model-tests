#!/usr/bin/env python3
"""Refresh/check CSP hashes and fail-closed guards on archived shell drivers.

Only tracked HTML/shell files are transformed. Reports' benchmark data and raw
outputs are not rewritten. Run --write after editing inline website scripts.
"""
import argparse
import base64
import hashlib
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_GUARD = '''# SECURITY: historical driver; may stop services, kill processes, or edit live presets.
if [ "${P100_ALLOW_ARCHIVED_DRIVER:-}" != "1" ]; then
  printf '%s\\n' 'Refusing archived driver. Review SECURITY.md; explicitly set P100_ALLOW_ARCHIVED_DRIVER=1 only in a disposable test environment.' >&2
  exit 2
fi
'''
SAFE_LAUNCHERS = {
    'results/2026-10-01/aider-polyglot-10h/ctr.sh',
    'results/2026-10-02/flash-next-full/polyglot/ctr.sh',
}


def secure_html(text):
    # Metadata must precede every resource reference. A meta CSP cannot set frame-ancestors.
    clean = re.sub(r'<meta\b(?=[^>]*(?:http-equiv=["\']Content-Security-Policy["\']|name=["\']referrer["\']))[^>]*>\s*', '', text, flags=re.I)
    hashes = ["'sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode() + "'"
              for body in re.findall(r'<script\b[^>]*>(.*?)</script>', clean, flags=re.S | re.I)]
    script = ' '.join(hashes) if hashes else "'none'"
    csp = (f"default-src 'none'; script-src {script}; script-src-attr 'none'; "
           "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
           "font-src 'self' https://fonts.gstatic.com; img-src 'self'; connect-src 'self'; "
           "base-uri 'none'; form-action 'none'; object-src 'none'")
    tags = f'<meta http-equiv="Content-Security-Policy" content="{csp}">\n<meta name="referrer" content="no-referrer">\n'
    return re.sub(r'(<head\b[^>]*>)\s*', lambda m: m.group(1) + '\n' + tags, clean, count=1, flags=re.I)


def secure_shell(text):
    if ARCHIVE_GUARD in text:
        return text
    first, sep, rest = text.partition('\n')
    if not first.startswith('#!'):
        raise ValueError('Archived driver lacks a shebang')
    return first + sep + ARCHIVE_GUARD + rest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='update tracked source metadata')
    mode.add_argument('--staged', action='store_true', help='check the index, not unstaged working files')
    args = parser.parse_args()
    entries = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--stage', '-z']).decode().split('\0')
    index = {}
    for entry in entries:
        if not entry:
            continue
        info, name = entry.split('\t', 1)
        _, sha, stage = info.split()
        if stage != '0':
            raise SystemExit('Resolve merge conflicts before checking security metadata')
        index[name] = sha
    batch = subprocess.Popen(['git', '-C', str(ROOT), 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) if args.staged else None
    changed = []
    for name in index:
        if name.endswith('.html'):
            transform = secure_html
        elif ((name.startswith('results/') and name.endswith('.sh') and name not in SAFE_LAUNCHERS)
              or name in ('rig/drive.sh', 'scripts/build_llama_cuda12.sh.bak-2026-09-19')):
            transform = secure_shell
        else:
            continue
        p = ROOT / name
        if batch:
            batch.stdin.write((index[name] + '\n').encode()); batch.stdin.flush()
            header = batch.stdout.readline().split()
            data = batch.stdout.read(int(header[2]))
            assert batch.stdout.read(1) == b'\n'
            old = data.decode()
        else:
            if not p.is_file():
                continue
            old = p.read_text()
        new = transform(old)
        if new != old:
            changed.append(name)
            if args.write:
                p.write_text(new)
    if batch:
        batch.stdin.close(); batch.stdout.close(); batch.wait()
    print(('Updated' if args.write else 'Stale security metadata:') + f' {len(changed)} files')
    if not args.write:
        for name in changed:
            print(name)
        if changed:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
