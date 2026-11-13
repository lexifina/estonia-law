# Estonian law, change by change

[Eesti](README.md) · **English**

<picture>
<source media="(prefers-color-scheme: dark)" srcset="data/effort-dark.svg">
<img alt="Estonian law in this repository: what it holds, changes by the year they took effect, completeness against the official sources, and the correctness of what is held" src="data/effort-light.svg" width="880">
</picture>

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is Estonia's national law, which global-law reads at `estonia/national/acts/`.

Three Estonian acts as a git repository: the Constitution (Eesti Vabariigi põhiseadus, PS), the Riigikogu Election Act (Riigikogu valimise seadus, RKVS) and the Personal Data Protection Act (Isikuandmete kaitse seadus, IKS). Each amending act is one commit, credited to that act and dated the day its changes took effect, at noon in Tallinn. The text is the Estonian consolidated text (terviktekst) published in [Riigi Teataja](https://www.riigiteataja.ee), the official online publication of the Republic of Estonia.

## The questions a lawyer asks, as git commands

| Question | Command |
| --- | --- |
| What did § 156 of the Constitution say on 1 January 2010? | `python tools/seisuga.py 2010-01-01 ps 156` |
| What did the whole Election Act say on 1 March 2015? | `python tools/seisuga.py 2015-03-01 rkvs` |
| Which act wrote each paragraph of § 48⁴ RKVS? | `git blame rkvs/para-048b4.md` |
| Every change to a section, with the act behind it | `git log -p ps/para-156.md` |
| Everything one amending act changed | `git show akt/103012020002` (tags are `akt/<Riigi Teataja id>`) |
| The act as it stood on a day | `git checkout ps/2015-08-13` (a tag per act per day it changed) |
| Every act that amended these laws, with its dates | [`muutmisaktid.csv`](muutmisaktid.csv) |
| Changes adopted but not yet in force | `git log main..tulevik` (empty today) |

## Dates

An Estonian act has several dates: adopted (vastu võetud), proclaimed by the President (välja kuulutatud), published in Riigi Teataja (avaldatud) and in force (jõustunud). The date that decides which text applies to a case is the day the change took effect, so **the author and committer date of each commit is that day, at noon in Tallinn**. The other dates are trailers in the commit message: `Adopted:`, `Proclaimed:`, `Published:`, `In-force:`. The day a change took effect is read from the amendment mark (muutmismärge) Riigi Teataja prints under each changed provision, and it is the day the consolidated version containing the change became valid.

## Who the author is

The author of a commit is the amending act, named by its Riigi Teataja reference (`RT I, 03.01.2020, 2`) at an address that cannot exist (`akt-103012020002@riigiteataja.invalid`, from the act's Riigi Teataja id), so `git blame` names the act that wrote each line. The committer is `Lexifina <estonia-law@lexifina.com>`. The first commit of each act is by the act as enacted (`RT 1992, 26, 349` for the Constitution).

A change is credited to an act only when Riigi Teataja's own marks say so: a mark on the changed section (or on its chapter heading, where a chapter was replaced whole) names the act and the day. Changes no mark explains are committed by `Riigi Teataja` and say so: spacing, corrupted characters in Riigi Teataja's own files for three 2004–2006 versions, and editorial changes such as dropping lists of publication references. One section that two acts changed on the same day, with marks that do not say which wrote which line, is a labelled commit by `Riigi Teataja` naming both.

## How it is checked

`tools/check_repo.py` reads every act back from git on every day its text changed (each of the 42 consolidated versions on its first day, plus two days inside a version) and compares every file with the text of that version in Riigi Teataja's XML: 0 mismatches in 4,670 files. It also compares the XML reading of each version with Riigi Teataja's own plain-text rendering of the same version (`/txt`), character by character apart from whitespace and Riigi Teataja's bracketed amendment notes: all 42 versions match. And it checks the sha256 of every source file against `data/versioonid.json`. Two builds from the same data give the same hashes for every commit and tag. Details in [`REPRODUCE.md`](REPRODUCE.md).

## What it does not show

- Versions before Riigi Teataja's electronic consolidated texts (2002). The Constitution was not amended before 2003, so its first commit is the 1992 text.
- Annexes, signatures and the publisher's notes (the "Õiend" at the end of the Constitution, error-correction notes); these are listed in REPRODUCE.md.
- Provisions of an act as enacted that came into force later than the act itself, unless Riigi Teataja published a separate version for them.
- Russian and English translations. Only the Estonian text has legal force.

Only Riigi Teataja is authoritative. This repository is a research aid.

## How it is built

`tools/build.py` reads Riigi Teataja's public API (`https://www.riigiteataja.ee/public-api/api/v1`), one request at a time with a pause between requests, and writes this repository from scratch. With the same data and the same `--today` it gives the same commits with the same hashes. No AI model runs when the history is built.

## Licence

The legal text is not protected by copyright (Autoriõiguse seadus § 5 p 3). Source: Riigi Teataja, https://www.riigiteataja.ee, published by the Ministry of Justice and Digital Affairs (Justiits- ja Digiministeerium). The history, messages, tables and tools are released under [CC0 1.0](LICENSE).

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
