#!/bin/bash
# force-push-guard.sh — Block dangerous --force flags
#
# Source: davepoon/buildwithclaude (MIT) — plugins/hooks-safety/hooks/force-push-guard.md
# Event: PreToolUse, matcher Bash
# Installed: 2026-05-13

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$COMMAND" ] && COMMAND=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print((d.get("tool_input") or {}).get("command") or "")' 2>/dev/null)
[ -z "$COMMAND" ] && exit 0

# npm install --force
if echo "$COMMAND" | grep -qE 'npm\s+install.*--force|npm\s+i\s.*--force'; then
    echo "BLOCKED: npm install --force bypasses peer dependency checks." >&2
    echo "Fix the dependency conflict instead of forcing." >&2
    exit 2
fi

# git push --force (not --force-with-lease)
if echo "$COMMAND" | grep -qE 'git\s+push.*--force($|\s)' && ! echo "$COMMAND" | grep -q 'force-with-lease'; then
    echo "BLOCKED: git push --force can destroy remote history." >&2
    echo "Use --force-with-lease for safer force-push." >&2
    exit 2
fi

# docker system prune --force
if echo "$COMMAND" | grep -qE 'docker\s+(system\s+)?prune.*-f|docker\s+(system\s+)?prune.*--force'; then
    echo "BLOCKED: docker prune --force removes all unused data without confirmation." >&2
    exit 2
fi

exit 0
