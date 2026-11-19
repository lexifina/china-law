# China: law history in git

[简体中文](README.md) · **English**

<picture>
<source media="(prefers-color-scheme: dark)" srcset="data/effort-dark.svg">
<img alt="Chinese law in this repository: what it holds, changes by the year they took effect, completeness against the official sources, and the correctness of what is held" src="data/effort-light.svg" width="880">
</picture>

The law of China as a git history: one file per article, one commit per version on the day it took effect, and the act that made each change as the commit's author. `git blame` names the act behind every paragraph; `git log` lists every change to an article; picking a date gives the text in force that day.

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is China's national law, which global-law reads at `china/national/acts/`.

**What is in it now:** the Constitution, as adopted in 1982 and changed by its five amendments, and 172 laws of the National People's Congress and its Standing Committee, all in force, with 190 versions: 15 of the Criminal Law, 3 of the Criminal Procedure Law, 2 each of the Company Law and the Labour Contract Law, and one each of the other 168. [`data/acts.json`](data/acts.json) lists every act with its folder, its versions and where its record starts; each act's folder has a `README.md` listing its versions.

Each law is a folder in [`法律/`](法律/) named by its Chinese title, one file per article (`法律/劳动合同法/第066条.md` is 第六十六条 of the 中华人民共和国劳动合同法, the Labour Contract Law), with `目录.md` for the headings of its parts and chapters and `附件N.md` for its annexes; the Constitution is [`宪法/`](宪法/), its preamble `宪法/序言.md`. Until 20 November 2026 these folders had pinyin names at the top of the repository (`laodonghetongfa/art-066.md`); [`data/paths.json`](data/paths.json) maps every old path to its new one, and `git log --follow` follows each file across the move. Article numbers are those of the version in force: where a change renumbers articles, git shows the text moving between files.

The text is in Chinese, as 中国人大网 publishes it, with full-width digits written as ASCII digits. An English translation is not part of this record.

## Questions as git commands

| Question | Command |
| --- | --- |
| Every change to Article 66 of the Labour Contract Law | `git log -p --follow --word-diff -- 法律/劳动合同法/第066条.md` |
| Which act wrote each line of Article 66? | `git blame 法律/劳动合同法/第066条.md` |
| Every version of the Labour Contract Law, with the day each took effect | `git log --format="%h %(trailers:key=In-force,valueonly,separator=) %an" -- 法律/劳动合同法 laodonghetongfa ':!法律/劳动合同法/README.md' ':!laodonghetongfa/README.md'` |
| Article 66 as in force on 1 January 2010 | `python tools/on_date.py 2010-01-01 法律/劳动合同法 66` |

**Outside git**, we also host this record publicly, for free:

- **[Ask Claude about Chinese law](https://global-law.lexifina.com/v1/try_claude?country=china)**: opens Claude with a first question ready.
- **[Ask ChatGPT](https://global-law.lexifina.com/v1/try_chatgpt?country=china)**: the same question in ChatGPT.
- **[Search Chinese law on our site](https://lexifina.com/law?country=china&q=%E5%B9%B4%E4%BC%91%E5%81%87)**: a search for "年休假" (annual leave), with each provision's text and its versions, no account needed.
- **[Developer REST API](https://global-law.lexifina.com/v1/search_law?query=%E5%B9%B4%E4%BC%91%E5%81%87&jurisdiction=china)**: the same search as JSON, with no key. See the [documentation here](https://lexifina.com/api/global-law).

Both assistants read the record through the free Global law connector (MCP, `https://global-law.lexifina.com/mcp`); the first time, the chat gives you the link that adds it. Ask in Chinese or in English.

**Host it yourself easily.** All it takes is git and Python, and the tools run on your machine:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add china/national/acts
python3 tools/law.py show 2026-01-01 china/national/acts/laodonghetongfa/art-066.md
```

Opened in Claude Code, Cursor, VS Code or Codex, the clone also starts a local MCP server with the same tools ([MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md)).

## Dates

Each commit is dated at noon, Asia/Shanghai, on the day the version took effect, and carries it in its `In-force:` trailer; the versions of every law but the Constitution also say where the day comes from, in `In-force-evidence:`:

- for a law as adopted or revised, its own commencement article (本法自……起施行);
- for a version made by an amending decision or a 刑法修正案, the commencement it states (本决定自……起施行, 本修正案自……起施行), often the day it was promulgated (自公布之日起施行); each of the Constitution's five amendments was adopted, promulgated and in force on the same day;
- a correction to the standard text printed in the 全国人大常委会公报 (two, both to the 1997 Criminal Law) carries the day of the version it corrects, and `tools/on_date.py` applies it to that version.

Each change is credited to the act that made it, as 中国人大网 names it (`中华人民共和国刑法修正案（十一）（2020年）`), at an address that cannot exist (`xingfa-xzan-2020@npc.gov.cn.invalid`). Where the record starts at a law's current consolidated text (45 laws), the whole text is credited to the latest amending act; the oldest texts of the Criminal Procedure Law (1997) and the Company Law (2018), the two corrections and one typographic difference in the Constitution's official 2018 text are credited to the publisher, `中国人大网 (全国人大常委会办公厅)`.

## How it is checked

- `tools/check_repo.py` compares the Constitution's 1982 version and its current text with the official pages, byte for byte and again by the letters and digits an independent extractor reads, and checks that every new wording an amendment quotes is in that version's files. The versions in between have no official consolidated text: they are the amendments applied.
- For every other act, the letters and digits of each source page (目录 and headings taken out) must equal those of the act's files, in order.
- `tools/test_repo.py` checks that `git blame` names an amending act, that `tools/on_date.py` gives the text before and after a known amendment, and that every law commit has an `In-force:` trailer. Two builds of the Constitution from the same pages gave the same head hash; see [`REPRODUCE.md`](REPRODUCE.md).
- History is append-only: no merge commits, the laws were added on top of the Constitution's history, and no published commit is rewritten.
- [vulnerabilities/](vulnerabilities/README.en.md): possible drafting mistakes in this law, found by global-law's detectors and checked by hand. Not run yet.

## What it does not show

- **Most national laws.** 173 are here; others in force, such as the 个人所得税法, the 网络安全法, the 食品安全法 and the 消费者权益保护法, are not yet.
- **Earlier wording of 97 laws.** Their record starts at a revision (修订, 50 laws), at the current consolidated text (45) or at the oldest full text 中国人大网 serves (2).
- **Repealed laws**, such as the 合同法 and the 物权法, which the 民法典 repealed on 1 January 2021.
- **Administrative and local regulations, judicial interpretations and case law**: the record holds the laws of the National People's Congress and its Standing Committee only. The National Laws Database (flk.npc.gov.cn) was not used: its robots.txt forbids automated collection.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [中国人大网](http://www.npc.gov.cn) (全国人大常委会办公厅, General Office of the NPC Standing Committee) | Official site of the NPC: the Constitution and its amendments, laws, amending decisions | partly: laws as adopted or revised and the decisions that amended them; otherwise the current text only | Each version names its page in a `Source:` trailer, and a consolidated text the decision behind it in `Decision:` |
| 全国人大常委会公报 (on 中国人大网) | Gazette of the NPC Standing Committee, as PDF | the text as published | The standard text of a law (立法法); used for the 民法典 and for the 1997 Criminal Law and its amendments to 2021 |

## Licence

See [`LICENSE`](LICENSE). Laws, resolutions and decisions of state organs, and their official translations, are not protected by copyright in China (著作权法第五条); 中国人大网 states no reuse terms for these pages. The tools and documentation are by Lexifina, under the MIT licence.

No AI model wrote or changed legal text, and none runs when the history is built; an AI model researched the source and wrote the scripts and the documentation (see [`REPRODUCE.md`](REPRODUCE.md)).

## Visualisations

- [visualisations/](visualisations/README.en.md): charts drawn from this repository. Not drawn yet.

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
