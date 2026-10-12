#!/usr/bin/env python3
"""Independent offline viewer for RepeatMasker calcDivergenceFromAlign summaries.

Apache-2.0 TAFFISH packaging helper. No upstream classification remapping:
retain every raw class and bin, including unknown classes and divergence >50.
"""
import argparse
import hashlib
import html
import json
import math
import os
import re
from pathlib import Path
import tempfile

TEMPLATE = Path('/opt/taffish-repeatmasker/landscape.html')
MAX_SAFE = 2**53 - 1


def integer(value):
    if not value.isascii() or not value.isdecimal():
        raise ValueError('expected nonnegative integer: ' + repr(value))
    result = int(value)
    if result > MAX_SAFE:
        raise ValueError('integer exceeds exact browser numeric range')
    return result


def parse_summary(path):
    raw = path.read_bytes()
    totals, bins, classes = {}, [], None
    section = None
    for number, line in enumerate(raw.decode('utf-8').splitlines(), 1):
        if not line.strip() or set(line.strip()) <= {'-', '\t', ' '}:
            continue
        if line.startswith('Class\tRepeat\tabsLen\twellCharLen\tKimura%'):
            section = 'families'
            continue
        if line.startswith('Coverage for each repeat'):
            section = 'coverage'
            continue
        try:
            if section == 'families':
                fields = line.split('\t')
                if len(fields) != 5 or not fields[0] or not fields[1]:
                    raise ValueError('expected five family columns')
                bp, well = integer(fields[2]), integer(fields[3])
                divergence = 0 if fields[4] == '----' and re.search(r'Simple|Low_complexity|ARTEFACT', fields[0]) else float(fields[4])
                if well > bp or not math.isfinite(divergence) or divergence < 0:
                    raise ValueError('invalid family lengths/divergence')
                totals[fields[0]] = totals.get(fields[0], 0) + bp
            elif section == 'coverage':
                fields = line.split()
                if fields[0] == 'Div':
                    if classes is not None:
                        raise ValueError('duplicate coverage header')
                    classes = fields[1:]
                    if not classes or len(set(classes)) != len(classes):
                        raise ValueError('empty or duplicate coverage classes')
                else:
                    if classes is None or len(fields) != len(classes) + 1:
                        raise ValueError('coverage column count mismatch')
                    bins.append([integer(value) for value in fields])
        except ValueError as exc:
            raise ValueError(f'line {number}: {exc}') from exc
    if not totals or not classes or not bins:
        raise ValueError('missing family/coverage data; generate with calcDivergenceFromAlign.pl -s FILE ALIGNMENTS')
    if set(classes) != set(totals):
        raise ValueError('family and coverage class inventories differ')
    if len({row[0] for row in bins}) != len(bins):
        raise ValueError('duplicate divergence bin')
    if max(sum(totals.values()), sum(sum(row[1:]) for row in bins)) > MAX_SAFE:
        raise ValueError('coverage totals exceed exact browser numeric range')
    return dict(schema='taffish-repeatmasker-landscape-v1', source=path.name,
                source_sha256=hashlib.sha256(raw).hexdigest(), classes=classes,
                class_bp=[totals[name] for name in classes], bins=sorted(bins))


def main():
    p = argparse.ArgumentParser(description='Create an independent, standalone offline repeat landscape (raw classes, all bins).')
    p.add_argument('--div', type=Path, required=True, help='calcDivergenceFromAlign.pl -s output')
    p.add_argument('--genome-size', type=integer, required=True, help='explicit positive genome denominator in bp (not inferred)')
    p.add_argument('--title', default='Repeat landscape', help='report title')
    p.add_argument('--output', type=Path, required=True, help='new HTML file; parent must exist')
    p.add_argument('--force', action='store_true', help='atomically replace an existing regular output file')
    a = p.parse_args()
    try:
        if not a.genome_size:
            raise ValueError('--genome-size must be positive')
        if a.output.resolve() == a.div.resolve():
            raise ValueError('output must not replace the input')
        if a.output.is_symlink() or (a.output.exists() and not a.output.is_file()):
            raise ValueError('output must not be a symlink or special file')
        if a.output.exists() and not a.force:
            raise ValueError('output exists; choose a new file or explicitly use --force')
        data = parse_summary(a.div)
        data.update(genome_size=a.genome_size, title=a.title)
        encoded = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
        replacements = {'@@TITLE@@': html.escape(a.title), '@@DATA@@': encoded}
        rendered = re.sub(r'@@TITLE@@|@@DATA@@', lambda m: replacements[m.group()], TEMPLATE.read_text())
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='.landscape-', dir=a.output.parent, delete=False) as f:
                name = f.name
                f.write(rendered)
                f.flush()
                os.fsync(f.fileno())
            if a.force:
                os.replace(name, a.output)
            else:
                os.link(name, a.output)  # Atomic no-clobber publication.
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
        print(f'Created {a.output} ({len(data["classes"])} raw classes, {len(data["bins"])} bins). Open locally in a browser; no network required.')
    except (OSError, ValueError, UnicodeError) as exc:
        p.exit(2, f'taf-repeatmasker-landscape: {exc}\n')


if __name__ == '__main__':
    main()
