"""Reads the official pages of 中国人大网 into a structure, and applies the five constitutional amendments.

A text is {'pre': [paragraphs of 序言], 'art': {number: [paragraphs]}, 'heads': [(label, title, first article)]}.
Every word of legal text comes from an official page: the 1982 text, an amendment's quoted words, or the 2018 text.
The table OPS says, for each amendment article, which provision it changes and how; the quoted words are read from
the amendment page by position (Q0 is the first “…” quotation of that amendment article, Q1 the second, ...).
"""
from __future__ import annotations

import html
import re

import sources

WS = ' 　\xa0  \t\r\n'
DIG = {'零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
NUM = '零〇一二三四五六七八九十百'


def cn_int(s: str) -> int:
    """一百零三 -> 103, 二十 -> 20, 十一 -> 11."""
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
        else:
            raise ValueError(s)
    return total + cur


def int_cn(n: int) -> str:
    """103 -> 一百零三, 20 -> 二十, 11 -> 十一 (the form the Constitution uses)."""
    d = '零一二三四五六七八九'
    if n < 10:
        return d[n]
    if n < 20:
        return '十' + (d[n % 10] if n % 10 else '')
    if n < 100:
        return d[n // 10] + '十' + (d[n % 10] if n % 10 else '')
    h, r = divmod(n, 100)
    if r == 0:
        return d[h] + '百'
    if r < 10:
        return d[h] + '百零' + d[r]
    return d[h] + '百' + d[r // 10] + '十' + (d[r % 10] if r % 10 else '')


def blocks(key: str, offline: bool = False) -> list[str]:
    """The text blocks (div/p) of a page's article body, tags removed, outer white space stripped."""
    status, raw = sources.fetch(key, offline)
    if status != 200:
        raise RuntimeError(f'{key}: HTTP {status}')
    b = raw.decode('utf-8')
    z = b[b.index('<div id="Zoom">'):b.index('<div class="editor">')]
    z = re.sub(r'<style.*?</style>', '', z, flags=re.S)
    z = re.sub(r'<(div|p|br)\b[^>]*>', '\x00', z, flags=re.I)
    z = html.unescape(re.sub(r'<[^>]+>', '', z))
    return [x.strip(WS) for x in z.split('\x00') if x.strip(WS)]


def page_head(key: str, offline: bool = False) -> str:
    """The <h3> line under the title: adoption and promulgation."""
    b = sources.fetch(key, offline)[1].decode('utf-8')
    m = re.search(r'<h3>(.*?)</h3>', b, re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip(WS) if m else ''


HEAD_RE = re.compile(r'(第[' + NUM + r']+[章节])[' + WS + r']*(.+)')
ART_RE = re.compile(r'第([' + NUM + r']+)条[' + WS + r']+(.*)')
ITEM_RE = re.compile(r'[（(]([' + NUM + r']+)[）)]')


def norm_title(t: str) -> str:
    return re.sub('[' + WS + ']', '', t)


def parse_text(key: str, offline: bool = False) -> dict:
    """Parses a full text of the Constitution (the 1982 page or the 2018 page)."""
    bl = blocks(key, offline)
    # The body starts at the second 序言 heading (the first is in the table of contents, 目录).
    pre_idx = [i for i, x in enumerate(bl) if norm_title(x) == '序言']
    if len(pre_idx) != 2:
        raise RuntimeError(f'{key}: expected 序言 twice, found {len(pre_idx)}')
    body = bl[pre_idx[1] + 1:]
    t = {'pre': [], 'art': {}, 'heads': []}
    cur = t['pre']
    pending = []
    for x in body:
        if not norm_title(x):
            continue
        m = HEAD_RE.fullmatch(x)
        if m and len(x) < 40 and not x.endswith('。'):
            pending.append((m.group(1), norm_title(m.group(2))))
            continue
        m = ART_RE.fullmatch(x)
        if m:
            n = cn_int(m.group(1))
            if n in t['art'] or (t['art'] and n != max(t['art']) + 1):
                raise RuntimeError(f'{key}: article {n} out of order')
            cur = t['art'][n] = []
            for label, title in pending:
                t['heads'].append((label, title, n))
            pending = []
            x = m.group(2)
        elif pending:
            raise RuntimeError(f'{key}: heading not followed by an article: {pending}')
        cur.append(x)
    return t


# ---------------------------------------------------------------- amendments

AMENDMENTS = [
    # key, year, the articles of the amendments (修正案) it contains
    ('a1988', 1988, range(1, 3)),
    ('a1993', 1993, range(3, 12)),
    ('a1999', 1999, range(12, 18)),
    ('a2004', 2004, range(18, 32)),
    ('a2018', 2018, range(32, 53)),
]


def amendment_articles(key: str, offline: bool = False) -> tuple[dict, list[str]]:
    """{number: text} of each amendment article; plus, for 2018, the blocks that follow 内容如下 in article 52."""
    out, extra, cur = {}, [], None
    for x in blocks(key, offline):
        m = ART_RE.fullmatch(x)
        if m and cur != 52:
            cur = cn_int(m.group(1))
            out[cur] = m.group(2)
        elif cur is not None and cur != 52:
            out[cur] += '\n' + x            # 2018 art. 44 has a second paragraph (art. 70)
        elif cur == 52:
            extra.append(x)
        else:
            raise RuntimeError(f'{key}: text before the first article: {x[:30]}')
    return out, extra


def quotes(s: str) -> list[str]:
    """The top-level “…” quotations of an amendment article, in order, with inner ‘…’ turned into “…”: in a quotation
    the Constitution's own double quotation marks are printed as single ones."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch == '“':
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == '”':
            depth -= 1
            if depth == 0:
                out.append(s[start:i].replace('‘', '“').replace('’', '”'))
    if depth:
        raise RuntimeError('unbalanced quotation: ' + s[:40])
    return out


# OPS[amendment article] = list of operations. Q(n) is the n-th quotation of that article, Q(-1) the last.
# Targets: 'pre' (序言) with a 1-based paragraph (自然段) number, or an article number with a 1-based paragraph (款).
#   ('paras', target, [old...], [new...])     consecutive paragraphs [old...] are replaced by [new...]
#   ('para', target, k, old, new)             paragraph k, which must equal old, becomes new
#   ('sub', target, k, old, new)              inside paragraph k, the words old become new
#   ('append', target, k, words)              words are added at the end of paragraph k
#   ('insert', target, k, words)              a new paragraph is inserted as paragraph k
#   ('item_sub', art, label, old, new)        in the item labelled （label）, the words old become new
#   ('item_insert', art, label, words)        an item is inserted as （label）; later items are renumbered
#   ('whole', target, k, new, [(old, new)...]) paragraph k is replaced by the text the amendment gives
#                                             (这一自然段相应地修改为); each (old, new) pair is checked, not applied
#   ('heading', old, new)                     a chapter title
#   ('section_insert', ...)                   2018 art. 52: a new section 7 with articles 123-127
class Q(int):
    pass


OPS = {
    1: [('insert', 11, 3, Q(0))],
    2: [('para', 10, 4, Q(0), Q(1))],
    3: [('sub', 'pre', 7, Q(0), Q(1))],
    4: [('append', 'pre', 10, Q(0))],
    5: [('paras', 7, [Q(0)], [Q(1)])],
    6: [('para', 8, 1, Q(0), Q(1))],
    7: [('paras', 15, [Q(0), Q(1)], [Q(2), Q(3), Q(4)])],
    8: [('paras', 16, [Q(0), Q(1)], [Q(2), Q(3)])],
    9: [('paras', 17, [Q(0), Q(1)], [Q(2), Q(3)])],
    10: [('para', 42, 3, Q(0), Q(1))],
    11: [('paras', 98, [Q(0)], [Q(1)])],
    12: [('para', 'pre', 7, Q(0), Q(1))],
    13: [('insert', 5, 1, Q(0))],
    14: [('paras', 6, [Q(0), Q(1)], [Q(2), Q(3)])],
    15: [('para', 8, 1, Q(0), Q(1))],
    16: [('paras', 11, [Q(0), Q(1), Q(2)], [Q(3), Q(4)])],
    17: [('paras', 28, [Q(0)], [Q(1)])],
    18: [('whole', 'pre', 7, Q(-1), [(Q(0), Q(1)), (Q(2), Q(3))])],
    19: [('sub', 'pre', 10, Q(0), Q(1))],
    20: [('para', 10, 3, Q(0), Q(1))],
    21: [('para', 11, 2, Q(0), Q(1))],
    22: [('paras', 13, [Q(0), Q(1)], [Q(2), Q(3), Q(4)])],
    23: [('insert', 14, 4, Q(0))],
    24: [('insert', 33, 3, Q(0))],
    25: [('para', 59, 1, Q(0), Q(1))],
    26: [('item_sub', 67, '二十', Q(0), Q(1))],
    27: [('paras', 80, [Q(0)], [Q(1)])],
    28: [('paras', 81, [Q(0)], [Q(1)])],
    29: [('item_sub', 89, '十六', Q(0), Q(1))],
    30: [('paras', 98, [Q(0)], [Q(1)])],
    31: [('heading', Q(0), Q(1)), ('insert', 136, 2, Q(2))],
    32: [('whole', 'pre', 7, Q(-1), [(Q(0), Q(1)), (Q(2), Q(3)), (Q(6), Q(7))])],
    33: [('whole', 'pre', 10, Q(-1), [(Q(0), Q(1)), (Q(2), Q(3))])],
    34: [('sub', 'pre', 11, Q(0), Q(1))],
    35: [('whole', 'pre', 12, Q(-1), [(Q(0), Q(1)), (Q(4), Q(5))])],
    36: [('append_after', 1, 2, Q(0), Q(1))],
    37: [('para', 3, 3, Q(0), Q(1))],
    38: [('sub', 4, 1, Q(0), Q(1))],
    39: [('whole', 24, 2, Q(-1), [(Q(0), Q(1))])],
    40: [('insert', 27, 3, Q(0))],
    41: [('item_insert', 62, '七', Q(1))],
    42: [('item_insert', 63, '四', Q(1))],
    43: [('paras', 65, [Q(0)], [Q(1)])],
    44: [('item_sub', 67, '六', Q(1), Q(2)), ('item_insert', 67, '十一', Q(3)), ('sub', 70, 1, Q(4), Q(5))],
    45: [('para', 79, 3, Q(0), Q(1))],
    46: [('item_sub', 89, '六', Q(1), Q(2)), ('item_sub', 89, '八', Q(3), Q(4))],
    47: [('insert', 100, 2, Q(0))],
    48: [('sub', 101, 2, Q(0), Q(1))],
    49: [('para', 103, 3, Q(0), Q(1))],
    50: [('whole', 104, 1, Q(-1), [(Q(0), Q(1))])],
    51: [('para', 107, 1, Q(0), Q(1))],
    52: [('section_insert',)],
}

# Hand decisions, applied by code and listed in REPRODUCE.md:
# - an inserted list item (2018 arts. 41, 42, 44) ends with the separator "；" that the neighbouring items carry,
#   because the amendment quotes the item without its list punctuation;
# - an item quotation's own label "(二十)" or "（六）" is dropped and the item keeps its label in the text;
# - 2018 art. 52's renumbering (第七节相应改为第八节, 第一百二十三条至第一百三十八条相应改为第一百二十八条至第一百四十三条)
#   moves the articles' text to the new numbers.


def _q(qs: list[str], v):
    if isinstance(v, Q):
        return qs[int(v)]
    if isinstance(v, list):
        return [_q(qs, x) for x in v]
    if isinstance(v, tuple):
        return tuple(_q(qs, x) for x in v)
    return v


def _paras(t: dict, target) -> list[str]:
    return t['pre'] if target == 'pre' else t['art'][target]


def _item_label(p: str) -> str | None:
    m = ITEM_RE.match(p)
    return m.group(1) if m else None


def _strip_label(s: str) -> str:
    m = ITEM_RE.match(s)
    return s[m.end():] if m else s


class ApplyError(Exception):
    pass


def apply_article(t: dict, n: int, text: str, extra: list[str]) -> list:
    """Applies amendment article n to t in place. Returns the provisions it touched: 'pre', article numbers, 'heads'."""
    qs = quotes(text)
    touched = []
    for op in OPS[n]:
        kind = op[0]
        args = [_q(qs, a) for a in op[1:]]
        if kind == 'paras':
            target, old, new = args
            ps = _paras(t, target)
            for i in range(len(ps) - len(old) + 1):
                if ps[i:i + len(old)] == old:
                    ps[i:i + len(old)] = new
                    break
            else:
                raise ApplyError(f'{n}: paragraphs not found in {target}')
            touched.append(target)
        elif kind == 'para':
            target, k, old, new = args
            ps = _paras(t, target)
            if ps[k - 1] != old:
                raise ApplyError(f'{n}: {target} para {k} differs from the quoted words')
            ps[k - 1] = new
            touched.append(target)
        elif kind == 'sub':
            target, k, old, new = args
            ps = _paras(t, target)
            if ps[k - 1].count(old) != 1:
                raise ApplyError(f'{n}: {target} para {k}: quoted words found {ps[k - 1].count(old)} times')
            ps[k - 1] = ps[k - 1].replace(old, new)
            touched.append(target)
        elif kind == 'append':
            target, k, words = args
            ps = _paras(t, target)
            ps[k - 1] = ps[k - 1] + words
            touched.append(target)
        elif kind == 'append_after':
            target, k, anchor, words = args
            ps = _paras(t, target)
            if ps[k - 1].count(anchor) != 1:
                raise ApplyError(f'{n}: anchor not found once')
            ps[k - 1] = ps[k - 1].replace(anchor, anchor + words)
            touched.append(target)
        elif kind == 'insert':
            target, k, words = args
            ps = _paras(t, target)
            if k - 1 > len(ps):
                raise ApplyError(f'{n}: {target} has no paragraph {k - 1}')
            ps.insert(k - 1, words)
            touched.append(target)
        elif kind == 'whole':
            target, k, new, pairs = args
            ps = _paras(t, target)
            for old_w, new_w in pairs:
                if old_w not in ps[k - 1] or new_w not in new:
                    raise ApplyError(f'{n}: check pair not found: {old_w[:20]} / {new_w[:20]}')
            ps[k - 1] = new
            touched.append(target)
        elif kind == 'item_sub':
            art, label, old, new = args
            ps = t['art'][art]
            old, new = _strip_label(old), _strip_label(new)
            hits = [i for i, p in enumerate(ps) if _item_label(p) == label]
            if len(hits) != 1 or ps[hits[0]].count(old) != 1:
                raise ApplyError(f'{n}: item {label} of art. {art} not found with the quoted words')
            ps[hits[0]] = ps[hits[0]].replace(old, new)
            touched.append(art)
        elif kind == 'item_insert':
            art, label, words = args
            ps = t['art'][art]
            want = cn_int(label)
            if _item_label(words) != label:
                raise ApplyError(f'{n}: inserted item is not labelled {label}')
            hits = [i for i, p in enumerate(ps) if _item_label(p) == int_cn(want - 1)]
            if len(hits) != 1:
                raise ApplyError(f'{n}: no item {want - 1} in art. {art}')
            at = hits[0] + 1
            sep = ps[hits[0]][-1]
            if sep != '；':
                raise ApplyError(f'{n}: item before the insertion does not end with ；')
            # renumber the later items of this list
            i = at
            while i < len(ps) and _item_label(ps[i]):
                m = ITEM_RE.match(ps[i])
                ps[i] = ps[i][:m.start(1)] + int_cn(cn_int(m.group(1)) + 1) + ps[i][m.end(1):]
                i += 1
            ps.insert(at, words + sep)
            touched.append(art)
        elif kind == 'heading':
            old, new = args
            hits = [i for i, h in enumerate(t['heads']) if h[1] == old]
            if len(hits) != 1:
                raise ApplyError(f'{n}: heading {old} not found')
            h = t['heads'][hits[0]]
            t['heads'][hits[0]] = (h[0], new, h[2])
            touched.append('heads')
        elif kind == 'section_insert':
            touched += _section_insert(t, n, text, extra)
        else:
            raise ApplyError(kind)
    return touched


def _section_insert(t: dict, n: int, text: str, extra: list[str]) -> list:
    """2018 art. 52: a new 第七节 监察委员会 with 第一百二十三条 to 第一百二十七条; the old 第七节 becomes 第八节 and
    the old 第一百二十三条 to 第一百三十八条 become 第一百二十八条 to 第一百四十三条."""
    if not ('增加一节，作为第七节“监察委员会”' in text and '分别作为第一百二十三条至第一百二十七条' in text):
        raise ApplyError('52: wording changed')
    if not extra or not extra[-1].startswith('第七节相应改为第八节，第一百二十三条至第一百三十八条相应改为第一百二十八条至第一百四十三条'):
        raise ApplyError('52: renumbering sentence not found')
    head = HEAD_RE.fullmatch(extra[0])
    if not head or head.group(1) != '第七节' or norm_title(head.group(2)) != '监察委员会':
        raise ApplyError('52: section heading not found')
    new_arts, cur = {}, None
    for x in extra[1:-1]:
        m = ART_RE.fullmatch(x)
        if m:
            cur = cn_int(m.group(1))
            new_arts[cur] = [m.group(2)]
        else:
            new_arts[cur].append(x)
    if sorted(new_arts) != list(range(123, 128)) or max(t['art']) != 138:
        raise ApplyError('52: unexpected numbering')
    arts = t['art']
    moved = {k + 5: arts.pop(k) for k in range(123, 139)}
    arts.update(new_arts)
    arts.update(moved)
    t['art'] = dict(sorted(arts.items()))
    heads = []
    for label, title, first in t['heads']:
        if label == '第七节':
            heads.append(('第七节', '监察委员会', 123))
            label = '第八节'
        if first >= 123:
            first += 5
        heads.append((label, title, first))
    t['heads'] = heads
    return list(range(123, 144)) + ['heads']
