"""Cloudflare Pages API client.

Wraps the Pages REST API + the wrangler CLI (for direct-upload deploys) on
your own Cloudflare account. Stdlib-only - uses urllib for HTTP, no
third-party deps.

Auth: Authorization: Bearer {CLOUDFLARE_API_TOKEN}. The same token is passed to
wrangler as an env var, so wrangler never needs `wrangler login` or
`wrangler whoami`. There is no hardcoded account ID: both
CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set in .env, and a
missing one fails loudly into the `ensure_ready('cloudflare')` setup
walkthrough rather than silently targeting the wrong account.

Token scope: Account / Cloudflare Pages: Edit.

Usage:
    from scripts.cloudflare_pages import CloudflarePagesClient
    cf = CloudflarePagesClient()
    projects = cf.list_projects()
    cf.deploy("apps/example-site", "example-site")

CLI:
    python scripts/cloudflare_pages.py verify
    python scripts/cloudflare_pages.py list-projects --table
    python scripts/cloudflare_pages.py deploy apps/example-site example-site
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://api.cloudflare.com/client/v4"
DEFAULT_DOMAIN_TIMEOUT = 600

# The one-line nudge shown whenever a credential is missing, so the failure
# routes into the guided "no dead skills" walkthrough instead of a raw stack
# trace. The cloudflare-pages skill body calls ensure_ready("cloudflare")
# before any deploy; this message is the standalone-script fallback.
SETUP_HINT = (
    "Cloudflare is not connected yet. Run /setup (or /doctor) and follow the "
    "Cloudflare walkthrough: it installs Node + wrangler, then has you create a "
    "free token (My Profile -> API Tokens -> Create Custom Token -> Account / "
    "Cloudflare Pages: Edit) and paste it into CLOUDFLARE_API_TOKEN, plus your "
    "Account ID into CLOUDFLARE_ACCOUNT_ID, in .env."
)
DEPLOYMENT_URL_PATTERN = re.compile(
    r"https://[a-f0-9]+\.[a-z0-9-]+\.pages\.dev",
    re.IGNORECASE,
)
PROJECT_NAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,56}[a-z0-9])?$")


class CloudflarePagesError(RuntimeError):
    def __init__(self, status: int, body: Any, method: str = "", url: str = ""):
        self.status = status
        self.body = body
        msg = f"Cloudflare Pages API {status}"
        if method or url:
            msg += f" on {method} {url}"
        if body:
            msg += f": {body}"
        super().__init__(msg)


def _load_dotenv(path: str | os.PathLike[str] | None = None) -> None:
    """Minimal .env loader. Reads KEY=VALUE lines, skips comments/blank lines.
    Does not override existing os.environ entries."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / ".env"
    p = Path(path)
    if not p.exists():
        return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


_load_dotenv()


class CloudflarePagesClient:
    def __init__(
        self,
        token: str | None = None,
        account_id: str | None = None,
        verify_on_init: bool = True,
    ):
        self.token = token or os.environ.get("CLOUDFLARE_API_TOKEN")
        if not self.token:
            raise CloudflarePagesError(401, f"CLOUDFLARE_API_TOKEN missing. {SETUP_HINT}")
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        if not self.account_id:
            # No hardcoded default: a missing account ID must fail loudly into
            # the setup walkthrough, never silently target someone else's account.
            raise CloudflarePagesError(401, f"CLOUDFLARE_ACCOUNT_ID missing. {SETUP_HINT}")
        self.api_base = API_BASE
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        if verify_on_init:
            self.verify_token()

    # ------------------------------------------------------------------ HTTP

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: dict[str, Any] | None = None,
        _retry: bool = True,
    ) -> Any:
        url = self.api_base + path
        if query:
            cleaned = {k: v for k, v in query.items() if v is not None}
            if cleaned:
                url += "?" + urllib.parse.urlencode(cleaned)
        headers = dict(self.headers)
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                if not raw:
                    return None
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return raw.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and _retry:
                retry_after = int(e.headers.get("Retry-After", "5") or "5")
                time.sleep(retry_after)
                return self._request(method, path, body=body, query=query, _retry=False)
            raw = e.read()
            try:
                err_body = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                err_body = raw.decode("utf-8", errors="replace") if raw else None
            raise CloudflarePagesError(e.code, err_body, method, url) from e

    # ------------------------------------------------------------------- Auth

    def verify_token(self) -> dict:
        """Verify token. Asserts both success=true AND result.status='active'."""
        data = self._request("GET", "/user/tokens/verify")
        result = (data or {}).get("result") or {}
        success = (data or {}).get("success") is True
        status = result.get("status")
        if not success:
            raise CloudflarePagesError(
                401,
                f"Token verify returned success=false. Body: {data}",
            )
        if status != "active":
            raise CloudflarePagesError(
                401,
                f"Token status is '{status}', expected 'active'. Regenerate at "
                "https://dash.cloudflare.com/profile/api-tokens.",
            )
        return {
            "success": success,
            "status": status,
            "id": result.get("id"),
            "expires_on": result.get("expires_on"),
            "not_before": result.get("not_before"),
        }

    # --------------------------------------------------------------- Projects

    def _projects_path(self, *parts: str) -> str:
        sub = "/".join(parts)
        base = f"/accounts/{self.account_id}/pages/projects"
        return base + (f"/{sub}" if sub else "")

    @staticmethod
    def _validate_project_name(name: str) -> None:
        if not isinstance(name, str) or not (1 <= len(name) <= 58):
            length = len(name) if isinstance(name, str) else "n/a"
            raise CloudflarePagesError(
                400,
                f"Project name must be 1-58 chars (got length={length}).",
            )
        if not PROJECT_NAME_PATTERN.match(name):
            raise CloudflarePagesError(
                400,
                f"Project name '{name}' invalid. Use lowercase letters, digits, "
                "and dashes; cannot start or end with a dash.",
            )

    def list_projects(self) -> list[dict]:
        """List all Pages projects on the account.

        The Pages projects list endpoint does not support pagination params
        (per_page/page return 400). It returns all projects (~100 ceiling per
        account) in one response. Use the dashboard or upgrade to cursor-based
        if Cloudflare adds it later.
        """
        data = self._request("GET", self._projects_path())
        return (data or {}).get("result") or []

    def get_project(self, name: str) -> dict:
        data = self._request("GET", self._projects_path(name))
        return (data or {}).get("result") or {}

    def create_project(
        self,
        name: str,
        production_branch: str = "main",
        build_config: dict | None = None,
    ) -> dict:
        self._validate_project_name(name)
        body: dict[str, Any] = {
            "name": name,
            "production_branch": production_branch,
        }
        if build_config is not None:
            body["build_config"] = build_config
        data = self._request("POST", self._projects_path(), body=body)
        return (data or {}).get("result") or {}

    # ---------------------------------------------------------- Custom Domains

    def _domains_path(self, project: str, domain: str | None = None) -> str:
        base = self._projects_path(project) + "/domains"
        return base + (f"/{domain.strip().lower()}" if domain else "")

    def list_domains(self, project: str) -> list[dict]:
        data = self._request("GET", self._domains_path(project))
        return (data or {}).get("result") or []

    def add_domain(self, project: str, domain_name: str) -> dict:
        body = {"name": domain_name.strip().lower()}
        data = self._request("POST", self._domains_path(project), body=body)
        return (data or {}).get("result") or {}

    def get_domain(self, project: str, domain_name: str) -> dict:
        data = self._request("GET", self._domains_path(project, domain_name))
        return (data or {}).get("result") or {}

    def force_revalidate_domain(self, project: str, domain_name: str) -> dict:
        data = self._request("PATCH", self._domains_path(project, domain_name))
        return (data or {}).get("result") or {}

    def delete_domain(self, project: str, domain_name: str) -> bool:
        self._request("DELETE", self._domains_path(project, domain_name))
        return True

    def wait_for_domain_active(
        self,
        project: str,
        domain_name: str,
        timeout: int = DEFAULT_DOMAIN_TIMEOUT,
        poll_initial: int = 10,
    ) -> dict:
        """Block until status, validation_data.status, AND verification_data.status are 'active'.

        Polling backoff: 10s for first 2 min, 30s up to 10 min, 60s up to timeout.
        Raises on any sub-status of 'error' or on timeout.
        """
        start = time.time()
        deadline = start + timeout
        last: dict = {}
        while time.time() < deadline:
            d = self.get_domain(project, domain_name)
            last = d
            top = d.get("status")
            val = (d.get("validation_data") or {}).get("status")
            ver = (d.get("verification_data") or {}).get("status")
            if top == "active" and val == "active" and ver == "active":
                return d
            for label, cur in (
                ("status", top),
                ("validation_data.status", val),
                ("verification_data.status", ver),
            ):
                if cur == "error":
                    err = (
                        (d.get("validation_data") or {}).get("error_message")
                        or (d.get("verification_data") or {}).get("error_message")
                        or "(no error_message returned)"
                    )
                    raise CloudflarePagesError(
                        500,
                        f"Domain {domain_name} on {project}: {label}=error. {err}",
                    )
            elapsed = time.time() - start
            if elapsed < 120:
                interval = poll_initial
            elif elapsed < 600:
                interval = 30
            else:
                interval = 60
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(interval, max(1, remaining)))
        raise CloudflarePagesError(
            504,
            f"Timed out polling domain {domain_name} on {project} after {timeout}s. "
            f"Last state: status={last.get('status')}, "
            f"validation={(last.get('validation_data') or {}).get('status')}, "
            f"verification={(last.get('verification_data') or {}).get('status')}.",
        )

    # ------------------------------------------------------------ Deployments

    def _deployments_path(
        self,
        project: str,
        deployment_id: str | None = None,
        *suffix: str,
    ) -> str:
        base = self._projects_path(project) + "/deployments"
        if deployment_id:
            base += f"/{deployment_id}"
            if suffix:
                base += "/" + "/".join(suffix)
        return base

    def list_deployments(
        self,
        project: str,
        env: str = "production",
        per_page: int = 25,
        page: int = 1,
    ) -> list[dict]:
        data = self._request(
            "GET",
            self._deployments_path(project),
            query={"env": env, "per_page": per_page, "page": page},
        )
        return (data or {}).get("result") or []

    def get_deployment(self, project: str, deployment_id: str) -> dict:
        data = self._request(
            "GET", self._deployments_path(project, deployment_id)
        )
        return (data or {}).get("result") or {}

    def get_build_logs(self, project: str, deployment_id: str) -> list[dict]:
        data = self._request(
            "GET",
            self._deployments_path(project, deployment_id, "history", "logs"),
        )
        result = (data or {}).get("result") or {}
        return result.get("data") or []

    def delete_deployment(
        self,
        project: str,
        deployment_id: str,
        force: bool = False,
    ) -> bool:
        try:
            self._request(
                "DELETE",
                self._deployments_path(project, deployment_id),
                query={"force": "true"} if force else None,
            )
            return True
        except CloudflarePagesError as e:
            body = e.body
            if isinstance(body, dict):
                errs = body.get("errors") or []
                msg = " ".join(str(x.get("message", "")) for x in errs).lower()
                if "production" in msg and ("delete" in msg or "alias" in msg):
                    raise CloudflarePagesError(
                        e.status,
                        "Cannot delete the live production deployment. "
                        "Roll back to a different deployment first, then delete the unaliased one. "
                        f"Original: {body}",
                    ) from e
            raise

    def rollback_deployment(self, project: str, target_deployment_id: str) -> dict:
        data = self._request(
            "POST",
            self._deployments_path(project, target_deployment_id, "rollback"),
        )
        return (data or {}).get("result") or {}

    # ------------------------------------------------------------ wrangler

    def deploy(
        self,
        project_dir: str,
        project_name: str,
        branch: str = "main",
        commit_message: str | None = None,
        commit_dirty: bool = True,
        no_bundle: bool = True,
        timeout: int = 600,
    ) -> dict:
        """Run `wrangler pages deploy` with env-var auth, parse stdout, reconcile via REST.

        Returns: {deployment_id, short_id, deployment_url, project_url, deployment_obj,
        stdout, stderr}.
        """
        which = subprocess.run(
            ["which", "wrangler"], capture_output=True, text=True
        )
        if which.returncode != 0:
            raise CloudflarePagesError(
                500,
                "wrangler not found on PATH. Install: npm i -g wrangler.",
            )

        cmd = [
            "wrangler",
            "pages",
            "deploy",
            project_dir,
            f"--project-name={project_name}",
            f"--branch={branch}",
            f"--commit-dirty={'true' if commit_dirty else 'false'}",
        ]
        if no_bundle:
            cmd.append("--no-bundle")
        if commit_message:
            cmd.append(f"--commit-message={commit_message}")

        env = {
            **os.environ,
            "CLOUDFLARE_API_TOKEN": self.token,
            "CLOUDFLARE_ACCOUNT_ID": self.account_id,
        }
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise CloudflarePagesError(
                proc.returncode,
                "wrangler pages deploy failed.\n"
                f"STDOUT:\n{proc.stdout}\n"
                f"STDERR:\n{proc.stderr}",
            )

        match = (
            DEPLOYMENT_URL_PATTERN.search(proc.stdout)
            or DEPLOYMENT_URL_PATTERN.search(proc.stderr)
        )
        deployment_url = match.group(0) if match else None

        latest = self.list_deployments(project_name, env="production", per_page=1)
        deployment_obj = latest[0] if latest else {}

        return {
            "deployment_id": deployment_obj.get("id"),
            "short_id": deployment_obj.get("short_id"),
            "deployment_url": deployment_url or deployment_obj.get("url"),
            "project_url": f"https://{project_name}.pages.dev",
            "deployment_obj": deployment_obj,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


# ===================================================================== CLI

def _print(obj: Any, pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(obj, indent=2, default=str))
    else:
        print(json.dumps(obj, default=str))


def _print_table(rows: list[dict], cols: list[str]) -> None:
    if not rows:
        print("(no rows)")
        return
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r.get(c, "")) for c in cols))


def _project_row(p: dict) -> dict:
    return {
        "name": p.get("name"),
        "subdomain": p.get("subdomain"),
        "production_branch": p.get("production_branch"),
        "created_on": p.get("created_on"),
    }


def _domain_row(d: dict) -> dict:
    return {
        "name": d.get("name"),
        "status": d.get("status"),
        "validation_status": (d.get("validation_data") or {}).get("status"),
        "verification_status": (d.get("verification_data") or {}).get("status"),
        "ca": d.get("certificate_authority"),
    }


def _deployment_row(d: dict) -> dict:
    stage = d.get("latest_stage") or {}
    return {
        "short_id": d.get("short_id"),
        "id": d.get("id"),
        "url": d.get("url"),
        "environment": d.get("environment"),
        "stage": stage.get("name"),
        "status": stage.get("status"),
        "created_on": d.get("created_on"),
    }


def _cli() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    common.add_argument("--table", action="store_true", help="Tab-separated table for list ops")

    p = argparse.ArgumentParser(
        prog="cloudflare-pages",
        description="Cloudflare Pages API CLI",
        parents=[common],
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verify", parents=[common], help="Verify the API token")

    sub.add_parser("list-projects", parents=[common], help="List Pages projects")

    sp = sub.add_parser("get-project", parents=[common], help="Get a project by name")
    sp.add_argument("name")

    sp = sub.add_parser("create-project", parents=[common], help="Create a direct-upload project")
    sp.add_argument("name")
    sp.add_argument("--branch", default="main")

    sp = sub.add_parser("list-domains", parents=[common], help="List custom domains on a project")
    sp.add_argument("project")

    sp = sub.add_parser("add-domain", parents=[common], help="Attach a custom domain to a project")
    sp.add_argument("project")
    sp.add_argument("domain")

    sp = sub.add_parser("get-domain", parents=[common], help="Get a custom domain status")
    sp.add_argument("project")
    sp.add_argument("domain")

    sp = sub.add_parser("revalidate-domain", parents=[common], help="Force domain re-validation (no body)")
    sp.add_argument("project")
    sp.add_argument("domain")

    sp = sub.add_parser("delete-domain", parents=[common], help="Detach a domain from a project")
    sp.add_argument("project")
    sp.add_argument("domain")

    sp = sub.add_parser("wait-for-active", parents=[common], help="Poll until domain is fully active")
    sp.add_argument("project")
    sp.add_argument("domain")
    sp.add_argument("--timeout", type=int, default=DEFAULT_DOMAIN_TIMEOUT)

    sp = sub.add_parser("deploy", parents=[common], help="Deploy a directory via wrangler")
    sp.add_argument("dir")
    sp.add_argument("project")
    sp.add_argument("--branch", default="main")
    sp.add_argument("--commit-message")
    sp.add_argument("--no-commit-dirty", action="store_true")
    sp.add_argument("--bundle", action="store_true", help="Disable --no-bundle (run Functions bundling)")

    sp = sub.add_parser("list-deployments", parents=[common], help="List recent deployments")
    sp.add_argument("project")
    sp.add_argument("--env", choices=["production", "preview"], default="production")
    sp.add_argument("--per-page", type=int, default=25)

    sp = sub.add_parser("get-deployment", parents=[common], help="Get a deployment by id")
    sp.add_argument("project")
    sp.add_argument("deployment_id")

    sp = sub.add_parser("delete-deployment", parents=[common], help="Delete a non-production deployment")
    sp.add_argument("project")
    sp.add_argument("deployment_id")
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("rollback", parents=[common], help="Promote a previous deployment to production")
    sp.add_argument("project")
    sp.add_argument("target_deployment_id")

    sp = sub.add_parser("build-logs", parents=[common], help="Fetch build logs for a deployment")
    sp.add_argument("project")
    sp.add_argument("deployment_id")

    args = p.parse_args()

    try:
        client = CloudflarePagesClient()

        if args.cmd == "verify":
            _print(client.verify_token(), args.pretty)
            return 0

        if args.cmd == "list-projects":
            projects = client.list_projects()
            if args.table:
                _print_table(
                    [_project_row(pr) for pr in projects],
                    ["name", "subdomain", "production_branch", "created_on"],
                )
            else:
                _print(projects, args.pretty)
            return 0

        if args.cmd == "get-project":
            _print(client.get_project(args.name), args.pretty)
            return 0

        if args.cmd == "create-project":
            _print(
                client.create_project(args.name, production_branch=args.branch),
                args.pretty,
            )
            return 0

        if args.cmd == "list-domains":
            domains = client.list_domains(args.project)
            if args.table:
                _print_table(
                    [_domain_row(d) for d in domains],
                    ["name", "status", "validation_status", "verification_status", "ca"],
                )
            else:
                _print(domains, args.pretty)
            return 0

        if args.cmd == "add-domain":
            _print(client.add_domain(args.project, args.domain), args.pretty)
            return 0

        if args.cmd == "get-domain":
            _print(client.get_domain(args.project, args.domain), args.pretty)
            return 0

        if args.cmd == "revalidate-domain":
            _print(client.force_revalidate_domain(args.project, args.domain), args.pretty)
            return 0

        if args.cmd == "delete-domain":
            client.delete_domain(args.project, args.domain)
            _print({"deleted": args.domain, "project": args.project}, args.pretty)
            return 0

        if args.cmd == "wait-for-active":
            _print(
                client.wait_for_domain_active(
                    args.project, args.domain, timeout=args.timeout
                ),
                args.pretty,
            )
            return 0

        if args.cmd == "deploy":
            result = client.deploy(
                args.dir,
                args.project,
                branch=args.branch,
                commit_message=args.commit_message,
                commit_dirty=not args.no_commit_dirty,
                no_bundle=not args.bundle,
            )
            slim = {k: v for k, v in result.items() if k not in ("stdout", "stderr", "deployment_obj")}
            _print(slim, args.pretty)
            return 0

        if args.cmd == "list-deployments":
            deps = client.list_deployments(args.project, env=args.env, per_page=args.per_page)
            if args.table:
                _print_table(
                    [_deployment_row(d) for d in deps],
                    ["short_id", "id", "url", "environment", "stage", "status", "created_on"],
                )
            else:
                _print(deps, args.pretty)
            return 0

        if args.cmd == "get-deployment":
            _print(client.get_deployment(args.project, args.deployment_id), args.pretty)
            return 0

        if args.cmd == "delete-deployment":
            client.delete_deployment(args.project, args.deployment_id, force=args.force)
            _print({"deleted": args.deployment_id, "project": args.project}, args.pretty)
            return 0

        if args.cmd == "rollback":
            _print(
                client.rollback_deployment(args.project, args.target_deployment_id),
                args.pretty,
            )
            return 0

        if args.cmd == "build-logs":
            logs = client.get_build_logs(args.project, args.deployment_id)
            if args.table:
                _print_table(logs, ["ts", "line"])
            else:
                _print(logs, args.pretty)
            return 0

    except CloudflarePagesError as e:
        print(f"Cloudflare Pages error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(_cli())
