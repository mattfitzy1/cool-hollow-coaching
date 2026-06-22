#!/bin/bash
# rm-safety-net.sh — Block rm on critical paths, allow safe cleanup targets
#
# Source: davepoon/buildwithclaude (MIT) — plugins/hooks-safety/hooks/rm-safety-net.md
# Event: PreToolUse, matcher Bash
# Installed: 2026-05-13
#
# Local customisation: SAFE_TARGETS extended with `\.firecrawl` (Firecrawl scratch
# directory used by the firecrawl skill). Scoped to project-local conventions.
#
# Fix 2026-06-16 (Karpathy guardrail review): target parser rewritten to inspect
# ALL rm arguments (was last-token-only via awk $NF), ignore flags and shell
# redirections, and recognise macOS temp roots (/var/folders, /private/tmp).
# Closes a false-positive (a redirect token like `2>/dev/null` was read as the
# target) and a false-negative (a dangerous target masked by a trailing safe one,
# e.g. `rm -rf important_dir node_modules`). Known remaining limitation: only the
# first `rm` in a command is analysed and the trigger is anchored to the start, so
# `rm` after `&&`/`;` in a compound command is not inspected (pre-existing).

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$COMMAND" ] && COMMAND=$(printf '%s' "$INPUT" | python3 -c 'import sys,json;d=json.load(sys.stdin);print((d.get("tool_input") or {}).get("command") or "")' 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# --- rm command analysis ---
if echo "$COMMAND" | grep -qE '^\s*(sudo\s+)?rm\s'; then
    SAFE_TARGETS="node_modules|dist|build|__pycache__|\.cache|\.pytest_cache|coverage|\.nyc_output|\.next|\.nuxt|tmp|temp|\.firecrawl"
    SAFE_ABS="^/tmp/|^/private/tmp/|^/var/folders/"   # unix + macOS per-user temp roots
    CRITICAL="^/\$|^/home|^/etc|^/usr|^/var|^/opt|^/root|^~|^\.\.|^\.git$|^\.env"

    # Is this a recursive/force rm (rm -rf, -fr, -r, -R, --recursive, ...)?
    RECURSIVE_FORCE=0
    if echo "$COMMAND" | grep -qE 'rm\s+.*-[rRf]*[rR][rRf]*'; then
        RECURSIVE_FORCE=1
    fi

    # Extract everything after the first `rm`, then strip command chaining and shell
    # redirections so we inspect ONLY real targets — not a redirect token, and not
    # just the last token (which let a dangerous target hide behind a safe one).
    ARGS=$(echo "$COMMAND" | perl -ne 'print "$1" if /\brm\s+(.*)/')
    ARGS="${ARGS%%;*}"                                          # cut at ;
    ARGS="${ARGS%%|*}"                                          # cut at | / ||
    ARGS="${ARGS%%&*}"                                          # cut at & / && / &>
    ARGS=$(printf '%s' "$ARGS" | perl -pe 's/\s*\d*[<>].*$//')  # cut at first redirect (incl. its fd digit)

    # Tokenise without glob expansion (read -ra), then inspect each target token.
    read -ra RM_TOKENS <<< "$ARGS"
    for TARGET in "${RM_TOKENS[@]}"; do
        case "$TARGET" in
            -*) continue ;;   # flag (e.g. -rf, --recursive), not a target
        esac

        # Path traversal — block regardless of flags
        if printf '%s' "$TARGET" | grep -qF '..'; then
            echo "BLOCKED: path traversal detected in rm target: $TARGET" >&2
            exit 2
        fi

        # Explicitly-safe targets (relative scratch dirs or temp roots) — token is fine
        if echo "$TARGET" | grep -qE "^(\./)?(${SAFE_TARGETS})(/|$)"; then
            continue
        fi
        if echo "$TARGET" | grep -qE "$SAFE_ABS"; then
            continue
        fi

        # Critical system paths — always block
        if echo "$TARGET" | grep -qE "$CRITICAL"; then
            echo "BLOCKED: rm targeting critical path: $TARGET" >&2
            exit 2
        fi

        # rm -rf on anything not explicitly safe — block
        if [ "$RECURSIVE_FORCE" -eq 1 ]; then
            echo "BLOCKED: rm -rf on non-safe target: $TARGET" >&2
            exit 2
        fi
    done
fi

# --- find -delete ---
if echo "$COMMAND" | grep -qE 'find\s.*-delete'; then
    FIND_PATH=$(echo "$COMMAND" | perl -ne 'print "$1" if /find\s+(\S+)/')
    if echo "$FIND_PATH" | grep -qE '^\.|^node_modules|^dist|^build|^/tmp'; then
        exit 0
    fi
    echo "BLOCKED: find -delete outside safe directory: $FIND_PATH" >&2
    exit 2
fi

# --- shred ---
if echo "$COMMAND" | grep -qE '^\s*(sudo\s+)?shred\s'; then
    echo "BLOCKED: shred command (secure file deletion)" >&2
    exit 2
fi

exit 0
