#!/usr/bin/env python3
"""Parse the rendered All_tasks HTML + completion.json into clean tasks.json."""
import re, json, html as ihtml

html = open('all_tasks.html').read()
completion = json.load(open('completion.json'))  # id(str) -> percent

# Split into rows by the data-ca-task-id marker
rows = re.split(r'<tr data-ca-task-id="', html)[1:]

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ihtml.unescape(s).replace('\xa0', ' ').strip()

TIER_PTS = {'Easy': 1, 'Medium': 2, 'Hard': 3, 'Elite': 4, 'Master': 5, 'Grandmaster': 6}
tasks = []
for r in rows:
    tid = int(r[:r.index('"')])
    tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
    if len(tds) < 6:
        continue
    monster = strip_tags(tds[0])
    name = strip_tags(tds[1])
    desc = strip_tags(tds[2])
    ttype = strip_tags(tds[3])
    tier_raw = strip_tags(tds[4])              # e.g. "Easy (1 pt)"
    m = re.match(r'([A-Za-z]+)', tier_raw)
    tier = m.group(1) if m else tier_raw
    points = TIER_PTS.get(tier, 0)
    comp_raw = strip_tags(tds[5])              # e.g. "58.1%" or ""
    cm = re.match(r'([\d.]+)%', comp_raw)
    comp = float(cm.group(1)) if cm else completion.get(str(tid))
    tasks.append({
        'id': tid, 'name': name, 'monster': monster, 'description': desc,
        'type': ttype, 'tier': tier, 'points': points, 'completion': comp,
    })

tasks.sort(key=lambda t: t['id'])
json.dump(tasks, open('tasks.json', 'w'), indent=None, separators=(',', ':'))

# sanity report
from collections import Counter
tc = Counter(t['tier'] for t in tasks)
missing = sum(1 for t in tasks if t['completion'] is None)
print(f"total={len(tasks)} tiers={dict(tc)} missing_completion={missing}")
print(f"total_points={sum(t['points'] for t in tasks)}")
print("sample:", json.dumps(tasks[0]))
