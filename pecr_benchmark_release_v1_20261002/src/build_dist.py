#!/usr/bin/env python3
"""Build a deterministic local archive from the explicit sealed release allow-list."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {'.py', '.md', '.json', '.jsonl', '.csv', '.txt', '.npz', '.tex', '.lock'}
ALLOWED_DIRS = {'src', 'cohorts', 'reference', 'protocol', 'coverage', 'reports',
                'audit', 'intervention', 'environment', 'acceptance', 'tables'}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(); out = args.out.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT), 'Use a new archive outside the release'
    seal = ROOT / 'SHA256SUMS.txt'
    assert seal.is_file(), 'Seal the reviewable release before archiving'
    paths = []
    for line in seal.read_text().splitlines():
        digest, relative = line.split('  ', 1)
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT) and not path.is_symlink()
        assert sha(path) == digest, relative
        parts = Path(relative).parts
        assert (len(parts) == 1 or parts[0] in ALLOWED_DIRS)
        assert path.name == 'LICENSE' or path.suffix in ALLOWED_SUFFIXES
        assert not any(s in parts for s in ('__pycache__', '.git', '.venv'))
        assert not any(s in path.name.lower() for s in ('raw_ledger', 'train.json', 'holdout'))
        # Method checkpoints here are numeric OOF predictions, never model weights.
        if 'checkpoint' in path.name.lower():
            import numpy as np
            assert path.suffix == '.npz'
            with np.load(path, allow_pickle=False) as data:
                assert all(data[k].ndim == 1 and data[k].dtype.kind in 'biufUS' for k in data.files)
        paths.append(path)
    paths.append(seal)
    with out.open('xb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode='w', format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(paths):
                info = archive.gettarinfo(str(path), arcname=str(Path(ROOT.name) / path.relative_to(ROOT)))
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                info.mode = 0o644
                info.pax_headers = {}
                with path.open('rb') as f:
                    archive.addfile(info, f)
    digest = sha(out)
    checksum = out.with_name(out.name + '.sha256')
    with checksum.open('x') as f:
        f.write(f'{digest}  {out.name}\n')
    print(json.dumps({'archive': str(out), 'sha256': digest, 'files': len(paths),
                      'bytes': out.stat().st_size, 'allow_list': 'SHA256SUMS.txt'}, indent=2))


if __name__ == '__main__':
    main()
