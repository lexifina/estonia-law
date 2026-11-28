<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Monitoring: what is read and what came of it

[Eesti keel](README.md)

How global-law monitors every country: [global-law monitoring/](https://github.com/lexifina/global-law/tree/main/monitoring). This page is the same for Estonia only: every time an official source is read, when, and what came of it (acts added, changed and removed). The machine-readable form is [data/checks/](../data/checks/) (JSON Lines, schema `lexifina-check/1`), in `git log` as `Kind: check` commits, and month by month in [checks/](checks/).

**Last check:** 2026-11-28 05:45 UTC, EU Publications Office (Estonia's measures transposing EU directives): 11 addresses read; 0 added, 0 changed, 0 removed; no change; 14 not published, 0 of them with no reason.

## Sources

| Source | Folders | How often | Last successful check | Last result | State |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (consolidated texts)](https://www.riigiteataja.ee) | `ps/`, `seadused/` | daily | 2026-11-28 05:43 UTC | no change | watched: one request every 6 seconds (its API limits how many it answers); texts here that came from copies of Riigi Teataja's data (legalize-ee, lahend.ee: see PLAN.md) are set to Riigi Teataja's own XML, as tools/build.py writes it, by correction commits |
| [Riigikogu open data (drafts and adopted laws)](https://api.riigikogu.ee) | `riigikogu/` | daily | 2026-11-28 05:44 UTC | changes found | watched: drafts and adopted laws, one request every 3 seconds (the API limits bursts); votes, transcripts and documents in riigikogu/ are not compared yet; the adopted texts of new laws are not written here yet (the tool that read them is gone) |
| [Tartu city council document register](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | `kov/tartu/` | — | — | — | not watched yet: its robots.txt disallows all automated reading (Disallow: /), so it is not read; Riigi Teataja publishes the council's regulations but not its decisions |
| [EU Publications Office (Estonia's measures transposing EU directives)](https://publications.europa.eu/webapi/rdf/sparql) | `eu-nim/` | daily | 2026-11-28 05:45 UTC | no change | watched: records of the measures only; their texts are in Riigi Teataja |

## The last 30 days

| Started (UTC) | Source | Read | Added | Changed | Removed | Not published (no reason) | Result | Commits |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| [2026-11-28 05:44](checks/2026-11.md#ee-eu-nim-20261128t054451z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-28 05:43](checks/2026-11.md#ee-riigikogu-20261128t054321z) | riigikogu | 21 | 0 | 10 | 0 | 392 (0) | changes found | [10](https://github.com/lexifina/estonia-law/compare/92e5777d638c...372f73b20d2d) |
| [2026-11-28 05:00](checks/2026-11.md#ee-riigi-teataja-20261128t050005z) | riigi-teataja | 43 | 0 | 0 | 0 | 33 (0) | no change | — |
| [2026-11-27 05:44](checks/2026-11.md#ee-eu-nim-20261127t054459z) | eu-nim | 12 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-27 05:43](checks/2026-11.md#ee-riigikogu-20261127t054327z) | riigikogu | 21 | 9 | 10 | 0 | 392 (0) | changes found | [20](https://github.com/lexifina/estonia-law/compare/06f3eaf58e5a...63485a9b00b6) |
| [2026-11-27 05:00](checks/2026-11.md#ee-riigi-teataja-20261127t050004z) | riigi-teataja | 44 | 0 | 6 | 0 | 32 (0) | changes found | — |
| [2026-11-26 05:13](checks/2026-11.md#ee-eu-nim-20261126t051356z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-26 05:12](checks/2026-11.md#ee-riigikogu-20261126t051213z) | riigikogu | 21 | 1 | 30 | 0 | 392 (0) | changes found | [31](https://github.com/lexifina/estonia-law/compare/8fee00e8b60e...76a562a246cf) |
| [2026-11-26 05:00](checks/2026-11.md#ee-riigi-teataja-20261126t050005z) | riigi-teataja | 46 | 0 | 0 | 0 | 18 (0) | no change | — |
| [2026-11-25 05:11](checks/2026-11.md#ee-eu-nim-20261125t051115z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-25 05:09](checks/2026-11.md#ee-riigikogu-20261125t050943z) | riigikogu | 21 | 2 | 19 | 0 | 395 (0) | changes found | [21](https://github.com/lexifina/estonia-law/compare/3383a13d004c...4e58c3fe1772) |
| [2026-11-25 05:00](checks/2026-11.md#ee-riigi-teataja-20261125t050003z) | riigi-teataja | 45 | 0 | 0 | 0 | 18 (0) | no change | — |
| [2026-11-24 05:10](checks/2026-11.md#ee-eu-nim-20261124t051017z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-24 05:09](checks/2026-11.md#ee-riigikogu-20261124t050912z) | riigikogu | 21 | 0 | 0 | 0 | 392 (0) | no change | — |
| [2026-11-24 05:00](checks/2026-11.md#ee-riigi-teataja-20261124t050001z) | riigi-teataja | 46 | 0 | 0 | 0 | 18 (0) | no change | — |
| [2026-11-23 22:42](checks/2026-11.md#ee-eu-nim-20261123t224202z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | no change | — |
| [2026-11-23 22:40](checks/2026-11.md#ee-riigikogu-20261123t224056z) | riigikogu | 21 | 0 | 0 | 0 | 392 (0) | no change | — |
| [2026-11-23 21:49](checks/2026-11.md#ee-riigi-teataja-20261123t214924z) | riigi-teataja | 74 | 0 | 0 | 0 | 18 (0) | changes found | [45](https://github.com/lexifina/estonia-law/compare/b4648e5829a2...6346b05da7f5) |
| [2026-11-23 21:47](checks/2026-11.md#ee-eu-nim-20261123t214749z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | changes found | [9](https://github.com/lexifina/estonia-law/compare/5ed2f842869e...703326cc8062) |
| [2026-11-23 21:46](checks/2026-11.md#ee-riigikogu-20261123t214614z) | riigikogu | 21 | 2 | 4 | 0 | 400 (0) | changes found | [62](https://github.com/lexifina/estonia-law/compare/27f2436e23ba...5ed2f842869e) |
| [2026-11-23 21:21](checks/2026-11.md#ee-riigi-teataja-20261123t212128z) | riigi-teataja | 54 | 0 | 0 | 0 | 35 (0) | changes found `verify-differ` `audit-disagrees` | [3](https://github.com/lexifina/estonia-law/compare/5b6a11ff7ec4...27f2436e23ba) |
| [2026-11-23 10:12](checks/2026-11.md#ee-eu-nim-20261123t101202z) | eu-nim | 1 | 0 | 0 | 0 | 23 (0) | no change | — |
| [2026-11-23 10:11](checks/2026-11.md#ee-riigikogu-20261123t101115z) | riigikogu | 16 | 0 | 0 | 0 | 457 (0) | no change | — |
| [2026-11-23 09:53](checks/2026-11.md#ee-riigi-teataja-20261123t095348z) | riigi-teataja | 77 | 0 | 0 | 0 | 21 (0) | no change `publish-lag` | — |

## Check it yourself

```
python tools/checktrail.py                      # the latest check of every source
python tools/checktrail.py --day 2026-11-23     # every check of a day
python tools/checktrail.py --act <id>           # when an act was seen and published
git log --grep='^Kind: check' --format='%ci %s'  # the checks in the history
```

Only the official publication has legal force; the texts here are copies for reading and searching.
