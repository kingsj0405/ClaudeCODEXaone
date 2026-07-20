---
description: Delegate a task to K-EXAONE 236B (LG AI Research, served by FriendliAI) through the opencode CLI. Use when you want a second opinion from K-EXAONE or a Korean-heavy response.
---

Forward the user's arguments to the `exaone-friendli:k-exaone` subagent and return its output as-is.

- The arguments after `/k-exaone` are the prompt for K-EXAONE.
- If no arguments are given, ask the user what they want K-EXAONE to do.
- Use the Agent tool with `subagent_type: "exaone-friendli:k-exaone"` and pass the full user prompt
  plus any flags (`--format json`, `--file <path>`, `--continue`, `--session <id>`). The subagent
  pins `--model friendli/LGAI-EXAONE/K-EXAONE-236B-A23B`.
- Do not add your own commentary or summary; the subagent already forwards opencode's raw stdout.
