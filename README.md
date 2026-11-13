# Eesti õigus muudatus muudatuse haaval

**Eesti** · [English](README.en.md)

<picture>
<source media="(prefers-color-scheme: dark)" srcset="data/et/effort-dark.svg">
<img alt="Eesti õigusaktid selles repositooriumis: sisu, muudatused jõustumisaasta järgi, täielikkus võrreldes ametlike allikatega ja sisu õigsus" src="data/et/effort-light.svg" width="880">
</picture>

Osa repositooriumist [lexifina/global-law](https://github.com/lexifina/global-law), mis on kõigi riikide õiguse ühine git-ajalugu: siin on Eesti riigisisene õigus, mida global-law loeb kaustast `estonia/national/acts/`.

Kolm Eesti õigusakti git-repositooriumina: Eesti Vabariigi põhiseadus (PS), Riigikogu valimise seadus (RKVS) ja isikuandmete kaitse seadus (IKS). Iga muutmisakt on üks commit, mille autoriks on see akt ja mille kuupäev on päev, mil akti muudatused jõustusid, keskpäeval Tallinna aja järgi. Tekst on Eesti Vabariigi ametlikus võrguväljaandes [Riigi Teatajas](https://www.riigiteataja.ee) avaldatud terviktekst.

## Juristi küsimused git-käskudena

| Küsimus | Käsk |
| --- | --- |
| Mida ütles põhiseaduse § 156 1. jaanuaril 2010? | `python tools/seisuga.py 2010-01-01 ps 156` |
| Mida ütles kogu Riigikogu valimise seadus 1. märtsil 2015? | `python tools/seisuga.py 2015-03-01 rkvs` |
| Milline akt kirjutas RKVS § 48⁴ iga lõike? | `git blame rkvs/para-048b4.md` |
| Paragrahvi kõik muudatused koos neid teinud aktiga | `git log -p ps/para-156.md` |
| Kõik, mida üks muutmisakt muutis | `git show akt/103012020002` (sildid on kujul `akt/<Riigi Teataja id>`) |
| Akt sellisena, nagu see kehtis teatud päeval | `git checkout ps/2015-08-13` (iga akti kohta üks silt iga päeva kohta, mil akt muutus) |
| Kõik nende seaduste muutmisaktid koos kuupäevadega | [`muutmisaktid.csv`](muutmisaktid.csv) |
| Vastu võetud, kuid veel jõustumata muudatused | `git log main..tulevik` (praegu tühi) |

## Kuupäevad

Eesti õigusaktil on mitu kuupäeva: vastuvõtmise, Vabariigi Presidendi poolt väljakuulutamise, Riigi Teatajas avaldamise ja jõustumise kuupäev. Kuupäev, mis määrab, milline tekst juhtumile kohaldub, on muudatuse jõustumise päev, seega **on iga commit'i autori ja committer'i kuupäev see päev, keskpäeval Tallinna aja järgi**. Teised kuupäevad on commit'i sõnumis trailer'itena: `Adopted:`, `Proclaimed:`, `Published:`, `In-force:`. Muudatuse jõustumise päev loetakse muutmismärkest, mille Riigi Teataja trükib iga muudetud sätte alla, ja see on päev, mil muudatust sisaldav terviktekst hakkas kehtima.

## Kes on autor

Commit'i autor on muutmisakt, mida nimetatakse selle Riigi Teataja viitega (`RT I, 03.01.2020, 2`) aadressil, mida ei saa olemas olla (`akt-103012020002@riigiteataja.invalid`, akti Riigi Teataja id põhjal), nii et `git blame` nimetab akti, mis iga rea kirjutas. Committer on `Lexifina <estonia-law@lexifina.com>`. Iga akti esimese commit'i autor on akt algsel kujul (põhiseaduse puhul `RT 1992, 26, 349`).

Muudatus omistatakse aktile ainult siis, kui seda ütlevad Riigi Teataja enda märked: muudetud paragrahvi juures olev märge (või peatüki pealkirja juures olev märge, kui peatükk asendati tervikuna) nimetab akti ja päeva. Muudatused, mida ükski märge ei selgita, on commit'itud nimega `Riigi Teataja` ja seda ka öeldakse: tühikute muudatused, rikutud märgid Riigi Teataja enda failides kolme 2004–2006 redaktsiooni puhul ning toimetuslikud muudatused, näiteks avaldamisviidete loendite eemaldamine. Üks paragrahv, mida kaks akti muutsid samal päeval ja mille märked ei ütle, kumb akt millise rea kirjutas, on märgistatud commit nimega `Riigi Teataja`, mis nimetab mõlemat akti.

## Kuidas seda kontrollitakse

`tools/check_repo.py` loeb iga akti git'ist tagasi iga päeva seisuga, mil selle tekst muutus (kõik 42 terviktekstiredaktsiooni nende esimesel päeval ning lisaks kaks päeva redaktsioonide sees), ja võrdleb iga faili selle redaktsiooni tekstiga Riigi Teataja XML-is: 4 670 failis 0 erinevust. Samuti võrdleb see iga redaktsiooni XML-ist loetud teksti Riigi Teataja enda lihttekstikujuga samast redaktsioonist (`/txt`) märk-märgilt, välja arvatud tühimärgid ja Riigi Teataja nurksulgudes muudatusmärkused: kõik 42 redaktsiooni ühtivad. Lisaks kontrollib see iga lähtefaili sha256-räsi faili `data/versioonid.json` alusel. Kaks ehitust samadest andmetest annavad igale commit'ile ja sildile samad räsid. Üksikasjad on failis [`REPRODUCE.md`](REPRODUCE.md).

## Mida see ei näita

- Redaktsioone, mis eelnevad Riigi Teataja elektroonilistele terviktekstidele (2002). Põhiseadust ei muudetud enne 2003. aastat, seega on selle esimene commit 1992. aasta tekst.
- Lisasid, allkirju ja väljaandja märkusi (põhiseaduse lõpus olev „Õiend“, veaparanduse märkused); need on loetletud failis REPRODUCE.md.
- Akti algse teksti sätteid, mis jõustusid hiljem kui akt ise, välja arvatud juhul, kui Riigi Teataja avaldas nende jaoks eraldi redaktsiooni.
- Vene- ja ingliskeelseid tõlkeid. Õigusjõud on ainult eestikeelsel tekstil.

Autoriteetne allikas on ainult Riigi Teataja. See repositoorium on uurimistöö abivahend.

## Kuidas see on ehitatud

`tools/build.py` loeb Riigi Teataja avalikku API-t (`https://www.riigiteataja.ee/public-api/api/v1`), üks päring korraga ja päringute vahel pausiga, ning kirjutab selle repositooriumi nullist. Samade andmete ja sama `--today` väärtusega annab see samad commit'id samade räsidega. Ajaloo ehitamisel ei kasutata ühtegi tehisintellekti mudelit.

## Litsents

Õigusakti tekst ei ole autoriõigusega kaitstud (Autoriõiguse seadus § 5 p 3). Allikas: Riigi Teataja, https://www.riigiteataja.ee, väljaandja Justiits- ja Digiministeerium. Ajalugu, sõnumid, tabelid ja tööriistad on avaldatud litsentsi [CC0 1.0](LICENSE) alusel.

See on ingliskeelse versiooni ([README.en.md](README.en.md)) tõlge; erinevuste korral kehtib ingliskeelne versioon.

## Veel

Repositooriumist [lexifina/global-law](https://github.com/lexifina/global-law) (inglise keeles):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): kõik funktsioonid ja mida iga korpus peab toetama (`git blame`, `law.py`, MCP-tööriistad)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): küsimused ja vastused · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): muudatuste ettepanekud · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): MCP-server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): kuidas see on tehtud · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): kui ajakohane iga korpus on · [Seire](https://github.com/lexifina/global-law/tree/main/monitoring): kas uuendused töötavad · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): kuidas iga ametlikku allikat muudatuste suhtes jälgitakse
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): kui kiired tööriistad on, mõõdetud
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): graafikud ja seosed kogu maailma õiguses
- [Haavatavused](https://github.com/lexifina/global-law/tree/main/vulnerabilities): vead õigusaktides avaldatud kujul
