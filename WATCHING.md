<!-- lawwatch: written from data/checks by the check trail; edit the records, not this page -->

# Allikate jälgimine: mida jälgitakse (Eesti)

[English](WATCHING.en.md)

Kuidas global-law jälgib iga riigi allikaid: [global-law WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md). See leht teeb sama ainult ühe riigi (Eesti) kohta: iga ametlik allikas, kust see repositoorium teksti võtab, mida sealt loetakse, kui tihti ja millal seda viimati loeti. Iga lugemine ja mis sellest tuli: [monitoring/](monitoring/README.md).

| Allikas | Mida loetakse | Kaustad | Kui tihti | Viimati loetud | Seis |
| --- | --- | --- | --- | --- | --- |
| [Riigi Teataja (terviktekstid)](https://www.riigiteataja.ee) | kehtivate seaduste arv, seadused, mille terviktekst on pärast eelmist kontrolli jõustunud (avaliku API otsing, uusimad eespool), iga siin oleva seaduse redaktsioonide loetelu ning iga siin oleva seaduse kehtiva redaktsiooni ja hoitavale järgnevate redaktsioonide XML (koos neis nimetatud muutmisaktidega); auditiks mõne redaktsiooni lihttekst | `ps/`, `seadused/` | iga päev | 2026-11-23 21:49 UTC | jälgitakse: üks päring iga 6 sekundi järel (selle API piirab vastatavate päringute arvu); siinsed tekstid, mis pärinevad Riigi Teataja andmete koopiatest (legalize-ee, lahend.ee: vt PLAN.md), viiakse parandusega vastavusse Riigi Teataja enda XML-iga, nagu tools/build.py selle kirjutab |
| [Riigikogu avaandmed (eelnõud ja vastuvõetud seadused)](https://api.riigikogu.ee) | iga Riigikogu koosseisu kõigi eelnõude register koos menetlusetapi, staatuse ja staatuse kuupäevaga (api/volumes/drafts, umbes üks päring koosseisu kohta) | `riigikogu/` | iga päev | 2026-11-23 22:40 UTC | jälgitakse: eelnõud ja vastuvõetud seadused, üks päring iga 3 sekundi järel (API piirab päringute hulka); riigikogu/ hääletusi, stenogramme ja dokumente veel ei võrrelda; uute seaduste vastuvõetud tekste siia veel ei kirjutata (neid lugenud tööriist on kadunud) |
| [Tartu Linnavolikogu dokumendiregister](https://info.raad.tartu.ee/dhs.nsf/volmaarused) | — | `kov/tartu/` | — | — | veel ei jälgita: selle robots.txt keelab igasuguse automaatse lugemise (Disallow: /), seega seda ei loeta; Riigi Teataja avaldab volikogu määrused, kuid mitte otsuseid |
| [Euroopa Liidu Väljaannete Talitus (Eesti meetmed EL-i direktiivide ülevõtmiseks)](https://publications.europa.eu/webapi/rdf/sparql) | kõik Eesti teatatud siseriiklikud ülevõtmismeetmed koos teatamise kuupäeva ja kirje viimase muutmise kuupäevaga (üks SPARQL-päring) | `eu-nim/` | iga päev | 2026-11-23 22:42 UTC | jälgitakse: ainult meetmete kirjed; nende tekstid on Riigi Teatajas |

Allikaid loetakse nende robots.txt ja kasutustingimuste piires, päringute vahel on pausid.
