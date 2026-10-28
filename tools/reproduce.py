"""Writes data/versioonid.json and REPRODUCE.md into the Estonian law repository, from the facts of the build that
made it. Called by build.py; kept apart so the record of how the repository was made reads as one document.

    python reproduce.py --compare REPO_A REPO_B    # compare two builds commit by commit; record it in verification.json
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = 'https://www.riigiteataja.ee'
API = SITE + '/public-api/api/v1'


def write_manifest(repo: Path, built: list[dict], acts: dict[str, dict], today: str) -> str:
    """Every source file the record comes from, with its sha256, so a rebuild can show it read the same bytes."""
    out = {'retrieved_for': today, 'source': API, 'acts': [{
        'slug': b['act']['slug'], 'group': b['act']['group'], 'title': b['versions'][-1]['meta']['title'],
        'short': b['versions'][-1]['meta']['short'],
        'versions': [{'id': v['id'], 'from': v['meta']['from'], 'to': v['meta']['to'], 'kind': v['meta']['kind'],
                      'xml': v['xml'], 'sha256': v['sha256']} for v in b['versions']],
    } for b in built], 'amending_acts': [{'id': a['id'], 'label': a['label'], 'xml': a['xml'], 'sha256': a['sha256']}
                                         for a in sorted(acts.values(), key=lambda a: a['id'])]}
    text = json.dumps(out, ensure_ascii=False, indent=1) + '\n'
    (repo / 'data').mkdir(exist_ok=True)
    (repo / 'data' / 'versioonid.json').write_text(text, encoding='utf-8', newline='\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def editorial_rows(built: list[dict], short: dict[str, str]) -> list[str]:
    import build as B
    rows = []
    for b in built:
        slug = b['act']['slug']
        by_day: dict[str, Counter] = {}
        for c in b['changes']:
            if not c['causes']:
                by_day.setdefault(c['day'], Counter())[B.editorial_kind(c)] += 1
        for day, n in sorted(by_day.items()):
            rows.append(f'| {short[slug]} | {day} | {n.get("typesetting", 0)} | {n.get("unreadable", 0)} | {n.get("editorial", 0)} |')
    return rows


def write_docs(repo: Path, built: list[dict], acts: dict[str, dict], stats: dict, requests: list[dict], today: str):
    import build as B
    data_sha = write_manifest(repo, built, acts, today)
    blob = subprocess.run(['git', 'hash-object', str(HERE / 'build.py')], capture_output=True, text=True).stdout.strip()
    pyv = sys.version.split()[0]
    gitv = subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()
    curlv = subprocess.run(['curl', '--version'], capture_output=True, text=True).stdout.split('\n')[0].split(' (')[0]
    files = {r['file'] for r in requests if r['file'].exists()}
    days = sorted({dt.date.fromtimestamp(f.stat().st_mtime).isoformat() for f in files})
    urls = {r['url'] for r in requests}
    n_list = sum(1 for u in urls if u.endswith('/redaktsioonid'))
    n_xml = sum(1 for u in urls if u.endswith('/xml'))
    short = {b['act']['slug']: b['versions'][-1]['meta']['short'] for b in built}
    verification = json.loads((HERE / 'verification.json').read_text(encoding='utf-8')) if (HERE / 'verification.json').exists() else {}
    det = verification.get('determinism')
    chk = verification.get('check')

    rows = '\n'.join(
        f'| {short[b["act"]["slug"]]} | {b["versions"][-1]["meta"]["title"]} | {b["act"]["group"]} | {len(b["versions"])} | '
        f'{b["versions"][0]["meta"]["from"]} to {b["versions"][-1]["meta"]["from"]} | {b["start_day"]} | '
        f'{sum(1 for k in b["states"][-1]["units"] if k != "sisukord")} |' for b in built)
    changes = [c for b in built for c in b['changes']]
    basis = Counter(c['basis'] if len(c['causes']) < 2 else 'ambiguous' for c in changes)
    used = {x for c in changes for x in c['causes']}
    silent = []
    for b in built:
        listed = {m['act']: m for v in b['versions'] for m in v['meta']['amendments'] if m['act']}
        for act_id, m in sorted(listed.items(), key=lambda x: (x[1]['in_force'] or '', x[0])):
            if act_id not in used:
                silent.append(f'| {short[b["act"]["slug"]]} | {m["label"]} | {m["in_force"] or ""} |')
    notes = Counter()
    for b in built:
        for v in b['versions']:
            for n in v['notes']:
                notes[(short[b['act']['slug']], n['kind'])] += 1
            if v['meta']['corrections']:
                notes[(short[b['act']['slug']], 'veaparandus')] += 1
    inside = [(short[b['act']['slug']], s['day'], b['versions'][s['version']]['meta']['from']) for b in built for s in b['states'] if s['inside']]

    if det:
        det_text = (f'On {det["date"]} two builds from the same cache into empty folders were compared commit by commit: '
                    f'{det["commits"]} commits on `main`, every one with the same hash, the same tree and the same tags '
                    f'({det["tags"]} tags). The tip of the law history (the commit before this documentation) was '
                    f'`{det["law_tip"]}` in both; the documentation commit was `{det["head"]}` in both. This file '
                    'was then rewritten with that result, which changes only the last commit.')
    else:
        det_text = 'Not yet recorded.'
    if chk:
        g = chk['git_vs_xml']
        t = chk['xml_vs_txt']
        chk_text = '\n'.join(
            [f'- **git against the XML:** ' + '; '.join(f'{short[s]}: {r["states"]} days ({r["versions"]} versions), {r["files"]} files, {r["mismatches"]} mismatches' for s, r in g.items()) + '.',
             f'- **XML against Riigi Teataja\'s plain text:** ' + '; '.join(f'{short[s]}: {r["versions"]} versions, {len(r["mismatches"])} differ' for s, r in t.items()) + '.',
             f'- **Source files:** {chk["sha256"]["files"]} sha256 sums in `data/versioonid.json`, {len(chk["sha256"]["mismatches"])} mismatches.',
             f'- Result: **{"all checks passed" if chk["ok"] else "FAILED"}**.'])
    else:
        chk_text = 'Not yet recorded.'

    text = f"""# How this history was made, and how to make it again

This file records exactly how the repository was built: the sources, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/estonia-law && cd estonia-law
python -X utf8 tools/build.py --repo ../rebuilt --today {today}
git -C ../rebuilt rev-parse main~1        # {stats['law_tip']}, the tip of the law history here
python -X utf8 tools/check_repo.py --repo ../rebuilt
```

`tools/build.py` needs Python 3.12 or later and git; it uses only the standard library (and `curl` when Python's own
HTTPS fails on a certificate chain). It reads Riigi Teataja's public API, or its own cache in `.cache/` beside the
script, and writes this repository from scratch. With the same data and the same `--today` it gives the same commits
with the same hashes. `data/versioonid.json` lists every source file with its sha256, so a rebuild can show it read
the same bytes (data sha256 of that file: `{data_sha}`). Riigi Teataja can publish new versions or edit old ones, so
a rebuild on a later day can differ; the sha256 sums show where.

## Sources

All legal text and all information about changes come from **Riigi Teataja**, the official online publication of
the Republic of Estonia, published by the Ministry of Justice and Digital Affairs. Nothing was typed in, summarised
or rewritten.

| What | Where |
| --- | --- |
| The consolidated versions of an act, by its group id | `{API}/akt/<group>/redaktsioonid` |
| Each version's text, its validity dates, its amendment marks and its list of amending acts | `{API}/akt/<id>/xml` (schema `tyviseadus_1_10.02.2010`) |
| Each amending act's title, issuer and dates | `{API}/akt/<id>/xml` (schema `muutmisseadus_1_10.02.2010`, or the act's own) |
| Riigi Teataja's plain text of each version, for the check only | `{API}/akt/<id>/txt` |

These are the endpoints Riigi Teataja's own web application calls (found in its JavaScript bundle). The older
`https://www.riigiteataja.ee/akt/<id>.xml` addresses that earlier tools used (LawVM) now return the web application.

| Act | Title | Group | Versions | Valid from | First commit | Sections today |
| --- | --- | ---: | ---: | --- | --- | ---: |
{rows}

The build read {n_list} version lists and {n_xml} XML files ({len(urls)} addresses); `check_repo.py` also reads one
plain-text file per version. The data was retrieved on {', '.join(days) if days else today}, one request at a time
with at least 1.5 seconds between requests, with the user agent `{B.UA}`.

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

1. `python -X utf8 scripts/estonia-law/build.py --today {today}` in Lexifina's own repository fetched the sources
   into the cache and wrote this repository. `tools/build.py` here is the same file as `scripts/estonia-law/build.py`
   there (git blob `{blob}`), with `tools/reproduce.py`, which writes this file, and `tools/check_repo.py`.
2. A second and third build with `--offline` (cache only) into empty folders were compared commit by commit (below).
3. `python -X utf8 scripts/estonia-law/check_repo.py --write` checked the repository (below).
4. The final build wrote this repository, and `git push -f origin main --tags` published it to GitHub, private.

It ran with Python {pyv}, {gitv} and {curlv} on Windows 11. No network service other than Riigi Teataja is involved.

### Rebuild check

{det_text}

### Check against Riigi Teataja

{chk_text}

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
- **Changes.** Consecutive states are compared section by section. {len(changes)} section changes were found.
- **Cause.** A change is credited to an act only on Riigi Teataja's own evidence, tried in this order:
  1. an amendment mark that is new in the section and dated the day of the change ({basis.get('new mark', 0) + basis.get('mark', 0)} changes);
  2. a mark in the section naming an act whose entry into force on that day (in part, "osaliselt …") the version's
     list of amending acts gives ({basis.get('mark and act list', 0)});
  3. a mark dated that day on the heading of the chapter or division the section is in, where a chapter was replaced
     whole ({basis.get('chapter mark', 0)});
  4. otherwise no act: the change is committed by `Riigi Teataja` and labelled ({basis.get('none', 0)}).
  A section whose marks name two acts in force on the same day, without saying which wrote which line, is committed
  by `Riigi Teataja` naming both ({basis.get('ambiguous', 0)}).
- **Commits.** {stats['commits']} commits: {stats['first_commits']} first texts (one per act), {stats['law_commits']}
  commits by amending acts (one per act per day it took effect, across all three laws),
  {stats['editorial_commits']} labelled changes without an amendment mark, {stats['ambiguous_commits']} labelled
  change with two candidate acts, and this documentation.
  - The author of a law commit is the amending act, `RT I, 03.01.2020, 2 <akt-103012020002@riigiteataja.invalid>`;
    the id is the act's Riigi Teataja id. The committer is `Lexifina <estonia-law@lexifina.com>`.
  - Author and committer dates are noon in Tallinn (UTC+2, or UTC+3 in summer time) on the day the change took
    effect. No date is before 1970, so none is clamped.
  - Trailers: `Issuer:`, `Adopted:`, `Proclaimed:`, `Published:`, `In-force:`, `Affecting:`, `Cause-basis:`,
    `Source:`; editorial commits have `In-force:` (the day the consolidated text changed) and `Version:`.
  - {stats['tags']} tags: one per act per day it changed (`ps/2015-08-13`) and one per amending act
    (`akt/103012020002`, or `akt/<id>/<day>` for an act that took effect in parts).
  - Changes in force after {today} would go on the branch `tulevik`; there are none in these acts today.

### Changes without an amendment mark

Committed by `Riigi Teataja`, never credited to a law. Counted by section:

| Act | Day | Typesetting only | Unreadable characters | Other editorial |
| --- | --- | ---: | ---: | ---: |
{chr(10).join(editorial_rows(built, short))}

"Typesetting" is a change of spaces or line breaks only. "Unreadable characters" are U+FFFD replacement characters
that are in Riigi Teataja's own XML of three RKVS versions (2004-04-08, 2004-10-29, 2005-07-10); the record keeps
them, as the source has them, and the next version's clean text is again an unexplained change. "Other editorial"
covers changes such as dropping the lists of earlier publication references after a statute's name (2009), replacing
the text of spent amending provisions with "[Käesolevast tekstist välja jäetud]" ("left out of this text"), and
moving a punctuation mark.

### Amending acts in the versions' lists that changed no text here

| Act | Amending act | In force |
| --- | --- | --- |
{chr(10).join(silent) if silent else '| – | – | – |'}

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
3. **Two days fall inside a version** ({', '.join(f'{a} {d} (version from {f})' for a, d, f in inside)}):
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
   directives. Counted in the source: {', '.join(f'{a} {k}: {n} versions' for (a, k), n in sorted(notes.items()))}.
7. **Riigi Teataja places §§ 104–110 of the Constitution outside any chapter** in its XML, after chapter VII; the
   act's README lists them under chapter VII. This affects only the README.
8. **Older marks give a reference without the act's id** (11 marks in RKVS); the id comes from the act-level list
   of amending acts in the same versions, which pairs the same reference with an id.

## What an AI model did

This repository was built on {today} in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
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

Checked on {today}:

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
"""
    (repo / 'REPRODUCE.md').write_text(text, encoding='utf-8', newline='\n')


def compare(a: str, b: str):
    """Compares two builds commit by commit and records the result in verification.json."""
    def run(repo, *args):
        return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, encoding='utf-8', check=True).stdout
    la = run(a, 'log', '--format=%H %T', 'main').split('\n')
    lb = run(b, 'log', '--format=%H %T', 'main').split('\n')
    ta = run(a, 'show-ref', '--tags')
    tb = run(b, 'show-ref', '--tags')
    same = la == lb and ta == tb
    print(f'{len(la) - 1} commits, identical: {same}')
    if not same:
        raise SystemExit(1)
    path = HERE / 'verification.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    data['determinism'] = {'date': dt.date.today().isoformat(), 'commits': len(la) - 1, 'tags': len(ta.splitlines()),
                           'head': run(a, 'rev-parse', 'main').strip(), 'law_tip': run(a, 'rev-parse', 'main~1').strip(),
                           'identical': True}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--compare':
        compare(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
