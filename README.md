# agentic-workflow

A harness-agnostic agentic coding setup. Everything in this repo works with
**any** AI coding agent or harness — opencode, ZCode, Claude Code, Gemini CLI,
Windsurf, VS Code, Cursor, Codex CLI, or whatever comes next. Nothing here is
locked to one tool.

## What's inside

| Path | What it is |
|---|---|
| `rules/AGENTS.md` | Global rules every agent should follow (no comments in files, per-session project docs, skills-lookup discipline, two-GitHub-account policy). Copy to the rules/instructions file of whichever harness you use. |
| `agents/` | Custom subagents: `code-reviewer`, `code-simplifier` (agent definitions). |
| `skills/` | The same two as agent-invocable skills (`SKILL.md` format — the open standard most harnesses read). |
| `templates/` | Per-session project documentation templates: `prd`, `architecture`, `design`, `rules`, `task`, `progress`. |
| `mcp/` | The universal MCP hub: token-free launcher scripts + reference server definitions + [per-harness wiring guide](mcp/WIRING.md). |
| `multi-account/` | Run two GitHub accounts on one machine: SSH host aliases + git identity switching via `includeIf` (the remote URL decides the identity). |
| `tools/export_opencode_sessions.py` | Export every chat session from an opencode SQLite DB into one folder per session (`SESSION.md` + `transcript.md`) so any agent can resume past work. |
| `docs/superpowers.md` | Notes on the [superpowers](https://github.com/obra/superpowers) skill framework installed in this setup. |

## Quick start on a new machine or harness

1. **MCP servers** — copy `mcp/github-personal.sh` + `mcp/github-work.sh` to
   `~/.config/mcp/`, make them executable, and put each account's fine-grained
   PAT in `~/.config/mcp/secrets/<account>.token` (chmod 600). Then wire the two
   servers into your harness using [mcp/WIRING.md](mcp/WIRING.md). Tokens never
   appear in argv or configs — scripts read the files at launch.
2. **Rules** — copy `rules/AGENTS.md` to your harness's instruction file
   (opencode: `~/.config/opencode/AGENTS.md` · ZCode: `~/.zcode/AGENTS.md` ·
   Claude Code: `~/.claude/CLAUDE.md` · Gemini CLI: `~/.gemini/GEMINI.md` ·
   any agent: `AGENTS.md` at repo root).
3. **Skills/agents** — copy `skills/` into `~/.agents/skills/` (shared,
   read by many harnesses) or the harness's own skills directory;
   `agents/` into its subagent directory if it supports one.
4. **Two GitHub accounts** — follow `multi-account/`: SSH aliases
   `github-personal` / `github-work` + `includeIf` git identity switching.
   After this, `git@github-personal:owner/repo.git` and
   `git@github-work:owner/repo.git` just work, with the right commit identity.
5. **Templates** — keep `templates/` anywhere; the rules instruct every agent
   to maintain `prd.md` / `architecture.md` / `design.md` / `rules.md` /
   `task.md` / `progress.md` per project.

## Principles

- **One config hub, many consumers.** Secrets live in files under
  `~/.config/mcp/secrets/`; agent configs only reference them. Rotating a
  token = replacing one file, restarting the agent.
- **Dedicated repo per project.** Every project gets its own GitHub repo —
  never a big combined repo. Carve-outs exclude `node_modules`, build output,
  and `.env`.
- **Ask before outward writes.** Agents must ask which account and confirm
  before pushing, creating PRs, or publishing anything.
- **Docs every session.** Each project session updates the six template files,
  so any agent (or human) can resume later.
