"""Generates the documentation commit of lexifina/china-law: README.md, REPRODUCE.md, LICENSE, corpus.json,
data/versions.json, xianfa/README.md and the tools/ copies. Called by build.py; deterministic for a given cache."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path

import sources
import text as T

HERE = Path(__file__).resolve().parent
TOOLS = ['build.py', 'text.py', 'sources.py', 'reproduce.py', 'check_repo.py', 'test_repo.py', 'on_date.py']


def blob(path: Path) -> str:
    data = path.read_bytes().replace(b'\r\n', b'\n')
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def page_sha(key: str) -> str:
    return hashlib.sha256(sources.fetch(key, True)[1]).hexdigest()


def tool_version(cmd) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()[0]
    except Exception:
        return 'unknown'


def documents(vs: list[dict], day: str) -> tuple[dict[str, str], str]:
    import build as B
    law = [v for v in vs]
    days = [v['day'] for v in law]
    first, last = days[0], days[-1]
    ver = json.loads((HERE / 'verification.json').read_text(encoding='utf-8')) if (HERE / 'verification.json').exists() \
        else {}
    rebuild = ('identical: two builds from the cache gave the same head hash' if ver.get('rebuild_identical')
               else 'not yet recorded')

    # change counts per provision
    counts, lastday = {}, {}
    for v in law[1:]:
        if v['kind'] == 'amendment':
            for p in v['touched']:
                counts[p] = counts.get(p, 0) + 1
                lastday[p] = v['day']
        else:
            for f in v['files']:
                p = B._prov(f)
                counts[p] = counts.get(p, 0) + 1
                lastday[p] = v['day']
    final = law[-1]['text']
    rows = [('目录', 'mulu.md', 'heads'), ('序言', 'xuyan.md', 'pre')]
    rows += [(f'第{T.int_cn(n)}条', f'art-{n:03d}.md', n) for n in final['art']]
    table = '\n'.join(f'| {a} | [{f}]({f}) | {counts.get(p, 0)} | {lastday.get(p, "")} |' for a, f, p in rows)
    act_readme = (f'# {B.ACT_NAME}\n\n'
                  f'{len(law)} versions in this record, in force from {first} (the last from {last}).\n'
                  'Article numbers are those of the version in force: the 2018 amendment inserted 第一百二十三条 to\n'
                  '第一百二十七条 and moved the old 第一百二十三条 to 第一百三十八条 to 第一百二十八条 to 第一百四十三条.\n\n'
                  '| Provision | File | Changes | Last changed |\n| --- | --- | ---: | --- |\n' + table + '\n')

    vers = []
    for v in law:
        vers.append({'in_force': v['day'], 'kind': v['kind'], 'author': v['author'][0],
                     'source': sources.url(v['key']),
                     'amendment_articles': [f'第{T.int_cn(n)}条' for n in v.get('articles', [])],
                     'affecting': [B.label(p) for p in v['touched']] if v['kind'] != 'editorial'
                     else [B.label(B._prov(f)) for f in v['files']],
                     'files': {f: hashlib.sha256(b.encode()).hexdigest() for f, b in sorted(B.render(v['text']).items())}})
    pages = [{'key': k, 'url': sources.url(k), 'retrieved': sources.retrieved(k), 'sha256': page_sha(k)}
             for k in sources.PAGES]
    versions_json = json.dumps({'act': B.ACT_NAME, 'versions': vers, 'pages': pages}, ensure_ascii=False, indent=1) + '\n'

    corpus = {
        'corpus': 'cn/national/acts',
        'name': 'Chinese law: 中华人民共和国宪法 (Constitution of the People\'s Republic of China, 1982, as amended)',
        'acts': [B.ACT_NAME],
        'history_from': first,
        'built': day,
        'dates': {'commit': 'in-force', 'other_trailers': ['Adopted', 'Promulgated'],
                  'time': '12:00 Asia/Shanghai (UTC+8; UTC+9 in the summer time of 1986-1991)'},
        'scope': {
            'trailer': 'Applies',
            'when_absent': 'this corpus records no scope notes (no commit carries Applies:); the absence is not a '
                           'statement that the change reaches every case',
            'default_reach': {
                'rule': 'no retroactivity, unless a special provision better protects rights and interests',
                'meaning': 'laws, administrative regulations, local regulations, autonomous and separate regulations '
                           'and rules do not apply retroactively, except special provisions made to better protect '
                           'the rights and interests of citizens, legal persons and other organisations; in criminal '
                           'law the law at the time of the act applies unless the later law is lighter',
                'authority': '中华人民共和国立法法第一百零四条 (2023年修正; 2015年文本第九十三条): "法律、行政法规、地方性法规、'
                             '自治条例和单行条例、规章不溯及既往，但为了更好地保护公民、法人和其他组织的权利和利益而作的特别规定除外。"; '
                             '中华人民共和国刑法第十二条',
                'decided_here': False}},
        'tool': 'tools/on_date.py',
        'in_force_trailer': 'In-force',
        'record_to': last,
        'citation': {'file': r'([a-z]+)/art-0*([0-9]+)\.md', 'cites': '第{n}条',
                     'numerals': 'zh-Hans: {n} is written in Chinese numerals (第一百零三条 = 103), as tools/text.py '
                                 'int_cn() does; with Arabic digits the rule finds nothing'},
        'label': 'China',
        'language': 'zh',
        'checked_on': day,
        'history': 'in-force',
        'record_note': f'The 1982 text and the 2018 text are checked word for word against the official pages of '
                       f'中国人大网 on {day}; the versions between are the 1982 text with each amendment applied.',
    }
    corpus_json = json.dumps(corpus, ensure_ascii=False, indent=2) + '\n'

    readme = f"""# China: law history

The Constitution of the People's Republic of China (中华人民共和国宪法) as a git history: one file per provision,
one commit per amendment, each dated the day it was promulgated and took effect (noon Asia/Shanghai), with the
amendment as the commit author. It follows the shared design of lexifina/global-law, which places it at `cn/`.

| In force | Commit author | What |
| --- | --- | --- |
""" + '\n'.join(f'| {v["day"]} | {v["author"][0]} | ' + (
        'the text as adopted' if v['kind'] == 'enactment' else
        f'amendment articles {v["articles"][0]}-{v["articles"][-1]}, {len(v["touched"])} provisions' if v['kind'] == 'amendment'
        else 'labelled typographic differences of the official 2018 text (credited to no act)') + ' |' for v in law) + f"""

## The questions

| Question | Command |
| --- | --- |
| What did 第十一条 say on 1 January 2000? | `python tools/on_date.py 2000-01-01 xianfa 11` |
| What did the preamble say before the 2018 amendment? | `python tools/on_date.py 2018-03-10 xianfa xuyan` |
| Which chapters and sections were there in 2003? | `python tools/on_date.py 2003-01-01 xianfa mulu` |
| Which amendments changed 第十一条? | `git log --follow --format=%an%x09%(trailers:key=In-force,valueonly) -- xianfa/art-011.md` |
| Which amendment wrote each line of 第十三条? | `git blame --line-porcelain main -- xianfa/art-013.md` |
| What did the 2004 amendment change? | `git show --stat xianfa/2004-03-14` |
| What changed between 1982 and 2018 in 第七十九条? | `git diff xianfa/1982-12-04 xianfa/2018-03-11 -- xianfa/art-079.md` |
| Which provisions did the 1993 amendment touch? | `git log -1 --format=%(trailers:key=Affecting,valueonly) xianfa/1993-03-29` |
| Every version and its day | `git tag --list xianfa/*` |

## The dates

Each commit's `In-force:` trailer is the day the change took effect: every amendment was adopted by the National
People's Congress and promulgated by its announcement (公告) on the same day, in force from promulgation (公布施行).
Commit dates are noon Asia/Shanghai on that day. `Adopted:` and `Promulgated:` trailers give the other dates.

## Reading it

- `xianfa/xuyan.md` is the preamble (序言), `xianfa/art-001.md` ... `xianfa/art-143.md` the articles (第一条 ...),
  `xianfa/mulu.md` the chapter and section headings (目录). One paragraph (款, or list item 项) per line.
- `python tools/on_date.py 2000-01-01 xianfa 11` prints 第十一条 as in force on that day; without the number it
  prints the whole text. Each commit has an `In-force:` trailer, which is the date to trust.
- `git log --follow xianfa/art-011.md` lists the amendments that changed an article; `git blame` names the
  amendment behind each line. Tags `xianfa/<day>` mark each version.
- Article numbers are those in force at the time: the 2018 amendment inserted 第一百二十三条 to 第一百二十七条
  (监察委员会) and moved the old 第一百二十三条 to 第一百三十八条 up by five. Git shows these as renames.
- After a rebuild, run `git fetch --force --tags`: a plain fetch keeps stale tags.

## How it was made

The source is 中国人大网 (www.npc.gov.cn), the website of the General Office of the NPC Standing Committee: the 1982
text, the five amendments and the 2018 consolidated text, all in its section 宪法、基本法和相关法律 > 宪法. The first
commit is the 1982 text. Each later commit applies one amendment (宪法修正案) to the text before it, using the words the
amendment itself quotes ("宪法第十条第四款“……”修改为：“……”"); the operations are listed in `tools/text.py`
(OPS). The 1982 version and the final version are checked word for word against the official pages; the versions in
between have no official consolidated text on the source, and are the amendment applied. After the 2018 amendment the
text differs from the official 2018 text in two characters; that difference is its own commit, authored by the
publisher, credited to no amendment and dated 2018-03-21, the day the official consolidated text was published.

The National Laws Database (flk.npc.gov.cn) was not used: its robots.txt disallows all crawlers and says
"禁止使用任何自动化工具、脚本、爬虫程序采集或复制网站数据".

Full detail, every command and the hashes are in [REPRODUCE.md](REPRODUCE.md). This is not legal advice; the
official text is the one the NPC publishes.
"""

    license_ = """Legal text

Laws, regulations, resolutions, decisions and orders of state organs and their official translations are not
protected by copyright in the People's Republic of China (中华人民共和国著作权法第五条). The texts here come from
中国人大网 (www.npc.gov.cn). Source: 中国人大网, https://www.npc.gov.cn/.

The 中国人大网 site publishes no reuse terms for this section that we could find; this repository stays private
until reuse is confirmed.

Tools and documentation

The scripts in tools/ and the documentation are by Lexifina, MIT licence:

Copyright (c) 2026 Lexifina

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

    page_rows = '\n'.join(f'| {p["key"]} | {p["url"]} | {p["retrieved"]} | `{p["sha256"][:16]}` |' for p in pages)
    tool_rows = '\n'.join(f'| tools/{t} | `{blob(HERE / t)}` |' for t in TOOLS)
    reproduce = f"""# REPRODUCE

How this repository was made, so that anyone can make it again, hash for hash.

## Sources

中国人大网 (www.npc.gov.cn), section 宪法、基本法和相关法律 > 宪法
(http://{sources.HOST}{sources.BASE}index.html). {len(pages)} pages, one request each (one keep-alive HTTP connection,
`Accept-Encoding: gzip`), cached gzip-compressed under the builder's `cache/` folder:

| Key | URL | Retrieved | sha256 of the page |
| --- | --- | --- | --- |
{page_rows}

- `1982`: 中华人民共和国宪法（1982年）, the text as adopted.
- `a1988` ... `a2018`: 中华人民共和国宪法修正案, the five amendments (articles 1-52 of the amendments).
- `2018`: 中华人民共和国宪法（2018年3月11日修正）, the consolidated text (a reprint of the Xinhua release of
  21 March 2018).

Terms checked first: www.npc.gov.cn/robots.txt disallows only YisouSpider. Laws are not protected by copyright
(著作权法第五条). flk.npc.gov.cn (国家法律法规数据库) was not used: its robots.txt has `Disallow: /` for every
agent and the comment "禁止使用任何自动化工具、脚本、爬虫程序采集或复制网站数据".

## Commands

From the lexifina repository (builder in `scripts/china-law/`; copies are in `tools/` here):

```
python -X utf8 scripts/china-law/sources.py                       # fetch the pages into the cache
python -X utf8 scripts/china-law/build.py --repo ../china-law --offline
python -X utf8 scripts/china-law/check_repo.py ../china-law       # word-for-word checks
python -X utf8 scripts/china-law/build.py --offline --verify-rebuild --repo ../china-law
python -X utf8 scripts/china-law/test_repo.py ../china-law
python -X utf8 scripts/test_corpus.py ../china-law tools/on_date.py
```

`build.py` refuses a non-empty target folder. It writes the whole history with one `git fast-import`. Commit and
author dates are noon Asia/Shanghai on the in-force day (UTC+8; China's 1986-1991 summer time is coded but no
version falls in it); the documentation commit is dated the retrieval day of the data ({day}).

## Tools

{platform.python_implementation()} {platform.python_version()}; {tool_version(['git', '--version'])}. Standard library only.

| File | git blob |
| --- | --- |
{tool_rows}

## Method and decisions made by hand

- Parsing: the text blocks (`div`/`p`) of each page's article body; white space at both ends removed; the table of
  contents (目录) skipped; chapter and section headings kept with the white space inside the title removed
  ("总　纲" → "总纲").
- Each amendment article is applied by the operation in `tools/text.py` OPS, which names the provision and the kind of
  change; the words come from the amendment page (its n-th “…” quotation). In a quotation the Constitution's own
  double quotation marks are printed as ‘…’; they are turned back into “…”.
- Paragraph numbers in OPS count 款 as lines; where a 款 holds a list (第六十五条, 第一百二十四条) the change is
  matched by its quoted words instead.
- An inserted list item (2018 amendment articles 41, 42, 44) takes the list separator "；" that its neighbours carry:
  the amendment quotes the item without list punctuation. The item quotation's own label "(二十)"/"（六）" is not
  copied; the item keeps its label in the text. Later items are renumbered as the amendment says.
- 2018 amendment article 44 has a second paragraph, which changes 第七十条; it is applied as part of article 44.
- 2018 amendment article 52 inserts 第七节 监察委员会 with 第一百二十三条 to 第一百二十七条 and renumbers the old
  第七节 and 第一百二十三条 to 第一百三十八条; the files move to the new numbers.
- Where the text the amendments produce differs from the official 2018 text, the difference is a separate commit,
  dated the day that text was published (新华社, 2018-03-21; In-force set to that day, Words-changed: no),
  authored by the publisher, `Kind: editorial`, credited to no amendment: "〇" (U+3007) in 序言 is printed "○"
  (U+25CB) in the 2018 page, and the 2018 amendment page prints a half-width colon in 第一百二十四条.
- Every amendment was adopted and promulgated on the same day (公布施行), which is the in-force day.

## Checks

- `check_repo.py`: the 1982 version and the final version equal the official pages byte for byte after rendering,
  and an independent word stream (letters and digits of the raw page body, by a separate minimal extractor) equals the
  repository's text; every quotation of a new text in each amendment is present in that version's files.
- Rebuild: {rebuild}.
- `test_repo.py` and `scripts/test_corpus.py`.

## AI

Built by Claude Code with Claude Opus 5.5 (`claude-opus-5-5`), which researched the source, wrote the scripts and the
documentation. No AI wrote or edited legal text, and no model runs at build time: every word of law comes from the
official pages, moved by the code above.
"""

    files = {
        'README.md': readme,
        'REPRODUCE.md': reproduce,
        'LICENSE': license_,
        'corpus.json': corpus_json,
        'data/versions.json': versions_json,
        'xianfa/README.md': act_readme,
    }
    for t in TOOLS:
        files['tools/' + t] = (HERE / t).read_text(encoding='utf-8').replace('\r\n', '\n')
    msg = ('Documentation, tables, tools and REPRODUCE.md\n\n'
           'README, REPRODUCE.md, LICENSE, corpus.json, data/versions.json, xianfa/README.md and the build tools.\n')
    return files, msg
