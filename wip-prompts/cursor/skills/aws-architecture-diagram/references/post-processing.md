# Post-processing pipeline

This repository does not install the Cursor PostToolUse draw.io hook. After writing a `.drawio` file, run the scripts in `scripts/lib/` yourself, in this order:

1. **post_process_drawio.py** — chains the fixers below
2. **validate_drawio.py** — XML structure, AWS4 shapes, edges, geometry

Do not run `drawio_url.py`. Do not generate or present a diagrams.net preview URL.

Fixers inside `post_process_drawio.py`:

1. **fix_nesting.py** — Region `container=0`, re-parent children
2. **fix_icon_colors.py** — icon `fillColor` matches category
3. **fix_step_badges.py** — nudge overlapping badges
4. **fix_placement** — moves `#f5f5f5` Users/external-actor boxes outside AWS Cloud. Do not draw in-account services as those boxes (see SKILL.md overlay)
5. **fix_legend_size** — legend height matches diagram

Dependency: `defusedxml>=0.7.1` from `scripts/requirements.txt`. Prefer `.pixi/envs/default/bin/python` or `backend/.venv/bin/python` when present, else `python3`. Do not run `scripts/validate-drawio.sh`; that is the upstream PostToolUse hook and this repo does not install it.
