"""Checks lexifina/china-law against the official pages.

    python -X utf8 scripts/china-law/check_repo.py ../china-law [--offline]

1. Byte check: the 1982 version (tag xianfa/1982-12-04) and the head's law files equal the official 1982 and 2018
   pages, parsed and rendered.
2. Independent word stream: the letters and digits (casefolded; everything else dropped) of each official page's raw
   article body, read by the minimal extractor below (not the build's parser), equal those of the repository's
   files: the 目录 first, then 序言 and the articles in order, with the body headings taken out of the page stream.
3. Amendment words: for every version made by an amendment, every new text the amendment quotes is present, word for
   word, in that version's files.
Blobs are read with one `git cat-file --batch` process.
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sources  # noqa: E402


class Repo:
    def __init__(self, path: Path):
        self.path = path
        self.p = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=path, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def git(self, *a) -> str:
        return subprocess.run(['git', *a], cwd=self.path, capture_output=True, check=True).stdout.decode('utf-8')

    def blob(self, rev_path: str) -> bytes:
        self.p.stdin.write(rev_path.encode() + b'\n')
        self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if head[-1] == b'missing':
            raise KeyError(rev_path)
        n = int(head[2])
        data = self.p.stdout.read(n)
        self.p.stdout.read(1)
        return data

    def files(self, rev: str, folder: str = 'xianfa/') -> dict[str, str]:
        names = [f for f in self.git('ls-tree', '-r', '--name-only', rev, folder).split('\n')
                 if f.endswith('.md') and not f.endswith('README.md')]
        return {f: self.blob(f'{rev}:{f}').decode('utf-8') for f in names}


def letters(s: str) -> str:
    return ''.join(ch for ch in s.casefold() if ch.isalnum())


def raw_stream(key: str, offline: bool) -> str:
    """Minimal extractor: the page's article body, tags removed, entities decoded, letters and digits only."""
    b = sources.fetch(key, offline)[1].decode('utf-8')
    z = b[b.index('<div id="Zoom">'):b.index('<div class="editor">')]
    z = re.sub(r'<style.*?</style>', ' ', z, flags=re.S)
    z = re.sub(r'<[^>]+>', ' ', z)
    return letters(html.unescape(z))


def order(f: str):
    n = f.rsplit('/', 1)[1][:-3]
    return (0, 0) if n == 'mulu' else (1, 0) if n == 'xuyan' else (2, int(n.split('-')[1]))


def stream_check(files: dict[str, str], key: str, offline: bool) -> list[str]:
    s = raw_stream(key, offline)
    i = s.find('目录')
    if i < 0:
        return [f'{key}: no 目录 in the page']
    s = s[i + 2:]
    mulu = files['xianfa/mulu.md'].split('\n')
    toc = letters(''.join(x for x in mulu if not x.startswith('#')))
    if not s.startswith(toc):
        return [f'{key}: the table of contents differs from xianfa/mulu.md']
    s = s[len(toc):]
    for h in [letters(x) for x in mulu if x.strip() and not x.startswith('#') and x.strip() != '序言']:
        j = s.find(h)
        if j < 0:
            return [f'{key}: heading {h} not in the page body']
        s = s[:j] + s[j + len(h):]
    mine = ''.join(letters(files[f]) for f in sorted(files, key=order) if not f.endswith('mulu.md'))
    if s != mine:
        k = next((n for n in range(min(len(s), len(mine))) if s[n] != mine[n]), min(len(s), len(mine)))
        return [f'{key}: word stream differs at {k}: page …{s[max(0, k - 15):k + 15]}… repo …{mine[max(0, k - 15):k + 15]}…']
    return []


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    repo = Repo(Path(sys.argv[1]).resolve())
    offline = '--offline' in sys.argv
    import build as B
    import text as T
    bad = []
    log = repo.git('log', '--reverse', '--format=%H%x09%(trailers:key=In-force,valueonly,separator=)%x09%an', 'main')
    commits = [x.split('\t') for x in log.strip().split('\n')]
    law = [c for c in commits if not c[2].startswith('Lexifina')]
    head = commits[-1][0]
    # 1 + 2: the first version and the head
    for key, rev in (('1982', law[0][0]), ('2018', head)):
        mine = repo.files(rev)
        official = B.render(T.parse_text(key, offline))
        if sorted(mine) != sorted(official):
            bad.append(f'{key}: file lists differ')
        diff = [f for f in sorted(official) if mine.get(f) != official[f]]
        bad += [f'{key}: {f} differs from the official text' for f in diff]
        bad += stream_check(mine, key, offline)
        print(f'{key}: {len(official)} files byte-checked, {len(diff)} mismatches; word stream checked')
    # 3: amendment words
    am = [c for c in law if c[2].startswith('宪法修正案')]
    n_words = 0
    for (key, year, rng), c in zip(T.AMENDMENTS, am):
        if f'（{year}年）' not in c[2]:
            bad.append(f'{key}: commit order')
            continue
        joined = '\n'.join(repo.files(c[0]).values())
        arts, _ = T.amendment_articles(key, offline)
        for n in rng:
            qs = T.quotes(arts[n])
            for op in T.OPS[n]:
                new = []
                if op[0] in ('para', 'sub'):
                    new = [op[4]]
                elif op[0] == 'paras':
                    new = op[3]
                elif op[0] in ('insert', 'append'):
                    new = [op[3]]
                elif op[0] == 'append_after':
                    new = [op[4]]
                elif op[0] == 'whole':
                    new = [op[3]]
                elif op[0] == 'item_sub':
                    new = [op[4]]
                elif op[0] == 'item_insert':
                    new = [op[3]]
                elif op[0] == 'heading':
                    new = [op[2]]
                for q in new:
                    w = T._strip_label(qs[int(q)])
                    n_words += 1
                    if w not in joined:
                        bad.append(f'{key} art. {n}: new words not in the version: {w[:30]}')
    print(f'amendment words: {n_words} quotations checked in {len(am)} versions')
    print(f'{len(bad)} mismatches')
    for b in bad:
        print('  ' + b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
