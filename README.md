# my-skills

Place for personal skills.

Each skill is a folder at the repo root holding a `SKILL.md`. That one layout serves every
way of consuming them — the `skills` CLI, a Claude Code plugin, or a plain copy.

## Skills

| Skill | What it does |
|---|---|
| [`comment-cleanup`](comment-cleanup/SKILL.md) | Cleans code comments so each says what the code **is** or **must be** — cutting history, rationale, consequences and measurements, and catching comments that describe code which no longer exists. |

## Installing

### `npx skills add`

```bash
npx skills add MarekHutnik/my-skills/comment-cleanup
```

Or take everything in the repo:

```bash
npx skills add MarekHutnik/my-skills
```

### As a Claude Code plugin

```
/plugin marketplace add MarekHutnik/my-skills
/plugin install my-skills@mhu-skills
```

The marketplace is `mhu-skills`; it ships one plugin, `my-skills`, which is the repo root.

### By hand

Copy a skill folder into `~/.claude/skills/` (personal) or `.claude/skills/` (one project):

```bash
cp -r comment-cleanup ~/.claude/skills/
```

## Adding a skill

1. Create `<skill-name>/SKILL.md` at the repo root. The folder name is the skill name.
2. Give it YAML frontmatter with `name` (matching the folder) and `description`. The
   description is what Claude matches against to decide when to load the skill, so write it
   as *when to use this*, not just what it is.
3. Add the folder to the `skills` array in [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)
   so the plugin path picks it up too.
4. Add a row to the table above.

Step 3 is the one that is easy to forget: skills live at the repo root for the `skills` CLI,
so the plugin has to be told about each one explicitly rather than scanning a `skills/`
directory.

## Licence

[Apache 2.0](LICENSE).
