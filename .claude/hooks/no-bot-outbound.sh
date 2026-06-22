#!/bin/bash
# no-bot-outbound.sh — Block any non-draft social publish at launch
#
# Event: PreToolUse, matcher Bash
# Built: 2026-06-16 (the enforced layer behind the
#        social-approval promise once permission prompts are off)
#
# Why this exists: the owner runs bypassPermissions, so the per-action approval
# prompt is gone. The only hard stop left on "nothing posts without me" is this
# hook. The rule is: the system DRAFTS, the owner SENDS. Anything that would push a
# post out without an explicit --draft is blocked. At launch, non-draft publish
# (--publish) is blocked ENTIRELY: every post lands as a Publer draft (or a
# manual-post handoff folder) for the owner to review and publish themselves.
#
# Modelled on credential-leak-guard.sh: read the Bash command, match the send
# paths, exit 2 (block) with a plain-English reason, otherwise exit 0.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$COMMAND" ] && COMMAND=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print((d.get("tool_input") or {}).get("command") or "")' 2>/dev/null)
[ -z "$COMMAND" ] && COMMAND="$INPUT"   # last-resort: match against raw JSON (fail-safe, may over-block)

[ -z "$COMMAND" ] && exit 0

# Only inspect commands that invoke a known send path. publer_post.py is the one
# send path today; new senders should be added here as they ship.
if echo "$COMMAND" | grep -qiE 'publer_post\.py'; then

    # The only non-draft path in publer_post.py is the explicit --publish flag.
    # At launch, block it outright: drafts only.
    if echo "$COMMAND" | grep -qiE '(^|[[:space:]])--publish([[:space:]]|=|$)'; then
        echo "BLOCKED: live publish is off at launch — posts go out as drafts for you to review." >&2
        echo "Nothing posts to social without you. Drop the --publish flag and it lands as a" >&2
        echo "Publer draft (or a manual-post folder), then you check it and hit publish yourself." >&2
        exit 2
    fi

    # Defence in depth: if a future call sets the Publer post state to anything
    # other than draft (e.g. state=scheduled / state=published) on the command
    # line, block that too. Drafts only at launch.
    if echo "$COMMAND" | grep -qiE 'state[[:space:]]*=[[:space:]]*["'\'']?(scheduled|published|live)'; then
        echo "BLOCKED: only draft posts are allowed at launch." >&2
        echo "The system drafts, you publish. Save it as a draft and review it first." >&2
        exit 2
    fi
fi

# Catch-all for any other obvious autonomous-send path that is not draft-gated.
# Blocks a raw curl/wget that posts to a publishing endpoint without review.
if echo "$COMMAND" | grep -qiE '(curl|wget)\b.*(publer\.com/api|graph\.facebook\.com|graph\.instagram\.com|api\.instagram\.com).*/(posts|media)(/publish)?'; then
    echo "BLOCKED: direct call to a social publishing endpoint." >&2
    echo "Nothing posts to social without you. Use the draft path and review it first." >&2
    exit 2
fi

exit 0
