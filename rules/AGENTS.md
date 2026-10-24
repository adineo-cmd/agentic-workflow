# Global Rules

## Rules (Always Applied)

### 1. No Comments — Remove All Comments
**Always remove every comment from all code and files.** Never add new comments. When editing any file, delete any existing `//`, `/* ... */`, `#`, `<!-- -->`, or `"""` comments found in the file. If the user asks about code, explain it in your response — do not add comments to files.

### 2. Project Documentation — Create/Update Every Session
**On every session, for the current working project (new or existing):**
- Create/update `prd.md` — requirements, scope, constraints, acceptance criteria
- Create/update `architecture.md` — components, data flow, key decisions
- Create/update `design.md` — visual style, colors, components, patterns
- Create/update `rules.md` — coding/review rules, constraints
- Create/update `task.md` — active tasks, backlog
- Create/update `progress.md` — completed, blocked, next steps, session timestamp

Use templates from `~/.config/opencode/project-templates/`. If a file does not exist in the project directory, create it from the template. If it exists, update it with the current session's progress/status. Never ask the user for permission to create/update these — it is mandatory.

### 3. Context Engineering — Use Every Session
**Always invoke the `context-engineering` skill at the start of every session.** Before any response or action (including clarifying questions or file exploration), load the skill and follow its checklist. Treat context as a finite resource. Use progressive disclosure, compaction, observation masking, and context partitioning. Monitor for context poisoning, distraction, confusion, and clash.

## Skills: check what is installed first, install only if missing

The `find-skills` skill is installed globally, but skills are model-invoked — it does not run on its own before every task. These rules make the lookup deterministic in every session.

1. **Inventory first.** Before starting a task, scan the skills already listed in your system context. If one of them covers the task, load it with the skill tool and follow it. Never re-download or re-install something already present.
2. **Search when uncovered.** If no installed skill covers the capability the task needs, invoke the `find-skills` skill to search the open agent skills ecosystem (skills.sh).
3. **Install globally, then use it.** When a match is found:

   ```bash
   npx -y skills add <owner/repo> --skill <skill-name> -g -a opencode -y
   ```

   The newly installed skill is not in this session's skill list, so read its `SKILL.md` directly (`~/.agents/skills/<name>/SKILL.md` or `~/.config/opencode/skills/<name>/SKILL.md`) and follow it for the rest of the task. It becomes auto-available in future sessions.

4. **Prefer specific skills over whole repos.** Install a single named skill, not an entire category or repo — many repos expose umbrella "category" skills that pull in dozens of unrelated ones.
5. **Pick proven skills.** Prefer high install counts on skills.sh and official sources (Anthropic, Vercel, GitHub, Microsoft). Check the skill's contents before installing if it ships scripts or unusual dependencies.
6. **Ask before installing** when the match is ambiguous, when the skill would run scripts with broad permissions, or when it would add more than a handful of skills.
7. **Keep the global set small.** Only install to the global scope (`-g`) when the skill is generally useful; otherwise install into the project with `--skill <name> -a opencode`.

## GitHub: two accounts — always ask which one

Two GitHub accounts are configured. Both have full read/write permission. **Never guess which to use.**

| Account | SSH remote | MCP tools | `gh` |
|---|---|---|---|
| `adineo-cmd` | `git@github-personal:owner/repo.git` | `github-personal_*` | `gh auth switch --user adineo-cmd` |
| `adineo-cmd2` | `git@github-work:owner/repo.git` | `github-work_*` | `gh auth switch --user adineo-cmd2` |

1. **Ask before any GitHub write.** Before pushing, creating a PR/issue/release, or otherwise writing to GitHub, ask the user which account to use (`adineo-cmd` or `adineo-cmd2`). Do not infer it from the repo path, the local git user, or the currently active `gh` account, and do not default to either one.
2. **Use the matching MCP namespace.** `github-personal_*` acts as `adineo-cmd`, `github-work_*` as `adineo-cmd2`. Both are authenticated and can run in the same session.
3. **Use the SSH alias form for git transport** so the right key and commit identity are used: `git@github-personal:...` or `git@github-work:...`. `~/.gitconfig` switches `user.name`/`user.email` automatically from the remote URL — never hardcode an identity.
4. **`gh` has one active account at a time.** Run `gh auth switch --user <username>` before `gh` write commands, and restore the previous account afterwards.
5. **Repos with no remote:** ask which account should own it before adding one.
