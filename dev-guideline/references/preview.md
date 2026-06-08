# Preview — `/dev-guideline preview`

Launches a local browser dashboard showing the project's `.agent/` state in a
three-column layout.

## Run

From the project root:

```
python ~/.claude/skills/dev-guideline/scripts/preview.py
```

Or via the skill subcommand `/dev-guideline preview`.

Default port is `7878`. Override with `--port`. Default host is `127.0.0.1`.

The script opens the user's default browser to `http://127.0.0.1:7878/`.

## What it shows

Three columns:

```
┌──────────┬────────────────────┬───────────┐
│ TASKS    │ <selected task>    │ PROGRESS  │
│ active   │ Description        │ Shipped   │
│ blocked  │ Checklist          │ In prog.  │
│ done     │ Resume             │ Planned   │
│          │ Notes              │           │
│ + new   │                    │ MEMORY    │
│ refresh  │                    │ entries   │
└──────────┴────────────────────┴───────────┘
```

- **Left**: TASKS list — `active`, `blocked`, recent `completed`. Click to load center.
- **Center**: selected task rendered as markdown with status badge, age, next-step preview.
- **Right**: `PROGRESS.md` shipped/in-progress/planned counts + link to full view;
  `MEMORY.md` entry count + last_updated + link to full view.

## Live reload

Server watches `.agent/` via SSE; any change to a markdown file pushes a refresh
to the browser. No need to manually reload.

## Read-only

The dashboard is a viewer. It does not edit files. Editing through a browser
endpoint is out of scope (write endpoints need auth and validation that aren't
worth it for a single-user local tool).

## Stopping the server

Ctrl+C in the terminal that started it. The process does not daemonize.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Port in use | another process on 7878 | `--port 7879` |
| Browser doesn't open | no default browser configured | open `http://127.0.0.1:7878/` manually |
| Empty dashboard | not in a project with `.agent/` | `cd` to the project, or run `/dev-guideline setup` |
| Markdown not rendering | local marked.js asset missing | reinstall the skill |
