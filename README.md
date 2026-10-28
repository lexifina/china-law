# China: law history

The Constitution of the People's Republic of China (中华人民共和国宪法) as a git history: one file per provision,
one commit per amendment, each dated the day it was promulgated and took effect (noon Asia/Shanghai), with the
amendment as the commit author. It follows the shared design of lexifina/global-law, which places it at `cn/`.

| In force | Commit author | What |
| --- | --- | --- |
| 1982-12-04 | 中华人民共和国宪法（1982年） | the text as adopted |
| 1988-04-12 | 宪法修正案（1988年） | amendment articles 1-2, 2 provisions |
| 1993-03-29 | 宪法修正案（1993年） | amendment articles 3-11, 8 provisions |
| 1999-03-15 | 宪法修正案（1999年） | amendment articles 12-17, 6 provisions |
| 2004-03-14 | 宪法修正案（2004年） | amendment articles 18-31, 14 provisions |
| 2018-03-11 | 宪法修正案（2018年） | amendment articles 32-52, 40 provisions |
| 2018-03-21 | 中国人大网 (全国人大常委会办公厅) | labelled typographic differences of the official 2018 text (credited to no act) |

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
