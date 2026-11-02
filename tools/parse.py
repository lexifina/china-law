"""Parses a full text of a Chinese law, as 中国人大网 (www.npc.gov.cn) publishes it, into provision files.

A text is: an optional 主席令 block, the adoption line (（……通过……）), an optional 目录 (table of contents), then the
body: headings (第X编 / 第X分编 / 第X章 / 第X节) and articles (第X条, 第X条之一 ...), one paragraph per block.
Units: `mulu` (the headings of the body, in order) and one unit per article, `art-NNN` or `art-NNN-K` for 之K.
No network: callers pass the page's text blocks (fetchpage.blocks).
"""
from __future__ import annotations

import re

WS = ' 　\xa0   \t\r\n'
NUM = '零〇一二三四五六七八九十百千'
DIG = {'零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
HEAD_RE = re.compile(r'(第[' + NUM + r']+(?:分编|编|章|节))[' + WS + r']*(.*)')
ART_RE = re.compile(r'第([' + NUM + r']+)[' + WS + r']*条(?:之([' + NUM + r']+))?[' + WS + r']*(.*)', re.S)


_FW = {0xFF10 + i: 0x30 + i for i in range(10)}


def FW_DIGITS(s: str) -> str:
    """Full-width digits (１９９７) as ASCII digits (1997), the form the current NPC texts use."""
    return s.translate(_FW)


class ParseError(RuntimeError):
    pass


def cn_int(s: str) -> int:
    """一千二百六十 -> 1260, 一百零三 -> 103, 十一 -> 11."""
    total, cur = 0, 0
    for ch in s:
        if ch in DIG:
            cur = DIG[ch]
        elif ch == '十':
            total += (cur or 1) * 10
            cur = 0
        elif ch == '百':
            total += cur * 100
            cur = 0
        elif ch == '千':
            total += cur * 1000
            cur = 0
        else:
            raise ValueError(s)
    return total + cur


def int_cn(n: int) -> str:
    """1260 -> 一千二百六十, 1003 -> 一千零三, 103 -> 一百零三, 11 -> 十一 (the form the NPC texts use)."""
    d = '零一二三四五六七八九'
    if n < 10:
        return d[n]
    if n < 20:
        return '十' + (d[n % 10] if n % 10 else '')
    if n < 100:
        return d[n // 10] + '十' + (d[n % 10] if n % 10 else '')
    if n < 1000:
        h, r = divmod(n, 100)
        if r == 0:
            return d[h] + '百'
        if r < 10:
            return d[h] + '百零' + d[r]
        return d[h] + '百' + (d[r // 10] + '十' if r >= 10 else '') + (d[r % 10] if r % 10 else '')
    k, r = divmod(n, 1000)
    if r == 0:
        return d[k] + '千'
    if r < 100:
        return d[k] + '千零' + (int_cn(r) if r >= 20 or r < 10 else '一' + int_cn(r))
    return d[k] + '千' + int_cn(r)


def squash(s: str) -> str:
    return re.sub('[' + WS + ']', '', s)


ANNEX_RE = re.compile(r'附件([一二三四五六七八九十]+)')
BARE_HEAD = re.compile(r'(附[' + WS + r']*则)')


def is_heading(x: str) -> re.Match | None:
    m = HEAD_RE.fullmatch(x)
    if not m and BARE_HEAD.fullmatch(x):
        return re.fullmatch(r'()(.*)', x, re.S)
    if m and len(x) <= 60 and not x.endswith(('。', '：', '；', '，')) and not re.match(r'第[' + NUM + r']+条', m.group(2)):
        return m
    return None


def label(n: int, k: int = 0) -> str:
    return f'第{int_cn(n)}条' + (f'之{int_cn(k)}' if k else '')


def parse(blocks: list[str], width: int = 3, h3: str = '') -> dict:
    """{'head': adoption line, 'units': {key: text}, 'headings': [(label, title)]}. The adoption line is the body's
    （……通过……） block, or else the page's <h3> line (h3), and the text starts at the body's first block."""
    blocks = [FW_DIGITS(x) for x in blocks]
    # An adoption line split over several blocks (（……通过，| ……修订）) is joined first.
    for i, x in enumerate(blocks[:60]):
        if x.startswith('（') and '通过' in x and '）' not in x:
            j = next((j for j in range(i + 1, min(i + 8, len(blocks))) if blocks[j].endswith('）')), None)
            if j is not None:
                blocks = blocks[:i] + [''.join(blocks[i:j + 1])] + blocks[j + 1:]
            break
    hi = next((i for i, x in enumerate(blocks[:60]) if x.startswith('（') and x.endswith('）') and '通过' in x), None)
    if hi is None:
        if not (h3.startswith('（') and '通过' in h3):
            raise ParseError('no adoption line')
        head, rest = h3, blocks
    else:
        head, rest = blocks[hi], blocks[hi + 1:]
    i = 0
    toc = []
    if rest and squash(rest[0]) == '目录':
        i = 1
        while i < len(rest):
            m = is_heading(rest[i])
            if not m:
                break
            if toc and squash(rest[i]) == squash(toc[0]):
                break        # the body's first heading repeats the table of contents' first entry
            toc.append(rest[i])
            i += 1
    heads: list[tuple[str, str]] = []
    arts: dict[tuple[int, int], list[str]] = {}
    annex: dict[int, list[str]] = {}
    cur = None
    prev = (0, 0)
    body = rest[i:]
    j = 0
    while j < len(body):
        x = body[j]
        j += 1
        m = is_heading(x)
        if m:
            title = squash(m.group(2))
            # A body heading broken over two blocks: the table of contents gives the whole heading.
            want = squash(toc[len(heads)]) if len(heads) < len(toc) else None
            while want and squash(x) != want and want.startswith(squash(x)) and j < len(body) \
                    and want.startswith(squash(x + body[j])):
                x += body[j]
                j += 1
                title = squash(HEAD_RE.fullmatch(x).group(2)) if HEAD_RE.fullmatch(x) else squash(x)
            heads.append((m.group(1), title))
            continue
        a = ART_RE.fullmatch(x)
        if a:
            n, k = cn_int(a.group(1)), cn_int(a.group(2)) if a.group(2) else 0
            ok = (k == 0 and n == prev[0] + 1) or (k and n == prev[0] and k == prev[1] + 1)
            if ok:
                cur = arts[(n, k)] = [a.group(3).strip(WS)]
                prev = (n, k)
                continue
            raise ParseError(f'article {label(n, k)} out of sequence after {label(*prev)}')
        fm = ANNEX_RE.fullmatch(x)
        if fm and arts:
            n = cn_int(fm.group(1))
            if n != len(annex) + 1:
                raise ParseError(f'annex {x} out of sequence')
            cur = annex[n] = []
            continue
        if cur is None:
            raise ParseError(f'text before the first article: {x[:40]}')
        cur.append(x)
    if not arts:
        raise ParseError('no articles')
    if toc and [squash(t) for t in toc] != [squash(f'{a}{b}') for a, b in heads]:
        raise ParseError('the table of contents differs from the body headings')
    units = {}
    if heads:
        units['mulu'] = '# 目录\n\n' + '\n\n'.join(f'{a}　{b}' if a else b for a, b in heads) + '\n'
    for (n, k), ps in arts.items():
        key = f'art-{n:0{width}d}' + (f'-{k}' if k else '')
        units[key] = f'# {label(n, k)}\n\n' + '\n\n'.join(ps) + '\n'
    for n, ps in annex.items():
        if not ps:
            raise ParseError(f'annex {n} is empty')
        units[f'fujian-{n}'] = f'# 附件{int_cn(n)}\n\n' + '\n\n'.join(ps) + '\n'
    return {'head': head, 'units': units, 'headings': heads, 'n_articles': len(arts),
            'last_article': max(arts)}


def letters(s: str) -> str:
    return ''.join(ch for ch in s.casefold() if ch.isalnum())
