<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Watching the sources: what is watched for Estonia

[Eesti keel](WATCHING.md)

How global-law watches every country's sources: [global-law WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md). This page is the same for Estonia only: every official source this repository takes text from, what is read on it, how often and when it was last read. Every read and what came of it: [monitoring/](monitoring/README.en.md).

| Source | What is read | Folders | How often | Last read | State |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (consolidated texts)](https://www.riigiteataja.ee) | the number of laws in force, the laws whose consolidated version came into force since the last check (the public API's search, newest first), the version list of each law held here, and the XML of each held law's version in force and of the versions after the one held (with the amending acts they name); for the audit, a few versions' plain text | `ps/`, `seadused/` | daily | 2026-11-23 21:21 UTC | watched: one request every 6 seconds (its API limits how many it answers); texts here that came from copies of Riigi Teataja's data (legalize-ee, lahend.ee: see PLAN.md) are set to Riigi Teataja's own XML, as tools/build.py writes it, by correction commits |
| [Riigikogu open data (drafts and adopted laws)](https://api.riigikogu.ee) | the register of every draft of every Riigikogu term, with its stage, status and status day (api/volumes/drafts, about one request per term) | `riigikogu/` | daily | 2026-11-23 21:46 UTC | watched: drafts and adopted laws, one request every 3 seconds (the API limits bursts); votes, transcripts and documents in riigikogu/ are not compared yet; the adopted texts of new laws are not written here yet (the tool that read them is gone) |
| [Tartu city council document register](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | — | `kov/tartu/` | — | — | not watched yet: its robots.txt disallows all automated reading (Disallow: /), so it is not read; Riigi Teataja publishes the council's regulations but not its decisions |
| [EU Publications Office (Estonia's measures transposing EU directives)](https://publications.europa.eu/webapi/rdf/sparql) | every national implementing measure Estonia notified, with its notification day and the day the record last changed (one SPARQL query) | `eu-nim/` | daily | 2026-11-23 21:47 UTC | watched: records of the measures only; their texts are in Riigi Teataja |

Sources are read within their robots.txt and terms, with pauses between requests.
