#!/usr/bin/env python3
"""Check exported HTML and CSS references before publication."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'docs'
errors = []
checked = 0

def check(value, origin):
    global checked
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        if 'ahmed-portfolio.local' in value:
            errors.append(f'{origin}: still points to local WordPress: {value}')
        return
    checked += 1
    target = (origin.parent / unquote(url.path)).resolve()
    if not target.is_relative_to(ROOT.resolve()):
        errors.append(f'{origin}: link leaves site: {value}')
    elif not target.exists():
        errors.append(f'{origin.relative_to(ROOT)}: missing {value}')

class References(HTMLParser):
    def __init__(self, origin):
        super().__init__()
        self.origin = origin
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if not value:
                continue
            if key in {'href', 'src', 'poster', 'data-gif', 'data-poster'}:
                check(value, self.origin)
            elif key == 'srcset':
                for item in value.split(','):
                    check(item.strip().split()[0], self.origin)
            elif key == 'style':
                for item in re.findall(r'''url\(["']?([^\)"']+)["']?\)''', value):
                    check(item, self.origin)

for path in ROOT.rglob('*.html'):
    References(path).feed(path.read_text())
for path in ROOT.rglob('*.css'):
    for item in re.findall(r'''url\(["']?([^\)"']+)["']?\)''', path.read_text()):
        check(item, path)
for path in ROOT.rglob('*'):
    if path.is_file() and path.suffix.lower() in {'.php', '.sql', '.blend', '.zip'}:
        errors.append('Unexpected source file: ' + str(path))
if errors:
    print('\n'.join(sorted(set(errors))))
    raise SystemExit(1)
print(f'PASS: {checked} local references; no missing files or WordPress links.')
