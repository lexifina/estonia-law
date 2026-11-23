<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Seire: mida loetakse ja mis sellest tuli

[English](README.en.md)

Kuidas global-law seirab kõiki riike: [global-law monitoring/](https://github.com/lexifina/global-law/tree/main/monitoring). See leht teeb sama ainult ühe riigi (Eesti) kohta: iga kord, kui ametlikku allikat loetakse, millal see juhtus ja mis sellest tuli (lisatud, muudetud ja kehtetuks tunnistatud aktid). Masinloetav kuju on [data/checks/](../data/checks/) (JSON Lines, skeem `lexifina-check/1`), `git log`-is `Kind: check` commit'idena ja kuude kaupa kaustas [checks/](checks/).

**Viimane kontroll:** 2026-11-23 10:12 UTC, Euroopa Liidu Väljaannete Talitus (Eesti meetmed EL-i direktiivide ülevõtmiseks): loetud 1 aadressi; lisatud 0, muudetud 0, eemaldatud 0; muutusi ei ole; avaldamata 23, neist põhjuseta 0.

## Allikad

| Allikas | Kaustad | Kui tihti | Viimane õnnestunud kontroll | Viimane tulemus | Seis |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (terviktekstid)](https://www.riigiteataja.ee) | `ps/`, `seadused/` | iga päev | 2026-11-23 10:11 UTC | muutusi ei ole | jälgitakse: ainult loetelud, mitte tekstid, üks päring iga 6 sekundi järel (selle API piirab vastatavate päringute arvu); osa siinseid tekste on Riigi Teataja andmete koopiatest (legalize-ee, lahend.ee: vt PLAN.md) |
| [Riigikogu avaandmed (eelnõud ja vastuvõetud seadused)](https://api.riigikogu.ee) | `riigikogu/` | iga päev | 2026-11-23 10:12 UTC | muutusi ei ole | jälgitakse: eelnõud ja vastuvõetud seadused, üks päring iga 3 sekundi järel (API piirab päringute hulka); riigikogu/ hääletusi, stenogramme ja dokumente veel ei võrrelda |
| [Tartu Linnavolikogu dokumendiregister](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | `kov/tartu/` | — | — | — | veel ei jälgita: selle robots.txt keelab igasuguse automaatse lugemise (Disallow: /), seega seda ei loeta; Riigi Teataja avaldab volikogu määrused, kuid mitte otsuseid |
| [Euroopa Liidu Väljaannete Talitus (Eesti meetmed EL-i direktiivide ülevõtmiseks)](https://publications.europa.eu/webapi/rdf/sparql) | `eu-nim/` | iga päev | 2026-11-23 10:12 UTC | muutusi ei ole | jälgitakse: ainult meetmete kirjed; nende tekstid on Riigi Teatajas |

## Viimased 30 päeva

| Algus (UTC) | Allikas | Loetud | Lisatud | Muudetud | Eemaldatud | Avaldamata (põhjuseta) | Tulemus | Commit'id |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
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
