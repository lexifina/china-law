"""Prints an act (the Constitution, xianfa, by default in the examples), or one provision of it, as it stood on a given day.

    python tools/on_date.py 2000-01-01 xianfa 11        # 第十一条 on 1 January 2000
    python tools/on_date.py 2000-01-01 xianfa xuyan     # the preamble (序言)
    python tools/on_date.py 2000-01-01 xianfa mulu      # the chapter and section headings (目录)
    python tools/on_date.py 2010-01-01 xianfa           # the whole text

Every commit carries the day its change took effect in an `In-force:` trailer. The text in force on a day is the last
ordinary commit whose In-force is on or before that day, with any correction commit (Kind: correction) whose
Corrects range holds the day applied file by file (the commit date is noon Asia/Shanghai on the same day, but the
trailer is the source of truth; do not rely on `git rev-list --before`, which reads your own time zone).
Standard library only.
"""
import datetime as dt
import re
import subprocess
import sys

NL = chr(10)
RS, US, GS = chr(0x1e), chr(0x1f), chr(0x1d)


def git(*args: str) -> str:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout


def order(path: str) -> tuple:
    name = path.rsplit('/', 1)[1][:-3]
    if name == 'mulu':
        return (0, 0)
    if name == 'xuyan':
        return (1, 0)
    m = re.fullmatch(r'art-(\d+)(?:-(\d+))?', name)
    if m:
        return (2, int(m.group(1)), int(m.group(2) or 0))
    m = re.fullmatch(r'fujian-(\d+)', name)
    return (4, int(m.group(1)), 0) if m else (3, 0, name)


def file_for(key: str, names: list[str] | None = None) -> str:
    """'11' -> art-011.md (art-0011.md in a folder numbered with four digits); '120-1' -> art-120-1.md (之一)."""
    m = re.fullmatch(r'(\d+)(?:-(\d+))?', key)
    if m:
        tail = f'-{int(m.group(2))}' if m.group(2) else ''
        for w in (3, 4):
            f = f'art-{int(m.group(1)):0{w}d}{tail}.md'
            if names is None or f in names:
                return f
        return f'art-{int(m.group(1)):03d}{tail}.md'
    return key if key.endswith('.md') else f'{key}.md'


def _log(act: str) -> list[tuple[str, str, str, str]]:
    """(commit, In-force, Kind, Corrects) of every commit touching act, newest first."""
    out = git('log', '--format=%H%x1f%(trailers:key=In-force,valueonly,separator=)%x1f'
              '%(trailers:key=Kind,valueonly,separator=)%x1f%(trailers:key=Corrects,valueonly,separator=%x1e)%x1d',
              'main', '--', act)
    rows = []
    for rec in out.split(GS):
        rec = rec.strip(NL)
        if rec:
            h, d, k, c = (rec.split(US) + ['', '', ''])[:4]
            rows.append((h, d.strip(), k.strip(), c))
    return rows


def commit_on(day: str, act: str) -> str:
    """The ordinary (not Kind: correction) commit with In-force on or before day, newest first in log order."""
    for h, d, k, _ in _log(act):
        if d and d <= day and k != 'correction':
            return h
    return ''


def corrections_on(day: str, act: str) -> list[str]:
    """Correction commits (Kind: correction, Corrects: <act> <from>..<to>) whose range holds day, oldest first; an
    open range ends the day before the next ordinary version (the shared reading rule, gitlaw_common/on.py)."""
    rows = _log(act)
    ordinary = sorted({d for _, d, k, _ in rows if d and k != 'correction'})
    hits = []
    for h, _, k, c in reversed(rows):
        if k != 'correction':
            continue
        for line in c.split(RS):
            parts = line.split()
            if len(parts) == 2 and parts[0] == act and '..' in parts[1]:
                a, _, b = parts[1].partition('..')
                if not b:
                    later = [x for x in ordinary if x > a]
                    b = (dt.date.fromisoformat(later[0]) - dt.timedelta(days=1)).isoformat() if later else '9999-12-31'
                if a <= day <= b:
                    hits.append(h)
    return hits


def files_on(day: str, act: str) -> dict[str, str]:
    """{path: '<commit>:<path>'} of the act's files on day, corrections applied."""
    commit = commit_on(day, act)
    files = {}
    if commit:
        for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split(NL):
            if f.endswith('.md') and not f.endswith('/README.md'):
                files[f] = f'{commit}:{f}'
    for h in corrections_on(day, act):
        listed = [x.strip() for x in git('log', '-1', '--format=%(trailers:key=Files,valueonly,separator=%x1e)', h)
                  .split(RS) if x.strip()]
        have = set(git('ls-tree', '-r', '--name-only', h, f'{act}/').split(NL))
        for f in listed:
            if f in have:
                files[f] = f'{h}:{f}'
            else:
                files.pop(f, None)
    return files


def blobs(specs: list[str]) -> list[str]:
    """One `git cat-file --batch` for every file (a git process per file is slow for an act of a thousand articles)."""
    out = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(x + NL for x in specs).encode(),
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
    files = files_on(day, act)
    if not files:
        first = sorted(d for _, d, k, _ in _log(act) if d)
        sys.exit(f'{act} is not in the record on {day}' + (f' (its record starts on {first[0]}).' if first else '.'))
    if len(sys.argv) > 3:
        names = [f.rsplit('/', 1)[1] for f in files]
        name = file_for(sys.argv[3], names)
        spec = files.get(f'{act}/{name}')
        if not spec:
            sys.exit(f'{act}/{name} was not in the text on {day}.')
        sys.stdout.write(blobs([spec])[0])
        return
    for text in blobs([files[f] for f in sorted(files, key=order)]):
        sys.stdout.write(text + NL)


if __name__ == '__main__':
    main()
