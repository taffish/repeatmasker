#!/usr/bin/env python3
"""Embed the upstream background asset; keep alignment behavior and data intact."""
import base64
from pathlib import Path

root = Path('/opt/RepeatMasker')
path = root / 'HTMLAnnotHeader.html'
original = path.read_text()
needle = 'url("bluegrad.jpg")'
assert original.count(needle) == 1, 'upstream HTML asset reference changed'
asset = base64.b64encode((root / 'bluegrad.jpg').read_bytes()).decode('ascii')
path.write_text(original.replace(needle, 'url("data:image/jpeg;base64,' + asset + '")'))
