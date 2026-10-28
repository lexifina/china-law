"""Prints the Constitution, or one provision of it, as it stood on a given day, from this repository's history.

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
    m = re.fullmatch(r'art-(\d+)', name)
    return (2, int(m.group(1))) if m else (3, name)


def file_for(key: str) -> str:
    if re.fullmatch(r'\d+', key):
        return f'art-{int(key):03d}.md'
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
        sys.exit(f'{act} is not in the record on {day} (the record starts on 1982-12-04).')
    if len(sys.argv) > 3:
        name = file_for(sys.argv[3])
        try:
            sys.stdout.write(git('show', f'{commit}:{act}/{name}'))
        except subprocess.CalledProcessError:
            sys.exit(f'{act}/{name} was not in the text on {day}.')
        return
    files = [f for f in git('ls-tree', '-r', '--name-only', commit, f'{act}/').split('\n')
             if f.endswith('.md') and not f.endswith('/README.md')]
    for f in sorted(files, key=order):
        sys.stdout.write(git('show', f'{commit}:{f}') + '\n')


if __name__ == '__main__':
    main()
