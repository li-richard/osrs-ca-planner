# OSRS Combat Achievements Route Planner

A single-file web app that finds the **easiest Combat Achievements you haven't done** and maps a route to your next tier. Built from live [OSRS Wiki](https://oldschool.runescape.wiki/w/Combat_Achievements) data (all 637 tasks, with crowdsourced completion rates).

![tier thresholds: Easy 41 → Grandmaster 2630](https://img.shields.io/badge/tasks-637-blue) ![no build step](https://img.shields.io/badge/dependencies-none-green)

## Features

- **Username sync** via [WikiSync](https://oldschool.runescape.wiki/w/RuneScape:WikiSync) — type your RSN and it checks off your completed tasks, computes your tier, and updates the plan.
- **Easiest path to next tier** — the lowest-difficulty set of unfinished tasks that clears the next reward threshold, grouped into expandable per-boss stops.
- **Convenient extras** — lower-completion ("harder") tasks that are cheap to grab where you already go (e.g. kill-count tasks that stack while you grind), with a separate "with extras" points total.
- **Achievability gates** — once synced, tasks you can't attempt yet (missing quests or skill levels, incl. Slayer) are hidden/flagged based on your account.
- **Skip / done** per task, **filters** (tier, type, Wilderness/Raids/Slayer category, search), **route value** ranking, and local-storage persistence.

### How "easiest" is scored
An ease score blends crowdsourced completion % (45%), tier (35%), and task type (20%); Kill Count ranks easiest, Speed hardest.

## Running it

The app is a single self-contained file, but the live WikiSync lookup needs to run from a real origin (opening `file://` directly is blocked by the browser's CORS / the WikiSync CDN). Use the included launcher, which also proxies the lookup server-side:

```bash
python3 serve.py      # serves http://localhost:8765 and opens your browser
```

Everything except the live lookup (manual check-off, paste-import, points entry) also works if you just open `osrs-combat-achievements.html` directly.

## Project layout

| Path | What |
|------|------|
| `osrs-combat-achievements.html` | The built, self-contained app (data embedded) |
| `app_template.html` | Template with a `/*__TASKS__*/` placeholder for the task data |
| `serve.py` | Local launcher + WikiSync proxy |
| `data/parse.py` | Parses the wiki data into `data/tasks.json` |
| `data/tasks.json` | Clean task dataset (637 tasks) |
| `data/completion.json` | Crowdsourced completion rates from the wiki |

## Rebuilding the data / app

```bash
# 1. fetch the raw sources (completion rates + the all-tasks table)
curl -s "https://oldschool.runescape.wiki/w/Module:Combat_Achievements/completion.json?action=raw" -o data/completion.json
curl -s "https://oldschool.runescape.wiki/api.php?action=parse&format=json&page=Combat_Achievements/All_tasks&prop=text&disablelimitreport=1" \
  | python3 -c "import sys,json; open('data/all_tasks.html','w').write(json.load(sys.stdin)['parse']['text']['*'])"

# 2. parse into data/tasks.json
cd data && python3 parse.py && cd ..

# 3. inject the data into the template -> osrs-combat-achievements.html
python3 - <<'PY'
import json
tmpl=open('app_template.html').read()
tasks=json.load(open('data/tasks.json'))
open('osrs-combat-achievements.html','w').write(tmpl.replace('/*__TASKS__*/[]', json.dumps(tasks,separators=(',',':'))))
PY
```

## Notes

- Not affiliated with Jagex. Data © OSRS Wiki contributors (CC BY-NC-SA).
- WikiSync only returns data for accounts that have the WikiSync RuneLite plugin enabled and synced.
- Boss requirement gates are verified against the wiki but check only level/quest completion (a few bosses have extra steps like an Achievement Diary).
