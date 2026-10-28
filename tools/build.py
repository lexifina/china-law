"""Builds lexifina/china-law: the Constitution of the People's Republic of China as a git history, one commit per
amendment, dated noon Asia/Shanghai on the day it was promulgated and took effect.

    python -X utf8 scripts/china-law/build.py --repo ../china-law [--offline] [--verify-rebuild]

Source: 中国人大网 (www.npc.gov.cn), section 宪法、基本法和相关法律 > 宪法: the 1982 text, the five amendments
(宪法修正案, 1988, 1993, 1999, 2004, 2018) and the 2018 consolidated text. The 1982 text is the first commit. Each
amendment is applied to the text before it by the operations in text.OPS, using the amendment's own quoted words.
After the 2018 amendment the text must equal the official 2018 text; any remaining difference is committed
separately, authored by the publisher and labelled, never credited to an amendment.
No network access with --offline (the cache under cache/ is used). No model runs at build time.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sources  # noqa: E402
import text as T  # noqa: E402

COMMITTER = ('Lexifina', 'china-law@lexifina.com')
PUBLISHER = ('中国人大网 (全国人大常委会办公厅)', 'www@npc.gov.cn.invalid')
ACT = 'xianfa'
ACT_NAME = '中华人民共和国宪法'
PLACEHOLDER_SUBJECT = 'sources, before any law'


# ---------------------------------------------------------------- dates

def shanghai_offset(day: dt.date) -> int:
    """UTC offset in hours. China kept summer time 1986-1991 (tz database, rule Shang): 1986 from 4 May to 14 Sep,
    1987-1991 from the first Sunday on or after 11 April to the first Sunday on or after 11 September."""
    def sun_on_or_after(y, m, d):
        x = dt.date(y, m, d)
        return x + dt.timedelta(days=(6 - x.weekday()) % 7)
    y = day.year
    if y == 1986:
        start, end = dt.date(1986, 5, 4), dt.date(1986, 9, 14)
    elif 1987 <= y <= 1991:
        start, end = sun_on_or_after(y, 4, 11), sun_on_or_after(y, 9, 11)
    else:
        return 8
    return 9 if start <= day < end else 8


def git_date(day: str, seq: int = 0) -> str:
    d = dt.date.fromisoformat(day)
    off = shanghai_offset(d)
    local = dt.datetime(d.year, d.month, d.day, 12, 0, seq, tzinfo=dt.timezone(dt.timedelta(hours=off)))
    return f'{int(local.timestamp())} +{off:02d}00'


def cn_date(s: str) -> str:
    m = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', s)
    return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'


def head_meta(h: str) -> dict:
    """（1988年4月12日第七届全国人民代表大会第一次会议通过　1988年4月12日全国人民代表大会公告第八号公布施行）"""
    m = re.fullmatch(r'（(\d{4}年\d{1,2}月\d{1,2}日)(.+?)通过[' + T.WS + r']*(\d{4}年\d{1,2}月\d{1,2}日)(全国人民代表大会公告.*?)公布施行）', h)
    if not m:
        raise RuntimeError('cannot read the adoption line: ' + h)
    return {'adopted': cn_date(m.group(1)), 'by': m.group(2), 'promulgated': cn_date(m.group(3)),
            'announcement': m.group(4), 'line': h}


# ---------------------------------------------------------------- rendering

def art_file(n: int) -> str:
    return f'{ACT}/art-{n:03d}.md'


def label(p) -> str:
    if p == 'pre':
        return '序言'
    if p == 'heads':
        return '目录'
    return f'第{T.int_cn(p)}条'


def render(t: dict) -> dict[str, str]:
    files = {f'{ACT}/mulu.md': '# 目录\n\n序言\n\n' + ''.join(f'{lb}　{ti}\n\n' for lb, ti, _ in t['heads'])
             .rstrip('\n') + '\n',
             f'{ACT}/xuyan.md': '# 序言\n\n' + '\n\n'.join(t['pre']) + '\n'}
    for n, ps in t['art'].items():
        files[art_file(n)] = f'# 第{T.int_cn(n)}条\n\n' + '\n\n'.join(ps) + '\n'
    return files


def provision_order(p):
    return (0, 0) if p == 'heads' else (1, 0) if p == 'pre' else (2, p)


# ---------------------------------------------------------------- versions

def versions(offline: bool) -> list[dict]:
    t = T.parse_text('1982', offline)
    m = head_meta(T.page_head('1982', offline))
    out = [{'kind': 'enactment', 'day': m['promulgated'], 'meta': m, 'key': '1982', 'text': copy.deepcopy(t),
            'author': ('中华人民共和国宪法（1982年）', 'xianfa-1982@npc.gov.cn.invalid'),
            'touched': ['heads', 'pre'] + list(t['art']), 'articles': []}]
    for key, year, rng in T.AMENDMENTS:
        arts, extra = T.amendment_articles(key, offline)
        if sorted(arts) != list(rng):
            raise RuntimeError(f'{key}: amendment articles {sorted(arts)}')
        touched = []
        for n in rng:
            for p in T.apply_article(t, n, arts[n], extra):
                if p not in touched:
                    touched.append(p)
        m = head_meta(T.page_head(key, offline))
        if m['adopted'] != m['promulgated']:
            raise RuntimeError(f'{key}: adopted and promulgated on different days')
        body = [f'第{T.int_cn(n)}条　{arts[n]}' for n in rng]
        if year == 2018:
            body += extra
        out.append({'kind': 'amendment', 'day': m['promulgated'], 'meta': m, 'key': key, 'year': year,
                    'text': copy.deepcopy(t), 'author': (f'宪法修正案（{year}年）', f'xianfa-xzha-{year}@npc.gov.cn.invalid'),
                    'touched': sorted(touched, key=provision_order), 'articles': list(rng), 'body': body})
    official = T.parse_text('2018', offline)
    a, b = render(t), render(official)
    if sorted(a) != sorted(b):
        raise RuntimeError('2018: the applied text and the official text have different provisions')
    diff = [f for f in sorted(a) if a[f] != b[f]]
    if diff:
        pub = published_2018(offline)
        if pub <= out[-1]['day']:
            raise RuntimeError('2018 text published before the amendment?')
        out.append({'kind': 'editorial', 'day': pub, 'key': '2018', 'text': official, 'author': PUBLISHER,
                    'files': diff, 'touched': [], 'before': a, 'after': b})
    return out


def published_2018(offline: bool) -> str:
    """The day the consolidated 2018 text was published: the Xinhua dateline (新华社北京3月21日电), in the year of
    the page's own date (2018年03月22日)."""
    b = sources.fetch('2018', offline)[1].decode('utf-8')
    m = re.search(r'新华社北京(\d{1,2})月(\d{1,2})日电', b)
    y = re.search(r'id="zzrq">(\d{4})年', b)
    if not (m and y):
        raise RuntimeError('2018: no Xinhua dateline')
    return f'{y.group(1)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}'


def char_diffs(a: str, b: str) -> list[str]:
    """Describes single-character differences between two texts of equal length (the only kind expected)."""
    if len(a) != len(b):
        return ['the lengths differ']
    return [f'“{x}” (U+{ord(x):04X}) → “{y}” (U+{ord(y):04X})' for x, y in zip(a, b) if x != y]


def message(v: dict, prev: dict | None) -> str:
    src = sources.url(v['key'])
    if v['kind'] == 'enactment':
        m = v['meta']
        return (f'{ACT_NAME}（1982年）\n\n'
                f'{ACT_NAME}{m["line"]}\n\n'
                'The Constitution of the People\'s Republic of China as adopted by the 5th National People\'s Congress\n'
                'at its 5th session on 4 December 1982 and promulgated and in force the same day, from the text\n'
                '中国人大网 publishes.\n\n'
                'Kind: Constitution\n'
                'Issuer: 全国人民代表大会\n'
                f'Adopted: {m["adopted"]}\n'
                f'Promulgated: {m["promulgated"]} ({m["announcement"]})\n'
                f'In-force: {v["day"]}\n'
                f'Source: {src}\n')
    if v['kind'] == 'amendment':
        m, year = v['meta'], v['year']
        names = [label(p) for p in v['touched']]
        summary = '、'.join(names) if len(names) <= 4 else '、'.join(names[:3]) + f'等{len(names)}处'
        subject = f'宪法修正案（{year}年）：{summary}'
        first, last = v['articles'][0], v['articles'][-1]
        lines = [subject, '',
                 f'中华人民共和国宪法修正案（第{T.int_cn(first)}条至第{T.int_cn(last)}条）{m["line"]}', '']
        lines += [x for x in v['body']] + ['']
        lines += [f'Amendment to the Constitution, articles {first} to {last} of the amendments, adopted by the National',
                  f'People\'s Congress on {m["adopted"]} and promulgated and in force the same day. Each change is',
                  'applied with the amendment\'s own words to the text before it.', '']
        renum = ''
        if year == 2018:
            renum = 'Renumbers: 第一百二十三条至第一百三十八条 -> 第一百二十八条至第一百四十三条\n'
        tr = ['Kind: Constitutional amendment (宪法修正案)', 'Issuer: 全国人民代表大会',
              f'Adopted: {m["adopted"]}', f'Promulgated: {m["promulgated"]} ({m["announcement"]})',
              f'In-force: {v["day"]}']
        tr += [f'Amendment-article: 第{T.int_cn(n)}条' for n in v['articles']]
        tr += [f'Affecting: 宪法{label(p)}' for p in v['touched']]
        tr += ['Evidence: the amendment text quotes the words it replaces and gives the new words; this version '
               'is the version before it with those changes applied (no official consolidated text of it is used)']
        if renum:
            tr.append(renum.strip())
        tr.append(f'Source: {src}')
        return '\n'.join(lines + tr) + '\n'
    # editorial
    det = []
    for f in v['files']:
        for d in char_diffs(v['before'][f], v['after'][f]):
            det.append(f'- {f}: {d}')
    names = [Path(f).stem for f in v['files']]
    return ('中国人大网 2018 年文本：与修正案原文的字形差异\n\n'
            'The official 2018 consolidated text on 中国人大网 (中华人民共和国宪法（2018年3月11日修正）, a reprint of\n'
            'the Xinhua release of 21 March 2018) differs from the text the five amendments produce in these\n'
            'characters only. No amendment makes these changes, so this commit is credited to the publisher and to\n'
            'no act. After it, the record equals the official 2018 text. The words in force do not change: the\n'
            'commit is dated, and its In-force trailer set, to the day that consolidated text was published\n'
            '(新华社北京3月21日电; the 中国人大网 page is dated 2018-03-22), so that a reading before that day\n'
            'gives the text the amendment itself produces.\n\n'
            + '\n'.join(det) + '\n\n'
            'Kind: editorial\n'
            'Words-changed: no\n'
            f'Published: {v["day"]} (新华社; reprinted by 中国人大网)\n'
            f'In-force: {v["day"]}\n'
            + ''.join(f'Affecting: 宪法{label(_prov(f))}\n' for f in v['files'])
            + f'Source: {src}\n')


def _prov(f: str):
    stem = Path(f).stem
    if stem == 'xuyan':
        return 'pre'
    if stem == 'mulu':
        return 'heads'
    return int(stem.split('-')[1])


def tag_name(day: str) -> str:
    return f'{ACT}/{day}'


# ---------------------------------------------------------------- git

def git(repo: Path, *args, input: bytes | None = None) -> str:
    r = subprocess.run(['git', *args], cwd=repo, input=input, capture_output=True)
    if r.returncode:
        raise RuntimeError(f'git {args[0]}: {r.stderr.decode(errors="replace")}')
    return r.stdout.decode('utf-8')


def data_block(b: bytes) -> bytes:
    return b'data %d\n' % len(b) + b + b'\n'


def write_repo(repo: Path, vs: list[dict], docs: dict[str, str], doc_day: str, doc_message: str):
    if repo.exists() and any(repo.iterdir()):
        raise SystemExit(f'{repo} is not empty: refusing to write a history into it')
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'core.autocrlf', 'false')
    out = bytearray()
    mark = 0
    tags = {}
    seq_by_day = {}
    for i, v in enumerate(vs):
        mark += 1
        seq = seq_by_day.get(v['day'], 0)
        seq_by_day[v['day']] = seq + 1
        date = git_date(v['day'], seq)
        name, email = v['author']
        out += b'commit refs/heads/main\nmark :%d\n' % mark
        out += f'author {name} <{email}> {date}\n'.encode()
        out += f'committer {COMMITTER[0]} <{COMMITTER[1]}> {date}\n'.encode()
        out += data_block(message(v, vs[i - 1] if i else None).encode())
        if mark > 1:
            out += b'from :%d\n' % (mark - 1)
        out += b'deleteall\n'
        for path, body in sorted(render(v['text']).items()):
            out += f'M 100644 inline {path}\n'.encode() + data_block(body.encode())
        tags[tag_name(v['day'])] = mark
        v['mark'] = mark
    # documentation commit
    mark += 1
    files = render(vs[-1]['text'])
    files.update(docs)
    date = git_date(doc_day)
    out += b'commit refs/heads/main\nmark :%d\n' % mark
    out += f'author {COMMITTER[0]} <{COMMITTER[1]}> {date}\n'.encode()
    out += f'committer {COMMITTER[0]} <{COMMITTER[1]}> {date}\n'.encode()
    out += data_block(doc_message.encode())
    out += b'from :%d\ndeleteall\n' % (mark - 1)
    for path, body in sorted(files.items()):
        mode = '100755' if path.startswith('tools/') and path.endswith('.py') else '100644'
        out += f'M {mode} inline {path}\n'.encode() + data_block(body.encode())
    for t, mk in sorted(tags.items()):
        out += f'reset refs/tags/{t}\nfrom :{mk}\n'.encode()
    out += b'done\n'
    git(repo, 'fast-import', '--quiet', '--done', input=bytes(out))
    git(repo, 'checkout', '-q', '-f', 'main')
    return tags


# ---------------------------------------------------------------- main

def data_day() -> str:
    days = sorted(sources.retrieved(k) for k in sources.PAGES)
    return days[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[2] / 'china-law'))
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--verify-rebuild', action='store_true',
                    help='build twice into temporary folders and compare the head hashes')
    a = ap.parse_args()
    for k in sources.PAGES:
        sources.fetch(k, a.offline)
    import reproduce
    if a.verify_rebuild:
        heads = []
        for i in range(2):
            tmp = HERE / 'cache' / f'rebuild-{i}'
            if tmp.exists():
                shutil.rmtree(tmp, onerror=lambda f, p, e: (os.chmod(p, 0o700), f(p)))
            vs = versions(True)
            docs, msg = reproduce.documents(vs, data_day())
            write_repo(tmp, vs, docs, data_day(), msg)
            heads.append(git(tmp, 'rev-parse', 'HEAD').strip())
        same = heads[0] == heads[1]
        target = Path(a.repo)
        main_head = git(target, 'rev-parse', 'main').strip() if (target / '.git').exists() else ''
        res = {'rebuild_heads': heads, 'identical': same, 'repo_main': main_head,
               'repo_main_identical': main_head == heads[0]}
        print(json.dumps(res, indent=1))
        (HERE / 'verification.json').write_text(json.dumps({'rebuild_identical': same, 'head': heads[0]},
                                                           indent=1) + '\n', encoding='utf-8', newline='\n')
        sys.exit(0 if same else 1)
    vs = versions(a.offline)
    docs, msg = reproduce.documents(vs, data_day())
    tags = write_repo(Path(a.repo), vs, docs, data_day(), msg)
    print(f'{len(vs) + 1} commits, {len(tags)} tags, head {git(Path(a.repo), "rev-parse", "HEAD").strip()}')


if __name__ == '__main__':
    main()
