#!/bin/bash
# em-dash-guard.sh - Block em dashes (U+2014) in writes to the owner's published surfaces
#
# Event: PreToolUse, matcher "Write|Edit"
# Installed: 2026-06-16 (em-dash guard ON)
# Rule: clean output. No em dashes in anything the owner publishes (captions,
#       content plans, app copy). Scoped to the surfaces they actually publish
#       from, so the guard genuinely fires. Internal notes, memory, code, plans
#       and CLAUDE.md itself are exempt by design (em dashes are fine there).
#
# Coverage boundary: catches em dashes in text written via Write/Edit (.md, .html,
# .txt) under the publishing surfaces. It does NOT catch a binary built by a
# script (e.g. a .docx), which does not go through the Write tool.

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE_PATH" ] && FILE_PATH=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print((d.get("tool_input") or {}).get("file_path") or "")' 2>/dev/null)
[ -z "$FILE_PATH" ] && exit 0

# Only guard the surfaces the owner publishes from (matches absolute or relative paths):
# their social posts, their content plans, and their app copy.
if ! echo "$FILE_PATH" | grep -qE '(^|/)(outputs/social|content|apps)/'; then
    exit 0
fi

# Content being written: Write uses .content, Edit uses .new_string.
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty' 2>/dev/null)
[ -z "$CONTENT" ] && CONTENT=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;ti=json.load(sys.stdin).get("tool_input") or {};print(ti.get("content") or ti.get("new_string") or "")' 2>/dev/null)
[ -z "$CONTENT" ] && exit 0

# U+2014 EM DASH as raw UTF-8 bytes (locale-independent; no grep -P dependency).
EM_DASH=$'\xe2\x80\x94'
if printf '%s' "$CONTENT" | grep -qF "$EM_DASH"; then
    echo "BLOCKED: em dash in a published file: $FILE_PATH" >&2
    echo "House style: no em dashes in anything you publish." >&2
    echo "Replace it with a comma, full stop, colon, or reword the sentence, then retry." >&2
    exit 2
fi

exit 0
