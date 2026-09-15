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
AUTH_FILE = ROOT / "jira-auth.local.json"
PLACEHOLDERS = ("SEU_", "YOUR_", "<", "PLACEHOLDER")


class JiraError(RuntimeError):
    pass


def key_of(value: str) -> str:
    key = value.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*-\d+", key):
        raise JiraError(f"INVALID_ISSUE_KEY: {value}")
    return key


def cache_file(key: str) -> Path:
    return ROOT / f"{key}.json"


def compact(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def load_cache(key: str, normalize: bool = True) -> dict[str, Any]:
    path = cache_file(key)
    if not path.exists():
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
    return payload


def write_cache(key: str, payload: dict[str, Any]) -> None:
    actual = str(payload.get("key") or "").upper()
    if actual and actual != key:
        raise JiraError(f"RESPONSE_KEY_MISMATCH: expected={key} actual={actual}")
    cache_file(key).write_text(compact(payload), encoding="utf-8")


def placeholder(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return True
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDERS)


def auth_from_template() -> tuple[str, str, str] | None:
    if not AUTH_FILE.exists():
        return None
    try:
        jira = json.loads(AUTH_FILE.read_text(encoding="utf-8")).get("jira", {})
    except Exception:
        return None
    base = str(jira.get("baseUrl") or "").rstrip("/")
    email = str(jira.get("email") or "")
    token = str(jira.get("apiToken") or "")
    if any(placeholder(v) for v in (base, email, token)):
        return None
    return (base, email, token) if base.startswith("https://") else None


def settings_candidates(explicit: str | None) -> list[Path]:
    paths: list[Path] = []
    if explicit:
        paths.append(Path(explicit).expanduser())
    if os.environ.get("JIRA_CLAUDE_SETTINGS"):
        paths.append(Path(os.environ["JIRA_CLAUDE_SETTINGS"]).expanduser())
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents):
        paths.append(parent / ".claude" / "settings.local.json")
    seen, unique = set(), []
    for path in paths:
        if str(path) not in seen:
            seen.add(str(path))
            unique.append(path)
    return unique


def auth_from_settings(path: Path) -> tuple[str, str, str] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        allowed = data.get("permissions", {}).get("allow", [])
    except Exception:
        return None
    for entry in allowed if isinstance(allowed, list) else []:
        if not isinstance(entry, str) or "curl" not in entry or "atlassian.net" not in entry:
            continue
        user = re.search(r"(?:^|\s)(?:-u|--user)\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s\)]+))", entry)
        url = re.search(r"https://[A-Za-z0-9.-]+\.atlassian\.net", entry)
        if not user or not url:
            continue
        credential = next((g for g in user.groups() if g is not None), "")
        if ":" not in credential:
            continue
        email, token = credential.split(":", 1)
        if email and token:
            return url.group(0).rstrip("/"), email, token
    return None


def resolve_auth(settings: str | None) -> tuple[str, str, str]:
    direct = auth_from_template()
    if direct:
        return direct
    for path in settings_candidates(settings):
        found = auth_from_settings(path)
        if found:
            return found
    raise JiraError(
        "AUTH_NOT_CONFIGURED: use local real values in infrastructure/jira/jira-auth.local.json "
        "or pass --settings <project>/.claude/settings.local.json"
    )


def fetch(key: str, settings: str | None) -> dict[str, Any]:
    base, email, token = resolve_auth(settings)
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
        labels = {401: "invalid or expired credential", 403: "no permission", 404: "issue not found or not visible"}
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
    write_cache(key, payload)
    return payload


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
    block_types = {"doc", "paragraph", "heading", "blockquote", "listItem", "bulletList", "orderedList", "table", "tableRow", "tableCell", "codeBlock"}
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
                comments.append({"author": author.get("displayName"), "created": item.get("created"), "body": adf_text(item.get("body"))})

    custom = []
    for field_id, raw in fields.items():
        if not field_id.startswith("customfield_") or raw in (None, "", [], {}):
            continue
        value = rendered.get(field_id)
        if value in (None, "", [], {}):
            value = raw
        custom.append({"id": field_id, "name": names.get(field_id) or field_id, "value": plain(value)})

    return {
        "key": payload.get("key"),
        "summary": fields.get("summary"),
        "status": status.get("name"),
        "issueType": issue_type.get("name"),
        "parent": parent.get("key"),
        "description": description,
        "comments": comments,
        "subtasks": [{"key": x.get("key"), "summary": (x.get("fields") or {}).get("summary")} for x in fields.get("subtasks", []) if isinstance(x, dict)],
        "labels": fields.get("labels") if isinstance(fields.get("labels"), list) else [],
        "customFields": custom,
    }


def emit(payload: Any, pretty: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None, separators=None if pretty else (",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical Jira cache helper")
    parser.add_argument("command", choices=("read", "fetch", "refresh", "validate"))
    parser.add_argument("issue_key")
    parser.add_argument("--settings", help="Project .claude/settings.local.json; used only on cache miss")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    key = key_of(args.issue_key)

    try:
        if args.command == "validate":
            load_cache(key, normalize=True)
            print(f"CACHE_OK: {key}: MINIFIED_SINGLE_LINE")
            return 0
        if args.command == "read":
            emit(normalized(load_cache(key, normalize=True)), args.pretty)
            return 0
        if args.command == "fetch":
            try:
                payload = load_cache(key, normalize=True)
            except JiraError as exc:
                if not str(exc).startswith(("CACHE_MISS:", "CACHE_INVALID_JSON:")):
                    raise
                payload = fetch(key, args.settings)
            emit(normalized(payload), args.pretty)
            return 0
        payload = fetch(key, args.settings)
        emit(normalized(payload), args.pretty)
        return 0
    except JiraError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
