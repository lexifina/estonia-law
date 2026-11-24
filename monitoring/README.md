<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Seire: mida loetakse ja mis sellest tuli

[English](README.en.md)

Kuidas global-law seirab kõiki riike: [global-law monitoring/](https://github.com/lexifina/global-law/tree/main/monitoring). See leht teeb sama ainult ühe riigi (Eesti) kohta: iga kord, kui ametlikku allikat loetakse, millal see juhtus ja mis sellest tuli (lisatud, muudetud ja kehtetuks tunnistatud aktid). Masinloetav kuju on [data/checks/](../data/checks/) (JSON Lines, skeem `lexifina-check/1`), `git log`-is `Kind: check` commit'idena ja kuude kaupa kaustas [checks/](checks/).

**Viimane kontroll:** 2026-11-24 05:10 UTC, Euroopa Liidu Väljaannete Talitus (Eesti meetmed EL-i direktiivide ülevõtmiseks): loetud 11 aadressi; lisatud 0, muudetud 0, eemaldatud 0; muutusi ei ole; avaldamata 14, neist põhjuseta 0.

## Allikad

| Allikas | Kaustad | Kui tihti | Viimane õnnestunud kontroll | Viimane tulemus | Seis |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (terviktekstid)](https://www.riigiteataja.ee) | `ps/`, `seadused/` | iga päev | 2026-11-24 05:09 UTC | muutusi ei ole | jälgitakse: üks päring iga 6 sekundi järel (selle API piirab vastatavate päringute arvu); siinsed tekstid, mis pärinevad Riigi Teataja andmete koopiatest (legalize-ee, lahend.ee: vt PLAN.md), viiakse parandusega vastavusse Riigi Teataja enda XML-iga, nagu tools/build.py selle kirjutab |
| [Riigikogu avaandmed (eelnõud ja vastuvõetud seadused)](https://api.riigikogu.ee) | `riigikogu/` | iga päev | 2026-11-24 05:10 UTC | muutusi ei ole | jälgitakse: eelnõud ja vastuvõetud seadused, üks päring iga 3 sekundi järel (API piirab päringute hulka); riigikogu/ hääletusi, stenogramme ja dokumente veel ei võrrelda; uute seaduste vastuvõetud tekste siia veel ei kirjutata (neid lugenud tööriist on kadunud) |
| [Tartu Linnavolikogu dokumendiregister](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | `kov/tartu/` | — | — | — | veel ei jälgita: selle robots.txt keelab igasuguse automaatse lugemise (Disallow: /), seega seda ei loeta; Riigi Teataja avaldab volikogu määrused, kuid mitte otsuseid |
| [Euroopa Liidu Väljaannete Talitus (Eesti meetmed EL-i direktiivide ülevõtmiseks)](https://publications.europa.eu/webapi/rdf/sparql) | `eu-nim/` | iga päev | 2026-11-24 05:10 UTC | muutusi ei ole | jälgitakse: ainult meetmete kirjed; nende tekstid on Riigi Teatajas |

## Viimased 30 päeva

| Algus (UTC) | Allikas | Loetud | Lisatud | Muudetud | Eemaldatud | Avaldamata (põhjuseta) | Tulemus | Commit'id |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| [2026-11-24 05:10](checks/2026-11.md#ee-eu-nim-20261124t051017z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | muutusi ei ole | — |
| [2026-11-24 05:09](checks/2026-11.md#ee-riigikogu-20261124t050912z) | riigikogu | 21 | 0 | 0 | 0 | 392 (0) | muutusi ei ole | — |
| [2026-11-24 05:00](checks/2026-11.md#ee-riigi-teataja-20261124t050001z) | riigi-teataja | 46 | 0 | 0 | 0 | 18 (0) | muutusi ei ole | — |
| [2026-11-23 22:42](checks/2026-11.md#ee-eu-nim-20261123t224202z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | muutusi ei ole | — |
| [2026-11-23 22:40](checks/2026-11.md#ee-riigikogu-20261123t224056z) | riigikogu | 21 | 0 | 0 | 0 | 392 (0) | muutusi ei ole | — |
| [2026-11-23 21:49](checks/2026-11.md#ee-riigi-teataja-20261123t214924z) | riigi-teataja | 74 | 0 | 0 | 0 | 18 (0) | leiti muutusi | [45](https://github.com/lexifina/estonia-law/compare/b4648e5829a2...6346b05da7f5) |
| [2026-11-23 21:47](checks/2026-11.md#ee-eu-nim-20261123t214749z) | eu-nim | 11 | 0 | 0 | 0 | 14 (0) | leiti muutusi | [9](https://github.com/lexifina/estonia-law/compare/5ed2f842869e...703326cc8062) |
| [2026-11-23 21:46](checks/2026-11.md#ee-riigikogu-20261123t214614z) | riigikogu | 21 | 2 | 4 | 0 | 400 (0) | leiti muutusi | [62](https://github.com/lexifina/estonia-law/compare/27f2436e23ba...5ed2f842869e) |
| [2026-11-23 21:21](checks/2026-11.md#ee-riigi-teataja-20261123t212128z) | riigi-teataja | 54 | 0 | 0 | 0 | 35 (0) | leiti muutusi `verify-differ` `audit-disagrees` | [3](https://github.com/lexifina/estonia-law/compare/5b6a11ff7ec4...27f2436e23ba) |
| [2026-11-23 10:12](checks/2026-11.md#ee-eu-nim-20261123t101202z) | eu-nim | 1 | 0 | 0 | 0 | 23 (0) | muutusi ei ole | — |
| [2026-11-23 10:11](checks/2026-11.md#ee-riigikogu-20261123t101115z) | riigikogu | 16 | 0 | 0 | 0 | 457 (0) | muutusi ei ole | — |
| [2026-11-23 09:53](checks/2026-11.md#ee-riigi-teataja-20261123t095348z) | riigi-teataja | 77 | 0 | 0 | 0 | 21 (0) | muutusi ei ole `publish-lag` | — |

## Kontrolli ise

```
python tools/checktrail.py                      # iga allika viimane kontroll
python tools/checktrail.py --day 2026-11-23     # ühe päeva kõik kontrollid
python tools/checktrail.py --act <id>           # millal akti nähti ja avaldati
git log --grep='^Kind: check' --format='%ci %s'  # kontrollid ajaloos
```

Õigusjõud on ainult ametlikul avaldamisel (Riigi Teataja); siinsed tekstid on koopiad lugemiseks ja otsimiseks.
