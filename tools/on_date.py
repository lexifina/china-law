"""Prints an act (the Constitution, xianfa, by default in the examples), or one provision of it, as it stood on a given day.

    python tools/on_date.py 2000-01-01 xianfa 11        # 第十一条 on 1 January 2000
    python tools/on_date.py 2000-01-01 xianfa xuyan     # the preamble (序言)
    python tools/on_date.py 2000-01-01 xianfa mulu      # the chapter and section headings (目录)
    python tools/on_date.py 2010-01-01 xianfa           # the whole text

Every commit carries the day its change took effect in an `In-force:` trailer. The text in force on a day is the last
commit whose In-force is on or before that day (the commit date is noon Asia/Shanghai on the same day, but the trailer
is the source of truth; do not rely on `git rev-list --before`, which reads your own time zone).
Standard library only.
"""
import datetime as dt
import re
import subprocess
import sys


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


def commit_on(day: str, act: str) -> str:
    out = git('log', '--format=%H%x09%(trailers:key=In-force,valueonly,separator=)', 'main', '--', act)
    for line in out.splitlines():
        h, _, d = line.partition('\t')
        if d.strip() and d.strip() <= day:
            return h
    return ''


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2]
    dt.date.fromisoformat(day)
    commit = commit_on(day, act)
    if not commit:
        first = git('log', '--reverse', '--format=%(trailers:key=In-force,valueonly,separator=)', 'main', '--', act).split()
        sys.exit(f'{act} is not in the record on {day}' + (f' (its record starts on {first[0]}).' if first else '.'))
    if len(sys.argv) > 3:
        names = [f.rsplit('/', 1)[1] for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split('\n') if f]
        name = file_for(sys.argv[3], names)
        try:
            sys.stdout.write(git('show', f'{commit}:{act}/{name}'))
        except subprocess.CalledProcessError:
            sys.exit(f'{act}/{name} was not in the text on {day}.')
        return
    files = [f for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split('\n')
             if f.endswith('.md') and not f.endswith('/README.md')]
    # One `git cat-file --batch` for every file (a git process per file is slow for an act of a thousand articles).
    files = sorted(files, key=order)
    out = subprocess.run(['git', 'cat-file', '--batch'], input=''.join(f'{commit}:{f}\n' for f in files).encode(),
                         capture_output=True, check=True).stdout
    i = 0
    for _ in files:
        end = out.index(b'\n', i)
        size = int(out[i:end].split()[2])
        sys.stdout.write(out[end + 1:end + 1 + size].decode('utf-8') + '\n')
        i = end + 1 + size + 1


if __name__ == '__main__':
    main()
