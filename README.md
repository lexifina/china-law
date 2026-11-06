# China: law history

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is China's national law, which global-law reads at `china/national/acts/`.

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

<!-- acts: begin -->
## More acts

Besides the Constitution, the record holds these acts, in the same layout: one folder per act, one file per
article (`art-NNN.md`; an article 之一 is `art-NNN-1.md`), `mulu.md` for the headings of the body (编, 章, 节)
and `fujian-N.md` for annexes (附件). Each commit is dated noon Asia/Shanghai on the day the version took
effect (`In-force:` trailer) and is authored by the law that made it. Where 中国人大网 has no earlier full text,
the first version is the oldest it has, credited to the publisher and labelled so. Tags `<folder>/<day>` mark
each version.

| Act | Folder | In force | Commit author | What |
| --- | --- | --- | --- | --- |
| 中华人民共和国民法典 | `minfadian/` | 2021-01-01 | 中华人民共和国民法典（2020年） | the text as adopted, 1261 files |
| 中华人民共和国刑法 | `xingfa/` | 1997-10-01 | 中华人民共和国刑法（1997年修订） | the text as adopted, 455 files |
| 中华人民共和国刑法 | `xingfa/` | 1997-10-01 | 中国人大网 (全国人大常委会办公厅) | correction to the 公报 standard text, 6 files |
| 中华人民共和国刑法 | `xingfa/` | 1998-12-29 | 全国人民代表大会常务委员会关于惩治骗购外汇、逃汇和非法买卖外汇犯罪的决定（1998年） | the amending act, 1 files |
| 中华人民共和国刑法 | `xingfa/` | 1999-12-25 | 中华人民共和国刑法修正案（1999年） | the amending act, 8 files |
| 中华人民共和国刑法 | `xingfa/` | 2001-08-31 | 中华人民共和国刑法修正案（二）（2001年） | the amending act, 1 files |
| 中华人民共和国刑法 | `xingfa/` | 2001-12-29 | 中华人民共和国刑法修正案（三）（2001年） | the amending act, 8 files |
| 中华人民共和国刑法 | `xingfa/` | 2002-12-28 | 中华人民共和国刑法修正案（四）（2002年） | the amending act, 8 files |
| 中华人民共和国刑法 | `xingfa/` | 2005-02-28 | 中华人民共和国刑法修正案（五）（2005年） | the amending act, 3 files |
| 中华人民共和国刑法 | `xingfa/` | 2006-06-29 | 中华人民共和国刑法修正案（六）（2006年） | the amending act, 20 files |
| 中华人民共和国刑法 | `xingfa/` | 2009-02-28 | 中华人民共和国刑法修正案（七）（2009年） | the amending act, 14 files |
| 中华人民共和国刑法 | `xingfa/` | 2009-08-27 | 全国人民代表大会常务委员会关于修改部分法律的决定（2009年） | the amending act, 2 files |
| 中华人民共和国刑法 | `xingfa/` | 2011-05-01 | 中华人民共和国刑法修正案（八）（2011年） | the amending act, 49 files |
| 中华人民共和国刑法 | `xingfa/` | 2015-11-01 | 中华人民共和国刑法修正案（九）（2015年） | the amending act, 56 files |
| 中华人民共和国刑法 | `xingfa/` | 2017-11-04 | 中华人民共和国刑法修正案（十）（2017年） | the amending act, 1 files |
| 中华人民共和国刑法 | `xingfa/` | 2021-03-01 | 中华人民共和国刑法修正案（十一）（2020年） | the amending act, 47 files |
| 中华人民共和国刑法 | `xingfa/` | 2024-03-01 | 中华人民共和国刑法修正案（十二）（2023年） | the amending act, 7 files |
| 中华人民共和国刑事诉讼法 | `xingshisusongfa/` | 1997-01-01 | 中国人大网 (全国人大常委会办公厅) | the oldest full text 中国人大网 has (1996年修正文本), 226 files |
| 中华人民共和国刑事诉讼法 | `xingshisusongfa/` | 2013-01-01 | 全国人民代表大会关于修改《中华人民共和国刑事诉讼法》的决定（2012年） | the amending act, 263 files |
| 中华人民共和国刑事诉讼法 | `xingshisusongfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国刑事诉讼法》的决定（2018年） | the amending act, 295 files |
| 中华人民共和国公司法 | `gongsifa/` | 2018-10-26 | 中国人大网 (全国人大常委会办公厅) | the oldest full text 中国人大网 has (2018年修正文本), 219 files |
| 中华人民共和国公司法 | `gongsifa/` | 2024-07-01 | 中华人民共和国公司法（2023年修订） | the revised text (修订), 267 files |
| 中华人民共和国劳动合同法 | `laodonghetongfa/` | 2008-01-01 | 中华人民共和国劳动合同法（2007年） | the text as adopted, 99 files |
| 中华人民共和国劳动合同法 | `laodonghetongfa/` | 2013-07-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国劳动合同法》的决定（2012年） | the amending act, 4 files |
| 中华人民共和国爱国主义教育法 | `aiguozhuyijiaoyufa/` | 2024-01-01 | 中华人民共和国爱国主义教育法（2023年） | the text as adopted, 41 files |
| 中华人民共和国保守国家秘密法 | `baoshouguojiamimifa/` | 2024-05-01 | 中华人民共和国保守国家秘密法（2024年修订） | the text as adopted, 66 files |
| 中华人民共和国标准化法 | `biaozhunhuafa/` | 2018-01-01 | 中华人民共和国标准化法（2017年修订） | the text as adopted, 46 files |
| 中华人民共和国兵役法 | `bingyifa/` | 2021-10-01 | 中华人民共和国兵役法（2021年修订） | the text as adopted, 66 files |
| 中华人民共和国残疾人保障法 | `canjirenbaozhangfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 69 files |
| 中华人民共和国测绘法 | `cehuifa/` | 2017-07-01 | 中华人民共和国测绘法（2017年修订） | the text as adopted, 69 files |
| 中华人民共和国长江保护法 | `changjiangbaohufa/` | 2021-03-01 | 中华人民共和国长江保护法（2020年） | the text as adopted, 97 files |
| 中华人民共和国车辆购置税法 | `chelianggouzhishuifa/` | 2019-07-01 | 中华人民共和国车辆购置税法（2018年） | the text as adopted, 19 files |
| 中华人民共和国城市房地产管理法 | `chengshifangdichanguanlifa/` | 2020-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国土地管理法》、《中华人民共和国城市房地产管理法》的决定（2019年） | the latest text (2019年修正文本), the oldest in this record, 74 files |
| 中华人民共和国城市居民委员会组织法 | `chengshijuminweiyuanhuizuzhifa/` | 2026-01-01 | 中华人民共和国城市居民委员会组织法（2025年修订） | the text as adopted, 51 files |
| 中华人民共和国城市维护建设税法 | `chengshiweihujiansheshuifa/` | 2021-09-01 | 中华人民共和国城市维护建设税法（2020年） | the text as adopted, 11 files |
| 中华人民共和国船舶吨税法 | `chuanbodunshuifa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 22 files |
| 中华人民共和国传染病防治法 | `chuanranbingfangzhifa/` | 2025-09-01 | 中华人民共和国传染病防治法（2025年修订） | the text as adopted, 116 files |
| 中华人民共和国出境入境管理法 | `chujingrujingguanlifa/` | 2013-07-01 | 中华人民共和国出境入境管理法（2012年） | the text as adopted, 94 files |
| 中华人民共和国出口管制法 | `chukouguanzhifa/` | 2020-12-01 | 中华人民共和国出口管制法（2020年） | the text as adopted, 50 files |
| 中华人民共和国促进科技成果转化法 | `cujinkejichengguozhuanhuafa/` | 2015-10-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国促进科技成果转化法》的决定（2015年） | the latest text (2015年修正文本), the oldest in this record, 53 files |
| 中华人民共和国档案法 | `danganfa/` | 2021-01-01 | 中华人民共和国档案法（2020年修订） | the text as adopted, 54 files |
| 中华人民共和国大气污染防治法 | `daqiwuranfangzhifa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 130 files |
| 中华人民共和国电力法 | `dianlifa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国电力法》等四部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 76 files |
| 中华人民共和国电影产业促进法 | `dianyingchanyecujinfa/` | 2017-03-01 | 中华人民共和国电影产业促进法（2016年） | the text as adopted, 61 files |
| 中华人民共和国电子商务法 | `dianzishangwufa/` | 2019-01-01 | 中华人民共和国电子商务法（2018年） | the text as adopted, 90 files |
| 中华人民共和国动物防疫法 | `dongwufangyifa/` | 2021-05-01 | 中华人民共和国动物防疫法（2021年修订） | the text as adopted, 114 files |
| 中华人民共和国对外关系法 | `duiwaiguanxifa/` | 2023-07-01 | 中华人民共和国对外关系法（2023年） | the text as adopted, 46 files |
| 中华人民共和国对外贸易法 | `duiwaimaoyifa/` | 2026-03-01 | 中华人民共和国对外贸易法（2025年修订） | the text as adopted, 84 files |
| 中华人民共和国法律援助法 | `falvyuanzhufa/` | 2022-01-01 | 中华人民共和国法律援助法（2021年） | the text as adopted, 72 files |
| 中华人民共和国反不正当竞争法 | `fanbuzhengdangjingzhengfa/` | 2025-10-15 | 中华人民共和国反不正当竞争法（2025年修订） | the text as adopted, 42 files |
| 中华人民共和国反电信网络诈骗法 | `fandianxinwangluozhapianfa/` | 2022-12-01 | 中华人民共和国反电信网络诈骗法（2022年） | the text as adopted, 51 files |
| 中华人民共和国防沙治沙法 | `fangshazhishafa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 48 files |
| 中华人民共和国反间谍法 | `fanjiandiefa/` | 2023-07-01 | 中华人民共和国反间谍法（2023年修订） | the text as adopted, 72 files |
| 中华人民共和国反家庭暴力法 | `fanjiatingbaolifa/` | 2016-03-01 | 中华人民共和国反家庭暴力法（2015年） | the text as adopted, 39 files |
| 中华人民共和国反恐怖主义法 | `fankongbuzhuyifa/` | 2018-04-27 | 全国人民代表大会常务委员会关于修改《中华人民共和国国境卫生检疫法》等六部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 98 files |
| 中华人民共和国反食品浪费法 | `fanshipinlangfeifa/` | 2021-04-29 | 中华人民共和国反食品浪费法（2021年） | the text as adopted, 32 files |
| 中华人民共和国反外国制裁法 | `fanwaiguozhicaifa/` | 2021-06-10 | 中华人民共和国反外国制裁法（2021年） | the text as adopted, 16 files |
| 中华人民共和国反洗钱法 | `fanxiqianfa/` | 2025-01-01 | 中华人民共和国反洗钱法（2024年修订） | the text as adopted, 66 files |
| 中华人民共和国反有组织犯罪法 | `fanyouzuzhifanzuifa/` | 2022-05-01 | 中华人民共和国反有组织犯罪法（2021年） | the text as adopted, 78 files |
| 中华人民共和国法治宣传教育法 | `fazhixuanchuanjiaoyufa/` | 2025-11-01 | 中华人民共和国法治宣传教育法（2025年） | the text as adopted, 66 files |
| 中华人民共和国妇女权益保障法 | `funvquanyibaozhangfa/` | 2023-01-01 | 中华人民共和国妇女权益保障法（2022年修订） | the text as adopted, 87 files |
| 中华人民共和国港口法 | `gangkoufa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国电力法》等四部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 63 files |
| 中华人民共和国高等教育法 | `gaodengjiaoyufa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国电力法》等四部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 70 files |
| 中华人民共和国各级人民代表大会常务委员会监督法 | `gejirenmindaibiaodahuichangwuweiyuanhuijiandufa/` | 2024-11-08 | 全国人民代表大会常务委员会关于修改《中华人民共和国各级人民代表大会常务委员会监督法》的决定（2024年） | the latest text (2024年修正文本), the oldest in this record, 66 files |
| 中华人民共和国耕地占用税法 | `gengdizhanyongshuifa/` | 2019-09-01 | 中华人民共和国耕地占用税法（2018年） | the text as adopted, 16 files |
| 中华人民共和国个人信息保护法 | `gerenxinxibaohufa/` | 2021-11-01 | 中华人民共和国个人信息保护法（2021年） | the text as adopted, 75 files |
| 中华人民共和国公共图书馆法 | `gonggongtushuguanfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 56 files |
| 中华人民共和国公共文化服务保障法 | `gonggongwenhuafuwubaozhangfa/` | 2017-03-01 | 中华人民共和国公共文化服务保障法（2016年） | the text as adopted, 66 files |
| 中华人民共和国公路法 | `gonglufa/` | 2017-11-05 | 全国人民代表大会常务委员会关于修改《中华人民共和国会计法》等十一部法律的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 88 files |
| 中华人民共和国公务员法 | `gongwuyuanfa/` | 2019-06-01 | 中华人民共和国公务员法（2018年修订） | the text as adopted, 114 files |
| 中华人民共和国公证法 | `gongzhengfa/` | 2018-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国法官法》等八部法律的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 48 files |
| 中华人民共和国公职人员政务处分法 | `gongzhirenyuanzhengwuchufenfa/` | 2020-07-01 | 中华人民共和国公职人员政务处分法（2020年） | the text as adopted, 69 files |
| 中华人民共和国关税法 | `guanshuifa/` | 2024-12-01 | 中华人民共和国关税法（2024年） | the text as adopted, 73 files |
| 中华人民共和国国防动员法 | `guofangdongyuanfa/` | 2026-10-01 | 中华人民共和国国防动员法（2026年修订） | the text as adopted, 83 files |
| 中华人民共和国国防法 | `guofangfa/` | 2021-01-01 | 中华人民共和国国防法（2020年修订） | the text as adopted, 74 files |
| 中华人民共和国国防交通法 | `guofangjiaotongfa/` | 2017-01-01 | 中华人民共和国国防交通法（2016年） | the text as adopted, 61 files |
| 中华人民共和国国防教育法 | `guofangjiaoyufa/` | 2024-09-21 | 中华人民共和国国防教育法（2024年修订） | the text as adopted, 43 files |
| 中华人民共和国国家安全法 | `guojiaanquanfa/` | 2015-07-01 | 中华人民共和国国家安全法（2015年） | the text as adopted, 85 files |
| 中华人民共和国国家发展规划法 | `guojiafazhanguihuafa/` | 2026-03-12 | 中华人民共和国国家发展规划法（2026年） | the text as adopted, 39 files |
| 中华人民共和国国家公园法 | `guojiagongyuanfa/` | 2026-01-01 | 中华人民共和国国家公园法（2025年） | the text as adopted, 64 files |
| 中华人民共和国国家情报法 | `guojiaqingbaofa/` | 2018-04-27 | 全国人民代表大会常务委员会关于修改《中华人民共和国国境卫生检疫法》等六部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 33 files |
| 中华人民共和国国家通用语言文字法 | `guojiatongyongyuyanwenzifa/` | 2026-01-01 | 中华人民共和国国家通用语言文字法（2025年修订） | the text as adopted, 33 files |
| 中华人民共和国国家勋章和国家荣誉称号法 | `guojiaxunzhangheguojiarongyuchenghaofa/` | 2016-01-01 | 中华人民共和国国家勋章和国家荣誉称号法（2015年） | the text as adopted, 21 files |
| 中华人民共和国国境卫生检疫法 | `guojingweishengjianyifa/` | 2025-01-01 | 中华人民共和国国境卫生检疫法（2024年修订） | the text as adopted, 58 files |
| 中华人民共和国国际刑事司法协助法 | `guojixingshisifaxiezhufa/` | 2018-10-26 | 中华人民共和国国际刑事司法协助法（2018年） | the text as adopted, 71 files |
| 中华人民共和国国务院组织法 | `guowuyuanzuzhifa/` | 2024-03-11 | 中华人民共和国国务院组织法（2024年修订） | the text as adopted, 20 files |
| 中华人民共和国固体废物污染环境防治法 | `gutifeiwuwuranhuanjingfangzhifa/` | 2020-09-01 | 中华人民共和国固体废物污染环境防治法（2020年修订） | the text as adopted, 127 files |
| 中华人民共和国海南自由贸易港法 | `hainanziyoumaoyigangfa/` | 2021-06-10 | 中华人民共和国海南自由贸易港法（2021年） | the text as adopted, 58 files |
| 中华人民共和国海商法 | `haishangfa/` | 2026-05-01 | 中华人民共和国海商法（2025年修订） | the text as adopted, 311 files |
| 中华人民共和国海上交通安全法 | `haishangjiaotonganquanfa/` | 2021-09-01 | 中华人民共和国海上交通安全法（2021年修订） | the text as adopted, 123 files |
| 中华人民共和国海洋环境保护法 | `haiyanghuanjingbaohufa/` | 2024-01-01 | 中华人民共和国海洋环境保护法（2023年修订） | the text as adopted, 125 files |
| 中华人民共和国航道法 | `hangdaofa/` | 2015-03-01 | 中华人民共和国航道法（2014年） | the text as adopted, 49 files |
| 中华人民共和国黑土地保护法 | `heitudibaohufa/` | 2022-08-01 | 中华人民共和国黑土地保护法（2022年） | the text as adopted, 38 files |
| 中华人民共和国红十字会法 | `hongshizihuifa/` | 2017-05-08 | 中华人民共和国红十字会法（2017年修订） | the text as adopted, 31 files |
| 中华人民共和国黄河保护法 | `huanghebaohufa/` | 2023-04-01 | 中华人民共和国黄河保护法（2022年） | the text as adopted, 123 files |
| 中华人民共和国环境保护法 | `huanjingbaohufa/` | 2015-01-01 | 中华人民共和国环境保护法（2014年修订） | the text as adopted, 71 files |
| 中华人民共和国环境影响评价法 | `huanjingyingxiangpingjiafa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国劳动法》等七部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 38 files |
| 中华人民共和国监察法 | `jianchafa/` | 2025-06-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国监察法》的决定（2024年） | the latest text (2024年修正文本), the oldest in this record, 79 files |
| 中华人民共和国监狱法 | `jianyufa/` | 2026-11-01 | 中华人民共和国监狱法（2026年修订） | the text as adopted, 122 files |
| 中华人民共和国家庭教育促进法 | `jiatingjiaoyucujinfa/` | 2022-01-01 | 中华人民共和国家庭教育促进法（2021年） | the text as adopted, 56 files |
| 中华人民共和国基本医疗卫生与健康促进法 | `jibenyiliaoweishengyujiankangcujinfa/` | 2020-06-01 | 中华人民共和国基本医疗卫生与健康促进法（2019年） | the text as adopted, 111 files |
| 中华人民共和国节约能源法 | `jieyuenengyuanfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 88 files |
| 中华人民共和国计量法 | `jiliangfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 35 files |
| 中华人民共和国精神卫生法 | `jingshenweishengfa/` | 2018-04-27 | 全国人民代表大会常务委员会关于修改《中华人民共和国国境卫生检疫法》等六部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 86 files |
| 中华人民共和国境外非政府组织境内活动管理法 | `jingwaifeizhengfuzuzhijingneihuodongguanlifa/` | 2017-11-05 | 全国人民代表大会常务委员会关于修改《中华人民共和国会计法》等十一部法律的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 55 files |
| 中华人民共和国军人保险法 | `junrenbaoxianfa/` | 2012-07-01 | 中华人民共和国军人保险法（2012年） | the text as adopted, 52 files |
| 中华人民共和国军人地位和权益保障法 | `junrendiweihequanyibaozhangfa/` | 2021-08-01 | 中华人民共和国军人地位和权益保障法（2021年） | the text as adopted, 72 files |
| 中华人民共和国军事设施保护法 | `junshisheshibaohufa/` | 2021-08-01 | 中华人民共和国军事设施保护法（2021年修订） | the text as adopted, 73 files |
| 中华人民共和国科学技术进步法 | `kexuejishujinbufa/` | 2022-01-01 | 中华人民共和国科学技术进步法（2021年修订） | the text as adopted, 118 files |
| 中华人民共和国科学技术普及法 | `kexuejishupujifa/` | 2024-12-25 | 中华人民共和国科学技术普及法（2024年修订） | the text as adopted, 61 files |
| 中华人民共和国劳动法 | `laodongfa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国劳动法》等七部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 108 files |
| 中华人民共和国老年人权益保障法 | `laonianrenquanyibaozhangfa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国劳动法》等七部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 86 files |
| 中华人民共和国立法法 | `lifafa/` | 2023-03-15 | 全国人民代表大会关于修改《中华人民共和国立法法》的决定（2023年） | the latest text (2023年修正文本), the oldest in this record, 121 files |
| 中华人民共和国陆地国界法 | `ludiguojiefa/` | 2022-01-01 | 中华人民共和国陆地国界法（2021年） | the text as adopted, 63 files |
| 中华人民共和国旅游法 | `lvyoufa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 113 files |
| 中华人民共和国密码法 | `mimafa/` | 2020-01-01 | 中华人民共和国密码法（2019年） | the text as adopted, 45 files |
| 中华人民共和国民事诉讼法 | `minshisusongfa/` | 2024-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国民事诉讼法》的决定（2023年） | the latest text (2023年修正文本), the oldest in this record, 307 files |
| 中华人民共和国民营经济促进法 | `minyingjingjicujinfa/` | 2025-05-20 | 中华人民共和国民营经济促进法（2025年） | the text as adopted, 79 files |
| 中华人民共和国民用航空法 | `minyonghangkongfa/` | 2026-07-01 | 中华人民共和国民用航空法（2025年修订） | the text as adopted, 263 files |
| 中华人民共和国母婴保健法 | `muyingbaojianfa/` | 2017-11-05 | 全国人民代表大会常务委员会关于修改《中华人民共和国会计法》等十一部法律的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 40 files |
| 中华人民共和国能源法 | `nengyuanfa/` | 2025-01-01 | 中华人民共和国能源法（2024年） | the text as adopted, 81 files |
| 中华人民共和国农产品质量安全法 | `nongchanpinzhilianganquanfa/` | 2023-01-01 | 中华人民共和国农产品质量安全法（2022年修订） | the text as adopted, 82 files |
| 中华人民共和国农村集体经济组织法 | `nongcunjitijingjizuzhifa/` | 2025-05-01 | 中华人民共和国农村集体经济组织法（2024年） | the text as adopted, 68 files |
| 中华人民共和国农村土地承包法 | `nongcuntudichengbaofa/` | 2019-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国农村土地承包法》的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 71 files |
| 中华人民共和国农民专业合作社法 | `nongminzhuanyehezuoshefa/` | 2018-07-01 | 中华人民共和国农民专业合作社法（2017年修订） | the text as adopted, 75 files |
| 中华人民共和国农业机械化促进法 | `nongyejixiehuacujinfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 36 files |
| 中华人民共和国期货和衍生品法 | `qihuoheyanshengpinfa/` | 2022-08-01 | 中华人民共和国期货和衍生品法（2022年） | the text as adopted, 156 files |
| 中华人民共和国清洁生产促进法 | `qingjieshengchancujinfa/` | 2012-07-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国清洁生产促进法》的决定（2012年） | the latest text (2012年修正文本), the oldest in this record, 41 files |
| 中华人民共和国青藏高原生态保护法 | `qingzanggaoyuanshengtaibaohufa/` | 2023-09-01 | 中华人民共和国青藏高原生态保护法（2023年） | the text as adopted, 64 files |
| 中华人民共和国契税法 | `qishuifa/` | 2021-09-01 | 中华人民共和国契税法（2020年） | the text as adopted, 16 files |
| 中华人民共和国企业所得税法 | `qiyesuodeshuifa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国电力法》等四部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 61 files |
| 中华人民共和国全国人民代表大会和地方各级人民代表大会代表法 | `quanguorenmindaibiaodahuihedifanggejirenmindaibiaodahuidaibiaofa/` | 2025-03-12 | 全国人民代表大会关于修改《中华人民共和国全国人民代表大会和地方各级人民代表大会代表法》的决定（2025年） | the latest text (2025年修正文本), the oldest in this record, 66 files |
| 中华人民共和国全国人民代表大会和地方各级人民代表大会选举法 | `quanguorenmindaibiaodahuihedifanggejirenmindaibiaodahuixuanjufa/` | 2020-10-18 | 全国人民代表大会常务委员会关于修改《中华人民共和国全国人民代表大会和地方各级人民代表大会选举法》的决定（2020年） | the latest text (2020年修正文本), the oldest in this record, 61 files |
| 中华人民共和国人口与计划生育法 | `renkouyujihuashengyufa/` | 2021-08-20 | 全国人民代表大会常务委员会关于修改《中华人民共和国人口与计划生育法》的决定（2021年） | the latest text (2021年修正文本), the oldest in this record, 49 files |
| 中华人民共和国人民检察院组织法 | `renminjianchayuanzuzhifa/` | 2019-01-01 | 中华人民共和国人民检察院组织法（2018年修订） | the text as adopted, 54 files |
| 中华人民共和国人民陪审员法 | `renminpeishenyuanfa/` | 2018-04-27 | 中华人民共和国人民陪审员法（2018年） | the text as adopted, 32 files |
| 中华人民共和国人民武装警察法 | `renminwuzhuangjingchafa/` | 2020-06-21 | 中华人民共和国人民武装警察法（2020年修订） | the text as adopted, 52 files |
| 中华人民共和国森林法 | `senlinfa/` | 2020-07-01 | 中华人民共和国森林法（2019年修订） | the text as adopted, 85 files |
| 中华人民共和国社会保险法 | `shehuibaoxianfa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国社会保险法》的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 99 files |
| 中华人民共和国社会救助法 | `shehuijiuzhufa/` | 2026-07-01 | 中华人民共和国社会救助法（2026年） | the text as adopted, 79 files |
| 中华人民共和国深海海底区域资源勘探开发法 | `shenhaihaidiquyuziyuankantankaifafa/` | 2016-05-01 | 中华人民共和国深海海底区域资源勘探开发法（2016年） | the text as adopted, 30 files |
| 中华人民共和国社区矫正法 | `shequjiaozhengfa/` | 2020-07-01 | 中华人民共和国社区矫正法（2019年） | the text as adopted, 64 files |
| 中华人民共和国湿地保护法 | `shidibaohufa/` | 2022-06-01 | 中华人民共和国湿地保护法（2021年） | the text as adopted, 66 files |
| 中华人民共和国水污染防治法 | `shuiwuranfangzhifa/` | 2018-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国水污染防治法》的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 104 files |
| 中华人民共和国数据安全法 | `shujuanquanfa/` | 2021-09-01 | 中华人民共和国数据安全法（2021年） | the text as adopted, 56 files |
| 中华人民共和国台湾同胞投资保护法 | `taiwantongbaotouzibaohufa/` | 2020-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国台湾同胞投资保护法》的决定（2019年） | the latest text (2019年修正文本), the oldest in this record, 14 files |
| 中华人民共和国特种设备安全法 | `tezhongshebeianquanfa/` | 2014-01-01 | 中华人民共和国特种设备安全法（2013年） | the text as adopted, 102 files |
| 中华人民共和国体育法 | `tiyufa/` | 2023-01-01 | 中华人民共和国体育法（2022年修订） | the text as adopted, 123 files |
| 中华人民共和国土地管理法 | `tudiguanlifa/` | 2020-01-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国土地管理法》、《中华人民共和国城市房地产管理法》的决定（2019年） | the latest text (2019年修正文本), the oldest in this record, 88 files |
| 中华人民共和国突发公共卫生事件应对法 | `tufagonggongweishengshijianyingduifa/` | 2025-11-01 | 中华人民共和国突发公共卫生事件应对法（2025年） | the text as adopted, 66 files |
| 中华人民共和国突发事件应对法 | `tufashijianyingduifa/` | 2024-11-01 | 中华人民共和国突发事件应对法（2024年修订） | the text as adopted, 107 files |
| 中华人民共和国退役军人保障法 | `tuiyijunrenbaozhangfa/` | 2021-01-01 | 中华人民共和国退役军人保障法（2020年） | the text as adopted, 86 files |
| 中华人民共和国土壤污染防治法 | `turangwuranfangzhifa/` | 2019-01-01 | 中华人民共和国土壤污染防治法（2018年） | the text as adopted, 100 files |
| 中华人民共和国外国国家豁免法 | `waiguoguojiahuomianfa/` | 2024-01-01 | 中华人民共和国外国国家豁免法（2023年） | the text as adopted, 23 files |
| 中华人民共和国外商投资法 | `waishangtouzifa/` | 2020-01-01 | 中华人民共和国外商投资法（2019年） | the text as adopted, 43 files |
| 中华人民共和国危险化学品安全法 | `weixianhuaxuepinanquanfa/` | 2026-05-01 | 中华人民共和国危险化学品安全法（2025年） | the text as adopted, 128 files |
| 中华人民共和国文物保护法 | `wenwubaohufa/` | 2025-03-01 | 中华人民共和国文物保护法（2024年修订） | the text as adopted, 102 files |
| 中华人民共和国无障碍环境建设法 | `wuzhangaihuanjingjianshefa/` | 2023-09-01 | 中华人民共和国无障碍环境建设法（2023年） | the text as adopted, 73 files |
| 中华人民共和国乡村振兴促进法 | `xiangcunzhenxingcujinfa/` | 2021-06-01 | 中华人民共和国乡村振兴促进法（2021年） | the text as adopted, 75 files |
| 中华人民共和国香港特别行政区维护国家安全法 | `xianggangtebiexingzhengquweihuguojiaanquanfa/` | 2020-06-30 | 中华人民共和国香港特别行政区维护国家安全法（2020年） | the text as adopted, 67 files |
| 中华人民共和国行政处罚法 | `xingzhengchufafa/` | 2021-07-15 | 中华人民共和国行政处罚法（2021年修订） | the text as adopted, 87 files |
| 中华人民共和国行政复议法 | `xingzhengfuyifa/` | 2024-01-01 | 中华人民共和国行政复议法（2023年修订） | the text as adopted, 91 files |
| 中华人民共和国行政诉讼法 | `xingzhengsusongfa/` | 2017-07-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国民事诉讼法》和《中华人民共和国行政诉讼法》的决定（2017年） | the latest text (2017年修正文本), the oldest in this record, 104 files |
| 中华人民共和国学前教育法 | `xueqianjiaoyufa/` | 2025-06-01 | 中华人民共和国学前教育法（2024年） | the text as adopted, 86 files |
| 中华人民共和国学位法 | `xueweifa/` | 2025-01-01 | 中华人民共和国学位法（2024年） | the text as adopted, 46 files |
| 中华人民共和国畜牧法 | `xumufa/` | 2023-03-01 | 中华人民共和国畜牧法（2022年修订） | the text as adopted, 95 files |
| 中华人民共和国循环经济促进法 | `xunhuanjingjicujinfa/` | 2018-10-26 | 全国人民代表大会常务委员会关于修改《中华人民共和国野生动物保护法》等十五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 59 files |
| 中华人民共和国烟叶税法 | `yanyeshuifa/` | 2018-07-01 | 中华人民共和国烟叶税法（2017年） | the text as adopted, 10 files |
| 中华人民共和国野生动物保护法 | `yeshengdongwubaohufa/` | 2023-05-01 | 中华人民共和国野生动物保护法（2022年修订） | the text as adopted, 65 files |
| 中华人民共和国疫苗管理法 | `yimiaoguanlifa/` | 2019-12-01 | 中华人民共和国疫苗管理法（2019年） | the text as adopted, 101 files |
| 中华人民共和国英雄烈士保护法 | `yingxionglieshibaohufa/` | 2018-05-01 | 中华人民共和国英雄烈士保护法（2018年） | the text as adopted, 30 files |
| 中华人民共和国印花税法 | `yinhuashuifa/` | 2022-07-01 | 中华人民共和国印花税法（2021年） | the text as adopted, 20 files |
| 中华人民共和国医师法 | `yishifa/` | 2022-03-01 | 中华人民共和国医师法（2021年） | the text as adopted, 68 files |
| 中华人民共和国义务教育法 | `yiwujiaoyufa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国产品质量法》等五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 64 files |
| 中华人民共和国原子能法 | `yuanzinengfa/` | 2026-01-15 | 中华人民共和国原子能法（2025年） | the text as adopted, 63 files |
| 中华人民共和国预备役人员法 | `yubeiyirenyuanfa/` | 2023-03-01 | 中华人民共和国预备役人员法（2022年） | the text as adopted, 66 files |
| 中华人民共和国预防未成年人犯罪法 | `yufangweichengnianrenfanzuifa/` | 2021-06-01 | 中华人民共和国预防未成年人犯罪法（2020年修订） | the text as adopted, 69 files |
| 中华人民共和国预算法 | `yusuanfa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国产品质量法》等五部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 102 files |
| 中华人民共和国渔业法 | `yuyefa/` | 2026-05-01 | 中华人民共和国渔业法（2025年修订） | the text as adopted, 91 files |
| 中华人民共和国噪声污染防治法 | `zaoshengwuranfangzhifa/` | 2022-06-05 | 中华人民共和国噪声污染防治法（2021年） | the text as adopted, 91 files |
| 中华人民共和国增值税法 | `zengzhishuifa/` | 2026-01-01 | 中华人民共和国增值税法（2024年） | the text as adopted, 39 files |
| 中华人民共和国证券法 | `zhengquanfa/` | 2020-03-01 | 中华人民共和国证券法（2019年修订） | the text as adopted, 227 files |
| 中华人民共和国职业病防治法 | `zhiyebingfangzhifa/` | 2018-12-29 | 全国人民代表大会常务委员会关于修改《中华人民共和国劳动法》等七部法律的决定（2018年） | the latest text (2018年修正文本), the oldest in this record, 89 files |
| 中华人民共和国职业教育法 | `zhiyejiaoyufa/` | 2022-05-01 | 中华人民共和国职业教育法（2022年修订） | the text as adopted, 70 files |
| 中华人民共和国仲裁法 | `zhongcaifa/` | 2026-03-01 | 中华人民共和国仲裁法（2025年修订） | the text as adopted, 97 files |
| 中华人民共和国中小企业促进法 | `zhongxiaoqiyecujinfa/` | 2018-01-01 | 中华人民共和国中小企业促进法（2017年修订） | the text as adopted, 62 files |
| 中华人民共和国中医药法 | `zhongyiyaofa/` | 2017-07-01 | 中华人民共和国中医药法（2016年） | the text as adopted, 64 files |
| 中华人民共和国专利法 | `zhuanlifa/` | 2021-06-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国专利法》的决定（2020年） | the latest text (2020年修正文本), the oldest in this record, 83 files |
| 中华人民共和国著作权法 | `zhuzuoquanfa/` | 2021-06-01 | 全国人民代表大会常务委员会关于修改《中华人民共和国著作权法》的决定（2020年） | the latest text (2020年修正文本), the oldest in this record, 68 files |
| 中华人民共和国资产评估法 | `zichanpinggufa/` | 2016-12-01 | 中华人民共和国资产评估法（2016年） | the text as adopted, 56 files |
| 中华人民共和国资源税法 | `ziyuanshuifa/` | 2020-09-01 | 中华人民共和国资源税法（2019年） | the text as adopted, 17 files |

- `python tools/on_date.py 2010-01-01 minfadian 2` prints 第二条 of that act as in force on that day.
- `git log --follow --format=%an%x09%(trailers:key=In-force,valueonly) -- xingshisusongfa/art-002.md` lists
  the laws that changed an article. Article numbers are those of the version in force; a decision that
  renumbers articles shows as changes to the files it moves.
- A version made from an amending decision's own wording (not from a republished full text) says so in its
  `Evidence:` trailer.

<!-- acts: end -->
