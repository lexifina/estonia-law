"""Checks the Estonian law repository against Riigi Teataja, in two independent ways:

1. git against the official XML: for every act and every day its text changed (each consolidated version's first day,
   and the two days inside a version that REPRODUCE.md describes), the files in git on that day must be exactly the
   files written from Riigi Teataja's XML of the version valid that day.
2. the XML reading against Riigi Teataja's own plain text: for every version, the words read from the XML, in order,
   must be the characters of Riigi Teataja's plain-text rendering of the same version (/akt/<id>/txt), ignoring
   whitespace, once the amendment notes Riigi Teataja prints in brackets and its editorial notes are taken out.
It also checks that every cached source file has the sha256 recorded in data/versioonid.json.

    python -X utf8 scripts/estonia-law/check_repo.py [--repo ../estonia-law] [--write]

Reads only the build's cache (run build.py first). --write records the result in verification.json beside this
script, for REPRODUCE.md. Standard library only.
"""
import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402

SUPERSCRIPT = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')


def git(repo: str, *args: str) -> str:
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, encoding='utf-8', check=True).stdout


def commit_on(repo: str, slug: str, day: str, branches: list[str]) -> str | None:
    branch = 'tulevik' if day > TODAY and 'tulevik' in branches else 'main'
    for line in git(repo, 'log', '--format=%H %ad', '--date=format:%Y-%m-%d', branch, '--', f'{slug}/').splitlines():
        h, d = line.split()
        if d <= day:
            return h
    return None


def canonical(s: str) -> str:
    """Characters only: no whitespace, superscripts as plain digits, no '^' (the txt writes 5^1 where the XML has a
    superscript)."""
    return re.sub(r'\s+', '', s.translate(SUPERSCRIPT).replace('^', ''))


def note_texts(v: dict) -> list[str]:
    """Footnotes on EU law and signature blocks as Riigi Teataja's plain text prints them after the act."""
    root = build.ET.fromstring(build.fetch(f'/akt/{v["id"]}/xml', offline=True))
    out = []
    for e in root.iter():
        name = e.tag.rsplit('}', 1)[-1]
        if name == 'normtehnmarkus' and len(list(e)) > 1:
            out.append(''.join(e.itertext()))
        elif name == 'allkirjastaja':     # printed as "Eiki Nestor / Riigikogu esimees"
            part = {c.tag.rsplit('}', 1)[-1]: ''.join(c.itertext()) for c in e}
            out.append(' '.join(part.get(k, '') for k in ('eesnimi', 'perekonnanimi', 'ametinimetus')))
    return out


def ours(v: dict) -> str:
    """The version as read from its XML, in document order: headings, section numbers and titles, lines."""
    units = {u['key']: u for u in v['units']}
    out = []
    for kind, x in v['order']:
        if kind == 'head':
            out.append(x)
        else:
            u = units[x]
            if x != 'preambul':
                out.append(u['label'] + '.' + (' ' + u['title'] if u['title'] else ''))
            out += [l['text'] for l in u['lines']]
    return '\n'.join(out)


def official(v: dict, first_line: str) -> str:
    """Riigi Teataja's plain text of the version, from the first line of the act's text, without the notes it adds:
    amendment notes "[RT I, … - jõust. …]", repeal notes reduced to "[Kehtetu]", error-correction notes, the
    Constitution's "Õiend", and the "( )" it prints for a paragraph without a number."""
    t = build.fetch(f'/akt/{v["id"]}/txt', offline=True).decode('utf-8').replace('\r', '')
    i = t.find(first_line[:40])
    if i < 0:
        raise SystemExit(f'{v["id"]}: first line not found in the txt')
    t = t[i:]
    t = re.sub(r'\[(?:Kehtetu|kehtetu)\s*[-–][^\]]*\]', '[Kehtetu]', t)
    t = re.sub(r'\[RT[^\]]*\]', '', t)
    t = re.sub(r'\n\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}\nVeaparandus[^\n]*', '', t)
    t = re.sub(r'\nÕiend[^\n]*\n.*', '', t, flags=re.S)
    t = re.sub(r'\(\s*\)', '', t)
    return t


def main():
    global TODAY
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[2] / 'estonia-law'))
    ap.add_argument('--today', default='2026-10-28')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    TODAY = args.today
    repo = args.repo
    built, acts = build.build_all(offline=True)
    branches = [b.strip(' *') for b in git(repo, 'branch', '--list').splitlines()]
    result = {'git_vs_xml': {}, 'xml_vs_txt': {}, 'sha256': {}}

    # 3. the source files
    manifest = json.loads((Path(repo) / 'data' / 'versioonid.json').read_text(encoding='utf-8'))
    recorded = {v['id']: v['sha256'] for a in manifest['acts'] for v in a['versions']}
    recorded.update({a['id']: a['sha256'] for a in manifest['amending_acts']})
    bad_sha = []
    for b in built:
        for v in b['versions']:
            if recorded.get(v['id']) != v['sha256']:
                bad_sha.append(v['id'])
    for a in acts.values():
        if recorded.get(a['id']) != a['sha256']:
            bad_sha.append(a['id'])
    result['sha256'] = {'files': len(recorded), 'mismatches': bad_sha}
    print(f'sha256: {len(recorded)} source files, {len(bad_sha)} mismatches')

    for b in built:
        slug = b['act']['slug']
        # 1. git against the XML
        states = files = bad = 0
        for s in b['states']:
            states += 1
            day = s['day']
            want = build.tree_of(s)
            h = commit_on(repo, slug, day, branches)
            have = {}
            if h:
                for f in git(repo, 'ls-tree', '--name-only', h, f'{slug}/').split():
                    name = f.split('/', 1)[1]
                    if name != 'README.md':
                        have[name] = git(repo, 'show', f'{h}:{f}')
            files += len(want)
            if have != want:
                bad += 1
                missing = sorted(set(want) - set(have))
                extra = sorted(set(have) - set(want))
                differ = sorted(k for k in set(want) & set(have) if want[k] != have[k])
                print(f'MISMATCH {slug} {day}: missing {missing[:5]} extra {extra[:5]} differ {differ[:5]}')
        result['git_vs_xml'][slug] = {'versions': len(b['versions']), 'states': states, 'files': files, 'mismatches': bad,
                                      'inside_days': [s['day'] for s in b['states'] if s['inside']]}
        print(f'{slug}: git vs XML: {states} days ({len(b["versions"])} versions), {files} files compared, {bad} mismatches')

        # 2. the XML reading against the official plain text
        failed = []
        for v in b['versions']:
            o = ours(v)
            A, B = canonical(o), canonical(official(v, o.split('\n')[0]))
            for note in note_texts(v):
                B = B.replace(canonical(note), '', 1)
            if A != B:
                sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
                ops = [op for op in sm.get_opcodes() if op[0] != 'equal']
                failed.append(v['id'])
                for op, i1, i2, j1, j2 in ops[:3]:
                    print(f'  TXT {slug} {v["meta"]["from"]} {op}: {A[max(0, i1 - 30):i2 + 30]!r} || {B[max(0, j1 - 30):j2 + 30]!r}')
        result['xml_vs_txt'][slug] = {'versions': len(b['versions']), 'mismatches': failed}
        print(f'{slug}: XML vs official txt: {len(b["versions"])} versions, {len(failed)} differ')

    ok = not bad_sha and all(r['mismatches'] == 0 for r in result['git_vs_xml'].values()) \
        and all(not r['mismatches'] for r in result['xml_vs_txt'].values())
    result['ok'] = ok
    if args.write:
        path = HERE / 'verification.json'
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        data['check'] = result
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('OK' if ok else 'FAILED')
    raise SystemExit(0 if ok else 1)


TODAY = '2026-10-28'

if __name__ == '__main__':
    main()
