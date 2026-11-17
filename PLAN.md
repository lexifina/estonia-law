# Estonia: what is counted, what is missing

Counted on 2026-11-17 from this repository's `main`.

## What counts as held

Riigi Teataja, which publishes Estonia's consolidated texts and the list of laws in force, does not allow automated access. The only official source this record can read is the Riigikogu's open data (api.riigikogu.ee), which holds each act **as the Riigikogu adopted it**.

So a law in force counts as held when either:

- its original adopted text **and** the adopted text of every amending act now in force are in [`riigikogu/seadused/`](riigikogu/seadused/). Together these are the law's full legislative text, but not a consolidated text, and this record does not merge the amendments into one; or
- a checked consolidated version is here and every amending act in force after it is in `riigikogu/seadused/`.

`ps/`, `rkvs/` and `iks/` hold consolidated versions read from Riigi Teataja. 27 more laws (for example `kars/`, the Penal Code) hold consolidated versions from [legalize-ee](https://github.com/legalize-dev/legalize-ee), a third-party mirror built from Riigi Teataja's yearly XML archives (see below).

| | Count |
| --- | --- |
| Laws in force, end of 2024 (government review of good lawmaking, reported by ERR on 22 April 2025) | 392 |
| Laws that may be in force, from the Riigikogu record ([`data/voimalikud-kehtivad-seadused.csv`](data/voimalikud-kehtivad-seadused.csv)) | 458 (an upper bound) |
| Laws in force with their original text here, as adopted | about 310 |
| Laws in force complete as adopted (original text and every amending act in force) | about 226 |
| Laws in force held by either rule | about 229 (233 with unvalidated texts) |
| Laws with consolidated versions from legalize-ee | 27 (388 versions) |
| Amending acts in force that amend those laws: here / all | 9,150 / 9,459 |
| Acts adopted by the Riigikogu: here / accepted bills in its record since 1992 | 3,402 / 4,644 |

**How the list of laws is made.** We take every accepted bill since 1992, keep the laws by title (not amending acts, budgets or ratifications), drop a law when it was re-enacted under the same name, and drop it when an adopted text here repeals it as a whole (`... seadus tunnistatakse kehtetuks`, with the year of its Riigi Teataja reference checked). That gives 458, more than the official 392, because repeals made by acts that are not here cannot be seen. Laws passed before the Riigikogu (Supreme Council, 1990–92) are not in its record. The shares use 392.

**How amendments are found.** An act amends a law when its adopted text has a section `<law> muutmine`, `<law>s tehakse ... muudatused` or `<law> § ...` (the longest law name wins). For an act whose text is not here, its title is used (`<law> ... muutmise seadus`). An amendment inside an act that is not here and does not name the law in its title cannot be seen, so "complete" means complete as far as the Riigikogu record shows. Acts adopted but not yet in force are not counted.

## Main codes

| Code | Bill | Adopted | Original text here | Amending acts in force here | Missing |
| --- | --- | --- | --- | --- | --- |
| Tsiviilseadustiku üldosa seadus | 9-121 SE | 2002 | yes | 40 of 40 | none |
| Võlaõigusseadus | 9-116 SE | 2001 | yes | 133 of 134 | 12-266 SE |
| Karistusseadustik (consolidated to 2026-01-01 in `kars/`; 15-880 SE after it) | 9-119 SE | 2001 | yes | 254 of 265 | 10-1112, 10-584, 10-683, 10-836, 10-599, 10-923, 10-931, 10-1087, 11-930, 12-140, 15-880 SE |
| Kriminaalmenetluse seadustik | 9-594 SE | 2003 | yes | 133 of 141 | 10-538, 10-683, 10-599, 10-923, 10-545, 10-964, 10-1087, 12-175 SE |
| Tsiviilkohtumenetluse seadustik | 10-208 SE | 2005 | yes | 102 of 107 | 10-779, 10-545, 11-583, 12-206, 12-346 SE |
| Asjaõigusseadus | 7-2021502 SE | 1993 | no | 76 of 81 | 7-612, 8-690, 10-731, 10-823, 13-405 SE |
| Äriseadustik | 7-733 SE | 1995 | no | 149 of 157 | 8-209, 8-323, 8-465, 8-557, 10-414, 10-469, 10-777, 10-951 SE |
| Perekonnaseadus | 11-543 SE | 2009 | yes | 30 of 32 | 12-214, 15-207 SE |
| Pärimisseadus | 11-56 SE | 2008 | yes | 10 of 10 | none |
| Töölepingu seadus | 11-299 SE | 2008 | yes | 105 of 107 | 11-317, 14-615 SE |
| Halduskohtumenetluse seadustik | 11-902 SE | 2011 | yes | 24 of 24 | none |
| Haldusmenetluse seadus | 9-456 SE | 2001 | yes | 70 of 70 | none |
| Väärteomenetluse seadustik | 9-441 SE | 2002 | yes | 80 of 85 | 10-584, 10-599, 10-545, 10-1087, 11-930 SE |
| Täitemenetluse seadustik | 10-143 SE | 2005 | yes | 93 of 95 | 10-779, 14-315 SE |
| Maksukorralduse seadus | 9-886 SE | 2002 | yes | 173 of 176 | 10-596, 10-921, 12-841 SE |

## Consolidated versions from legalize-ee

[legalize-ee](https://github.com/legalize-dev/legalize-ee) publishes Riigi Teataja's consolidated texts, built from its yearly XML archives (last update 2026-06-23). This record takes a version only when it passes two checks:

- at least 80% of its text units (subsections, points) match word for word the Riigikogu's adopted texts of the law and its amending acts in `riigikogu/seadused/`. The rest are mostly wording that amendments changed word by word;
- legalize-ee drops the superscript in subsection and point numbers (`(5²)` comes out as `(5)`). Every such number must be restored from an adopted text, or the version is not used.

Only laws whose newest legalize-ee version passes are taken, so no folder ends on an outdated text: 27 laws, 388 versions. Each commit says `Source: legalize-ee (upstream Riigi Teataja XML, RT id …)` and links the official page. As a test, all five versions of the Personal Data Protection Act in legalize-ee, once restored, equal `iks/` (read from Riigi Teataja) in every section.

The Code of Criminal Procedure, the Employment Contracts Act and the Code of Enforcement Procedure are in legalize-ee, but their newest versions fail the check, so they are not taken. The Law of Obligations Act, the General Part of the Civil Code Act, the Code of Civil Procedure and the Commercial Code are not in legalize-ee.

## Main codes from other sources (2026-11-17)

On 2026-11-17 the main codes were taken from any reachable source, to be validated later:

| Code | Folder | Version in force from | Source | Status |
| --- | --- | --- | --- | --- |
| Tsiviilseadustiku üldosa seadus | `riigikogu/seadused/` | as adopted + 40 amending acts | Riigikogu | checked |
| Võlaõigusseadus | `vos/` | 2026-09-01 | Riigi Teataja XML 120062026018, copied by a third party | checked against the adopted texts (92% of lines) |
| Karistusseadustik | `kars/` | 2026-10-01 | lahend.ee | **not yet validated** (legalize-ee versions up to 2026-01-01 are checked) |
| Kriminaalmenetluse seadustik | `krms/` | 2026-11-01 | lahend.ee | **not yet validated** |
| Tsiviilkohtumenetluse seadustik | `tsms/` | 2026-06-30 | lahend.ee | **not yet validated** |

Also from lahend.ee and not yet validated: Täitemenetluse seadustik (`tms/`, 2026-10-01) and Halduskohtumenetluse seadustik (`hkms/`, 2026-06-12). Also from Riigi Teataja XML: Perekonnaseadus (`pks/`, 2025-01-01). lahend.ee drops superscripts in section numbers (restored here by order) and in references inside the text (`§-s 1331` stands for § 133¹; not restored). Each such commit carries `Validation: pending - not yet checked against Riigi Teataja`. The Commercial Code is not taken: lahend.ee's newest version is from 2024.

## What is missing, and why

[`data/puuduvad-aktid.csv`](data/puuduvad-aktid.csv) lists the 380 acts that laws in force need and that are not here:

- **191 acts adopted in 1992–99.** The Riigikogu's record of these bills holds the initial draft, the explanatory memorandum and the lists of proposed amendments, but no adopted text, and its document search finds no adopted texts for those years. The original texts of the Law of Property Act (1993) and the Commercial Code (1995) are among them.
- **189 later acts held back** because two independent readings of their files disagree (for example the two PDF engines order a table differently), or because the bill has several adopted-text files that differ. Nothing is committed on one reading alone, and there is no OCR. A second pass on 2026-11-17, which also accepts agreement in a second reading order, added 143 of the 304 acts held back for this reason.

**Consolidated texts.** This record does not merge amendments into a text itself. Doing so could only be checked against Riigi Teataja's consolidated text, and four of the five main codes also lack amending acts. Consolidated texts here are Riigi Teataja's own, read directly (`ps/`, `rkvs/`, `iks/`) or through legalize-ee.

## What would close the gap

Access to Riigi Teataja's consolidated texts (its API or a bulk download) for this record's fetcher. That would give every law in force as consolidated, with its versions since 2002, and would also give the 1992–99 original texts and the official list of laws in force.
