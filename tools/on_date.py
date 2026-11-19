"""Prints an act, or one provision of it, as it stood on a given day.

    python tools/on_date.py 2000-01-01 宪法 11              # 第十一条 on 1 January 2000
    python tools/on_date.py 2000-01-01 宪法 序言            # the preamble
    python tools/on_date.py 2000-01-01 宪法 目录            # the chapter and section headings
    python tools/on_date.py 2010-01-01 法律/劳动合同法 66
    python tools/on_date.py 2024-01-01 法律/刑法 120之一     # 第一百二十条之一 (also: 120-1)
    python tools/on_date.py 2010-01-01 宪法                 # the whole text

Every commit carries the day its change took effect in an `In-force:` trailer. The text in force on a day is the last
ordinary commit whose In-force is on or before that day, with any correction commit (Kind: correction) whose
Corrects range holds the day applied file by file (the commit date is noon Asia/Shanghai on the same day, but the
trailer is the source of truth; do not rely on `git rev-list --before`, which reads your own time zone).

Folders and files have Chinese names since the layout commit of 2026-11-20 (Kind: layout). Before it, each act was a
pinyin folder at the top (xianfa/, laodonghetongfa/) with files art-NNN.md, art-NNN-K.md (之K), xuyan.md, mulu.md and
fujian-N.md. data/paths.json maps every old folder and file to its new place; this tool reads both, and accepts the
old folder names too (python tools/on_date.py 2010-01-01 laodonghetongfa 66). Standard library only.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

NL = chr(10)
RS, US, GS = chr(0x1e), chr(0x1f), chr(0x1d)
ZHI = '一二三四五六七八九十'


def git(*args: str) -> str:
    return subprocess.run(['git', '-c', 'core.quotePath=false', *args], capture_output=True, text=True,
                          encoding='utf-8', check=True).stdout


def _paths() -> dict:
    try:
        with open(os.path.join('data', 'paths.json'), encoding='utf-8') as fh:
            return json.load(fh)
    except OSError:
        try:
            return json.loads(git('show', 'main:data/paths.json'))
        except subprocess.CalledProcessError:
            return {'paths': {}, 'files': {}}


PATHS = _paths()
OLD2NEW = PATHS.get('paths', {})
NEW2OLD = {v: k for k, v in OLD2NEW.items()}


def new_name(old: str) -> str:
    """Old file name (art-066.md, art-120-1.md, xuyan.md, mulu.md, fujian-2.md) -> new (第066条.md ...)."""
    m = re.fullmatch(r'art-(\d+)(?:-(\d+))?\.md', old)
    if m:
        return f'第{m.group(1)}条' + (f'之{ZHI[int(m.group(2)) - 1]}' if m.group(2) else '') + '.md'
    m = re.fullmatch(r'fujian-(\d+)\.md', old)
    if m:
        return f'附件{m.group(1)}.md'
    return {'xuyan.md': '序言.md', 'mulu.md': '目录.md'}.get(old, old)


def order(path: str) -> tuple:
    name = path.rsplit('/', 1)[1][:-3]
    if name == '目录':
        return (0, 0, 0)
    if name == '序言':
        return (1, 0, 0)
    m = re.fullmatch(r'第(\d+)条(?:之([一二三四五六七八九十]))?', name)
    if m:
        return (2, int(m.group(1)), ZHI.index(m.group(2)) + 1 if m.group(2) else 0)
    m = re.fullmatch(r'附件(\d+)', name)
    return (4, int(m.group(1)), 0) if m else (3, 0, name)


def file_for(key: str, names: list[str] | None = None) -> str:
    """'11' -> 第011条.md (第0011条.md in a folder numbered with four digits); '120-1' or '120之一' -> 第120条之一.md;
    序言/目录/附件N, and the old names xuyan/mulu/fujian-N."""
    key = {'xuyan': '序言', 'mulu': '目录'}.get(key, key)
    m = re.fullmatch(r'fujian-(\d+)', key)
    if m:
        key = f'附件{m.group(1)}'
    m = re.fullmatch(r'(\d+)(?:(?:-(\d+))|(?:之([一二三四五六七八九十])))?', key)
    if m:
        tail = ''
        if m.group(2):
            tail = '之' + ZHI[int(m.group(2)) - 1]
        elif m.group(3):
            tail = '之' + m.group(3)
        for w in (3, 4):
            f = f'第{int(m.group(1)):0{w}d}条{tail}.md'
            if names is None or f in names:
                return f
        return f'第{int(m.group(1)):03d}条{tail}.md'
    return key if key.endswith('.md') else f'{key}.md'


def resolve(act: str) -> tuple[str, str | None]:
    """(new folder, old folder or None) for an act given by either name."""
    act = act.strip('/')
    if act in OLD2NEW:
        return OLD2NEW[act], act
    return act, NEW2OLD.get(act)


def _log(new: str, old: str | None) -> list[tuple[str, str, str, str]]:
    """(commit, In-force, Kind, Corrects) of every commit touching the act (either place), newest first."""
    out = git('log', '--format=%H%x1f%(trailers:key=In-force,valueonly,separator=)%x1f'
              '%(trailers:key=Kind,valueonly,separator=)%x1f%(trailers:key=Corrects,valueonly,separator=%x1e)%x1d',
              'main', '--', new, *([old] if old else []))
    rows = []
    for rec in out.split(GS):
        rec = rec.strip(NL)
        if rec:
            h, d, k, c = (rec.split(US) + ['', '', ''])[:4]
            rows.append((h, d.strip(), k.strip(), c))
    return rows


def commit_on(day: str, rows) -> str:
    """The ordinary (not Kind: correction or layout) commit with In-force on or before day, newest first."""
    for h, d, k, _ in rows:
        if d and d <= day and k not in ('correction', 'layout'):
            return h
    return ''


def corrections_on(day: str, rows, names: set) -> list[str]:
    """Correction commits (Kind: correction, Corrects: <act> <from>..<to>) whose range holds day, oldest first; an
    open range ends the day before the next ordinary version (the shared reading rule, gitlaw_common/on.py)."""
    ordinary = sorted({d for _, d, k, _ in rows if d and k not in ('correction', 'layout')})
    hits = []
    for h, _, k, c in reversed(rows):
        if k != 'correction':
            continue
        for line in c.split(RS):
            parts = line.split()
            if len(parts) == 2 and parts[0] in names and '..' in parts[1]:
                a, _, b = parts[1].partition('..')
                if not b:
                    later = [x for x in ordinary if x > a]
                    b = (dt.date.fromisoformat(later[0]) - dt.timedelta(days=1)).isoformat() if later else '9999-12-31'
                if a <= day <= b:
                    hits.append(h)
    return hits


def _tree(commit: str, new: str, old: str | None) -> dict[str, str]:
    """{new path: '<commit>:<path as stored>'} of the act's text files at commit (new place, else old place)."""
    out = {}
    for f in git('ls-tree', '-r', '--name-only', commit, f'{new}/').split(NL):
        if f.endswith('.md') and not f.endswith('/README.md'):
            out[f] = f'{commit}:{f}'
    if not out and old:
        for f in git('ls-tree', '-r', '--name-only', commit, f'{old}/').split(NL):
            if f.endswith('.md') and not f.endswith('/README.md'):
                out[f'{new}/{new_name(f.rsplit("/", 1)[1])}'] = f'{commit}:{f}'
    return out


def files_on(day: str, act: str) -> dict[str, str]:
    """{new path: '<commit>:<path>'} of the act's files on day, corrections applied."""
    new, old = resolve(act)
    rows = _log(new, old)
    commit = commit_on(day, rows)
    files = _tree(commit, new, old) if commit else {}
    names = {new, new.rsplit('/', 1)[-1]} | ({old} if old else set())
    for h in corrections_on(day, rows, names):
        listed = [x.strip() for x in git('log', '-1', '--format=%(trailers:key=Files,valueonly,separator=%x1e)', h)
                  .split(RS) if x.strip()]
        have = _tree(h, new, old)
        for f in listed:
            nf = f if f.startswith(new + '/') else f'{new}/{new_name(f.rsplit("/", 1)[1])}'
            if nf in have:
                files[nf] = have[nf]
            else:
                files.pop(nf, None)
    return files


def blobs(specs: list[str]) -> list[str]:
    """One `git cat-file --batch` for every file (a git process per file is slow for an act of a thousand articles)."""
    out = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(x + NL for x in specs).encode('utf-8'),
                         capture_output=True, check=True).stdout
    res, i = [], 0
    for _ in specs:
        end = out.index(b'\n', i)
        size = int(out[i:end].split()[2])
        res.append(out[end + 1:end + 1 + size].decode('utf-8'))
        i = end + 1 + size + 1
    return res


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2]
    dt.date.fromisoformat(day)
    new, old = resolve(act)
    files = files_on(day, act)
    if not files:
        first = sorted(d for _, d, k, _ in _log(new, old) if d and k != 'layout')
        sys.exit(f'{new} is not in the record on {day}' + (f' (its record starts on {first[0]}).' if first else '.'))
    if len(sys.argv) > 3:
        names = [f.rsplit('/', 1)[1] for f in files]
        fname = file_for(sys.argv[3], names)
        spec = files.get(f'{new}/{fname}')
        if not spec:
            sys.exit(f'{new}/{fname} was not in the text on {day}.')
        sys.stdout.write(blobs([spec])[0])
        return
    for text in blobs([files[f] for f in sorted(files, key=order)]):
        sys.stdout.write(text + NL)


if __name__ == '__main__':
    main()
