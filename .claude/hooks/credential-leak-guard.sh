#!/bin/bash
# credential-leak-guard.sh — Block credential hunting and exfiltration
#
# Source: davepoon/buildwithclaude (MIT) — plugins/hooks-safety/hooks/credential-leak-guard.md
# Event: PreToolUse, matcher Bash
# Installed: 2026-05-13

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$COMMAND" ] && COMMAND=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print((d.get("tool_input") or {}).get("command") or "")' 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# Pattern 1: env/printenv piped to grep for secrets
if echo "$COMMAND" | grep -qiE '(env|printenv|set)\s*\|.*grep.*\b(token|secret|key|password|credential|auth|oauth|cookie|session|api.key)\b'; then
    echo "BLOCKED: Credential hunting via environment variable scanning" >&2
    exit 2
fi

# Pattern 2: find searching for credential files
if echo "$COMMAND" | grep -qiE 'find\s.*-name\s.*\*?(token|secret|credential|password|\.key|\.pem|\.p12|\.pfx|\.keystore|\.jks|\.env)'; then
    echo "BLOCKED: Credential hunting via file system search" >&2
    exit 2
fi

# Pattern 3: Direct access to SSH credentials
if echo "$COMMAND" | grep -qE 'cat\s+(~|/home|/root)/.ssh/(id_|authorized_keys|known_hosts|config)'; then
    echo "BLOCKED: Direct SSH credential access" >&2
    exit 2
fi

# Pattern 4: System credential files
if echo "$COMMAND" | grep -qE 'cat\s+(/etc/shadow|/etc/gshadow|/etc/passwd)'; then
    echo "BLOCKED: System credential file access" >&2
    exit 2
fi

# Pattern 5: Cloud provider credentials
if echo "$COMMAND" | grep -qE 'cat\s+(~|/home|/root)/\.(aws|gcloud|azure|kube)/(credentials|config|token)'; then
    echo "BLOCKED: Cloud provider credential access" >&2
    exit 2
fi

# Pattern 6: Browser credential stores
if echo "$COMMAND" | grep -qiE 'find\s.*\.(chrome|firefox|mozilla|safari).*\b(login|password|cookie|token)\b'; then
    echo "BLOCKED: Browser credential hunting" >&2
    exit 2
fi

# Pattern 7: HTTP upload of credential files
if echo "$COMMAND" | grep -qiP 'curl\s.*-d\s+@[^\s]*(\.env|\.pem|\.key|credentials|\.ssh/id_)|wget\s.*--post-file[= ][^\s]*(\.env|\.pem|\.key|credentials|\.ssh/id_)'; then
    echo "BLOCKED: Credential file exfiltration via HTTP upload" >&2
    exit 2
fi

# Pattern 8: Piping credential files to HTTP clients
if echo "$COMMAND" | grep -qiP 'cat\s+[^\s]*(\.env|\.pem|\.key|credentials|\.ssh/id_)\S*\s*\|.*curl|cat\s+[^\s]*(\.env|\.pem|\.key|credentials|\.ssh/id_)\S*\s*\|.*wget'; then
    echo "BLOCKED: Credential file piped to HTTP client" >&2
    exit 2
fi

exit 0
