#!/usr/bin/env python3
"""Install analytics only in the production package; source previews stay untracked."""
from pathlib import Path
import hashlib
import shutil
import sys

root = Path(__file__).resolve().parents[1]
output = Path(sys.argv[1])
script = root / 'analytics.js'
version = hashlib.sha256(script.read_bytes()).hexdigest()[:12]
shutil.copy2(script, output / 'analytics.js')
shutil.copytree(root / 'privacidad', output / 'privacidad', dirs_exist_ok=True)
paths = ['index.html', 'en/index.html', 'novias/index.html', 'xv-anos/index.html',
         'en/bridal/index.html', 'en/quinceanera/index.html', 'tienda/index.html', 'privacidad/index.html']
for name in paths:
    file = output / name
    html = file.read_text(encoding='utf-8')
    assert 'data-site-analytics' not in html, f'Analytics already installed: {name}'
    html = html.replace('</head>', f'<script data-site-analytics src="/analytics.js?v={version}" defer></script>\n</head>', 1)
    if name != 'privacidad/index.html':
        label = 'Privacy & analytics' if name.startswith('en/') else 'Privacidad y analítica'
        link = f'<a href="/privacidad/">{label}</a>'
        if name == 'tienda/index.html':
            marker = 'GABY PADILLA</span></footer>'
            replacement = 'GABY PADILLA · ' + link + '</span></footer>'
        else:
            marker = '<span>Playas de Tijuana · Tijuana · Tecate · Valle de Guadalupe</span>'
            replacement = link + marker
        assert marker in html, f'Footer marker missing: {name}'
        html = html.replace(marker, replacement, 1)
    file.write_text(html, encoding='utf-8')
print(f'GA4 installed once on {len(paths)} production pages; footer privacy links added.')
