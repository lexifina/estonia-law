# How this history was made, and how to make it again

This file records exactly how the repository was built: the sources, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/estonia-law && cd estonia-law
python -X utf8 tools/build.py --repo ../rebuilt --today 2026-10-28
git -C ../rebuilt rev-parse main~1        # 81f02b1b0be6bab0d6327c6fe74a5a8e84275059, the tip of the law history here
python -X utf8 tools/check_repo.py --repo ../rebuilt
```

`tools/build.py` needs Python 3.12 or later and git; it uses only the standard library (and `curl` when Python's own
HTTPS fails on a certificate chain). It reads Riigi Teataja's public API, or its own cache in `.cache/` beside the
script, and writes this repository from scratch. With the same data and the same `--today` it gives the same commits
with the same hashes. `data/versioonid.json` lists every source file with its sha256, so a rebuild can show it read
the same bytes (data sha256 of that file: `ba615441cb346f2deae61962bd017bdf375aab229f09bd4db30bcd269d7e419c`). Riigi Teataja can publish new versions or edit old ones, so
a rebuild on a later day can differ; the sha256 sums show where.

## Sources

All legal text and all information about changes come from **Riigi Teataja**, the official online publication of
the Republic of Estonia, published by the Ministry of Justice and Digital Affairs. Nothing was typed in, summarised
or rewritten.

| What | Where |
| --- | --- |
| The consolidated versions of an act, by its group id | `https://www.riigiteataja.ee/public-api/api/v1/akt/<group>/redaktsioonid` |
| Each version's text, its validity dates, its amendment marks and its list of amending acts | `https://www.riigiteataja.ee/public-api/api/v1/akt/<id>/xml` (schema `tyviseadus_1_10.02.2010`) |
| Each amending act's title, issuer and dates | `https://www.riigiteataja.ee/public-api/api/v1/akt/<id>/xml` (schema `muutmisseadus_1_10.02.2010`, or the act's own) |
| Riigi Teataja's plain text of each version, for the check only | `https://www.riigiteataja.ee/public-api/api/v1/akt/<id>/txt` |

These are the endpoints Riigi Teataja's own web application calls (found in its JavaScript bundle). The older
`https://www.riigiteataja.ee/akt/<id>.xml` addresses that earlier tools used (LawVM) now return the web application.

| Act | Title | Group | Versions | Valid from | First commit | Sections today |
| --- | --- | ---: | ---: | --- | --- | ---: |
| PS | Eesti Vabariigi põhiseadus | 151381 | 7 | 2002-06-01 to 2026-03-01 | 1992-07-03 | 169 |
| RKVS | Riigikogu valimise seadus | 155356 | 29 | 2002-07-18 to 2024-10-01 | 2002-07-18 | 113 |
| IKS | Isikuandmete kaitse seadus | 1045568 | 6 | 2019-01-15 to 2026-10-01 | 2019-01-15 | 78 |

The build read 3 version lists and 82 XML files (85 addresses); `check_repo.py` also reads one
plain-text file per version. The data was retrieved on 2026-10-28, one request at a time
with at least 1.5 seconds between requests, with the user agent `Lexifina estonia-law builder (https://github.com/lexifina/estonia-law; corpus@lexifina.com)`.

### Why these acts

- **The Constitution (PS)**: the act every corpus starts from. Seven consolidated versions since 2002, every change
  marked, with a 1992 original text.
- **The Riigikogu Election Act (RKVS)**: frequently amended (29 versions from 2002 to 2024), well structured (chapters,
  divisions, sections, paragraphs, points), and every version is in the XML. It also shows the older versions' quirks
  that a careful record has to handle.
- **The Personal Data Protection Act (IKS)**: a recent act (2019) amended in 2023–2026, as the counterpart of the
  Swiss record's data protection act.

All three have XML for every version, and every version names its amending acts with their in-force dates, so the
cause and day of each change can be read rather than guessed.

## The build, step by step

1. `python -X utf8 scripts/estonia-law/build.py --today 2026-10-28` in Lexifina's own repository fetched the sources
   into the cache and wrote this repository. `tools/build.py` here is the same file as `scripts/estonia-law/build.py`
   there (git blob `e9135cf99ee72212fae8cb6ac11d85c76df3bfe4`), with `tools/reproduce.py`, which writes this file, and `tools/check_repo.py`.
2. A second and third build with `--offline` (cache only) into empty folders were compared commit by commit (below).
3. `python -X utf8 scripts/estonia-law/check_repo.py --write` checked the repository (below).
4. The final build wrote this repository, and `git push -f origin main --tags` published it to GitHub, private.

It ran with Python 3.12.10, git version 2.46.0.windows.1 and curl 8.21.0 on Windows 11. No network service other than Riigi Teataja is involved.

### Rebuild check

On 2026-10-28 two builds from the same cache into empty folders were compared commit by commit: 59 commits on `main`, every one with the same hash, the same tree and the same tags (87 tags). The tip of the law history (the commit before this documentation) was `81f02b1b0be6bab0d6327c6fe74a5a8e84275059` in both; the documentation commit was `e7a75916112c180ade84c97449d7aaa1ec78e6db` in both. This file was then rewritten with that result, which changes only the last commit.

### Check against Riigi Teataja

- **git against the XML:** PS: 8 days (7 versions), 1360 files, 0 mismatches; RKVS: 30 days (29 versions), 2842 files, 0 mismatches; IKS: 6 days (6 versions), 468 files, 0 mismatches.
- **XML against Riigi Teataja's plain text:** PS: 7 versions, 0 differ; RKVS: 29 versions, 0 differ; IKS: 6 versions, 0 differ.
- **Source files:** 82 sha256 sums in `data/versioonid.json`, 0 mismatches.
- Result: **all checks passed**.

The first check compares git with the XML on every day the text changed: each version's first day, and the days
inside a version listed under "Decisions" below. The second compares the XML reading with Riigi Teataja's own plain
text of each version, ignoring whitespace, with superscripts written as digits, after removing the notes Riigi
Teataja adds in brackets ("[RT I, 03.01.2020, 2 - jõust. 13.01.2020]", the citation in "[Kehtetu - …]"), its
error-correction notes ("Veaparandus"), the Constitution's closing "Õiend" and the "( )" it prints for a paragraph
without a number.

## How the text and the commits are derived

Everything below is done by `tools/build.py`, deterministically.

- **Text.** Each section (paragrahv) of each version is one file, `para-NNN.md` after Riigi Teataja's own element
  id (`para5b1` is § 5¹, so `para-005b1.md`); the preamble is `preambul.md` and the chapter and division headings are
  `sisukord.md`. Each lõige and each punkt is one line with its number, followed by a blank line; points are list
  items. A line break printed inside a provision starts a new line. A provision Riigi Teataja shows as repealed reads
  `[Kehtetu]`. Superscript digits are written as superscript characters (§ 5¹); other superscripts as `^` (the
  divisors `2^0,9` in RKVS § 63). Non-breaking spaces become spaces and runs of whitespace one space. Amendment
  marks, footnotes on EU law and the publisher's notes are read separately and left out of the text.
- **Changes.** Consecutive states are compared section by section. 385 section changes were found.
- **Cause.** A change is credited to an act only on Riigi Teataja's own evidence, tried in this order:
  1. an amendment mark that is new in the section and dated the day of the change (297 changes);
  2. a mark in the section naming an act whose entry into force on that day (in part, "osaliselt …") the version's
     list of amending acts gives (1);
  3. a mark dated that day on the heading of the chapter or division the section is in, where a chapter was replaced
     whole (3);
  4. otherwise no act: the change is committed by `Riigi Teataja` and labelled (83).
  A section whose marks name two acts in force on the same day, without saying which wrote which line, is committed
  by `Riigi Teataja` naming both (1).
- **Commits.** 59 commits: 3 first texts (one per act), 44
  commits by amending acts (one per act per day it took effect, across all three laws),
  10 labelled changes without an amendment mark, 1 labelled
  change with two candidate acts, and this documentation.
  - The author of a law commit is the amending act, `RT I, 03.01.2020, 2 <akt-103012020002@riigiteataja.invalid>`;
    the id is the act's Riigi Teataja id. The committer is `Lexifina <estonia-law@lexifina.com>`.
  - Author and committer dates are noon in Tallinn (UTC+2, or UTC+3 in summer time) on the day the change took
    effect. No date is before 1970, so none is clamped.
  - Trailers: `Issuer:`, `Adopted:`, `Proclaimed:`, `Published:`, `In-force:`, `Affecting:`, `Cause-basis:`,
    `Source:`; editorial commits have `In-force:` (the day the consolidated text changed) and `Version:`.
  - 87 tags: one per act per day it changed (`ps/2015-08-13`) and one per amending act
    (`akt/103012020002`, or `akt/<id>/<day>` for an act that took effect in parts).
  - Changes in force after 2026-10-28 would go on the branch `tulevik`; there are none in these acts today.

### Changes without an amendment mark

Committed by `Riigi Teataja`, never credited to a law. Counted by section:

| Act | Day | Typesetting only | Unreadable characters | Other editorial |
| --- | --- | ---: | ---: | ---: |
| RKVS | 2003-03-21 | 0 | 0 | 8 |
| RKVS | 2004-01-01 | 7 | 0 | 0 |
| RKVS | 2004-02-14 | 8 | 0 | 0 |
| RKVS | 2004-04-08 | 9 | 3 | 0 |
| RKVS | 2004-10-29 | 7 | 6 | 0 |
| RKVS | 2005-07-10 | 7 | 3 | 0 |
| RKVS | 2006-07-14 | 1 | 3 | 2 |
| RKVS | 2009-01-16 | 0 | 0 | 5 |
| RKVS | 2011-01-01 | 9 | 0 | 4 |
| IKS | 2023-11-01 | 0 | 0 | 1 |

"Typesetting" is a change of spaces or line breaks only. "Unreadable characters" are U+FFFD replacement characters
that are in Riigi Teataja's own XML of three RKVS versions (2004-04-08, 2004-10-29, 2005-07-10); the record keeps
them, as the source has them, and the next version's clean text is again an unexplained change. "Other editorial"
covers changes such as dropping the lists of earlier publication references after a statute's name (2009), replacing
the text of spent amending provisions with "[Käesolevast tekstist välja jäetud]" ("left out of this text"), and
moving a punctuation mark.

### Amending acts in the versions' lists that changed no text here

| Act | Amending act | In force |
| --- | --- | --- |
| PS | RT I 2003, 64, 429 | 2004-01-06 |

For example the Constitution's 2003 Amendment Act (EU membership referendum) is a separate constitutional act that
Riigi Teataja lists with the Constitution but does not print in its text.

## Decisions made by hand

These were made after looking at the data, and are in the code.

1. **The text is the Estonian consolidated text.** English and Russian translations exist for some versions and
   have no legal force; they are not used.
2. **The first commit of an act whose first version is "algtekst-terviktekst"** (the original text, unamended) is
   dated the day the act came into force, as the XML's own `vastuvõetud / jõustumine` gives it, not the day Riigi
   Teataja's database begins. For the Constitution that is 1992-07-03, ten years before the first version
   (2002-06-01); the Constitution was first amended in 2003, so its text was the same throughout.
3. **Two days fall inside a version** (PS 2005-10-17 (version from 2004-01-06), RKVS 2014-07-01 (version from 2014-04-01)):
   - The Constitution's 2004 version prints both wordings of § 156(1), headed "[… sõnastus kuni 16.10.2005]" and
     "[… sõnastus alates 17.10.2005]". The record keeps the old wording until 16.10.2005 and commits the new one on
     17.10.2005, credited to RT I 2003, 29, 174, whose mark gives that day.
   - The RKVS version valid from 2014-04-01 was changed in place to replace "Regionaalminister" with "Valdkonna eest
     vastutav minister" in § 7(3) "from 1 July 2014", under § 107³(4) of the Government of the Republic Act; its mark
     names RT I, 29.06.2014, 109 and 2014-07-01. The record keeps the previous wording until 2014-06-30.
   These two are the only places where the git text on a version's first day is not that version's text, and the
   check compares them on the day the mark gives.
4. **A change is dated by the version that contains it**, which in every other case is the day its mark gives.
5. **Changes without a mark are labelled and never credited to an act**, even when only one act took effect that
   day; Riigi Teataja's editorial changes happen on such days too.
6. **Publisher's notes are not text**: the Constitution's closing "Õiend" (the editorial statement on which printing
   the text follows), HTML notes and signature blocks, error-correction notes ("Veaparandus") and footnotes naming EU
   directives. Counted in the source: PS html: 6 versions, PS õiend: 7 versions, RKVS html: 1 versions, RKVS veaparandus: 15 versions.
7. **Riigi Teataja places §§ 104–110 of the Constitution outside any chapter** in its XML, after chapter VII; the
   act's README lists them under chapter VII. This affects only the README.
8. **Older marks give a reference without the act's id** (11 marks in RKVS); the id comes from the act-level list
   of amending acts in the same versions, which pairs the same reference with an id.

## What an AI model did

This repository was built on 2026-10-28 in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
(model id `claude-opus-5-5`), working from a goal set by the user at Lexifina: private "git for law" repositories for
some smaller countries, to the standard of Lexifina's existing corpora (Swiss, UK, US, German).

The model:

- **Researched the source and the prior art:** Riigi Teataja's API (from its web application's JavaScript), its XML,
  the Riigi Teataja Act and the Copyright Act (read through the same API), and the projects below.
- **Wrote all the code and text in this repository:** `tools/build.py`, `tools/reproduce.py`,
  `tools/check_repo.py`, `tools/seisuga.py`, the README, this file and the licence, and chose the design in them.
- **Ran the commands above** and checked the results.

The model did **not**:

- **Write or edit any legal text.** Every word of every section, every date, reference and title is copied by the
  script from Riigi Teataja.
- **Take part in building or checking the history.** No AI model is called by any script here.

The user decided the scope and decides when, if ever, the repository is made public. The work was not reviewed line
by line by a lawyer. Only Riigi Teataja is authoritative.

## The research behind the design

Checked on 2026-10-28:

- [eliask/lawvm](https://github.com/eliask/lawvm) (MIT): compiles amending acts into point-in-time text and has
  Estonian support. We used its notes on Riigi Teataja: the `muutmismarge` elements and their `joustumine` dates,
  `terviktekstiGrupiID` as the id shared by an act's versions, "osaliselt <date>" notes for partial entry into
  force, and that the site needs curl-style fetching. Its `/akt/<id>.xml` and `akti_redaktsioonid.xml` addresses no
  longer serve data; we use the public API instead. No code was copied.
- [legalize-dev](https://github.com/legalize-dev): legislation as git repositories, one commit per consolidated
  version; no Estonian corpus was found there.
- Lexifina's own corpora (Swiss, UK, US Code, Grundgesetz), whose shared rules this repository follows.

Those projects commit consolidated versions or replay amending acts. This record makes each commit an amending act
on the day it took effect, names it from Riigi Teataja's own marks, and keeps every change the marks do not explain
apart and labelled.
