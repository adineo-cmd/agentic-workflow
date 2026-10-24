# MCP wiring — same two servers, every harness

The two servers (`github-personal` → account `adineo-cmd`, `github-work` →
account `adineo-cmd2`) both reach `https://api.githubcopilot.com/mcp/` through
the stdio launcher scripts in this directory. The scripts read each token from
`~/.config/mcp/secrets/<account>.token` at launch and pass it via an
environment variable — tokens never appear in argv, logs, or agent configs.

`mcp-servers.json` in this directory is the canonical definition (standard
`mcpServers` schema). All snippets below point at the scripts after you copy
them to `~/.config/mcp/`.

## opencode — `~/.config/opencode/opencode.jsonc`

```jsonc
{
  "mcp": {
    "github-personal": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer {file:~/.config/mcp/secrets/github-personal.token}"
      }
    },
    "github-work": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer {file:~/.config/mcp/secrets/github-work.token}"
      }
    }
  }
}
```

(opencode can also use the stdio scripts — the native `remote` type avoids
node entirely.)

## ZCode — `~/.zcode/cli/config.json`

```json
{
  "mcp": {
    "servers": {
      "github-personal": {
        "type": "stdio",
        "command": "/home/YOU/.config/mcp/github-personal.sh"
      },
      "github-work": {
        "type": "stdio",
        "command": "/home/YOU/.config/mcp/github-work.sh"
      }
    }
  }
}
```

## Claude Code — `~/.claude.json`

```json
{
  "mcpServers": {
    "github-personal": {
      "type": "stdio",
      "command": "/home/YOU/.config/mcp/github-personal.sh"
    },
    "github-work": {
      "type": "stdio",
      "command": "/home/YOU/.config/mcp/github-work.sh"
    }
  }
}
```

## Gemini CLI — `~/.gemini/settings.json`

```json
{
  "mcpServers": {
    "github-personal": {
      "command": "/home/YOU/.config/mcp/github-personal.sh"
    },
    "github-work": {
      "command": "/home/YOU/.config/mcp/github-work.sh"
    }
  }
}
```

## Windsurf — `~/.codeium/windsurf/mcp_config.json`

Same shape as Claude Code (`mcpServers` with `command`, no `type` needed).

## VS Code — `~/.config/Code/User/mcp.json`

```json
{
  "servers": {
    "github-personal": {
      "type": "stdio",
      "command": "/home/YOU/.config/mcp/github-personal.sh"
    },
    "github-work": {
      "type": "stdio",
      "command": "/home/YOU/.config/mcp/github-work.sh"
    }
  }
}
```

## Cursor — `~/.cursor/mcp.json`

Same shape as Claude Code (`mcpServers`).

## Any other harness

Anything that speaks MCP over stdio can launch the scripts directly:

```
/home/YOU/.config/mcp/github-personal.sh
```

Anything that speaks MCP over HTTP can hit the URL with
`Authorization: Bearer $(cat ~/.config/mcp/secrets/github-personal.token)`.

## Maintenance

- **Rotate a token:** overwrite `~/.config/mcp/secrets/<account>.token`,
  restart the agent. No config edits anywhere.
- **Add an account:** new token file + one more launcher script copied from
  an existing one + one more entry per harness.
- Replace `/home/YOU` with your home path in the snippets above (or run
  `sed -i "s|/home/YOU|$HOME|g"` after copying).
