"""Prints an act, or one section of it, as it stood on a given day, from this repository's history.

    python tools/seisuga.py 2010-01-01 ps 156      # § 156 of the Constitution on 1 January 2010
    python tools/seisuga.py 2010-01-01 rkvs 48b4   # § 48⁴ of the Riigikogu Election Act ("b4" is the superscript 4)
    python tools/seisuga.py 2020-01-01 iks         # every section of the Personal Data Protection Act on that day

Each commit is dated noon in Tallinn on the day its change took effect, so the text in force on a day is the last
commit on or before it that touched the act. Changes adopted but not yet in force are on the branch "tulevik"; a day
after today reads from there. Standard library only.
"""
import datetime as dt
import re
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout


def file_name(key: str) -> str:
    if key in ('preambul', 'sisukord'):
        return f'{key}.md'
    m = re.fullmatch(r'(\d+)(b\d+)?', key)
    return f'para-{int(m.group(1)):03d}{m.group(2) or ""}.md' if m else f'para-{key}.md'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2]
    dt.date.fromisoformat(day)
    future = git('branch', '--list', 'tulevik').strip()
    branch = 'tulevik' if day > dt.date.today().isoformat() and future else 'main'
    # %ad with a format shows each commit's day in its own time zone (Tallinn), which is the day it took effect.
    commit = ''
    for line in git('log', '--format=%H %ad', '--date=format:%Y-%m-%d', branch, '--', f'{act}/').splitlines():
        h, d = line.split()
        if d <= day:
            commit = h
            break
    if not commit:
        sys.exit(f'{act} is not in the record on {day}.')
    if len(sys.argv) > 3:
        name = file_name(sys.argv[3])
        try:
            print(git('show', f'{commit}:{act}/{name}'), end='')
        except subprocess.CalledProcessError:
            sys.exit(f'{act}/{name} was not in the text on {day}.')
        return
    files = [f for f in git('ls-tree', '--name-only', commit, f'{act}/').split()
             if f.endswith('.md') and not f.endswith('/README.md')]
    for f in files:
        print(git('show', f'{commit}:{f}'))


if __name__ == '__main__':
    main()
