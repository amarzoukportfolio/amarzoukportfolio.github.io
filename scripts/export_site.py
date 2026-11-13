#!/usr/bin/env python3
"""Export the public local WordPress portfolio for GitHub Pages (stdlib only)."""
import argparse
import concurrent.futures
import html
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from urllib.parse import quote, unquote, urlsplit, urljoin
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSET = re.compile(r'''(?:https?://ahmed-portfolio\.local)?(/(?:wp-content|wp-includes)/[^\s"'<>),;]+)''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='http://ahmed-portfolio.local')
    parser.add_argument('--wordpress-root', default='/Users/amarzouk/Local Sites/ahmed-portfolio/app/public')
    parser.add_argument('--public-url', default='https://amarzoukportfolio.github.io')
    args = parser.parse_args()
    source = args.source.rstrip('/')
    public = args.public_url.rstrip('/')
    assets = set()
    def get(path):
        with urlopen(source + path, timeout=60) as response:
            return response.read()
    pages = json.loads(get('/wp-json/wp/v2/pages?per_page=100&_fields=link,slug,status'))
    pages = [p for p in pages if p['status'] == 'publish' and p['slug'] != 'sample-page']
    stage = Path(tempfile.mkdtemp(prefix='portfolio-export-'))
    try:
        def transform(text, path):
            # Remove discovery/admin endpoints, never needed by the static site.
            text = re.sub(r'<link\b[^>]*(?:wp-json|xmlrpc\.php|rel=["\'](?:canonical|shortlink)["\'])[^>]*>', '', text, flags=re.I)
            text = re.sub(r'<script\b[^>]*type=["\']speculationrules["\'][^>]*>.*?</script>', '', text, flags=re.S|re.I)
            text = re.sub(r'<meta\b[^>]*name=["\']generator["\'][^>]*>', '', text, flags=re.I)
            assets.update(unquote(urlsplit(html.unescape(m.group(1))).path) for m in ASSET.finditer(text))
            # Use relative links so both username sites and project sites work.
            prefix = posixpath.relpath('/', posixpath.dirname('/' + path))
            def relative(match):
                target = html.unescape(match.group(0))
                parsed = urlsplit(target)
                if parsed.netloc and parsed.netloc != urlsplit(source).netloc:
                    return match.group(0)
                result = posixpath.join(prefix, parsed.path.lstrip('/'))
                if parsed.path.endswith('/') and not result.endswith('/'):
                    result += '/'
                if parsed.query and not parsed.path.startswith(('/wp-content/', '/wp-includes/')):
                    result += '?' + parsed.query
                if parsed.fragment:
                    result += '#' + parsed.fragment
                return html.escape(result, quote=True)
            pattern = re.escape(source) + r'''[^\s"'<>),;]*'''
            text = re.sub(pattern, relative, text)
            # Some page content uses root-relative media and navigation.
            text = re.sub(r'''(?<=["'])/(?!/)([^"'<>\s]*)''', lambda m: posixpath.join(prefix, m.group(1)), text)
            return text
        for page in pages:
            path = urlsplit(page['link']).path
            output = path.lstrip('/') + 'index.html'
            dest = stage / output
            dest.parent.mkdir(parents=True, exist_ok=True)
            markup = transform(get(path).decode(), output)
            # Link previews and canonical addresses require absolute public URLs.
            page_url = public + path
            markup = re.sub(r'(<meta\b[^>]*property="og:url"[^>]*content=")[^"]*(")', lambda m: m[1] + html.escape(page_url, quote=True) + m[2], markup)
            markup = re.sub(r'(<meta\b[^>]*property="og:image"[^>]*content=")([^"]*)(")', lambda m: m[1] + html.escape(urljoin(page_url, html.unescape(m[2])), quote=True) + m[3], markup)
            markup = markup.replace('</head>', '<link rel="canonical" href="' + html.escape(page_url, quote=True) + '"></head>')
            dest.write_text(markup)
        copied = set()
        while assets - copied:
            batch = assets - copied
            for asset in sorted(batch):
                if '..' in Path(asset).parts or Path(asset).suffix.lower() in {'.php', '.sql', '.zip', '.blend'}:
                    raise ValueError('Unexpected asset: ' + asset)
                local = Path(args.wordpress_root) / asset.lstrip('/')
                dest = stage / asset.lstrip('/')
                dest.parent.mkdir(parents=True, exist_ok=True)
                if local.is_file():
                    shutil.copy2(local, dest)
                else:
                    dest.write_bytes(get(quote(asset, safe='/')))
                if dest.suffix.lower() in {'.css', '.js', '.svg'}:
                    text = dest.read_text()
                    if dest.suffix.lower() == '.css':
                        for value in re.findall(r'''url\(["']?([^\)"']+)["']?\)''', text):
                            if not value.startswith(('data:', 'https:', 'http:', '#')):
                                assets.add(posixpath.normpath(posixpath.join(posixpath.dirname(asset), value)))
                    dest.write_text(transform(text, asset.lstrip('/')))
                copied.add(asset)
        # Keep stable download addresses in addition to cache-busting filenames.
        download_dir = stage / 'wp-content/uploads/ahmed-portfolio'
        for stem in ['Ahmed-Marzouk-CV', 'Ahmed-Marzouk-Portfolio']:
            versions = list(download_dir.glob(stem + '-*.pdf'))
            if len(versions) != 1:
                raise ValueError('Expected one current download for ' + stem)
            shutil.copy2(versions[0], download_dir / (stem + '.pdf'))
        # Preserve prior versioned portfolio PDF URLs already shared with visitors.
        # Older CV versions are not kept: they included referees' contact details.
        previous_downloads = ROOT / 'docs/wp-content/uploads/ahmed-portfolio'
        for previous in previous_downloads.glob('Ahmed-Marzouk-Portfolio-*.pdf'):
            destination = download_dir / previous.name
            if not destination.exists():
                shutil.copy2(previous, destination)
        (stage / '.nojekyll').touch()
        # Preserve the old student project URL as a static redirect.
        old = stage / 'student-projects/raspberry-pi-ai-robot/index.html'
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../student-project-collection/"><title>Student projects</title><a href="../student-project-collection/">View student projects</a>')
        largest = max((p.stat().st_size, str(p.relative_to(stage))) for p in stage.rglob('*') if p.is_file())
        if largest[0] >= 100 * 1024 * 1024:
            raise ValueError('Asset exceeds GitHub file limit: ' + str(largest))
        docs = ROOT / 'docs'
        backup = ROOT / '.previous-export'
        if backup.exists():
            shutil.rmtree(backup)
        if docs.exists():
            docs.rename(backup)
        shutil.copytree(stage, docs)
        if backup.exists():
            shutil.rmtree(backup)
        files = [p for p in docs.rglob('*') if p.is_file()]
        print(json.dumps({'pages': len(pages), 'assets': len(copied), 'files': len(files), 'megabytes': round(sum(p.stat().st_size for p in files)/1024**2, 1), 'largest': largest}, indent=2))
    finally:
        shutil.rmtree(stage)

if __name__ == '__main__':
    main()
