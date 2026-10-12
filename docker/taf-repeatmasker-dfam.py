#!/usr/bin/python3
"""Explicit, pinned Dfam 4.0 member installation; never called implicitly."""
import argparse
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

CATALOG = Path('/opt/taffish-repeatmasker/dfam-4.0.catalog.json')
MANIFEST = 'taffish-famdb.json'
INVENTORY = 'taffish-famdb.sha256'
READY = 'taffish-famdb.ready'

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def catalog():
    return json.loads(CATALOG.read_text())

def selected(parts):
    data = catalog()
    choices = {m['file'][7:-6]: m for m in data['members'] if m['file'] != 'dfam40.0.h5.gz'}
    unknown = set(parts) - choices.keys()
    if unknown:
        raise ValueError('unknown partition: ' + ', '.join(sorted(unknown)) + '; use list')
    names = {'dfam40.0.h5.gz'} | {choices[p]['file'] for p in parts}
    return [m for m in data['members'] if m['file'] in names]

def regular(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing, non-regular or symlink member: ' + str(path))

def verify(root, quick=False):
    root = Path(root)
    for name in (MANIFEST, INVENTORY, READY):
        regular(root / name)
    ready = (root / READY).read_text().strip()
    if ready != digest(root / INVENTORY):
        raise ValueError('inventory/ready checksum mismatch')
    doc = json.loads((root / MANIFEST).read_text())
    if doc.get('schema') != 1 or doc.get('release') != '4.0' or doc.get('catalog_sha256') != digest(CATALOG):
        raise ValueError('incompatible or unpinned FamDB inventory; prepare a new root')
    members = doc['members']
    expected = selected(doc['parts'])
    if [m['file'] + '.gz' for m in members] != [m['file'] for m in expected]:
        raise ValueError('selected partitions disagree with inventory')
    lines = []
    for m, upstream in zip(members, expected):
        if not re.fullmatch(r'dfam40\.(?:0|(?:curated|uncurated)\.(?:consensus|hmm)\.\d+)\.h5', m['file']):
            raise ValueError('unsafe member name')
        if m['source_md5'] != upstream['md5'] or m['source_url'] != upstream['url']:
            raise ValueError('source identity mismatch')
        path = root / m['file']
        regular(path)
        if path.stat().st_size != m['bytes']:
            raise ValueError('member size mismatch: ' + m['file'])
        if not quick and digest(path) != m['sha256']:
            raise ValueError('member SHA256 mismatch: ' + m['file'])
        lines.append(m['sha256'] + '  ' + m['file'])
    lines.append(digest(root / MANIFEST) + '  ' + MANIFEST)
    if (root / INVENTORY).read_text() != '\n'.join(lines) + '\n':
        raise ValueError('manifest/inventory checksum mismatch')
    actual = {p.name for p in root.iterdir() if p.name.endswith('.h5')}
    if actual != {m['file'] for m in members}:
        raise ValueError('untracked HDF5 files in prepared root')
    return doc

def install(args):
    members = selected(args.part)
    root = Path(args.db_root).absolute()
    if root.is_symlink():
        raise ValueError('install target must not be a symlink')
    plan = {'release': '4.0', 'root': str(root), 'parts': sorted(set(args.part)),
            'compressed_bytes': sum(m['compressed_bytes'] for m in members), 'members': members}
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    root.parent.mkdir(parents=True, exist_ok=True)
    lockpath = root.parent / ('.' + root.name + '.install.lock')
    fd = os.open(lockpath, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another installation holds ' + str(lockpath))
        if root.exists() and any(root.iterdir()):
            doc = verify(root)
            if doc['parts'] != plan['parts']:
                raise ValueError('existing root has different partitions; use a new empty root')
            print('Already installed and SHA256 verified: ' + str(root))
            return
        cache = root.parent / ('.' + root.name + '.downloads')
        if cache.is_symlink():
            raise ValueError('download cache must not be a symlink')
        cache.mkdir(mode=0o700, exist_ok=True)
        if cache.stat().st_uid != os.getuid() or cache.stat().st_mode & 0o077:
            raise ValueError('download cache must be owned by caller and private (0700)')
        # HDF5 expansion is data-dependent; reject low space conservatively and
        # reserve headroom continuously during decompression, not only at start.
        reserve = 64 * 1024 * 1024
        estimate = plan['compressed_bytes'] * 4 + reserve
        if shutil.disk_usage(root.parent).free < estimate:
            raise ValueError('insufficient free space for conservative 4x compressed estimate')
        stage = Path(tempfile.mkdtemp(prefix='.' + root.name + '.stage-', dir=root.parent))
        try:
            inventory = []
            for m in members:
                archive = cache / m['file']
                if archive.is_symlink():
                    raise ValueError('symlink in download cache: ' + str(archive))
                if archive.exists() and archive.stat().st_size >= m['compressed_bytes']:
                    if archive.stat().st_size != m['compressed_bytes'] or digest(archive, 'md5') != m['md5']:
                        raise ValueError('corrupt cached archive; inspect/remove this exact file before retry: ' + str(archive))
                else:
                    print('Downloading ' + m['file'], flush=True)
                    subprocess.run(['curl', '--fail', '--location', '--proto', '=https',
                                    '--retry', '3', '--retry-all-errors', '--connect-timeout', '30',
                                    '--continue-at', '-', '--output', str(archive), m['url']], check=True)
                if archive.stat().st_size != m['compressed_bytes'] or digest(archive, 'md5') != m['md5']:
                    raise ValueError('official size/MD5 mismatch; invalid cache retained for diagnosis: ' + str(archive))
                target = stage / m['file'][:-3]
                h = hashlib.sha256()
                with gzip.open(archive, 'rb') as src, target.open('xb') as dst:
                    for block in iter(lambda: src.read(4 * 1024 * 1024), b''):
                        if shutil.disk_usage(stage).free < len(block) + reserve:
                            raise ValueError('free-space reserve exhausted while expanding ' + m['file'])
                        dst.write(block)
                        h.update(block)
                    dst.flush()
                    os.fsync(dst.fileno())
                target.chmod(0o644)
                inventory.append({'file': target.name, 'bytes': target.stat().st_size,
                                  'sha256': h.hexdigest(), 'source_md5': m['md5'], 'source_url': m['url']})
            doc = {'schema': 1, 'release': '4.0', 'license': 'CC0-1.0',
                   'catalog_sha256': digest(CATALOG), 'parts': plan['parts'], 'members': inventory}
            (stage / MANIFEST).write_text(json.dumps(doc, indent=2) + '\n')
            lines = [m['sha256'] + '  ' + m['file'] for m in inventory]
            lines.append(digest(stage / MANIFEST) + '  ' + MANIFEST)
            (stage / INVENTORY).write_text('\n'.join(lines) + '\n')
            (stage / READY).write_text(digest(stage / INVENTORY) + '\n')
            verify(stage)
            # Parse the real database before publication; no half-ready root.
            subprocess.run(['famdb.py', '-i', str(stage), 'info'], check=True)
            for path in stage.iterdir():
                path.chmod(0o644)
            stage.chmod(0o755)
            os.replace(stage, root)
            print('Installed and verified: ' + str(root))
            print('Ordinary users need read/traverse access to this root and every ancestor.')
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        # Keep the lock inode: unlinking it could split concurrent lock owners.

def main():
    p = argparse.ArgumentParser(description='Pinned Dfam 4.0 selective installer; no whole-family default download.')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('list', help='show fixed member IDs, sizes, checksums and URLs')
    i = sub.add_parser('install', help='atomically install root + explicitly selected partitions')
    i.add_argument('--db-root', required=True)
    i.add_argument('--part', action='append', required=True, help='e.g. curated.consensus.0; repeat for more members')
    i.add_argument('--dry-run', action='store_true')
    v = sub.add_parser('verify', help='verify local ready state, identity and full SHA256 hashes')
    v.add_argument('--db-root', required=True)
    v.add_argument('--quick', action='store_true', help='check inventory and member sizes without rehashing all HDF5 data')
    a = p.parse_args()
    try:
        if a.command == 'list':
            print(json.dumps(catalog(), indent=2))
        elif a.command == 'install':
            install(a)
        else:
            verify(a.db_root, a.quick)
            print('Verified (' + ('inventory/size' if a.quick else 'full SHA256') + '): ' + a.db_root)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print('taf-repeatmasker-dfam: ' + str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
