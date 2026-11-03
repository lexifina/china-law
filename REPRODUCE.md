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

<!-- acts: begin -->
## More acts

Pages of 中国人大网 (www.npc.gov.cn), retrieved up to 2026-11-03. Each page is parsed into its adoption line, the
headings of its body and its articles (`parse.py`); the letters and digits of the page body (目录 removed,
each heading removed once) must equal those of the article files, in order. Full-width digits are written
as ASCII digits (the form the current texts use); nothing else in the text is changed.

| Act | In force | Kind | Page | sha256 of the page |
| --- | --- | --- | --- | --- |
| 中华人民共和国民法典 | 2021-01-01 | law | http://www.npc.gov.cn/wxzlhgb/c27214/gb2020/202006/P020230313538731037747.pdf | `261066267a44172e` |
| 中华人民共和国刑法 | 1997-10-01 | law | http://www.npc.gov.cn/npc/c1773/c1848/c21114/c25714/c25716/201905/t20190522_46193.html | `0e4f21c8efed7af0` |
| 中华人民共和国刑法 | 1997-10-01 | correction | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 1998-12-29 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 1999-12-25 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2001-08-31 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2001-12-29 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2002-12-28 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2005-02-28 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2006-06-29 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2009-02-28 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2009-08-27 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2011-05-01 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2015-11-01 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2017-11-04 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2021-03-01 | amendment | http://www.npc.gov.cn/wxzlhgb/c27214/gb2021/202104/P020230313538043179978.pdf | `2252a75f5549dbd9` |
| 中华人民共和国刑法 | 2024-03-01 | amendment | http://www.npc.gov.cn/npc/c2/c30834/202312/t20231229_433988.html | `126a466e4e85cec5` |
| 中华人民共和国刑事诉讼法 | 1997-01-01 | oldest | http://www.npc.gov.cn/cwhhdbdh/c6626/c7487/c7528/201905/t20190523_388735.html | `2fa9963b7f641377` |
| 中华人民共和国刑事诉讼法 | 2013-01-01 | amendment | http://www.npc.gov.cn/npc/c2434/c17314/c17320/201905/t20190522_56090.html | `4b058bf37dcb7233` |
| 中华人民共和国刑事诉讼法 | 2018-10-26 | amendment | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276591.html | `96451606f0ef9cf4` |
| 中华人民共和国公司法 | 2018-10-26 | oldest | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276469.html | `c8838121a158edd9` |
| 中华人民共和国公司法 | 2024-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202312/t20231229_433999.html | `aef5ccfbae8eb958` |
| 中华人民共和国劳动合同法 | 2008-01-01 | law | http://www.npc.gov.cn/npc/c2/c183/c198/201905/t20190522_26978.html | `51b14a86fda43ecd` |
| 中华人民共和国劳动合同法 | 2013-07-01 | amendment | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190522_76069.html | `` |
| 中华人民共和国爱国主义教育法 | 2024-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202310/t20231024_432535.html | `cbc971c4b3b34a5d` |
| 中华人民共和国保守国家秘密法 | 2024-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202402/t20240227_434859.html | `8a9897d99b4323d3` |
| 中华人民共和国标准化法 | 2018-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278360.html | `4161468a8481b198` |
| 中华人民共和国兵役法 | 2021-10-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313076.html | `992b4dc82b323c7d` |
| 中华人民共和国残疾人保障法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276668.html | `ed5852a2a1b09024` |
| 中华人民共和国测绘法 | 2017-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_277996.html | `245a58fd84fb34f0` |
| 中华人民共和国长江保护法 | 2021-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202012/t20201226_309444.html | `59e0af275bb92f4b` |
| 中华人民共和国车辆购置税法 | 2019-07-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276782.html | `dc6ba2c0933c025d` |
| 中华人民共和国城市房地产管理法 | 2020-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201909/t20190905_300665.html | `76dff1f875cc1731` |
| 中华人民共和国城市居民委员会组织法 | 2026-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202510/t20251028_449063.html | `28d768ddcbcb2c31` |
| 中华人民共和国城市维护建设税法 | 2021-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202008/t20200811_307180.html | `383db479586c225d` |
| 中华人民共和国船舶吨税法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276656.html | `6d1d11ec435cf137` |
| 中华人民共和国传染病防治法 | 2025-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202504/t20250430_445085.html | `aeefcd95a025fc29` |
| 中华人民共和国出境入境管理法 | 2013-07-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190522_86959.html | `f61127cc71ee0049` |
| 中华人民共和国出口管制法 | 2020-12-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202010/t20201017_308277.html | `7e238432424a9d3e` |
| 中华人民共和国促进科技成果转化法 | 2015-10-01 | current | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_222148.html | `8d4fc33205f01861` |
| 中华人民共和国档案法 | 2021-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202006/t20200620_306637.html | `82da7cfadafe4794` |
| 中华人民共和国大气污染防治法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276620.html | `442336d1f22ee4f8` |
| 中华人民共和国电力法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296657.html | `a5bb1bcfd9088be3` |
| 中华人民共和国电影产业促进法 | 2017-03-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_274572.html | `14c3bc190b651eea` |
| 中华人民共和国电子商务法 | 2019-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281583.html | `cb907b4a1af9b218` |
| 中华人民共和国动物防疫法 | 2021-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202101/t20210122_309854.html | `a706b99859ae0866` |
| 中华人民共和国对外关系法 | 2023-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202306/t20230628_430341.html | `2782733479347c69` |
| 中华人民共和国对外贸易法 | 2026-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202512/t20251227_450709.html | `262677464808d448` |
| 中华人民共和国法律援助法 | 2022-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313079.html | `972cf1394cb958cd` |
| 中华人民共和国反不正当竞争法 | 2025-10-15 | law | http://www.npc.gov.cn/npc/c2/c30834/202506/t20250627_446247.html | `e03997d569751268` |
| 中华人民共和国反电信网络诈骗法 | 2022-12-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202209/t20220902_319186.html | `6a03ead995feb4b0` |
| 中华人民共和国防沙治沙法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276649.html | `f6d3fd5ba6a7ae28` |
| 中华人民共和国反间谍法 | 2023-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202304/t20230426_429064.html | `e0ba2b6914b59637` |
| 中华人民共和国反家庭暴力法 | 2016-03-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190521_260193.html | `b08e50b210979fa6` |
| 中华人民共和国反恐怖主义法 | 2018-04-27 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281474.html | `d1cc0967884481c0` |
| 中华人民共和国反食品浪费法 | 2021-04-29 | law | http://www.npc.gov.cn/npc/c2/c30834/202104/t20210429_311300.html | `549325988f9ffa04` |
| 中华人民共和国反外国制裁法 | 2021-06-10 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311892.html | `c02794a5ad35f169` |
| 中华人民共和国反洗钱法 | 2025-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202411/t20241108_440887.html | `95125a28cdd731cd` |
| 中华人民共和国反有组织犯罪法 | 2022-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202112/t20211224_315575.html | `76b5bc43543cc1c5` |
| 中华人民共和国法治宣传教育法 | 2025-11-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202509/t20250912_447756.html | `02827ffd752f4c62` |
| 中华人民共和国妇女权益保障法 | 2023-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202210/t20221030_320091.html | `76ca295e3d89d5fc` |
| 中华人民共和国港口法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296655.html | `3105a30c046a48a5` |
| 中华人民共和国高等教育法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296658.html | `50bd2d4f6ea547ba` |
| 中华人民共和国各级人民代表大会常务委员会监督法 | 2024-11-08 | current | http://www.npc.gov.cn/npc/c2/c30834/202412/t20241219_441639.html | `143eb1f631857241` |
| 中华人民共和国耕地占用税法 | 2019-09-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276764.html | `b82b75377cdd04c2` |
| 中华人民共和国个人信息保护法 | 2021-11-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313088.html | `23eeb747cb57b852` |
| 中华人民共和国公共图书馆法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276640.html | `e416760e382f0c0f` |
| 中华人民共和国公共文化服务保障法 | 2017-03-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_274710.html | `1125ce711c63bab4` |
| 中华人民共和国公路法 | 2017-11-05 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278501.html | `66056a334b39a91e` |
| 中华人民共和国公务员法 | 2019-06-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_273712.html | `09713dbbf8164065` |
| 中华人民共和国公证法 | 2018-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278152.html | `681394cd9865d4cd` |
| 中华人民共和国公职人员政务处分法 | 2020-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202006/t20200620_306633.html | `2ca17e7d411e00cf` |
| 中华人民共和国关税法 | 2024-12-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202404/t20240426_436843.html | `660c314a04f46d96` |
| 中华人民共和国国防动员法 | 2026-10-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202608/t20260828_457230.html | `1e3953f0d6a10dc6` |
| 中华人民共和国国防法 | 2021-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202012/t20201226_309438.html | `0533a1745527e9a0` |
| 中华人民共和国国防交通法 | 2017-01-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_270150.html | `f58075de9ba34c8f` |
| 中华人民共和国国防教育法 | 2024-09-21 | law | http://www.npc.gov.cn/npc/c2/kgfb/202409/t20240913_439623.html | `c78ab25a61648297` |
| 中华人民共和国国家安全法 | 2015-07-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190521_259980.html | `4e7bdc4a8c9efeb3` |
| 中华人民共和国国家发展规划法 | 2026-03-12 | law | http://www.npc.gov.cn/npc/c2/c30834/202603/t20260313_453202.html | `062e8ba9ae962507` |
| 中华人民共和国国家公园法 | 2026-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202509/t20250912_447755.html | `ccad8b29d82ad86f` |
| 中华人民共和国国家情报法 | 2018-04-27 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281475.html | `47b3b0ec01c24732` |
| 中华人民共和国国家通用语言文字法 | 2026-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202512/t20251227_450731.html | `d773cde792c14346` |
| 中华人民共和国国家勋章和国家荣誉称号法 | 2016-01-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_222322.html | `621cee5b1cd9c707` |
| 中华人民共和国国境卫生检疫法 | 2025-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202406/t20240628_437887.html | `d4d03a09c50f3791` |
| 中华人民共和国国际刑事司法协助法 | 2018-10-26 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276507.html | `ace8cbcd4e652fc7` |
| 中华人民共和国国务院组织法 | 2024-03-11 | law | http://www.npc.gov.cn/npc/c2/kgfb/202403/t20240312_435950.html | `dfbfb8c3d7e70428` |
| 中华人民共和国固体废物污染环境防治法 | 2020-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202004/t20200430_305758.html | `d88aa0a5624e2a72` |
| 中华人民共和国海南自由贸易港法 | 2021-06-10 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311889.html | `29793c3c689d20e9` |
| 中华人民共和国海商法 | 2026-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202510/t20251028_449061.html | `fdcd3e7ef561cea0` |
| 中华人民共和国海上交通安全法 | 2021-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202104/t20210429_311310.html | `805e739fe897504a` |
| 中华人民共和国海洋环境保护法 | 2024-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202310/t20231024_432550.html | `4ce13f5b3a53c00e` |
| 中华人民共和国航道法 | 2015-03-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_221273.html | `18a75a992a36c269` |
| 中华人民共和国黑土地保护法 | 2022-08-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202206/t20220624_318288.html | `d01afe9540703495` |
| 中华人民共和国红十字会法 | 2017-05-08 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_274784.html | `328064bfa21297c5` |
| 中华人民共和国黄河保护法 | 2023-04-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202210/t20221030_320097.html | `f615876a5f551982` |
| 中华人民共和国环境保护法 | 2015-01-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190521_255975.html | `b5f9582d6ef25b97` |
| 中华人民共和国环境影响评价法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296647.html | `c541775591fa1ff9` |
| 中华人民共和国监察法 | 2025-06-01 | current | http://www.npc.gov.cn/npc/c2/c30834/202502/t20250205_442676.html | `58af6297de40a242` |
| 中华人民共和国监狱法 | 2026-11-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202604/t20260430_454309.html | `fd970d765cd5dfdf` |
| 中华人民共和国家庭教育促进法 | 2022-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202110/t20211023_314286.html | `efc6cedc45a61954` |
| 中华人民共和国基本医疗卫生与健康促进法 | 2020-06-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201912/t20191231_304414.html | `902a5d411a04d15f` |
| 中华人民共和国节约能源法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276677.html | `8c9b39adb8beda85` |
| 中华人民共和国计量法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276613.html | `ab54819343faf3f3` |
| 中华人民共和国精神卫生法 | 2018-04-27 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281477.html | `bfc563ecd500e62b` |
| 中华人民共和国境外非政府组织境内活动管理法 | 2017-11-05 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278496.html | `7d5df2b39254d25d` |
| 中华人民共和国军人保险法 | 2012-07-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190522_176397.html | `0ab110af30d412b0` |
| 中华人民共和国军人地位和权益保障法 | 2021-08-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311890.html | `c94d1fbb7fa1e1fc` |
| 中华人民共和国军事设施保护法 | 2021-08-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311891.html | `73eef1152d84257a` |
| 中华人民共和国科学技术进步法 | 2022-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202112/t20211224_315585.html | `efd3c8737861b540` |
| 中华人民共和国科学技术普及法 | 2024-12-25 | law | http://www.npc.gov.cn/npc/c2/c30834/202412/t20241225_442044.html | `7e9c69eac13310bd` |
| 中华人民共和国劳动法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296651.html | `053a3ea2adf9930d` |
| 中华人民共和国老年人权益保障法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296650.html | `36f326554033e081` |
| 中华人民共和国立法法 | 2023-03-15 | current | http://www.npc.gov.cn/npc/c2/kgfb/202303/t20230314_424438.html | `a10b7011c5856990` |
| 中华人民共和国陆地国界法 | 2022-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202110/t20211023_314278.html | `2a36b82eda9c4d7e` |
| 中华人民共和国旅游法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276612.html | `9b07ce910572ad63` |
| 中华人民共和国密码法 | 2020-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201910/t20191026_301700.html | `94fbc11daacf6f4d` |
| 中华人民共和国民事诉讼法 | 2024-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/202401/P020240108541839745616.pdf | `dc46ad25f6910b35` |
| 中华人民共和国民营经济促进法 | 2025-05-20 | law | http://www.npc.gov.cn/npc/c2/c30834/202504/t20250430_445088.html | `b63b710a22f61daf` |
| 中华人民共和国民用航空法 | 2026-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202512/t20251227_450737.html | `fe9e7f3e3c03183d` |
| 中华人民共和国母婴保健法 | 2017-11-05 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278505.html | `f5cc745c8326e749` |
| 中华人民共和国能源法 | 2025-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202411/t20241108_440884.html | `a312e4604f9e6933` |
| 中华人民共和国农产品质量安全法 | 2023-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202209/t20220902_319195.html | `5e72a2ec2280e024` |
| 中华人民共和国农村集体经济组织法 | 2025-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202406/t20240628_437883.html | `7ac58a27c64d24ac` |
| 中华人民共和国农村土地承包法 | 2019-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296645.html | `1d83cd50a3e5f7b5` |
| 中华人民共和国农民专业合作社法 | 2018-07-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_275660.html | `e22bc8ac8c371e09` |
| 中华人民共和国农业机械化促进法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276623.html | `6af1494667683dc5` |
| 中华人民共和国期货和衍生品法 | 2022-08-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202204/t20220420_317569.html | `34571b0dc5100470` |
| 中华人民共和国清洁生产促进法 | 2012-07-01 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190522_84437.html | `9df1e5c220676093` |
| 中华人民共和国青藏高原生态保护法 | 2023-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202304/t20230426_429053.html | `53dcd5aaf6294608` |
| 中华人民共和国契税法 | 2021-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202008/t20200811_307161.html | `7e77dc332e021160` |
| 中华人民共和国企业所得税法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296654.html | `62fc2b7640815cd1` |
| 中华人民共和国全国人民代表大会和地方各级人民代表大会代表法 | 2025-03-12 | current | http://www.npc.gov.cn/npc/c2/kgfb/202503/t20250312_444229.html | `9ac34140f4bd8f03` |
| 中华人民共和国全国人民代表大会和地方各级人民代表大会选举法 | 2020-10-18 | current | http://www.npc.gov.cn/npc/c2/c30834/202011/t20201119_308799.html | `2d31396456e22f68` |
| 中华人民共和国人口与计划生育法 | 2021-08-20 | current | http://www.npc.gov.cn/npc/c2/c30834/202109/t20210903_313395.html | `90ebffb4b9873efd` |
| 中华人民共和国人民检察院组织法 | 2019-01-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276534.html | `9344d1ea883ed0c7` |
| 中华人民共和国人民陪审员法 | 2018-04-27 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281445.html | `9e984fec57ae559b` |
| 中华人民共和国人民武装警察法 | 2020-06-21 | law | http://www.npc.gov.cn/npc/c2/c30834/202006/t20200620_306630.html | `18d7620102829616` |
| 中华人民共和国森林法 | 2020-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201912/t20191231_304410.html | `7414fe235cea7bd5` |
| 中华人民共和国社会保险法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296659.html | `76bed54a6450d51f` |
| 中华人民共和国社会救助法 | 2026-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202604/t20260430_454303.html | `e549fe1141134c0c` |
| 中华人民共和国深海海底区域资源勘探开发法 | 2016-05-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190521_290521.html | `eb68e3f90c65d033` |
| 中华人民共和国社区矫正法 | 2020-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201912/t20191231_304419.html | `a6f583df8c648412` |
| 中华人民共和国湿地保护法 | 2022-06-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202112/t20211224_315589.html | `525aedf9a63e265e` |
| 中华人民共和国水污染防治法 | 2018-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278105.html | `761e2f57b788c808` |
| 中华人民共和国数据安全法 | 2021-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311888.html | `7dfac5b56c3c6b56` |
| 中华人民共和国台湾同胞投资保护法 | 2020-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201912/t20191231_304364.html | `4ce5f5071eac73cb` |
| 中华人民共和国特种设备安全法 | 2014-01-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_184539.html | `edc94a2d04e9d2d6` |
| 中华人民共和国体育法 | 2023-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202206/t20220624_318292.html | `61b11cd6fe7545ea` |
| 中华人民共和国土地管理法 | 2020-01-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201909/t20190905_300663.html | `c7b4546acb04d1fb` |
| 中华人民共和国突发公共卫生事件应对法 | 2025-11-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202509/t20250912_447763.html | `457702d2b05a75fd` |
| 中华人民共和国突发事件应对法 | 2024-11-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202406/t20240628_437888.html | `e7e3c08fbec641de` |
| 中华人民共和国退役军人保障法 | 2021-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202011/t20201111_308670.html | `64dcddeb1d304795` |
| 中华人民共和国土壤污染防治法 | 2019-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281576.html | `4de4465cb4086b00` |
| 中华人民共和国外国国家豁免法 | 2024-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202309/t20230901_431424.html | `fa4fb384bf43dfe8` |
| 中华人民共和国外商投资法 | 2020-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_297827.html | `8c3729f1b73e9d36` |
| 中华人民共和国危险化学品安全法 | 2026-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202512/t20251227_450708.html | `055c495245c63d49` |
| 中华人民共和国文物保护法 | 2025-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202411/t20241108_440882.html | `739609573cf3b7a4` |
| 中华人民共和国无障碍环境建设法 | 2023-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202306/t20230628_430340.html | `d9db35443265bac7` |
| 中华人民共和国乡村振兴促进法 | 2021-06-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202104/t20210429_311287.html | `7db46bf90aa04933` |
| 中华人民共和国香港特别行政区维护国家安全法 | 2020-06-30 | law | http://www.npc.gov.cn/npc/c2/c30834/202007/t20200701_306793.html | `cf17c1a102cad673` |
| 中华人民共和国行政处罚法 | 2021-07-15 | law | http://www.npc.gov.cn/npc/c2/c30834/202101/t20210122_309857.html | `2beff7613c158882` |
| 中华人民共和国行政复议法 | 2024-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202309/t20230901_431409.html | `a86e57e7aa2b1568` |
| 中华人民共和国行政诉讼法 | 2017-07-01 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_278106.html | `32f31dcd23d93de2` |
| 中华人民共和国学前教育法 | 2025-06-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202411/t20241108_440883.html | `cbcb9a31da244f54` |
| 中华人民共和国学位法 | 2025-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202404/t20240426_436840.html | `8a085ceaec7524e2` |
| 中华人民共和国畜牧法 | 2023-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202210/t20221030_320096.html | `021510de67f0defc` |
| 中华人民共和国循环经济促进法 | 2018-10-26 | current | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_276633.html | `c10a320458adfea9` |
| 中华人民共和国烟叶税法 | 2018-07-01 | law | http://www.npc.gov.cn/npc/c2/c12435/c12488/201905/t20190521_271474.html | `be09ebd820dec6bb` |
| 中华人民共和国野生动物保护法 | 2023-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202212/t20221230_321016.html | `88ee7d7def5e4e71` |
| 中华人民共和国疫苗管理法 | 2019-12-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201907/t20190702_299244.html | `0ef1037c90120c1f` |
| 中华人民共和国英雄烈士保护法 | 2018-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_281441.html | `921f982d78919ea2` |
| 中华人民共和国印花税法 | 2022-07-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202106/t20210610_311898.html | `17e25d97c68ecd47` |
| 中华人民共和国医师法 | 2022-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202108/t20210820_313104.html | `2b2b0b7177bdfed0` |
| 中华人民共和国义务教育法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296656.html | `6149a6ad5b83ad17` |
| 中华人民共和国原子能法 | 2026-01-15 | law | http://www.npc.gov.cn/npc/c2/c30834/202509/t20250912_447757.html | `7ed106f593d7dbb1` |
| 中华人民共和国预备役人员法 | 2023-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202212/t20221230_321022.html | `6e69532e41abc5a0` |
| 中华人民共和国预防未成年人犯罪法 | 2021-06-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202012/t20201226_309441.html | `0caeb2c476753df9` |
| 中华人民共和国预算法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296660.html | `f93a9f3c1d1fcef5` |
| 中华人民共和国渔业法 | 2026-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202512/t20251227_450727.html | `12d85b94665f0bd5` |
| 中华人民共和国噪声污染防治法 | 2022-06-05 | law | http://www.npc.gov.cn/npc/c2/c30834/202112/t20211224_315601.html | `49219f1c347c5e82` |
| 中华人民共和国增值税法 | 2026-01-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202412/t20241225_442038.html | `8d40aed0471685d8` |
| 中华人民共和国证券法 | 2020-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201912/t20191231_304436.html | `3fa6770767f43423` |
| 中华人民共和国职业病防治法 | 2018-12-29 | current | http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296649.html | `d1c06e8b7c7f872f` |
| 中华人民共和国职业教育法 | 2022-05-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202204/t20220420_317575.html | `011afdce44169509` |
| 中华人民共和国仲裁法 | 2026-03-01 | law | http://www.npc.gov.cn/npc/c2/c30834/202509/t20250912_447762.html | `b8433fc0b220adeb` |
| 中华人民共和国中小企业促进法 | 2018-01-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_275294.html | `7636a92cc8b61b7f` |
| 中华人民共和国中医药法 | 2017-07-01 | law | http://www.npc.gov.cn/npc/c2/c12435/201905/t20190521_274720.html | `58b5175ea09ce01a` |
| 中华人民共和国专利法 | 2021-06-01 | current | http://www.npc.gov.cn/npc/c2/c30834/202011/t20201119_308800.html | `cfd63f800f50ea32` |
| 中华人民共和国著作权法 | 2021-06-01 | current | http://www.npc.gov.cn/npc/c2/c30834/202011/t20201119_308796.html | `4ec0f57790c81e71` |
| 中华人民共和国资产评估法 | 2016-12-01 | law | http://www.npc.gov.cn/npc/c2/c10134/201905/t20190521_292871.html | `bf852db62d5f0b24` |
| 中华人民共和国资源税法 | 2020-09-01 | law | http://www.npc.gov.cn/npc/c2/c30834/201908/t20190826_300501.html | `cc00b86113bdc0e2` |

The day each version took effect is read from the source: the law's own commencement article, or the
amending decision's (本决定自……起施行 / 自公布之日起施行); `In-force-evidence:` in each commit names it.
Main is append-only: these commits were added on top of the Constitution history, which is unchanged.

<!-- acts: end -->
