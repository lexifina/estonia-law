<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Watching the sources: what is watched for Estonia

[Eesti keel](WATCHING.md)

How global-law watches every country's sources: [global-law WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md). This page is the same for Estonia only: every official source this repository takes text from, what is read on it, how often and when it was last read. Every read and what came of it: [monitoring/](monitoring/README.en.md).

| Source | What is read | Folders | How often | Last read | State |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (consolidated texts)](https://www.riigiteataja.ee) | the number of laws in force, the laws whose consolidated version came into force since the last check (the public API's search, newest first), and the version list of each law held here | `ps/`, `seadused/` | daily | 2026-11-23 09:53 UTC | watched: lists only, no texts, one request every 6 seconds (its API limits how many it answers); some texts here come from copies of Riigi Teataja's data (legalize-ee, lahend.ee: see PLAN.md) |
| [Riigikogu open data (drafts and adopted laws)](https://api.riigikogu.ee) | the register of every draft of every Riigikogu term, with its stage, status and status day (api/volumes/drafts, about one request per term) | `riigikogu/` | daily | 2026-11-23 10:11 UTC | watched: drafts and adopted laws, one request every 3 seconds (the API limits bursts); votes, transcripts and documents in riigikogu/ are not compared yet |
| [Tartu city council document register](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | — | `kov/tartu/` | — | — | not watched yet: its robots.txt disallows all automated reading (Disallow: /), so it is not read; Riigi Teataja publishes the council's regulations but not its decisions |
| [EU Publications Office (Estonia's measures transposing EU directives)](https://publications.europa.eu/webapi/rdf/sparql) | every national implementing measure Estonia notified, with its notification day and the day the record last changed (one SPARQL query) | `eu-nim/` | daily | 2026-11-23 10:12 UTC | watched: records of the measures only; their texts are in Riigi Teataja |

Sources are read within their robots.txt and terms, with pauses between requests.
