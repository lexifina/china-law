# REPRODUCE

How this repository was made, so that anyone can make it again, hash for hash.

## Sources

中国人大网 (www.npc.gov.cn), section 宪法、基本法和相关法律 > 宪法
(http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/index.html). 8 pages, one request each (one keep-alive HTTP connection,
`Accept-Encoding: gzip`), cached gzip-compressed under the builder's `cache/` folder:

| Key | URL | Retrieved | sha256 of the page |
| --- | --- | --- | --- |
| index | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/index.html | 2026-10-28 | `5c2ef02ba2d36223` |
| 1982 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241028_440219.html | 2026-10-28 | `beddada5a0adc450` |
| a1988 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241017_440090.html | 2026-10-28 | `44d345913759813d` |
| a1993 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241017_440089.html | 2026-10-28 | `ce571f0dc50bf6ec` |
| a1999 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241017_440088.html | 2026-10-28 | `fd0fa87b3c31ef12` |
| a2004 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241017_440087.html | 2026-10-28 | `d30f48313e197c67` |
| a2018 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202410/t20241028_440233.html | 2026-10-28 | `74211eb6c0fb472c` |
| 2018 | http://www.npc.gov.cn/npc/c34354/xgjbfwyh/xgjbfwyh002/xgjbfwyh003/202409/t20240905_439070.html | 2026-10-28 | `7eea2f6360fb3b66` |

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
version falls in it); the documentation commit is dated the retrieval day of the data (2026-10-28).

## Tools

CPython 3.12.10; git version 2.46.0.windows.1. Standard library only.

| File | git blob |
| --- | --- |
| tools/build.py | `0c4c7c7d4f19b50e361450abfe13b03242d7c3b4` |
| tools/text.py | `6f0c9b289d3941aac1700be8d9507e79124d2841` |
| tools/sources.py | `aaa77708a0c939cf3431f9bccf18fa57ad9aabce` |
| tools/reproduce.py | `f5bba21d1ca6c408b25447428edd14badcb23920` |
| tools/check_repo.py | `74d34871b3a45c5a0fd85bf2172f5dea8da3b3d9` |
| tools/test_repo.py | `3ed1c70181731cf5423456362aaf50cb58461c61` |
| tools/on_date.py | `70f9246eec6eb5fbbd3f9e556ef226e77b6105c2` |

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
- Rebuild: identical: two builds from the cache gave the same head hash.
- `test_repo.py` and `scripts/test_corpus.py`.

## AI

Built by Claude Code with Claude Opus 5.5 (`claude-opus-5-5`), which researched the source, wrote the scripts and the
documentation. No AI wrote or edited legal text, and no model runs at build time: every word of law comes from the
official pages, moved by the code above.
