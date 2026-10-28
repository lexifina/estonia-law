"""Builds a git history of Estonian law from Riigi Teataja, in which every amending act is one commit, dated the day
its changes took effect.

    python -X utf8 scripts/estonia-law/build.py [--repo ../estonia-law] [--today YYYY-MM-DD] [--offline]

Riigi Teataja (the official publication of the Republic of Estonia, published by the Ministry of Justice and
Digital Affairs) keeps every consolidated version (terviktekst) of each act as XML, with the day it is valid from and
to. Every provision that an amending act changed carries an amendment mark (muutmismärge) naming that act by its
Riigi Teataja reference and giving the day the change took effect. We read every version of the acts below, compare
consecutive versions section (paragrahv) by section, and credit each change to the act whose marks newly appear in
that section with that day as their entry into force. A change that no mark explains is committed on its own and
labelled as unexplained, never credited to a law.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / '.cache'
SITE = 'https://www.riigiteataja.ee'
API = SITE + '/public-api/api/v1'
UA = 'Lexifina estonia-law builder (https://github.com/lexifina/estonia-law; corpus@lexifina.com)'
THROTTLE = 1.5          # seconds between requests to riigiteataja.ee
COMMITTER = ('Lexifina', 'estonia-law@lexifina.com')
FUTURE_BRANCH = 'tulevik'

# The acts in the record: Riigi Teataja's group id (terviktekstiGrupiID, the same for every version of an act) and a
# short slug for the repository's folders.
ACTS = [
    {'group': 151381, 'slug': 'ps'},       # Eesti Vabariigi põhiseadus (the Constitution)
    {'group': 155356, 'slug': 'rkvs'},     # Riigikogu valimise seadus (Riigikogu Election Act)
    {'group': 1045568, 'slug': 'iks'},     # Isikuandmete kaitse seadus (Personal Data Protection Act)
]

# ---------------------------------------------------------------- fetching

REQUESTS: list[dict] = []
_last = [0.0]


def fetch(path: str, offline: bool = False) -> bytes:
    """GET API + path, cached on disk by the path, so a rebuild reads the same bytes."""
    url = API + path
    key = hashlib.sha256(url.encode()).hexdigest()[:32]
    file = CACHE / key
    REQUESTS.append({'url': url, 'file': file})
    if file.exists():
        return file.read_bytes()
    if offline:
        raise SystemExit(f'not cached: {url}')
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / '.gitignore').write_text('*\n', encoding='utf-8', newline='\n')
    wait = THROTTLE - (time.monotonic() - _last[0])
    if wait > 0:
        time.sleep(wait)
    body = None
    for attempt in range(4):
        _last[0] = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
            break
        except Exception:
            # urllib can fail on a self-signed certificate in this machine's chain; curl uses the system store.
            out = subprocess.run(['curl', '-sS', '-f', '-L', '--max-time', '120', '-A', UA, '--', url], capture_output=True)
            if out.returncode == 0:
                body = out.stdout
                break
            time.sleep(3 * (attempt + 1))
    if body is None:
        raise SystemExit(f'could not fetch {url}')
    if body.lstrip()[:15].lower().startswith(b'<!doctype html'):
        raise SystemExit(f'got the web application instead of data: {url}')
    file.write_bytes(body)
    return body


def fetch_json(path: str, offline: bool = False):
    return json.loads(fetch(path, offline))


# ---------------------------------------------------------------- reading one version's XML

SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


def day_of(s: str | None) -> str | None:
    """'2015-08-13+03:00' or '2015-08-13' -> '2015-08-13'."""
    return s.strip()[:10] if s and s.strip() else None


def ee_day(s: str) -> str:
    """'17.10.2005' -> '2005-10-17'."""
    d, m, y = s.split('.')
    return f'{int(y):04d}-{int(m):02d}-{int(d):02d}'


def sup_text(s: str) -> str:
    return s.translate(SUP) if s.isdigit() else '^' + s


def html_text(s: str) -> str:
    """The display number of a unit, held as an HTML fragment: '§ 5<sup>1</sup>. ' -> '§ 5¹.'"""
    s = re.sub(r'<sup>\s*([^<]*?)\s*</sup>', lambda m: sup_text(m.group(1)), s or '')
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s.replace(' ', ' ')).strip()


class Reader:
    """One consolidated version: its metadata and its sections (paragrahv), each as lines of text with the amendment
    marks found inside it."""

    def __init__(self, xml: bytes):
        self.root = ET.fromstring(xml)
        self.ns = '{' + self.root.tag[1:].split('}')[0] + '}' if self.root.tag.startswith('{') else ''
        self.notes: list[dict] = []        # what is left out of the text, for the record
        self.uid = 0                       # numbers each lõige and alampunkt, so a line knows which one it is in
        self.order: list[tuple] = []       # headings and sections in document order, for the check against the txt

    def t(self, name: str) -> str:
        return self.ns + name

    def name(self, e) -> str:
        return e.tag[len(self.ns):] if e.tag.startswith(self.ns) else e.tag

    # -- metadata

    def ref(self, am) -> dict:
        """An avaldamismarge (Riigi Teataja reference) as {'id', 'label', 'published'}."""
        if am is None:
            return {'id': '', 'label': '', 'published': None}
        g = lambda n: (am.findtext(self.t(n)) or '').strip()
        part, year, nr, art, pub = g('RTosa'), g('RTaasta'), g('RTnr'), g('RTartikkel'), day_of(g('avaldamineKuupaev'))
        if nr and not year and pub:     # some numbered issues give the year only in the publication date
            year = pub[:4]
        if nr:      # the numbered issues used until 2010: "RT I 2003, 29, 174"
            label = f'{part} {year}, {nr}, {art}'
        elif pub:   # the dated issues used since 2010: "RT I, 27.04.2011, 1"
            label = f'{part}, {pub[8:10]}.{pub[5:7]}.{pub[:4]}, {art}'
        else:
            label = f'{part} {year} {art}'.strip()
        return {'id': g('aktViide').rstrip('/').rsplit('/', 1)[-1], 'label': label, 'published': pub}

    def mark(self, mm) -> dict:
        am = mm.find(self.t('avaldamismarge'))
        r = self.ref(am) if am is not None else {'id': '', 'label': '', 'published': None}
        note = re.sub(r'\s+', ' ', ''.join(mm.find(self.t('tavatekst')).itertext())).replace(' ', ' ').strip() \
            if mm.find(self.t('tavatekst')) is not None else ''
        return {'act': r['id'], 'label': r['label'], 'published': r['published'],
                'adopted': day_of(mm.findtext(self.t('aktikuupaev'))), 'in_force': day_of(mm.findtext(self.t('joustumine'))),
                'note': note}

    def meta(self) -> dict:
        md = self.root.find(self.t('metaandmed'))
        f = lambda p: md.findtext('/'.join(self.t(x) for x in p.split('/')))
        own = md.find(self.t('avaldamismarge'))
        enacted = md.find(self.t('vastuvoetud'))
        return {
            'id': (f('globaalID') or '').strip(), 'group': (f('terviktekstiGrupiID') or '').strip(),
            'kind': (f('tekstiliik') or '').strip(), 'issuer': (f('valjaandja') or '').strip(),
            'short': (f('lyhend') or '').strip(),
            'title': re.sub(r'\s+', ' ', self.inline(self.root.find(self.t('aktinimi')).find('.//' + self.t('pealkiri')))).strip(),
            'from': day_of(f('kehtivus/kehtivuseAlgus')), 'to': day_of(f('kehtivus/kehtivuseLopp')),
            'ref': self.ref(own) if own is not None else None,
            'enacted': {'adopted': day_of(enacted.findtext(self.t('aktikuupaev'))),
                        'in_force': day_of(enacted.findtext(self.t('joustumine'))),
                        'ref': self.ref(enacted.find(self.t('avaldamismarge')))} if enacted is not None else None,
            'amendments': [self.mark(m) for m in self.root.findall(self.t('muutmismarge'))],
            'corrections': [{'day': day_of(v.findtext(self.t('veaparandusKuupaev'))),
                             'text': re.sub(r'\s+', ' ', v.findtext(self.t('veaparandusTekst')) or '').strip()}
                            for v in self.root.iter(self.t('veaparandus'))],
        }

    # -- text

    def inline(self, e) -> str:
        """The words of a tavatekst: line breaks as newlines, superscripts as superscript characters, references as
        their displayed text; formatting (italic, bold) is dropped."""
        out = [e.text or '']
        for c in e:
            n = self.name(c)
            if n == 'reavahetus':
                out.append('\n')
            elif n == 'sup':
                out.append(sup_text(''.join(c.itertext()).strip()))
            elif n == 'viide':
                out.append(''.join(c.find(self.t('kuvatavTekst')).itertext()) if c.find(self.t('kuvatavTekst')) is not None else '')
            elif n in ('muutmismarge', 'normtehnmarkus'):
                pass        # amendment marks and footnotes on EU law are read separately
            else:
                out.append(self.inline(c))
            out.append(c.tail or '')
        return ''.join(out)

    def sisu_lines(self, st) -> list[str]:
        """The lines of a sisuTekst: each line break in the official text starts a new line."""
        parts = []
        for c in st:
            n = self.name(c)
            if n == 'tavatekst':
                parts.append(self.inline(c))
            elif n == 'viide':
                parts.append(''.join(c.find(self.t('kuvatavTekst')).itertext()) if c.find(self.t('kuvatavTekst')) is not None else '')
            elif n == 'HTMLKonteiner':
                self.notes.append({'kind': 'html', 'text': html_text(c.text or '')})
        text = ''.join(parts).replace(' ', ' ')
        lines = [re.sub(r'[ \t\r\n]+', ' ', l).strip() for l in text.split('\n')]
        return [l for l in lines if l]

    def marks_in(self, e) -> list[dict]:
        return [self.mark(m) for m in e.iter(self.t('muutmismarge'))]

    def own_marks(self, e) -> list[dict]:
        return [self.mark(m) for m in e.findall(self.t('muutmismarge'))]

    def repealed(self, e) -> bool:
        return any(m['note'].lower().startswith('kehtetu') for m in self.own_marks(e))

    def unit_lines(self, e, level: int) -> list[dict]:
        """Lines of a lõige or alampunkt (and the alampunkt inside a lõige)."""
        n = self.name(e)
        num = html_text(e.findtext(self.t('kuvatavNr')) or '')
        out: list[dict] = []
        texts: list[str] = []
        for st in e.findall(self.t('sisuTekst')):
            texts.extend(self.sisu_lines(st))
        if texts and texts[0].startswith('Õiend'):
            # Riigi Teataja's editorial statement at the end of the Constitution ("Õiend": which printing the text
            # follows and which typing errors were corrected). It is the publisher's note, not a provision.
            self.notes.append({'kind': 'õiend', 'text': ' '.join(texts)})
            return []
        if not texts and self.repealed(e):
            texts = ['[Kehtetu]']
        self.uid += 1
        for i, s in enumerate(texts):
            out.append({'level': level, 'text': f'{num} {s}'.strip() if i == 0 and num else s, 'u': self.uid})
        if not texts and num:
            out.append({'level': level, 'text': num, 'u': self.uid})
        for c in e.findall(self.t('alampunkt')):
            out.extend(self.unit_lines(c, level + 1))
        return out

    def sections(self) -> tuple[list[dict], list[dict]]:
        """The act's units in order: the preamble, then every paragrahv with its chapter (and division) headings."""
        sisu = self.root.find(self.t('sisu'))
        units: list[dict] = []
        heads: list[dict] = []
        chapter: list[str] = []

        def words(e) -> str:
            return re.sub(r'\s+', ' ', self.inline(e).replace(' ', ' ')).strip() if e is not None else ''

        def heading(e, kind: str) -> str:
            num = html_text(e.findtext(self.t('kuvatavNr')) or '')
            return ' '.join(x for x in (num, words(e.find(self.t(kind + 'Pealkiri')))) if x)

        def paragrahv(p, path: list[str]):
            nr_e = p.find(self.t('paragrahvNr'))
            nr = (nr_e.text or '').strip() if nr_e is not None else ''
            sup = nr_e.get('ylaIndeks') if nr_e is not None else None
            key = f'{int(nr):03d}' + (f'b{sup}' if sup else '') if nr.isdigit() else re.sub(r'\W+', '-', nr)
            label = html_text(p.findtext(self.t('kuvatavNr')) or f'§ {nr}.').rstrip('.')
            lines: list[dict] = []
            for c in p:
                n = self.name(c)
                if n == 'sisuTekst':
                    lines.extend({'level': 0, 'text': s} for s in self.sisu_lines(c))
                elif n == 'loige':
                    lines.extend(self.unit_lines(c, 0))
            if not lines and self.repealed(p):
                lines = [{'level': 0, 'text': '[Kehtetu]'}]
            units.append({'key': key, 'label': label, 'title': words(p.find(self.t('paragrahvPealkiri'))),
                          'section': list(path), 'lines': lines, 'marks': self.marks_in(p)})
            self.order.append(('unit', key))

        def walk(e, path: list[str]):
            for c in e:
                n = self.name(c)
                if n in ('peatykk', 'jagu', 'osa', 'alljagu'):
                    h = heading(c, n)
                    heads.append({'path': path + [h], 'marks': self.own_marks(c)})
                    self.order.append(('head', h))
                    if n in ('peatykk', 'osa'):
                        chapter[:] = path + [h]
                    walk(c, path + [h])
                elif n == 'paragrahv':
                    # Riigi Teataja's XML of the Constitution places §§ 104-110 after chapter VII rather than in it;
                    # a section outside any chapter is listed under the chapter before it.
                    paragrahv(c, path or chapter)
                elif n in ('preambul', 'sisuTekst') and e is sisu:
                    units.append({'key': 'preambul', 'label': 'Preambul', 'title': '', 'section': [],
                                  'lines': [{'level': 0, 'text': l} for l in self.sisu_lines(c)], 'marks': self.marks_in(c)})
                    self.order.append(('unit', 'preambul'))
        walk(sisu, [])
        return units, heads


# ---------------------------------------------------------------- wording that changes inside one version

ALT = re.compile(r'^\[(?:[^\]]*?)sõnastus (kuni|alates) (\d{1,2}\.\d{1,2}\.\d{4})\]$')


def resolve(lines: list[dict], day: str) -> list[dict]:
    """Older consolidated texts sometimes print two wordings of a provision, each headed "[… sõnastus kuni 16.10.2005]"
    or "[… sõnastus alates 17.10.2005]". Keep the wording that applies on the day."""
    out: list[dict] = []
    mode = None     # None: always; ('kuni', d): until d; ('alates', d): from d
    unit = None
    for l in lines:
        if l.get('u') != unit:      # a printed wording ends with its lõige or alampunkt
            mode, unit = None, l.get('u')
        body = re.sub(r'^\(\d+[^)]*\)\s*', '', l['text'])
        m = ALT.match(body)
        if m:
            mode = (m.group(1), ee_day(m.group(2)))
            prefix = l['text'][:len(l['text']) - len(body)].strip()
            if prefix:  # the number of the lõige is printed before the first bracket; carry it to the wording kept
                mode = mode + (prefix,)
            continue
        if mode is None:
            out.append(l)
            continue
        keep = day <= mode[1] if mode[0] == 'kuni' else day >= mode[1]
        if keep:
            text = l['text']
            if len(mode) > 2 and not text.startswith(mode[2]):
                text = f'{mode[2]} {text}'
            out.append({**l, 'text': text})
    return out


def switch_days(units: list[dict], start: str, end: str | None) -> list[str]:
    """Days inside a version's validity on which a printed "sõnastus alates" wording takes over."""
    days = set()
    for u in units:
        for l in u['lines']:
            m = ALT.match(re.sub(r'^\(\d+[^)]*\)\s*', '', l['text']))
            if m and m.group(1) == 'alates':
                d = ee_day(m.group(2))
                if d > start and (end is None or d < end):
                    days.add(d)
    return sorted(days)


# ---------------------------------------------------------------- the record of one act

DATE_IN_NOTE = re.compile(r'(?:osaliselt|jõustub)\s+(\d{1,2}\.\d{1,2}\.\d{4})')


def mark_days(m: dict) -> set[str]:
    """The days a mark says its change took effect: its own date and any later part named in its note ("…, osaliselt
    01.10.2024", "…, lõige 3 jõustub 01.10.2024")."""
    days = {m['in_force']} if m['in_force'] else set()
    days |= {ee_day(d) for d in DATE_IN_NOTE.findall(m['note'])}
    return days


def act_days(version: dict) -> dict[str, set[str]]:
    """The days each amending act took effect, from the version's own list of amending acts."""
    out: dict[str, set[str]] = {}
    for m in version['meta']['amendments']:
        if m['act']:
            out.setdefault(m['act'], set()).update(mark_days(m))
    return out


def head_num(heading: str) -> str:
    """'4. peatükk VALIMISTE KORRALDUS' -> '4. peatükk'."""
    m = re.match(r'^(\S+\s+(?:peatükk|jagu|osa|alljagu))\b', heading)
    return m.group(1) if m else heading


def mark_key(m: dict) -> tuple:
    return (m['act'], m['in_force'], m['note'])


def toc_unit(heads: list[dict]) -> dict:
    """The act's chapters and divisions as one unit, so a change to a heading is a change to a line."""
    return {'key': 'sisukord', 'label': 'Sisukord', 'title': '', 'section': [],
            'lines': [{'level': len(h['path']) - 1, 'text': h['path'][-1]} for h in heads],
            'marks': [m for h in heads for m in h['marks']]}


def unit_text(u: dict | None) -> tuple:
    if u is None:
        return ()
    return (u['label'], u['title'], tuple((l['level'], l['text']) for l in u['lines']))


def read_versions(act: dict, offline: bool) -> list[dict]:
    """Every consolidated version of the act, oldest first, with its parsed text."""
    listing = fetch_json(f'/akt/{act["group"]}/redaktsioonid', offline)['redaktsioonid']
    out = []
    for r in listing:
        xml = fetch(f'/akt/{r["id"]}/xml', offline)
        rd = Reader(xml)
        meta = rd.meta()
        units, heads = rd.sections()
        if str(meta['group']) != str(act['group']) or str(meta['id']) != str(r['id']):
            raise SystemExit(f'{act["slug"]}: version {r["id"]} does not identify itself as listed')
        out.append({'id': str(r['id']), 'meta': meta, 'units': units, 'heads': heads, 'notes': rd.notes, 'order': rd.order,
                    'sha256': hashlib.sha256(xml).hexdigest(), 'xml': f'{API}/akt/{r["id"]}/xml'})
    out.sort(key=lambda v: v['meta']['from'])
    # A few older marks give the Riigi Teataja reference without the act's id; the act-level list of amending acts
    # in the same versions gives the id for that reference.
    by_label = {m['label']: m['act'] for v in out for m in v['meta']['amendments'] if m['act']}
    for v in out:
        for u in v['units']:
            for m in u['marks']:
                if not m['act'] and m['label'] in by_label:
                    m['act'] = by_label[m['label']]
        for h in v['heads']:
            for m in h['marks']:
                if not m['act'] and m['label'] in by_label:
                    m['act'] = by_label[m['label']]
    for a, b in zip(out, out[1:]):
        if a['meta']['from'] == b['meta']['from']:
            raise SystemExit(f'{act["slug"]}: two versions valid from {a["meta"]["from"]}')
    return out


def states_of(versions: list[dict]) -> list[dict]:
    """The text of the act on each day it changed. Usually that is one state per version. Two kinds of day fall inside a
    version's validity and get a state of their own:
    - a wording printed in the version as "[… sõnastus alates 17.10.2005]" takes over from the one printed as
      "[… sõnastus kuni 16.10.2005]";
    - a section carries a new amendment mark dated after the version's first day (Riigi Teataja changed the version
      in place, for example to replace a minister's title from the day a reorganisation took effect). Before that day
      the section reads as in the previous version."""
    out: list[dict] = []
    for i, v in enumerate(versions):
        start, end = v['meta']['from'], v['meta']['to']
        before = out[-1]['units'] if out else {}
        inside: dict[str, str] = {}
        if i:
            prev_units = {u['key']: u for u in versions[i - 1]['units']}
            for u in v['units']:
                if u['key'] not in prev_units or any(ALT.match(re.sub(r'^\(\d+[^)]*\)\s*', '', l['text'])) for l in u['lines']):
                    continue
                old = {mark_key(m) for m in prev_units[u['key']]['marks']}
                new = [m for m in u['marks'] if mark_key(m) not in old]
                days = sorted(d for m in new for d in mark_days(m) if d > start and (end is None or d <= end))
                if days and not any(start in mark_days(m) for m in new):
                    inside[u['key']] = days[0]
        for day in sorted({start} | set(switch_days(v['units'], start, end)) | set(inside.values())):
            units = {}
            held = []
            for u in v['units'] + [toc_unit(v['heads'])]:
                src = u
                if u['key'] in inside and day < inside[u['key']]:
                    src = before[u['key']]
                    held.append(u['key'])
                units[u['key']] = {**src, 'lines': resolve(src['lines'], day)}
            out.append({'day': day, 'version': i, 'units': units, 'heads': v['heads'], 'inside': day != start, 'held': held})
    return out


def build_act(act: dict, offline: bool) -> dict:
    versions = read_versions(act, offline)
    states = states_of(versions)
    first = versions[0]['meta']
    # The first commit is the act as Riigi Teataja first gives it. Where that is the original text
    # ("algtekst-terviktekst") the act came into force earlier than the database's first version, on the day the
    # XML's own "vastuvõetud / jõustumine" gives; nothing changed it before the second version.
    start_day = states[0]['day']
    enacted_in_force = min((v['meta']['enacted']['in_force'] for v in versions
                            if v['meta']['enacted'] and v['meta']['enacted']['in_force']), default=None)
    if first['kind'] == 'algtekst-terviktekst' and enacted_in_force and enacted_in_force < start_day:
        start_day = enacted_in_force
    changes = []     # one per state after the first: [{'unit', 'before', 'after', 'causes', 'basis'}]
    problems = []
    for prev, cur in zip(states, states[1:]):
        D = cur['day']
        keys = list(dict.fromkeys(list(prev['units']) + list(cur['units'])))
        for k in keys:
            a, b = prev['units'].get(k), cur['units'].get(k)
            if unit_text(a) == unit_text(b):
                continue
            old = {mark_key(m) for m in (a['marks'] if a else [])}
            cur_marks = b['marks'] if b else []
            new = [m for m in cur_marks if mark_key(m) not in old]
            causes = sorted({m['act'] for m in new if D in mark_days(m) and m['act']})
            basis = 'new mark'
            if not causes:
                causes = sorted({m['act'] for m in cur_marks if D in mark_days(m) and m['act']})
                basis = 'mark'
            if not causes:
                # The section's mark names an act, and the act-level list of the same version says that act took
                # effect on this day, in part ("…, osaliselt 16.05.2016") or in full.
                listed = act_days(versions[cur['version']])
                causes = sorted({m['act'] for m in (new or cur_marks) if m['act'] and D in listed.get(m['act'], ())})
                basis = 'mark and act list'
            if not causes:
                # A chapter or division replaced as a whole carries the mark on its heading, not on each section.
                # Headings are matched by their number ("4. peatükk"), since the replacement can rename them.
                path = [head_num(p) for p in (b or a)['section']]
                causes = sorted({m['act'] for h in cur['heads'] if [head_num(p) for p in h['path']] == path[:len(h['path'])]
                                 for m in h['marks'] if D in mark_days(m) and m['act']})
                basis = 'chapter mark'
            if not causes:
                basis = 'none'
                problems.append(f'{act["slug"]} {k} {D}: no amendment mark for this day')
            changes.append({'day': D, 'state': cur, 'key': k, 'before': a, 'after': b, 'causes': causes, 'basis': basis,
                            'kind': 'inserted' if a is None else 'removed' if b is None else 'amended'})
    return {'act': act, 'versions': versions, 'states': states, 'changes': changes, 'problems': problems,
            'start_day': start_day}


# ---------------------------------------------------------------- the amending acts

def amending_act(act_id: str, offline: bool) -> dict:
    """Title, issuer and dates of an act named by an amendment mark, from that act's own XML in Riigi Teataja."""
    xml = fetch(f'/akt/{act_id}/xml', offline)
    rd = Reader(xml)
    md = rd.root.find(rd.t('metaandmed'))
    ref = rd.ref(md.find(rd.t('avaldamismarge')))
    enacted = md.find(rd.t('vastuvoetud'))
    proclaimed = md.find('/'.join(rd.t(x) for x in ('valjakuulutamine', 'valjakuulutatud', 'kuupaev')))
    name = rd.root.find(rd.t('aktinimi'))
    title = re.sub(r'\s+', ' ', rd.inline(name.find('.//' + rd.t('pealkiri')))).strip() if name is not None else ''
    return {'id': act_id, 'label': ref['label'], 'published': ref['published'], 'title': title,
            'issuer': (md.findtext(rd.t('valjaandja')) or '').strip(), 'type': (md.findtext(rd.t('dokumentLiik')) or '').strip(),
            'adopted': day_of(enacted.findtext(rd.t('aktikuupaev'))) if enacted is not None else None,
            'proclaimed': day_of(proclaimed.text) if proclaimed is not None else None,
            'sha256': hashlib.sha256(xml).hexdigest(), 'xml': f'{API}/akt/{act_id}/xml'}


# ---------------------------------------------------------------- files

def file_name(key: str) -> str:
    return f'{key}.md' if key in ('preambul', 'sisukord') else f'para-{key}.md'


def unit_md(u: dict) -> str:
    """A section as Markdown: its number and heading, then one line per lõige, punkt or printed line, each followed by
    a blank line. Points are list items, indented by their depth."""
    if u['key'] in ('preambul', 'sisukord'):
        head = f'# {u["label"]}'
    else:
        head = f'# {u["label"]}.' + (f' {u["title"]}' if u['title'] else '')
    out = [head, '']
    for l in u['lines']:
        out += [('  ' * (l['level'] - 1) + '- ' if l['level'] else '') + l['text'], '']
    return '\n'.join(out).rstrip('\n') + '\n'


def tree_of(state: dict) -> dict[str, str]:
    """Every file of one act on one day: {file name: content}."""
    return {file_name(k): unit_md(u) for k, u in state['units'].items()}


def is_repeal(before: dict | None, after: dict | None) -> bool:
    def gone(u):
        return u is not None and bool(u['lines']) and all(
            re.fullmatch(r'(\(\S+\)\s*|\S+\)\s*)?\[Kehtetu\]', l['text']) for l in u['lines'])
    return gone(after) and not gone(before)


def kind_of_change(c: dict) -> str:
    if c['kind'] == 'amended' and is_repeal(c['before'], c['after']):
        return 'repealed'
    return c['kind']


def editorial_kind(c: dict) -> str:
    """What an unexplained change is, as far as the text shows."""
    a = '\n'.join(t for _, t in unit_text(c['before'])[2]) if c['before'] else ''
    b = '\n'.join(t for _, t in unit_text(c['after'])[2]) if c['after'] else ''
    if '�' in a + b:
        return 'unreadable'
    if c['before'] and c['after'] and re.sub(r'\s', '', a) == re.sub(r'\s', '', b) \
            and unit_text(c['before'])[:2] == unit_text(c['after'])[:2]:
        return 'typesetting'
    return 'editorial'


# ---------------------------------------------------------------- the git repository

def git(repo: Path, *args: str, env: dict | None = None, input: str | None = None) -> str:
    out = subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, encoding='utf-8', env=env, input=input)
    if out.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {out.stderr}')
    return out.stdout


def last_sunday(year: int, month: int) -> dt.date:
    d = (dt.date(year, month + 1, 1) if month < 12 else dt.date(year + 1, 1, 1)) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def tallinn_offset(day: dt.date) -> int:
    """Hours ahead of UTC at noon in Tallinn. Summer time runs from the last Sunday in March to the last Sunday in
    September (until 1995) or October (from 1996); Estonia kept winter time from 31 October 1999 to 31 March 2002."""
    if dt.date(1999, 10, 31) <= day < dt.date(2002, 3, 31):
        return 2
    end = last_sunday(day.year, 9 if day.year <= 1995 else 10)
    return 3 if last_sunday(day.year, 3) <= day < end else 2


def commit_date(day: str, seconds: int = 0) -> str:
    """Noon in Tallinn on the day. Git cannot store a date before 1970: such a day becomes 1970-01-01, a second apart
    per commit, and the real day stays in the trailers. (No act in this record needs it.)"""
    d = dt.date.fromisoformat(day)
    if d.year < 1970:
        return f'@{seconds} +0000'
    off = tallinn_offset(d)
    stamp = int(dt.datetime(d.year, d.month, d.day, 12, tzinfo=dt.timezone(dt.timedelta(hours=off))).timestamp())
    return f'@{stamp} +0{off}00'


def section_list(items: list[tuple[str, dict]], short: dict[str, str]) -> str:
    return ', '.join(f'{short[slug]} {u["label"]}' for slug, u in items)


def subject_list(items: list[tuple[str, dict]], short: dict[str, str], limit: int = 6) -> str:
    by_act: dict[str, list[str]] = {}
    for slug, u in items:
        by_act.setdefault(slug, []).append(u['label'])
    parts = []
    for slug, labels in by_act.items():
        shown = labels[:limit] + ([f'+{len(labels) - limit}'] if len(labels) > limit else [])
        parts.append(f'{short[slug]} ' + ', '.join(shown))
    return '; '.join(parts)


KINDS = [('inserted', 'Lisatud / Inserted'), ('amended', 'Muudetud / Amended'),
         ('repealed', 'Kehtetuks tunnistatud / Repealed'), ('removed', 'Tekstist välja jäetud / Removed from the text')]
BASIS = {'new mark': 'amendment mark on the section', 'mark': 'amendment mark on the section',
         'mark and act list': "amendment mark on the section, and the act's entry into force in the version's list of amending acts",
         'chapter mark': 'amendment mark on the chapter or division heading'}
EDITORIAL = [('typesetting', 'Ladumine (ainult tühikud või reavahetused) / Typesetting (spaces or line breaks only)'),
             ('unreadable', 'Loetamatud märgid (U+FFFD) lähtefailis / Unreadable characters (U+FFFD) in the source file'),
             ('editorial', 'Muu toimetuslik muudatus / Other editorial change')]
RT = ('Riigi Teataja', 'toimetus@riigiteataja.invalid')


def act_email(act_id: str) -> str:
    return f'akt-{act_id}@riigiteataja.invalid'


def events_of(built: list[dict]) -> dict[tuple, list]:
    """Commits to make, keyed (day, rank, cause): the first text of each act; each amending act on each day it took
    effect, across every act in the record; a section that several acts changed on one day; and each act's changes
    on a day that no amendment mark explains."""
    events: dict[tuple, list] = {}
    for b in built:
        slug = b['act']['slug']
        events.setdefault((b['start_day'], 0, ('first', slug)), []).append((slug, None, b['states'][0], None))
        for c in b['changes']:
            if len(c['causes']) == 1:
                key = (c['day'], 1, ('act', c['causes'][0]))
            elif c['causes']:
                key = (c['day'], 2, ('ambiguous', slug, tuple(c['causes'])))
            else:
                key = (c['day'], 3, ('rt', slug))
            events.setdefault(key, []).append((slug, c['key'], c['state'], c))
    return events


def write_repo(repo: Path, built: list[dict], acts: dict[str, dict], docs: Path, today: str, extra) -> dict:
    """Rebuilds the repository from scratch (it is deterministic), keeping the remote it is pushed to."""
    remote = None
    if (repo / '.git').exists():
        out = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=repo, capture_output=True, text=True)
        remote = out.stdout.strip() or None

    def force(fn, path, _exc):
        os.chmod(path, 0o700)
        fn(path)
    if repo.exists():
        for p in repo.iterdir():
            shutil.rmtree(p, onexc=force) if p.is_dir() else p.unlink()
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'config', 'core.autocrlf', 'false')
    git(repo, 'config', 'core.quotepath', 'false')
    if remote:
        git(repo, 'remote', 'add', 'origin', remote)

    short = {b['act']['slug']: b['versions'][-1]['meta']['short'] or b['act']['slug'].upper() for b in built}
    by_slug = {b['act']['slug']: b for b in built}
    events = events_of(built)

    def order(e):
        day, rank, cause = e
        if cause[0] == 'act':
            a = acts[cause[1]]
            return (day, rank, a.get('published') or '', a['label'], cause[1])
        return (day, rank, '', '', str(cause))

    tags: dict[str, str] = {}
    act_days_seen: dict[str, list[str]] = {}
    switched = False
    commits = []
    for n, ev in enumerate(sorted(events, key=order)):
        day, rank, cause = ev
        items = events[ev]
        if day > today and not switched:
            # Changes adopted but not yet in force live on their own branch, so main is the law today.
            git(repo, 'checkout', '-q', '-b', FUTURE_BRANCH)
            switched = True
        for slug, key, state, c in items:
            folder = repo / slug
            if c is None:       # the act's first text: every file
                folder.mkdir(parents=True, exist_ok=True)
                for name, text in tree_of(state).items():
                    (folder / name).write_text(text, encoding='utf-8', newline='\n')
                continue
            path = folder / file_name(key)
            if c['after'] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(unit_md(state['units'][key]), encoding='utf-8', newline='\n')
        git(repo, 'add', '-A')
        when = commit_date(day, n + 1)
        changed = sorted(((slug, c['after'] or c['before']) for slug, key, state, c in items if c is not None),
                         key=lambda x: (x[0], x[1]['key']))
        affecting = section_list(changed, short)
        if cause[0] == 'first':
            slug = cause[1]
            b = by_slug[slug]
            v = b['versions'][0]
            meta = v['meta']
            enacted = next((x['meta']['enacted'] for x in reversed(b['versions']) if x['meta']['enacted']), None) or {}
            if meta['kind'] == 'algtekst-terviktekst':
                eref = enacted['ref'] if enacted.get('ref', {}).get('id') else meta['ref']
                author, email = eref['label'], act_email(eref['id'])
                msg = [f'{short[slug]}: algtekst ({eref["label"]})', '',
                       f'{meta["title"]}, nagu see vastu võeti. Riigi Teataja esimene redaktsioon (kehtiv alates',
                       f'{meta["from"]}) on algtekst-terviktekst: seadus muutmata kujul.', '',
                       f'The act as enacted. The first version Riigi Teataja holds (valid from {meta["from"]}) is the',
                       'original text with no amendments, so it is the text from the day the act came into force.', '',
                       f'Issuer: {meta["issuer"]}']
                if enacted.get('adopted'):
                    msg.append(f'Adopted: {enacted["adopted"]}')
                if meta['ref'] and meta['ref'].get('published'):
                    msg.append(f'Published: {meta["ref"]["published"]} ({eref["label"]})')
                msg.append(f'In-force: {day}')
                if day != meta['from']:
                    msg.append(f'Version-valid-from: {meta["from"]}')
                msg += [f'Version: {v["id"]}', f'Source: {SITE}/akt/{v["id"]}']
            else:
                author, email = RT
                msg = [f'{short[slug]}: terviktekst seisuga {day}', '',
                       f'{meta["title"]}: the first consolidated version Riigi Teataja holds. Who wrote the older',
                       'text is not known to this record.', '', f'In-force: {day}', f'Version: {v["id"]}',
                       f'Source: {SITE}/akt/{v["id"]}']
            if day < '1970-01-01':
                msg.append(f'Git-date-clamped: {day}')
        elif cause[0] == 'act':
            a = acts[cause[1]]
            author, email = a['label'], act_email(a['id'])
            bases = sorted({BASIS[c['basis']] for _, _, _, c in items})
            msg = [f'{subject_list(changed, short)} ({a["label"]})', '']
            if a.get('title'):
                msg += [a['title'], '']
            for k, name in KINDS:
                ls = sorted(((slug, c['after'] or c['before']) for slug, key, state, c in items if kind_of_change(c) == k),
                            key=lambda x: (x[0], x[1]['key']))
                if ls:
                    msg.append(f'{name}: {section_list(ls, short)}')
            msg.append('')
            if a.get('issuer'):
                msg.append(f'Issuer: {a["issuer"]}')
            if a.get('adopted'):
                msg.append(f'Adopted: {a["adopted"]}')
            if a.get('proclaimed'):
                msg.append(f'Proclaimed: {a["proclaimed"]}')
            if a.get('published'):
                msg.append(f'Published: {a["published"]} ({a["label"]})')
            msg += [f'In-force: {day}', f'Affecting: {affecting}', 'Cause-basis: ' + '; '.join(bases),
                    f'Source: {SITE}/akt/{a["id"]}']
            act_days_seen.setdefault(a['id'], []).append(day)
        elif cause[0] == 'ambiguous':
            author, email = RT
            cands = [acts[x] for x in cause[2]]
            msg = [f'{subject_list(changed, short)}: {len(cands)} samal päeval jõustunud akti', '',
                   'Selle paragrahvi muutmismärked nimetavad mitut samal päeval jõustunud akti ega ütle, milline',
                   'neist millise rea kirjutas. Muudatust ei omistata ühelegi neist.', '',
                   "The section's amendment marks name several acts that took effect on the same day and do not say",
                   'which of them wrote which line. The change is not credited to any one of them.', '']
            msg += [f'Candidate: {x["label"]} ({x["title"]})' for x in cands]
            msg += [f'In-force: {day}', f'Affecting: {affecting}']
            msg += [f'Source: {SITE}/akt/{x["id"]}' for x in cands]
        else:
            slug = cause[1]
            author, email = RT
            v = by_slug[slug]['versions'][items[0][2]['version']]
            msg = [f'{subject_list(changed, short)}: muudatus ilma muutmismärketa', '',
                   'Riigi Teataja tervikteksti redaktsioon muutis nende paragrahvide teksti, kuid ükski muutmismärge',
                   'ei nimeta sel päeval jõustunud muudatust. Muudatust ei omistata ühelegi seadusele.', '',
                   'The consolidated text changed in these sections, but no amendment mark names a change taking',
                   'effect on this day. The change is not credited to any law.', '']
            for k, name in EDITORIAL:
                ls = sorted(((s, c['after'] or c['before']) for s, key, state, c in items if editorial_kind(c) == k),
                            key=lambda x: (x[0], x[1]['key']))
                if ls:
                    msg.append(f'{name}: {section_list(ls, short)}')
            msg += ['', f'In-force: {day}', f'Affecting: {affecting}', f'Version: {v["id"]}', f'Source: {SITE}/akt/{v["id"]}']
        env = {**os.environ, 'GIT_AUTHOR_NAME': author, 'GIT_AUTHOR_EMAIL': email, 'GIT_AUTHOR_DATE': when,
               'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': when}
        git(repo, 'commit', '-q', '--allow-empty', '-F', '-', env=env, input='\n'.join(msg) + '\n')
        head = git(repo, 'rev-parse', 'HEAD').strip()
        commits.append({'day': day, 'cause': cause, 'hash': head, 'author': author})
        for slug in sorted({s for s, _, _, _ in items}):
            tags[f'{slug}/{day}'] = head
        if cause[0] == 'act':
            tags[f'akt/{cause[1]}/{day}'] = head
    # An act that took effect on one day is tagged akt/<id>; one that took effect in parts keeps a tag per day.
    for act_id, days in act_days_seen.items():
        if len(set(days)) == 1:
            tags[f'akt/{act_id}'] = tags.pop(f'akt/{act_id}/{days[0]}')
    for name, head in sorted(tags.items()):
        git(repo, 'tag', '-f', name, head)

    # Documentation, tables, tools and the record of how it was made come last, by Lexifina, on main (merged into the
    # future branch). They are dated --today, the day the data was retrieved, so a rebuild on another day from the
    # same data gives the same hashes.
    if switched:
        git(repo, 'checkout', '-q', 'main')
    law_tip = git(repo, 'rev-parse', 'HEAD').strip()
    for p in sorted(docs.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            dest = repo / p.relative_to(docs)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    (repo / 'tools').mkdir(exist_ok=True)
    for name in ('build.py', 'reproduce.py', 'check_repo.py'):
        if (HERE / name).exists():
            (repo / 'tools' / name).write_bytes((HERE / name).read_bytes())
    write_tables(repo, built, acts, short, today)
    stats = {'commits': len(commits) + 1, 'law_commits': sum(1 for c in commits if c['cause'][0] == 'act'),
             'first_commits': sum(1 for c in commits if c['cause'][0] == 'first'),
             'editorial_commits': sum(1 for c in commits if c['cause'][0] == 'rt'),
             'ambiguous_commits': sum(1 for c in commits if c['cause'][0] == 'ambiguous'),
             'tags': len(tags), 'law_tip': law_tip, 'future': switched}
    extra(repo, built, acts, stats, REQUESTS, today)
    git(repo, 'add', '-A')
    when = commit_date(today)
    env = {**os.environ, 'GIT_AUTHOR_NAME': COMMITTER[0], 'GIT_AUTHOR_EMAIL': COMMITTER[1], 'GIT_AUTHOR_DATE': when,
           'GIT_COMMITTER_NAME': COMMITTER[0], 'GIT_COMMITTER_EMAIL': COMMITTER[1], 'GIT_COMMITTER_DATE': when}
    git(repo, 'commit', '-q', '-m', 'Dokumentatsioon, tabelid, tööriistad ja REPRODUCE.md', env=env)
    if switched:
        git(repo, 'checkout', '-q', FUTURE_BRANCH)
        git(repo, 'merge', '-q', '--no-edit', 'main', env=env)
        git(repo, 'checkout', '-q', 'main')
    return stats


def write_tables(repo: Path, built: list[dict], acts: dict[str, dict], short: dict[str, str], today: str):
    """muutmisaktid.csv (the amending acts and what they changed) and a README per act listing its sections."""
    touched: dict[str, set] = {}
    days: dict[str, set] = {}
    for b in built:
        for c in b['changes']:
            if len(c['causes']) == 1:
                touched.setdefault(c['causes'][0], set()).add(short[b['act']['slug']])
                days.setdefault(c['causes'][0], set()).add(c['day'])
    rows = []
    for a in sorted(acts.values(), key=lambda a: (a.get('published') or '', a['label'])):
        if a['id'] not in touched:
            continue
        rows.append({'viide': a['label'], 'akt': f'{SITE}/akt/{a["id"]}', 'pealkiri': a['title'], 'valjaandja': a['issuer'],
                     'vastu_voetud': a.get('adopted') or '', 'valja_kuulutatud': a.get('proclaimed') or '',
                     'avaldatud': a.get('published') or '', 'joustunud': ' '.join(sorted(days[a['id']])),
                     'muudab': ' '.join(sorted(touched[a['id']]))})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    (repo / 'muutmisaktid.csv').write_text(buf.getvalue(), encoding='utf-8', newline='\n')

    for b in built:
        slug = b['act']['slug']
        last = b['versions'][-1]['meta']
        now = next((s for s in reversed(b['states']) if s['day'] <= today), b['states'][-1])
        counts: dict[str, int] = {}
        lasts: dict[str, str] = {}
        for c in b['changes']:
            if c['day'] <= today:
                counts[c['key']] = counts.get(c['key'], 0) + 1
                lasts[c['key']] = c['day']
        out = [f'# {last["title"]} ({short[slug]})', '',
               f'Riigi Teataja: <{SITE}/akt/{b["versions"][-1]["id"]}> · {len(b["versions"])} redaktsiooni / versions, '
               f'{b["versions"][0]["meta"]["from"]} … {last["from"]}', '',
               '| Paragrahv | Pealkiri | Muudatusi / Changes | Viimati / Last |', '| --- | --- | ---: | --- |']
        section = None
        for key, u in now['units'].items():
            if key == 'sisukord':
                continue
            sec = ' › '.join(u['section'])
            if sec != section and sec:
                out.append(f'| **{sec}** | | | |')
                section = sec
            out.append(f'| [{u["label"]}]({file_name(key)}) | {u["title"]} | {counts.get(key, 0)} | {lasts.get(key, "")} |')
        (repo / slug / 'README.md').write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- main

def build_all(offline: bool) -> tuple[list[dict], dict[str, dict]]:
    built = [build_act(a, offline) for a in ACTS]
    ids = sorted({x for b in built for c in b['changes'] for x in c['causes']})
    acts = {i: amending_act(i, offline) for i in ids}
    return built, acts


def main():
    from collections import Counter
    from reproduce import write_docs
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[2] / 'estonia-law'))
    ap.add_argument('--offline', action='store_true', help='read only the cache; fail on anything not cached')
    ap.add_argument('--today', default=dt.date.today().isoformat(),
                    help='the day the data was retrieved: dates the documentation commit and splits off future changes')
    args = ap.parse_args()
    built, acts = build_all(args.offline)
    for b in built:
        basis = Counter(c['basis'] for c in b['changes'])
        print(f'{b["act"]["slug"]}: {len(b["versions"])} versions {b["versions"][0]["meta"]["from"]}..'
              f'{b["versions"][-1]["meta"]["from"]}, {len(b["states"])} states, {len(b["changes"])} section changes {dict(basis)}')
    stats = write_repo(Path(args.repo), built, acts, HERE / 'repo', args.today, write_docs)
    print(f'repo: {stats} -> {args.repo}')


if __name__ == '__main__':
    main()
