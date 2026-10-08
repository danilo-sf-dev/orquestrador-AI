#!/usr/bin/env python3
"""Canonical Jira cache helper: cache-first fetch/write/read with explicit Basic Auth."""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent.parent
AUTH_FILE = ROOT / "jira-auth.local.json"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_REF = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")


class JiraError(RuntimeError):
    pass


def key_of(value: str) -> str:
    text = value.strip()
    match = re.search(r"([A-Za-z][A-Za-z0-9_]*-\d+)", text)
    key = (match.group(1) if match else text).upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*-\d+", key):
        raise JiraError(f"INVALID_ISSUE_KEY: {value}")
    return key


TIPO_PASTA = {
    "Épico": "Épico",
    "História": "História",
    "Delivery": "Delivery",
    "Sub-tarefa": "Sub-tarefa",
}
TIPO_TAG = {
    "Épico": "EPICO",
    "História": "HISTORIA",
    "Delivery": "DELIVERY",
    "Sub-tarefa": "SUB-TAREFA",
}
SEM_SPRINT = "(SEM SPRINT)"
EPIC_SUFFIX = " [Épico]"
EPIC_UNCACHED = " (não cacheado)"
LEVEL0 = ("História", "Delivery")


def issue_type_name(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else {}
    return str(((fields.get("issuetype") or {}).get("name")) or "")


def parent_key_of(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else {}
    return str(((fields.get("parent") or {}).get("key")) or "")


def resolve_epic(payload: dict[str, Any]) -> str | None:
    """Resolve the epic key: epic-link fields first, then walk up the parent chain (bounded)."""
    fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else {}
    direct = fields.get("customfield_10008") or fields.get("customfield_10432")
    if direct:
        return str(direct)
    if issue_type_name(payload) == "Épico":
        return None

    current = payload
    for _ in range(3):
        parent_key = parent_key_of(current)
        if not parent_key:
            return None
        parent_path = find_cache_path(parent_key)
        if parent_path is None:
            # Parent not cached: a level-0 child still has the epic as its parent.
            return parent_key if issue_type_name(current) in LEVEL0 else None
        try:
            parent_payload = json.loads(parent_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if issue_type_name(parent_payload) == "Épico":
            return parent_key
        current = parent_payload
    return None


def sprint_of(payload: Any) -> dict[str, Any] | None:
    """Last entry of customfield_10010 is the current sprint; earlier entries are carry-over."""
    if not isinstance(payload, dict):
        return None
    fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else {}
    sprints = fields.get("customfield_10010")
    if isinstance(sprints, list) and sprints and isinstance(sprints[-1], dict):
        return sprints[-1]
    return None


def sprint_label(payload: Any) -> str:
    sprint = sprint_of(payload)
    if not sprint:
        return SEM_SPRINT
    name, sid = sprint.get("name"), sprint.get("id")
    if name and sid is not None:
        return f"{name} ({sid})"
    return str(name) if name else SEM_SPRINT


def find_cache_path(key: str) -> Path | None:
    """Locate an existing cache file for KEY under the tree layout or the legacy flat layout."""
    flat = ROOT / f"{key}.json"
    if flat.exists():
        return flat
    pattern = re.compile(rf"^{re.escape(key)}(\s*\[|\.)")
    for candidate in sorted(ROOT.rglob(f"{key}*.json")):
        if pattern.match(candidate.name):
            return candidate
    return None


def epic_directory(epic_key: str) -> Path:
    """Directory of an epic, keeping the '(não cacheado)' marker in sync in both directions."""
    base = ROOT / f"{epic_key}{EPIC_SUFFIX}"
    decorated = ROOT / f"{epic_key}{EPIC_SUFFIX}{EPIC_UNCACHED}"
    cached = find_cache_path(epic_key) is not None
    if cached and decorated.exists() and not base.exists():
        decorated.rename(base)
        return base
    if cached:
        return base
    if base.exists() and not decorated.exists():
        base.rename(decorated)
    return decorated


def cache_path(key: str, payload: dict[str, Any] | None = None) -> Path:
    """Canonical tree path for KEY. Without payload, only an existing file can be resolved."""
    if payload is None:
        existing = find_cache_path(key)
        return existing if existing is not None else ROOT / f"{key}.json"

    itype = issue_type_name(payload)
    if itype == "Épico":
        return epic_directory(key) / f"{key}[EPICO].json"

    parent_key = parent_key_of(payload)
    if not parent_key:
        return ROOT / f"{key}.json"

    parent_payload = None
    parent_path = find_cache_path(parent_key)
    if parent_path is not None:
        try:
            parent_payload = json.loads(parent_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parent_payload = None
    parent_type = issue_type_name(parent_payload)

    if parent_type == "Épico":
        epic_key, owner_key, owner_payload = parent_key, key, payload
    elif parent_type in LEVEL0:
        epic_key = parent_key_of(parent_payload) or parent_key
        owner_key, owner_payload = parent_key, parent_payload
    elif itype in LEVEL0:
        epic_key, owner_key, owner_payload = parent_key, key, payload
    else:
        # Sub-task whose parent is not cached: no reliable epic/sprint to derive.
        return ROOT / f"{key}.json"

    owner_type = issue_type_name(owner_payload) or itype
    folder = TIPO_PASTA.get(owner_type, owner_type or "Item")
    tag = TIPO_TAG.get(itype, itype.upper() or "ITEM")
    directory = epic_directory(epic_key) / sprint_label(owner_payload) / f"{owner_key} [{folder}]"
    return directory / f"{key}[{tag}].json"


def compact(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def load_cache(key: str, normalize: bool = True) -> dict[str, Any]:
    path = find_cache_path(key)
    if path is None:
        raise JiraError(f"CACHE_MISS: {key}")
    raw = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise JiraError(f"CACHE_INVALID_JSON: {key}: line={exc.lineno} col={exc.colno}") from exc
    if not isinstance(payload, dict):
        raise JiraError(f"CACHE_INVALID_ROOT: {key}")
    actual = str(payload.get("key") or "").upper()
    if actual and actual != key:
        raise JiraError(f"CACHE_KEY_MISMATCH: expected={key} actual={actual}")
    canonical = compact(payload)
    if normalize and raw != canonical:
        path.write_text(canonical, encoding="utf-8")
    elif path.parent == ROOT:
        # Legacy flat cache: migrate into the tree layout once the payload is known.
        target = cache_path(key, payload)
        if target != path and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            path.replace(target)
    if issue_type_name(payload) == "Épico":
        epic_directory(key)
    return payload


def write_cache(key: str, payload: dict[str, Any]) -> None:
    actual = str(payload.get("key") or "").upper()
    if actual and actual != key:
        raise JiraError(f"RESPONSE_KEY_MISMATCH: expected={key} actual={actual}")
    path = cache_path(key, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compact(payload), encoding="utf-8")
    if issue_type_name(payload) == "Épico":
        epic_directory(key)


def load_dotenv(path: Path = ENV_FILE) -> None:
    """Load simple KEY=VALUE pairs without external dependencies. Existing process env wins."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def resolve_env_ref(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    match = ENV_REF.fullmatch(text)
    if not match:
        raise JiraError(
            f"AUTH_CONFIG_INVALID: jira-auth.local.json field {field_name} must reference an env var like ${{JIRA_EMAIL}}"
        )
    env_name = match.group(1)
    resolved = os.environ.get(env_name, "").strip()
    if not resolved:
        raise JiraError(f"AUTH_ENV_MISSING: {env_name}: configure {ENV_FILE}")
    return resolved


def resolve_auth() -> tuple[str, str, str]:
    if not AUTH_FILE.exists():
        raise JiraError(f"AUTH_NOT_CONFIGURED: missing {AUTH_FILE}")
    load_dotenv()
    try:
        data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        jira = data.get("jira", {})
    except Exception as exc:
        raise JiraError(f"AUTH_INVALID_JSON: {AUTH_FILE}") from exc

    base = resolve_env_ref(jira.get("baseUrl"), "baseUrl").rstrip("/")
    email = resolve_env_ref(jira.get("email"), "email")
    token = resolve_env_ref(jira.get("apiToken"), "apiToken")

    if not base.startswith("https://"):
        raise JiraError("AUTH_INVALID_BASE_URL: expected https://...")
    return base, email, token


def get_issue(key: str) -> dict[str, Any]:
    """Raw GET of a single issue. Does not touch the cache."""
    base, email, token = resolve_auth()
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    url = f"{base}/rest/api/3/issue/{urllib.parse.quote(key)}?expand=renderedFields,names"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {basic}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body, status = response.read(), response.status
    except urllib.error.HTTPError as exc:
        labels = {
            401: "invalid or expired credential",
            403: "no permission",
            404: "issue not found or not visible",
        }
        raise JiraError(f"HTTP_{exc.code}: {labels.get(exc.code, 'Jira request failed')}") from exc
    except urllib.error.URLError as exc:
        raise JiraError(f"NETWORK_ERROR: {exc.reason}") from exc

    if status != 200:
        raise JiraError(f"HTTP_{status}: unexpected Jira response")
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception as exc:
        raise JiraError("INVALID_JIRA_RESPONSE: expected UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise JiraError("INVALID_JIRA_RESPONSE: root must be an object")
    return payload


def fetch(key: str) -> dict[str, Any]:
    payload = get_issue(key)
    write_cache(key, payload)
    return payload


def ensure_chain(key: str) -> dict[str, Any]:
    """Ensure KEY and its ancestor chain (parent story -> epic) are cached.

    Returns the normalized payload of KEY. Ancestors already cached are left
    untouched (no Jira call); missing ancestors are fetched.
    """
    path = find_cache_path(key)
    payload = load_cache(key) if path is not None else fetch(key)

    seen = {key}
    current = payload
    for _ in range(4):
        parent_key = parent_key_of(current)
        if not parent_key or parent_key in seen:
            break
        seen.add(parent_key)
        parent_path = find_cache_path(parent_key)
        if parent_path is None:
            current = fetch(parent_key)
        else:
            current = load_cache(parent_key)

    epic_key = resolve_epic(payload)
    if epic_key and epic_key not in seen and find_cache_path(epic_key) is None:
        try:
            fetch(epic_key)
        except JiraError:
            pass

    load_cache(key)  # promotes/settles the tree placement after ancestors exist
    return normalized(load_cache(key))



def adf_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "\n".join(filter(None, (adf_text(x) for x in node)))
    if not isinstance(node, dict):
        return str(node)
    if node.get("type") == "text":
        return str(node.get("text") or "")
    if node.get("type") == "hardBreak":
        return "\n"
    content = node.get("content") if isinstance(node.get("content"), list) else []
    parts = [adf_text(x) for x in content]
    block_types = {
        "doc", "paragraph", "heading", "blockquote", "listItem", "bulletList",
        "orderedList", "table", "tableRow", "tableCell", "codeBlock",
    }
    sep = "\n" if node.get("type") in block_types else ""
    return sep.join(filter(None, parts)).strip()


def plain(value: Any) -> Any:
    if isinstance(value, dict) and value.get("type") == "doc":
        return adf_text(value)
    if isinstance(value, str) and "<" in value and ">" in value:
        text = re.sub(r"<br\s*/?>|</p\s*>", "\n", value, flags=re.I)
        return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
    return value


def normalized(payload: dict[str, Any]) -> dict[str, Any]:
    fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else {}
    rendered = payload.get("renderedFields") if isinstance(payload.get("renderedFields"), dict) else {}
    names = payload.get("names") if isinstance(payload.get("names"), dict) else {}
    status = fields.get("status") if isinstance(fields.get("status"), dict) else {}
    issue_type = fields.get("issuetype") if isinstance(fields.get("issuetype"), dict) else {}
    parent = fields.get("parent") if isinstance(fields.get("parent"), dict) else {}

    description = adf_text(fields.get("description"))
    if not description and isinstance(rendered.get("description"), str):
        description = plain(rendered["description"])

    comments = []
    comment_block = fields.get("comment")
    if isinstance(comment_block, dict):
        for item in comment_block.get("comments", []):
            if isinstance(item, dict):
                author = item.get("author") if isinstance(item.get("author"), dict) else {}
                comments.append(
                    {
                        "author": author.get("displayName"),
                        "created": item.get("created"),
                        "body": adf_text(item.get("body")),
                    }
                )

    custom = []
    for field_id, raw in fields.items():
        if not field_id.startswith("customfield_") or raw in (None, "", [], {}):
            continue
        value = rendered.get(field_id)
        if value in (None, "", [], {}):
            value = raw
        custom.append(
            {"id": field_id, "name": names.get(field_id) or field_id, "value": plain(value)}
        )

    epic = resolve_epic(payload)
    current_sprint = sprint_of(payload)
    assignee = fields.get("assignee") if isinstance(fields.get("assignee"), dict) else {}
    creator = fields.get("creator") if isinstance(fields.get("creator"), dict) else {}

    return {
        "key": payload.get("key"),
        "summary": fields.get("summary"),
        "status": status.get("name"),
        "issueType": issue_type.get("name"),
        "parent": parent.get("key"),
        "epic": epic,
        "sprint": current_sprint,
        "backlog": current_sprint is None,
        "assignee": assignee.get("displayName"),
        "creator": creator.get("displayName"),
        "description": description,
        "comments": comments,
        "subtasks": [
            {"key": x.get("key"), "summary": (x.get("fields") or {}).get("summary")}
            for x in fields.get("subtasks", [])
            if isinstance(x, dict)
        ],
        "labels": fields.get("labels") if isinstance(fields.get("labels"), list) else [],
        "customFields": custom,
    }


def emit(payload: Any, pretty: bool) -> None:
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical Jira cache helper")
    parser.add_argument(
        "command",
        choices=("read", "fetch", "refresh", "validate", "chain"),
        help="chain: ensure the issue plus its parent story and epic are cached",
    )
    parser.add_argument("issue_key")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        key = key_of(args.issue_key)
        if args.command == "validate":
            load_cache(key, normalize=True)
            print(f"CACHE_OK: {key}: MINIFIED_SINGLE_LINE")
            return 0
        if args.command == "read":
            emit(normalized(load_cache(key, normalize=True)), args.pretty)
            return 0
        if args.command == "chain":
            emit(ensure_chain(key), args.pretty)
            return 0
        if args.command == "fetch":
            try:
                payload = load_cache(key, normalize=True)
            except JiraError as exc:
                if not str(exc).startswith(("CACHE_MISS:", "CACHE_INVALID_JSON:")):
                    raise
                payload = fetch(key)
            emit(normalized(payload), args.pretty)
            return 0

        payload = fetch(key)
        emit(normalized(payload), args.pretty)
        return 0
    except JiraError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
