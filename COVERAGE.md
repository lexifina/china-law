# Coverage of the core law

How much of each core category of Chinese law is on `main`, against the official total for it, on 2026-11-22 (172,735 commits). Regenerated with each documentation commit from [`data/coverage.csv`](data/coverage.csv); the plan for every part is in [`PLAN.md`](PLAN.md).

| Category | Official total | Here | % | Gap | Why the gap |
| --- | ---: | ---: | ---: | ---: | --- |
| 宪法及其修正案 (Constitution and its amendments) | 6 versions | 6 | 100.0% | 0 | - |
| 法律（现行和已废止，各修正/修订版本） (Laws, in force and repealed, every version) | 474 versions | 474 | 100.0% | 0 | 8 not yet in force (outside the total; committed on their day) |
| 修正案和修改、废止法律的决定 (Amendments and decisions amending or repealing laws) | 100 instruments | 98 | 98.0% | 2 | 1 no Word file in the flk mirror; 1 title clash with another record (held); 1 not yet in force (outside the total; committed on their day) |
| 法律解释 (Legislative interpretations) | 27 records | 27 | 100.0% | 0 | - |
| 有关法律问题和重大问题的决定 (Decisions on legal and major questions) | 188 records | 186 | 98.9% | 2 | 2 no Word file in the flk mirror |
| 行政法规（各版本，含已废止） (Administrative regulations, every version, incl. repealed) | 862 versions | 858 | 99.5% | 4 | 2 same words as a version on main, dated differently (hand check); 2 no Word file in the flk mirror; 5 not yet in force (outside the total; committed on their day) |
| 监察法规 (Supervision regulations) | 3 records | 3 | 100.0% | 0 | - |
| 司法解释（最高人民法院、最高人民检察院） (Judicial interpretations (SPC and SPP)) | 859 records | 859 | 100.0% | 0 | - |
| 部门规章（现行） (Departmental rules in force) | 2,667 rules | 2,463 | 92.4% | 204 | rules whose text shows a table wait for their own page at www.gov.cn (one request per 10 s, shared with other lanes); held rules (no stated date, path clash) and listings matched under another title; older versions and repealed rules come from the ministries' 部令 pages (no official total) |
| 地方政府规章（现行） (Local government rules in force) | 7,848 rules | 7,819 | 99.6% | 29 | rules whose text shows a table wait for their own page at www.gov.cn (one request per 10 s, shared with other lanes); held rules (no stated date, path clash) and listings matched under another title |
| 地方性法规、自治条例、单行条例、经济特区法规（各版本，含已废止） (Local regulations, autonomy and separate regulations, SEZ regulations: every version, incl. repealed) | 24,217 versions | 21,776 | 89.9% | 2,441 | 2,133 no stated 施行/公布 date in the record or the text (held); 84 older versions not yet back-filled (labelled corrections); 63 not an act (守则, procedure rules: left out); 56 Word file unreadable; 52 no Word file in the flk mirror; 18 stated dates disagree (held); 14 control characters in the text (held); 8 same words as a version on main, dated differently (hand check); 6 Word file without paragraph breaks (held); 6 unit since abolished (莱芜市; held); 1 other holds |
| 地方修改、废止决定和法规性决定 (Local amending/repeal decisions and normative decisions) | 2,027 instruments | 2,005 | 98.9% | 22 | 8 no Word file in the flk mirror; 7 Word file unreadable; 3 older versions not yet back-filled (labelled corrections); 1 control characters in the text (held); 1 no stated 施行/公布 date in the record or the text (held); 1 not an act (守则, procedure rules: left out); 1 stated dates disagree (held) |
| 中央党内法规（中央和部委党内法规，现行） (Central Party regulations in force) | 374 regulations | 92 | 24.6% | 282 | the 12371.cn 党内法规库 lists 131 items; most state no 发布/施行 day (held); the rest are not published on an open official list |
| 军事法规、军事规章 (Military regulations) | not published | 0 | - | - | not published (only titles in the news; no official text online) |
| 条约 (Treaties) | 7,437 treaties | 6,629 | 89.1% | 808 | 530 dated on a signature or ratification day with no stated 生效 day (listed as pending in data/date-corrections.json); the rest still being read from the database (one page per 10 s), or with no stated 生效 day (held) |

Where each total comes from:

- 宪法及其修正案: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1 (宪法 1982 + 修正案 1988, 1993, 1999, 2004, 2018).
- 法律（现行和已废止，各修正/修订版本）: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1 (法律: 有效, 已修改, 已废止, 尚未生效).
- 修正案和修改、废止法律的决定: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1.
- 法律解释: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1.
- 有关法律问题和重大问题的决定: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1 (flk marks this list 部分, partial).
- 行政法规（各版本，含已废止）: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1; 国家行政法规库 (xzfg.moj.gov.cn) lists 604 in force with 1,190 versions.
- 监察法规: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1.
- 司法解释（最高人民法院、最高人民检察院）: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-11-19, via the mirror lawtext/law-flk-vol1 (有效, 已修改, 已废止).
- 部门规章（现行）: 国家规章库 (www.gov.cn/zhengce/xxgk/gjgzk) listing total, read by cn-gzk.
- 地方政府规章（现行）: 国家规章库 province listings (sum of 31 totals), read by cn-gzk.
- 地方性法规、自治条例、单行条例、经济特区法规（各版本，含已废止）: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-04-19, via the mirror lawtext/law-flk-vol2 (地方法规).
- 地方修改、废止决定和法规性决定: 国家法律法规数据库 (flk.npc.gov.cn) record list of 2026-04-19, via the mirror lawtext/law-flk-vol2.
- 中央党内法规（中央和部委党内法规，现行）: 《中国共产党党内法规体系》 (中共中央办公厅法规局, 2021-08-04): 211 中央 + 163 部委党内法规 in force on 2021-07-01.
- 军事法规、军事规章: no official list or total is published.
- 条约: 外交部 条约数据库 (treaty.mfa.gov.cn) listing, read by cn-treaty.

A record counts as here when its version is on `main`: committed from the source, already there from another source on the same day, or back-filled as a labelled correction (`Kind: correction`) where history had moved past it. Records are never dated on an estimate: a record whose 施行 or 公布 day is stated nowhere is held, and counts in the gap.
