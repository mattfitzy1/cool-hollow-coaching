---
name: cloudflare-pages
description: >
  Cloudflare Pages capability - projects, deployments, custom domains, SSL
  provisioning, rollback. Wraps the Pages REST API + the wrangler CLI on
  the client's own Cloudflare account. Triggers on: Cloudflare Pages, wrangler,
  pages.dev, .pages.dev subdomain, deploy a static site, put my app live,
  custom domain on Cloudflare, Pages deployment, rollback deployment,
  cool-hollow project, deploy the client app.
user-invocable: false
requires:
  - tool: cloudflare
    type: key
    requires_bin: [wrangler]
    requires_runtime: [node]
    account: "Cloudflare"
    bundle: app
    plan: "Free"
    signup: "https://dash.cloudflare.com/sign-up → then My Profile → API Tokens → Create Custom Token (Account / Cloudflare Pages: Edit)"
    where: "API token into CLOUDFLARE_API_TOKEN; Account ID (right sidebar on any domain/Pages page) into CLOUDFLARE_ACCOUNT_ID, in .env"
    spend: "Free tier covers everything here (500 builds/month, 100 custom domains per project)"
    verify: "python scripts/cloudflare_pages.py verify"
    optional: false
---

# Cloudflare Pages

**Before doing anything with cloudflare, run `ensure_ready("cloudflare")`.** If its software or its credential is missing, or its verify fails, **do not attempt the task and do not error out.** Run the setup walkthrough below (install the software if needed, then what to sign up for, the exact link and click path, where the key goes in `.env`, then verify) and only once it passes, continue with what the owner originally asked.

Project + deployment + custom domain ops on the client's own Cloudflare account. Implementation: `scripts/cloudflare_pages.py` (stdlib `urllib` + `wrangler` subprocess). Deep reference: `reference/services/cloudflare-pages.md`.

This is how the client app goes live. The flagship use is `cf.deploy("apps/cool-hollow", "cool-hollow")`, which publishes the live app to `https://cool-hollow.pages.dev`.

V1 covers project create/read, full custom domain CRUD with three-status SSL polling, and deployment list/get/rollback/build-logs. The deploy itself shells out to `wrangler pages deploy`. Project delete and Git-connected projects are deferred to V2 - see Maintenance.

## Setup

This is a **key tool** (`type: key`), not a login tool. There are two things to set, both in `.env`, and a missing one fails loudly into this walkthrough rather than silently targeting the wrong account:

```
CLOUDFLARE_API_TOKEN=...        # the token you create below
CLOUDFLARE_ACCOUNT_ID=...       # your account ID (no hardcoded default exists)
```

`ensure_ready("cloudflare")` runs in this order:

1. **Prerequisites (Layer 0).** Checks Node and `wrangler` are installed. If not, the walkthrough installs them via Homebrew first (`brew install node`, then `npm i -g wrangler`). Never `wrangler login` or `wrangler whoami` - wrangler is fed the token from the environment instead.
2. **Credential.** Sign up free at `https://dash.cloudflare.com/sign-up`. Then My Profile → API Tokens → **Create Custom Token** with a single permission: **Account / Cloudflare Pages: Edit** (no others). Paste it into `CLOUDFLARE_API_TOKEN=`. Copy your **Account ID** (right-hand sidebar on any domain or Pages page) into `CLOUDFLARE_ACCOUNT_ID=`. Save the file.
3. **Verify.** A token-scoped REST call (`python scripts/cloudflare_pages.py verify`, which hits `/user/tokens/verify` and asserts the token is active). Not a wrangler login check.

The key is never echoed back into the conversation - the owner pastes it into `.env` and the script reads the file.

Wrangler reads `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` from the environment automatically - the client passes both into the `wrangler pages deploy` subprocess so OAuth/login is bypassed entirely.

```python
from scripts.cloudflare_pages import CloudflarePagesClient

cf = CloudflarePagesClient()       # reads from .env, verifies token on init
project = cf.get_project("cool-hollow")
```

CLI for Bash sessions:

```bash
python scripts/cloudflare_pages.py verify
python scripts/cloudflare_pages.py list-projects --table
python scripts/cloudflare_pages.py deploy apps/cool-hollow cool-hollow
python scripts/cloudflare_pages.py list-deployments cool-hollow --table
```

## Key Endpoints

### Projects

| What | Code |
|---|---|
| List all Pages projects | `cf.list_projects()` |
| Get project by name | `cf.get_project("cool-hollow")` |
| Create direct-upload project | `cf.create_project("cool-hollow", production_branch="main")` |

### Custom Domains

| What | Code |
|---|---|
| List domains on a project | `cf.list_domains("cool-hollow")` |
| Attach a custom domain | `cf.add_domain("cool-hollow", "www.coolhollow.com")` |
| Get one domain (status snapshot) | `cf.get_domain("cool-hollow", "www.coolhollow.com")` |
| Force re-validation (no body) | `cf.force_revalidate_domain("cool-hollow", "www.coolhollow.com")` |
| Block until SSL fully provisioned | `cf.wait_for_domain_active("cool-hollow", "www.coolhollow.com", timeout=600)` |
| Detach domain | `cf.delete_domain("cool-hollow", "old.coolhollow.com")` |

### Deployments

| What | Code |
|---|---|
| List recent deployments (production by default) | `cf.list_deployments("cool-hollow", env="production", per_page=25)` |
| Get a single deployment | `cf.get_deployment("cool-hollow", deployment_id)` |
| Build logs for a deployment | `cf.get_build_logs("cool-hollow", deployment_id)` |
| Roll back to a previous deployment | `cf.rollback_deployment("cool-hollow", target_id)` |
| Delete a non-production deployment | `cf.delete_deployment("cool-hollow", id, force=False)` |
| Deploy a directory via wrangler | `cf.deploy("apps/cool-hollow", "cool-hollow")` |

## Common Patterns

### 1. Deploy the client app (the hot path)

```python
cf = CloudflarePagesClient()
result = cf.deploy("apps/cool-hollow", "cool-hollow", branch="main")
print(result["deployment_id"], result["deployment_url"], result["project_url"])
# e.g. dc412cea-..., https://abc123.cool-hollow.pages.dev, https://cool-hollow.pages.dev
```

The client shells out to `wrangler pages deploy <dir> --project-name=... --branch=... --commit-dirty=true --no-bundle`, parses stdout for the deployment URL, then calls `list_deployments(env="production", per_page=1)` for the canonical record. Returns `{deployment_id, short_id, deployment_url, project_url, deployment_obj, stdout, stderr}`.

### 2. Attach a custom domain end-to-end

The 522 trap matters: ALWAYS add the domain on Cloudflare BEFORE the CNAME lands at the registrar. Doing it in the wrong order returns 522 from CF.

```python
from scripts.cloudflare_pages import CloudflarePagesClient

cf = CloudflarePagesClient()

# 1. Tell Cloudflare about the domain FIRST.
cf.add_domain("cool-hollow", "www.coolhollow.com")

# 2. Now point the CNAME at the project subdomain (at your domain registrar):
#    www  CNAME  cool-hollow.pages.dev

# 3. Skip Cloudflare's 5-min auto-revalidation cycle.
cf.force_revalidate_domain("cool-hollow", "www.coolhollow.com")

# 4. Block until status, validation_data.status, AND verification_data.status
#    are all "active". Polls 10s/30s/60s with backoff.
cf.wait_for_domain_active("cool-hollow", "www.coolhollow.com", timeout=600)
```

Apex web forwarding (apex → www, 301) is a one-time click in the domain registrar's dashboard.

### 3. Roll back a bad deploy

```python
cf = CloudflarePagesClient()
deps = cf.list_deployments("cool-hollow", env="production", per_page=10)
# Pick the last known-good deployment.
target = deps[1]["id"]                              # one before current
cf.rollback_deployment("cool-hollow", target)    # promotes target back to production
```

`DELETE /deployments/{id}` is rejected on the live production deployment - roll back first, then delete the now-unaliased one.

### 4. Find the latest production deployment URL

```python
proj = cf.get_project("cool-hollow")
canonical = proj.get("canonical_deployment", {})
print(canonical.get("url"))
```

`canonical_deployment` updates with ~30s lag after a new production deploy. `latest_deployment` may differ from `canonical_deployment` briefly.

### 5. Wait for SSL with the three-status check

```python
import time
from scripts.cloudflare_pages import CloudflarePagesClient

cf = CloudflarePagesClient()
project, domain = "cool-hollow", "www.example.com"

cf.add_domain(project, domain)
# ... CNAME landed at registrar ...
cf.force_revalidate_domain(project, domain)

# Manual polling form (illustrative - wait_for_domain_active does this for you):
deadline = time.time() + 600
while time.time() < deadline:
    d = cf.get_domain(project, domain)
    top = d.get("status")
    val = (d.get("validation_data") or {}).get("status")
    ver = (d.get("verification_data") or {}).get("status")
    if top == val == ver == "active":
        break
    time.sleep(10)
```

Production code should use `wait_for_domain_active` - it raises with the `error_message` if any sub-status flips to `error`, and uses 10s/30s/60s backoff so the API rate budget survives a long wait.

## Reference

### Domain status state machine

A domain is fully provisioned only when ALL THREE are `active`:

| Field | Meaning |
|---|---|
| `status` (top-level) | High-level state: `initializing` → `pending` → `active` (or `deactivated` / `blocked` / `error`) |
| `validation_data.status` | TXT/HTTP validation state |
| `verification_data.status` | CNAME verification state (CDN routing) |

Community-confirmed: `verification_data.status="active"` can coexist with `validation_data.status="error"`. Single check would silently hide failures.

### URL type taxonomy (easy to confuse)

| Type | Example | When it points where |
|---|---|---|
| Deployment URL | `dc412cea.cool-hollow.pages.dev` | Atomic, immutable. Always serves that one build. |
| Project URL | `cool-hollow.pages.dev` | Always latest production deployment. |
| Branch alias URL | `main.cool-hollow.pages.dev` | Latest deployment on that branch. |
| Custom domain URL | `www.coolhollow.com` | Same content as project URL once SSL provisioned. |

### Project name constraints

- 1-58 chars, lowercase letters, digits, dashes only.
- No leading or trailing dash.
- Validated client-side before the API call (saves a round-trip).

### Free plan limits (relevant)

| Limit | Value |
|---|---|
| Custom domains per project | 100 |
| Files per site | 20,000 (Free) / 100,000 (paid) |
| Max file size | 25 MiB |
| Concurrent builds | 1 (Free) / 5 (Pro) |
| Builds per month | 500 (Free) |
| Build timeout | 20 min |
| Header rules | 100 |
| Redirects | 2,000 static + 100 dynamic |
| Projects per account | ~100 (soft, support can raise) |

### HTTP status codes

- `200` / `201` - success
- `400` - bad request (project name violates regex, body schema wrong, query params not accepted on this endpoint)
- `401` - unauthorized (token expired, disabled, wrong scope, or wrong endpoint)
- `404` - project / domain / deployment id wrong, or not on this account
- `409` - conflict (domain already attached, name collision)
- `429` - rate limit (1200/5min global). Client honours `Retry-After` and retries once.
- `522` - see gotcha #1 - CNAME reached the registrar before the domain was attached on Cloudflare.

## Rate Limits

1200 requests / 5 min global per user (cumulative across dashboard + REST + Terraform). Polling discipline: 10s for first 2 min, 30s up to 10 min, 60s after that. `wait_for_domain_active` implements this. 429 → client reads `Retry-After`, sleeps, retries once.

## Manual Steps

None for V1 - pure API path. Apex web forwarding (apex → www, 301) is a one-time click in the domain registrar's dashboard, only when the owner adds a custom domain.

## Maintenance

### Known Gotchas

1. **The 522 trap.** Adding the CNAME at the registrar BEFORE calling `add_domain` on Cloudflare returns 522. Order is: `add_domain` first, then the CNAME at the registrar, then `force_revalidate_domain` to skip the 5-min auto-retry cycle.
2. **Three-status SSL check is mandatory.** A domain is fully provisioned only when `status`, `validation_data.status`, AND `verification_data.status` are all `active`. Community-confirmed cases of one being active and another in error.
3. **`PATCH /domains/{domain}` is a no-body call.** The PATCH itself triggers immediate re-validation. Sending a body returns 400.
4. **Wrangler `pages deploy` has no JSON output.** Stable regex: `https://[a-f0-9]+\.[a-z0-9-]+\.pages\.dev`. Always pair the regex match with `list_deployments(env="production", per_page=1)` for the canonical record.
5. **Don't rapid create/delete projects.** Two compounding penalties: Let's Encrypt rate limit (up to a week ban after repeated cycles) AND undocumented ~24h cooldown on the `<name>.pages.dev` subdomain after deletion. V1 omits `delete_project` entirely - manual via dashboard if absolutely needed.
6. **`canonical_deployment` lags ~30s** after a new production deploy. Tests that compare the post-deploy canonical pointer should retry once after 30s.
7. **`DELETE /deployments/{id}` is rejected on the live production deployment.** Roll back first (`rollback_deployment`), then delete the now-unaliased one. The client's `delete_deployment` re-raises with a hint when CF returns this error.
8. **CAA records can block SSL issuance.** Cloudflare uses Google Trust Services + Let's Encrypt. If a CAA record exists at the apex that excludes both, issuance fails silently. Diagnostic: `dig CAA <domain>`.
9. **Apex on third-party DNS not supported.** Pages won't issue an SSL cert for an apex domain unless the zone is on Cloudflare nameservers. For a domain whose DNS lives at another registrar, only attach `www.{domain}`; apex 301-to-www happens via the registrar's web forwarding.
10. **`per_page`/`page` are not accepted on `/pages/projects` list.** Endpoint returns all projects in one shot. The client doesn't send these params (would 400). `/pages/projects/{name}/deployments` does accept `per_page`.
11. **Pages → Workers Static Assets convergence (2024 announcement).** Pages REST API still active and stable, no deprecations. New platform features land on Workers Static Assets first. V3 trigger = official Pages deprecation.
12. **No webhook on SSL provisioning complete.** No notification fires when a domain transitions from pending to active. Polling is mandatory - `wait_for_domain_active` is the prescribed pattern.
13. **No hardcoded account ID.** Both `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` must be set; a missing one raises a `CloudflarePagesError` that points at the setup walkthrough. This is deliberate - there is no default account to fall back to.

### Improvement Backlog

- Add `delete_project` with explicit confirmation prompt + cooldown warning when a real "delete and reuse name" use case appears.
- Add `update_project` (PATCH) for build_config / env vars / compatibility_date.
- Add Git-connected project creation + deploy hook integration when push-to-deploy becomes a real need.
- Add `retry_deployment` once Git-connected projects are in scope.
- Add webhooks/notifications subscription if a "notify on deploy" use case lands.
- Migrate to Workers Static Assets if/when Cloudflare deprecates the Pages REST API.
