#!/usr/bin/env bash
# Universal GitHub MCP launcher — work account (adineo-cmd2).
# Works with any agent that supports stdio MCP servers
# (Claude Code, Gemini CLI, Windsurf, VS Code, ZCode, opencode, Cursor, ...).
# The token is passed via environment variable so it never appears in argv or logs.
set -euo pipefail
GITHUB_MCP_TOKEN="$(cat "$HOME/.config/mcp/secrets/github-work.token")" \
  exec npx -y mcp-remote https://api.githubcopilot.com/mcp/ \
    --header 'Authorization: Bearer ${GITHUB_MCP_TOKEN}'
