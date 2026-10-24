# Superpowers in this setup

[Superpowers](https://github.com/obra/superpowers) is a complete software
development methodology built on composable agent skills. It is installed
locally at `~/.config/opencode/superpowers/` (a clone of the upstream repo)
and its skills are exposed to opencode automatically.

## Skills included

brainstorming · writing-plans · executing-plans · subagent-driven-development ·
dispatching-parallel-agents · test-driven-development · systematic-debugging ·
verification-before-completion · requesting-code-review ·
receiving-code-review · finishing-a-development-branch · using-git-worktrees ·
writing-skills · using-superpowers

## Installing into other harnesses

The upstream README keeps a per-harness install matrix (Claude Code, Codex,
Cursor, Gemini CLI, opencode, and more). The generic route that works for any
skills-capable agent:

```bash
npx -y skills add obra/superpowers -g -a <agent-name>
```

Or clone the repo and point the harness's skills directory at
`superpowers/skills/`.

## How it combines with this repo

- `rules/AGENTS.md` instructs agents to inventory installed skills first and
  search the ecosystem (`find-skills`) only when nothing covers the task —
  superpowers provides the methodology layer under that discipline.
- Project templates in `templates/` pair with superpowers' planning skills
  (`writing-plans`, `executing-plans`) — plans live in
  `docs/superpowers/plans/` inside each project.
