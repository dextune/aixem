#!/usr/bin/env python3
"""Canonical documentation compiler, validator, static-site generator, and release utilities for AIXEM 0.5."""
from __future__ import annotations

import argparse
import dataclasses
import fnmatch
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unicodedata
import zipfile
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator
from urllib.parse import unquote, urlsplit

import mistune
import yaml
from bs4 import BeautifulSoup
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
META = DOCS / "_meta"
GENERATED = META / "generated"
SITE = ROOT / "site"
REFERENCE = ROOT / "reference"
RELEASE_DIR = ROOT / "release"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "0.5.1"
RELEASE_ID = f"AIXEM-SRP-{VERSION}-2026-08-12"
FIXED_TIME = "2026-08-12T00:00:00Z"
REQ_RE = re.compile(r"\bAIXEM-REQ-[A-Z0-9-]+-[0-9]{4}\b")
DOC_ID_RE = re.compile(r"^AIXEM-[A-Z0-9-]+-[0-9]{3,4}$")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
RAW_LINK_RE = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
EXPLICIT_ANCHOR_RE = re.compile(r"<a\s+(?:[^>]*?\s+)?(?:id|name)=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.+#-]{1,}")
STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "shall", "must", "into", "when", "where",
    "each", "every", "only", "than", "then", "also", "under", "over", "without", "within", "about",
    "aixem", "document", "documentation", "page", "section", "system", "profile", "guide", "index",
}

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".go", ".js", ".mjs", ".css", ".html", ".svg", ".xml", ".sh", ".toml", ".ini", ".cfg", ".aixem", ".fbs", ".iso-ebnf", ".mod", ""}


class AixemDocsError(RuntimeError):
    """Raised for deterministic documentation or release failures."""


@dataclasses.dataclass(frozen=True)
class Heading:
    level: int
    text: str
    anchor: str
    line: int


@dataclasses.dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    anchor: str
    line: int
    statement: str


@dataclasses.dataclass
class Document:
    path: Path
    rel: str
    meta: dict[str, Any]
    body: str
    headings: list[Heading]
    anchors: set[str]
    requirements: list[Requirement]
    sha256: str
    bytes: int

    @property
    def id(self) -> str:
        return str(self.meta["id"])

    @property
    def site_path(self) -> str:
        return str(PurePosixPath(self.rel).with_suffix(".html"))


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8", newline="\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_term(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower().strip()
    value = re.sub(r"[^a-z0-9+#.]+", "-", value)
    return value.strip("-")


def strip_inline_markdown(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    return html.unescape(value).strip()


def slugify(value: str) -> str:
    value = strip_inline_markdown(value).lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise AixemDocsError(f"missing YAML front matter: {path.relative_to(ROOT)}")
    marker = raw.find("\n---\n", 4)
    if marker < 0:
        raise AixemDocsError(f"unterminated YAML front matter: {path.relative_to(ROOT)}")
    front = raw[4:marker]
    body = raw[marker + 5 :]
    meta = yaml.safe_load(front)
    if not isinstance(meta, dict):
        raise AixemDocsError(f"front matter is not an object: {path.relative_to(ROOT)}")
    return meta, body


def extract_headings(body: str) -> tuple[list[Heading], set[str]]:
    headings: list[Heading] = []
    anchors = set(EXPLICIT_ANCHOR_RE.findall(body))
    used: dict[str, int] = {}
    for match in HEADING_RE.finditer(body):
        raw_text = match.group(2)
        base = slugify(raw_text)
        index = used.get(base, 0)
        used[base] = index + 1
        anchor = base if index == 0 else f"{base}-{index}"
        line = body.count("\n", 0, match.start()) + 1
        text = strip_inline_markdown(raw_text)
        headings.append(Heading(len(match.group(1)), text, anchor, line))
        anchors.add(anchor)
    return headings, anchors


def _paragraph_after(body: str, offset: int) -> str:
    tail = body[offset:]
    lines: list[str] = []
    started = False
    for raw in tail.splitlines():
        line = raw.strip()
        if not started:
            if not line or line.startswith("<a ") or line.startswith("#"):
                continue
            started = True
        if started and not line:
            break
        if started:
            lines.append(line)
    return " ".join(lines)


def extract_requirements(body: str, headings: list[Heading]) -> list[Requirement]:
    definitions: list[Requirement] = []
    seen: set[str] = set()
    for match in re.finditer(r"<a\s+id=[\"'](AIXEM-REQ-[^\"']+)[\"']\s*></a>", body):
        rid = match.group(1)
        if not REQ_RE.fullmatch(rid) or rid in seen:
            continue
        heading_match = re.search(rf"^###\s+{re.escape(rid)}\s*[—-]\s*(.+?)\s*$", body[match.end():], re.MULTILINE)
        title = heading_match.group(1).strip() if heading_match else rid
        statement_offset = match.end() + (heading_match.end() if heading_match else 0)
        statement = _paragraph_after(body, statement_offset)
        line = body.count("\n", 0, match.start()) + 1
        definitions.append(Requirement(rid, title, rid, line, statement))
        seen.add(rid)
    return definitions


def load_documents(root: Path = DOCS) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(root.rglob("*.md")):
        if "_meta" in path.relative_to(root).parts:
            continue
        meta, body = parse_front_matter(path)
        headings, anchors = extract_headings(body)
        requirements = extract_requirements(body, headings)
        data = path.read_bytes()
        documents.append(Document(path, path.relative_to(root).as_posix(), meta, body, headings, anchors, requirements, sha256_bytes(data), len(data)))
    return documents


def document_maps(documents: Iterable[Document]) -> tuple[dict[str, Document], dict[str, Document]]:
    by_id: dict[str, Document] = {}
    by_path: dict[str, Document] = {}
    for doc in documents:
        if doc.id in by_id:
            raise AixemDocsError(f"duplicate document ID {doc.id}: {by_id[doc.id].rel}, {doc.rel}")
        if doc.rel in by_path:
            raise AixemDocsError(f"duplicate canonical path {doc.rel}")
        by_id[doc.id] = doc
        by_path[doc.rel] = doc
    return by_id, by_path


def load_yaml(path: Path) -> Any:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        raise AixemDocsError(f"empty YAML file: {path.relative_to(ROOT)}")
    return data



CANONICAL_FOOTER = "---\n\nThis file is canonical authored documentation. Generated HTML, agent cards, route indexes, and traceability records are derived from its metadata and content."
PATCH_MARKER_RE = re.compile(r"<!--\s*[^>]*0\.5\.\d+[^>]*(?::(?:start|end|begin)|(?:start|end|begin)\s*)[^>]*-->", re.IGNORECASE)
CONTROLLED_DOMAINS = {
    "agent", "architecture", "authoring", "concepts", "conformance", "documentation", "examples",
    "file-formats", "getting-started", "governance", "releases", "routing", "schematic", "specifications", "symbols",
}
CONTROLLED_KINDS = {
    "index", "specification", "contract", "profile", "policy", "reference", "guide", "cookbook",
    "concept", "architecture", "adr", "conformance", "release-note", "example",
}


def deterministic_token_estimate(body: str) -> int:
    """Return the release-stable approximate token count used for authored metadata checks."""
    return max(1, (len(body.encode("utf-8")) + 3) // 4)


def load_repository_document_policy() -> dict[str, Any]:
    path = META / "repository-document-policy.yaml"
    policy = load_yaml(path)
    errors = validate_json_schema(policy, META / "schema" / "repository-document-policy.schema.json", path.relative_to(ROOT).as_posix())
    role_ids = [str(role.get("id", "")) for role in policy.get("roles", [])]
    if len(role_ids) != len(set(role_ids)):
        errors.append("repository document policy contains duplicate role IDs")
    if errors:
        raise AixemDocsError("repository document policy invalid:\n" + "\n".join(errors))
    return policy


def _path_matches_role(rel: str, role: dict[str, Any]) -> bool:
    included = any(fnmatch.fnmatchcase(rel, pattern) for pattern in role.get("include", []))
    excluded = any(fnmatch.fnmatchcase(rel, pattern) for pattern in role.get("exclude", []))
    return included and not excluded


def _repository_markdown_paths(root: Path = ROOT) -> list[Path]:
    return [
        path for path in sorted(root.rglob("*.md"))
        if path.is_file() and ".git" not in path.parts and "site" not in path.relative_to(root).parts
        and "reference" not in path.relative_to(root).parts
    ]


def _resolve_repository_link(source_rel: str, target: str) -> str | None:
    split = urlsplit(target)
    if split.scheme or split.netloc or target.startswith(("mailto:", "data:", "javascript:")):
        return None
    raw = unquote(split.path)
    if not raw or raw.startswith("/"):
        return None
    base = PurePosixPath(source_rel).parent
    normalized = PurePosixPath(os.path.normpath((base / raw).as_posix()))
    rel = normalized.as_posix()
    if rel == ".." or rel.startswith("../"):
        return None
    if raw.endswith("/"):
        rel = (normalized / "README.md").as_posix()
    elif rel.endswith(".html"):
        rel = rel[:-5] + ".md"
    return rel


def _markdown_inbound_references(markdown_paths: list[Path]) -> dict[str, list[str]]:
    inbound: dict[str, set[str]] = defaultdict(set)
    known = {path.relative_to(ROOT).as_posix() for path in markdown_paths}
    for source in markdown_paths:
        source_rel = source.relative_to(ROOT).as_posix()
        text = source.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text) + RAW_LINK_RE.findall(text):
            resolved = _resolve_repository_link(source_rel, target)
            if resolved in known and resolved != source_rel:
                inbound[resolved].add(source_rel)
    return {key: sorted(value) for key, value in inbound.items()}


def _machine_path_references(markdown_rels: list[str]) -> dict[str, list[str]]:
    """Find authored non-Markdown consumers in one bounded source scan."""
    refs: dict[str, set[str]] = defaultdict(set)
    targets = set(markdown_rels)
    root_targets = {rel for rel in targets if "/" not in rel}
    path_token = re.compile(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.md|(?<![A-Za-z0-9_.-])[A-Z][A-Z0-9_]*\.md")
    candidates: list[Path] = []
    for base in (ROOT / "tools", ROOT / "tests", ROOT / "implementation", META):
        if base.exists():
            candidates.extend(path for path in base.rglob("*") if path.is_file())
    for path in (ROOT / "Makefile", ROOT / "VERSION", ROOT / "planning" / "index.yaml"):
        if path.is_file():
            candidates.append(path)
    for path in sorted(set(candidates)):
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() == ".md" or "generated" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"VERSION", "Makefile", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for token in set(path_token.findall(text)):
            normalized = token.lstrip("./")
            if normalized in targets:
                refs[normalized].add(rel)
            elif token in root_targets:
                refs[token].add(rel)
    return {key: sorted(value) for key, value in refs.items()}



def _markdown_outbound_references(markdown_paths: list[Path]) -> dict[str, list[str]]:
    """Return safe repository-local Markdown-to-Markdown edges."""
    known = {path.relative_to(ROOT).as_posix() for path in markdown_paths}
    outbound: dict[str, set[str]] = defaultdict(set)
    for source in markdown_paths:
        source_rel = source.relative_to(ROOT).as_posix()
        text = source.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text) + RAW_LINK_RE.findall(text):
            resolved = _resolve_repository_link(source_rel, target)
            if resolved in known and resolved != source_rel:
                outbound[source_rel].add(str(resolved))
    return {key: sorted(value) for key, value in outbound.items()}


def _plain_markdown_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors = {match.group(1) for match in EXPLICIT_ANCHOR_RE.finditer(text)}
    anchors.update(slugify(match.group(2)) for match in HEADING_RE.finditer(text))
    return anchors


def _root_deferred_targets(policy: dict[str, Any]) -> set[str]:
    """Return explicitly governed generated paths that may not exist before compilation."""
    return {str(PurePosixPath(str(item))) + ("/" if str(item).endswith("/") else "") for item in policy.get("rootReferenceDeferredTargets", [])}


def _validate_root_links(policy: dict[str, Any]) -> dict[str, Any]:
    """Validate every local link emitted by approved root Markdown entrypoints."""
    errors: list[str] = []
    checked = 0
    deferred = _root_deferred_targets(policy)
    for name in sorted(policy.get("rootMarkdownAllowlist", [])):
        source = ROOT / name
        if not source.is_file():
            errors.append(f"missing root document {name}")
            continue
        text = source.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text) + RAW_LINK_RE.findall(text):
            split = urlsplit(target)
            if split.scheme or split.netloc or target.startswith(("mailto:", "data:", "javascript:")):
                continue
            raw = unquote(split.path)
            candidate = source if not raw else (source.parent / raw).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{name}: link escapes repository root: {target}")
                continue
            checked += 1
            if not candidate.exists():
                try:
                    candidate_rel = candidate.relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    candidate_rel = ""
                if raw.endswith("/"):
                    candidate_rel += "/"
                deferred_generated = {
                    "docs/_meta/generated/document-index.json",
                    "docs/_meta/generated/route-index.json",
                    "docs/_meta/generated/task-packet-index.json",
                    "docs/_meta/generated/requirement-traceability.json",
                    "docs/_meta/generated/dependency-graph.json",
                    "docs/_meta/generated/artifact-map.json",
                    "docs/_meta/generated/repository-document-inventory.json",
                    "docs/_meta/generated/document-relationship-audit.json",
                    "docs/_meta/generated/path-migration-index.json",
                }
                if candidate_rel in deferred or candidate_rel in deferred_generated:
                    continue
                errors.append(f"{name}: unresolved local link {target}")
                continue
            if split.fragment and candidate.is_file() and candidate.suffix.lower() == ".md":
                if split.fragment not in _plain_markdown_anchors(candidate):
                    errors.append(f"{name}: unresolved Markdown anchor {target}")
    return {"valid": not errors, "rootDocuments": len(policy.get("rootMarkdownAllowlist", [])), "linksChecked": checked, "errors": errors}


def _root_reference_coverage(policy: dict[str, Any]) -> dict[str, Any]:
    """Require the root reference map to expose every governed repository area."""
    source_name = str(policy.get("rootReferenceMap", "REFERENCE.md"))
    source = ROOT / source_name
    required = [str(item) for item in policy.get("rootReferenceRequiredTargets", [])]
    deferred = _root_deferred_targets(policy)
    errors: list[str] = []
    linked: set[str] = set()
    if not source.is_file():
        errors.append(f"missing root reference map {source_name}")
    else:
        text = source.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text) + RAW_LINK_RE.findall(text):
            split = urlsplit(target)
            if split.scheme or split.netloc or target.startswith(("mailto:", "data:", "javascript:")):
                continue
            raw = unquote(split.path)
            if not raw:
                continue
            candidate = (source.parent / raw).resolve()
            try:
                rel = candidate.relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                continue
            if raw.endswith("/") or candidate.is_dir():
                rel += "/"
            if candidate.exists() or rel in deferred:
                linked.add(rel)
    missing = sorted(item for item in required if item not in linked)
    if missing:
        errors.append(f"{source_name} does not link required repository targets: {', '.join(missing)}")
    return {
        "valid": not errors,
        "referenceMap": source_name,
        "targets": len(required),
        "linked": len(required) - len(missing),
        "missing": missing,
        "errors": errors,
    }


def _section_index_coverage(documents: list[Document]) -> dict[str, Any]:
    """Require each authored category index to link every navigation member."""
    errors: list[str] = []
    by_id, _ = document_maps(documents)
    nav = load_yaml(META / "navigation.yaml")
    sections: list[dict[str, Any]] = []
    total_items = 0
    linked_items = 0
    for section in nav.get("sections", []):
        index_id = str(section.get("index", ""))
        index_doc = by_id.get(index_id)
        if not index_doc:
            continue
        targets = set()
        for target in LINK_RE.findall(index_doc.body) + RAW_LINK_RE.findall(index_doc.body):
            rel, _fragment = resolve_markdown_link(index_doc, target, {doc.rel: doc for doc in documents})
            if rel:
                targets.add(rel)
        missing: list[str] = []
        for item_id in section.get("items", []):
            total_items += 1
            target_doc = by_id.get(str(item_id))
            if target_doc and target_doc.rel in targets:
                linked_items += 1
            else:
                missing.append(str(item_id))
        if missing:
            errors.append(f"navigation section {section.get('id')} index {index_id} does not link: {', '.join(missing)}")
        sections.append({
            "id": section.get("id"),
            "index": index_id,
            "items": len(section.get("items", [])),
            "linked": len(section.get("items", [])) - len(missing),
            "missing": missing,
        })
    return {"valid": not errors, "sections": len(sections), "items": total_items, "linked": linked_items, "records": sections, "errors": errors}


def _root_reachability(policy: dict[str, Any], markdown_paths: list[Path], entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Prove that README can chain to every human-authored Markdown document."""
    primary = str(policy.get("primaryRootEntrypoint", "README.md"))
    outbound = _markdown_outbound_references(markdown_paths)
    distances: dict[str, int] = {primary: 0}
    parents: dict[str, str | None] = {primary: None}
    queue: deque[str] = deque([primary])
    while queue:
        source = queue.popleft()
        for target in outbound.get(source, []):
            if target not in distances:
                distances[target] = distances[source] + 1
                parents[target] = source
                queue.append(target)
    human_paths = sorted(str(item["path"]) for item in entries if item.get("humanAuthored"))
    unreachable = sorted(path for path in human_paths if path not in distances)
    max_depth = max((distances[path] for path in human_paths if path in distances), default=0)
    deepest = sorted(path for path in human_paths if distances.get(path) == max_depth)
    primary_exists = (ROOT / primary).is_file()
    return {
        "valid": not unreachable and primary_exists,
        "primaryEntrypoint": primary,
        "humanAuthored": len(human_paths),
        "reachable": len(human_paths) - len(unreachable),
        "unreachable": unreachable,
        "maxDepth": max_depth,
        "deepestDocuments": deepest,
        "errors": [f"root reference chain cannot reach {path}" for path in unreachable],
    }


def _current_release_coherence(documents: list[Document], routes: list[dict[str, Any]]) -> dict[str, Any]:
    """Check operational entrypoints and active route paths against VERSION."""
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def record(name: str, valid: bool, detail: str) -> None:
        checks.append({"id": name, "valid": valid, "detail": detail})
        if not valid:
            errors.append(f"{name}: {detail}")

    expected = {
        "releaseNote": ROOT / "docs" / "releases" / f"{VERSION}.md",
        "validationIndex": ROOT / "validation" / "releases" / VERSION / "README.md",
        "planningRecord": ROOT / "planning" / "releases" / VERSION,
    }
    for name, path in expected.items():
        record(name, path.exists(), f"expected current-release path {path.relative_to(ROOT).as_posix()}")
    for name in ("README.md", "START_HERE.md", "REFERENCE.md"):
        path = ROOT / name
        record(f"rootVersion:{name}", path.is_file() and VERSION in path.read_text(encoding="utf-8"), f"{name} must identify {VERSION}")

    by_id, _ = document_maps(documents)
    nav = load_yaml(META / "navigation.yaml")
    release_section = next((item for item in nav.get("sections", []) if item.get("id") == "releases"), {})
    current_doc = next((doc for doc in documents if doc.rel == f"releases/{VERSION}.md"), None)
    record("releaseNavigation", bool(current_doc and release_section.get("items", []) and release_section["items"][-1] == current_doc.id), "current release note must be the final release navigation item")

    publish = next((route for route in routes if route.get("id") == "publish-release"), None)
    publish_release_docs = []
    if publish:
        publish_release_docs = [step.get("document") for step in publish.get("steps", []) if by_id.get(step.get("document")) and by_id[step.get("document")].meta.get("domain") == "releases"]
    record("publishRouteCurrentState", not publish_release_docs, f"publish-release must not depend on historical release notes: {publish_release_docs}")

    stale_route_paths: list[str] = []
    version_path_re = re.compile(r"validation/evidence/(\d+\.\d+(?:\.\d+){1,2})/")
    for route in routes:
        for key in ("artifacts", "derived", "prohibited"):
            for pattern in (route.get("writes") or {}).get(key, []):
                match = version_path_re.search(str(pattern))
                if match and match.group(1) != VERSION:
                    stale_route_paths.append(f"{route.get('id')}:{pattern}")
    record("routeReleasePaths", not stale_route_paths, f"active routes contain stale release-scoped paths: {stale_route_paths}")

    agent_release_paths = (
        ROOT / "validation/agent-evals-3/manifest.json",
        ROOT / "validation/agent-evals-3/results/summary.json",
        ROOT / "validation/agent-evals-3/results/tier-b-status.json",
        ROOT / "validation/agent-evals-3/results/readiness/readiness-report.json",
    )
    stale_agent_release_paths: list[str] = []
    for path in agent_release_paths:
        if not path.is_file():
            stale_agent_release_paths.append(f"{path.relative_to(ROOT).as_posix()}:missing")
            continue
        data = read_json(path)
        observed = data.get("repositoryRelease") or data.get("release")
        if observed != RELEASE_ID:
            stale_agent_release_paths.append(f"{path.relative_to(ROOT).as_posix()}:{observed}")
    record("agentEvaluationRepositoryRelease", not stale_agent_release_paths, f"Agent Evaluation 3 operational evidence must identify {RELEASE_ID}: {stale_agent_release_paths}")

    metadata_path = RELEASE_DIR / "release-metadata.json"
    if metadata_path.is_file():
        metadata = read_json(metadata_path)
        record("releaseMetadataVersion", metadata.get("version") == VERSION and metadata.get("release") == RELEASE_ID, f"release metadata must identify {VERSION} and {RELEASE_ID}")

    return {"valid": not errors, "version": VERSION, "release": RELEASE_ID, "checks": checks, "errors": errors}


def _authority_scope_review(documents: list[Document], policy: dict[str, Any]) -> dict[str, Any]:
    """Detect ambiguous normative authority-scope ownership."""
    owners: dict[str, list[str]] = defaultdict(list)
    for doc in documents:
        if doc.meta.get("status") != "normative":
            continue
        for scope in doc.meta.get("authority", []):
            owners[str(scope)].append(doc.id)
    allowed = set(policy.get("sharedNormativeAuthorityScopes", []))
    collisions = {scope: sorted(ids) for scope, ids in owners.items() if len(ids) > 1 and scope not in allowed}
    errors = [f"normative authority scope {scope} has multiple owners: {', '.join(ids)}" for scope, ids in sorted(collisions.items())]
    return {
        "valid": not errors,
        "normativeScopes": len(owners),
        "sharedAllowed": sorted(allowed),
        "collisions": collisions,
        "errors": errors,
    }


def build_document_relationship_audit(
    documents: list[Document],
    routes: list[dict[str, Any]] | None = None,
    *,
    entries: list[dict[str, Any]] | None = None,
    markdown_paths: list[Path] | None = None,
) -> dict[str, Any]:
    """Build the deterministic root, index, release, and authority relationship audit."""
    policy = load_repository_document_policy()
    routes = routes if routes is not None else load_routes()
    markdown_paths = markdown_paths if markdown_paths is not None else _repository_markdown_paths()
    if entries is None:
        # Minimal role classification used only when called outside repository audit.
        entries = []
        for path in markdown_paths:
            rel = path.relative_to(ROOT).as_posix()
            matches = [role for role in policy.get("roles", []) if _path_matches_role(rel, role)]
            role = matches[0] if len(matches) == 1 else {"humanAuthored": True}
            entries.append({"path": rel, "humanAuthored": bool(role.get("humanAuthored"))})
    root_links = _validate_root_links(policy)
    repository_areas = _root_reference_coverage(policy)
    reachability = _root_reachability(policy, markdown_paths, entries)
    section_coverage = _section_index_coverage(documents)
    release_coherence = _current_release_coherence(documents, routes)
    authority_scopes = _authority_scope_review(documents, policy)
    errors = [
        *root_links["errors"],
        *repository_areas["errors"],
        *reachability["errors"],
        *section_coverage["errors"],
        *release_coherence["errors"],
        *authority_scopes["errors"],
    ]
    return {
        "schema": "https://schemas.aixem.org/documentation/document-relationship-audit/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": not errors,
        "rootLinkIntegrity": root_links,
        "repositoryAreaCoverage": repository_areas,
        "rootReachability": reachability,
        "sectionIndexCoverage": section_coverage,
        "currentReleaseCoherence": release_coherence,
        "authorityScopeReview": authority_scopes,
        "errors": errors,
    }


def load_path_migrations() -> dict[str, Any]:
    path = META / "path-migrations.yaml"
    data = load_yaml(path)
    errors = validate_json_schema(data, META / "schema" / "path-migrations.schema.json", path.relative_to(ROOT).as_posix())
    if errors:
        raise AixemDocsError("path migration registry invalid:\n" + "\n".join(errors))
    return data


def build_path_migration_index(documents: list[Document]) -> dict[str, Any]:
    by_id, _ = document_maps(documents)
    records = []
    for item in load_path_migrations().get("migrations", []):
        doc = by_id.get(str(item["document"]))
        records.append({
            **item,
            "fromSitePath": str(PurePosixPath(str(item["from"])[5:]).with_suffix(".html")),
            "toSitePath": str(PurePosixPath(str(item["to"])[5:]).with_suffix(".html")),
            "targetDigest": doc.sha256 if doc else None,
        })
    return {
        "schema": "https://schemas.aixem.org/documentation/path-migration-index/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "migrations": sorted(records, key=lambda value: (value["from"], value["to"])),
    }


def validate_path_migrations(documents: list[Document], *, require_redirects: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    by_id, _ = document_maps(documents)
    active_paths = {f"docs/{doc.rel}": doc for doc in documents}
    migrations = load_path_migrations().get("migrations", [])
    old_paths = [str(item.get("from", "")) for item in migrations]
    if len(old_paths) != len(set(old_paths)):
        errors.append("path migration registry contains duplicate prior paths")
    graph: dict[str, str] = {}
    for item in migrations:
        old = str(item.get("from", "")); new = str(item.get("to", "")); doc_id = str(item.get("document", ""))
        if old == new:
            errors.append(f"path migration source equals target: {old}")
        if old in active_paths:
            errors.append(f"prior path remains active: {old}")
        target = active_paths.get(new)
        if target is None:
            errors.append(f"path migration target is not canonical: {new}")
        elif target.id != doc_id:
            errors.append(f"path migration identity mismatch: {old} -> {new} declares {doc_id}, observed {target.id}")
        if doc_id not in by_id:
            errors.append(f"path migration references unknown document ID {doc_id}")
        graph[old] = new
        if require_redirects:
            old_site = SITE / PurePosixPath(old[5:]).with_suffix(".html")
            if not old_site.is_file():
                errors.append(f"site redirect missing for prior path {old}")
            elif str(PurePosixPath(new[5:]).with_suffix(".html")) not in old_site.read_text(encoding="utf-8"):
                errors.append(f"site redirect target mismatch for prior path {old}")
    for start in sorted(graph):
        seen: set[str] = set(); node = start
        while node in graph:
            if node in seen:
                errors.append(f"path migration cycle detected from {start}")
                break
            seen.add(node); node = graph[node]
    return {"valid": not errors, "migrations": len(migrations), "redirectsChecked": require_redirects, "errors": errors}


def audit_repository_documents(documents: list[Document] | None = None, *, require_redirects: bool = False) -> dict[str, Any]:
    """Classify, name-check, lifecycle-check, and inventory every repository Markdown file."""
    documents = documents or load_documents()
    policy = load_repository_document_policy()
    markdown_paths = _repository_markdown_paths()
    markdown_rels = [path.relative_to(ROOT).as_posix() for path in markdown_paths]
    inbound = _markdown_inbound_references(markdown_paths)
    machine_refs = _machine_path_references(markdown_rels)
    roles = policy["roles"]
    errors: list[str] = []
    warnings: list[str] = []
    doc_by_path = {f"docs/{doc.rel}": doc for doc in documents}
    nav = load_yaml(META / "navigation.yaml")
    nav_ids = {value for section in nav.get("sections", []) for value in [section.get("index"), *section.get("items", [])]}
    reserved = set(policy["reservedFilenames"])
    default_pattern = re.compile(str(policy["defaultFilenamePattern"]))

    planning = load_yaml(ROOT / "planning" / "index.yaml")
    errors.extend(validate_json_schema(planning, META / "schema" / "planning-index.schema.json", "planning/index.yaml"))
    registered_plans = {str(item.get("path", "")) for item in planning.get("plans", [])}
    planning_readme = (ROOT / "planning" / "README.md").read_text(encoding="utf-8")
    release_index_text = (ROOT / "validation" / "releases" / "README.md").read_text(encoding="utf-8")
    evidence_index_text = (ROOT / "validation" / "evidence" / "README.md").read_text(encoding="utf-8")

    entries: list[dict[str, Any]] = []
    role_counts: Counter[str] = Counter()
    for path, rel in zip(markdown_paths, markdown_rels):
        matches = [role for role in roles if _path_matches_role(rel, role)]
        if len(matches) != 1:
            errors.append(f"{rel}: expected exactly one document role, matched {[r['id'] for r in matches]}")
            role = {"id": "unknown", "lifecycle": "current", "status": "active", "humanAuthored": True, "discoverabilityOwner": "none"}
        else:
            role = matches[0]
        role_id = str(role["id"]); role_counts[role_id] += 1
        name = path.name
        allowed_special = set(role.get("allowedFilenames", []))
        if name in reserved and name not in allowed_special:
            errors.append(f"{rel}: reserved filename {name} is not allowed for role {role_id}")
        if name not in reserved:
            pattern = re.compile(str(role.get("filenamePattern", policy["defaultFilenamePattern"])))
            release_filename = role_id == "canonical-document" and rel.startswith("docs/releases/") and bool(re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+){0,2}\.md", name))
            if not pattern.fullmatch(name) and not release_filename:
                errors.append(f"{rel}: filename violates {role_id} naming policy")
        discoverable = True
        if role_id == "canonical-document":
            doc = doc_by_path.get(rel)
            discoverable = bool(doc and doc.id in nav_ids)
        elif role_id == "implementation-plan":
            discoverable = rel in registered_plans and rel.removeprefix("planning/") in planning_readme
        elif role_id == "validation-release-index":
            version = PurePosixPath(rel).parts[2]
            discoverable = f"{version}/README.md" in release_index_text
        elif role_id == "validation-report":
            index_path = path.parent / "README.md"
            discoverable = index_path.is_file() and f"({name})" in index_path.read_text(encoding="utf-8")
        elif role_id == "evidence-review":
            discoverable = f"(reviews/{name})" in evidence_index_text
        elif role_id == "verification-run-report":
            discoverable = (path.parent.parent / "summary.json").is_file() or (path.parent.parent / "summary.json").parent.is_dir()
        elif role_id == "evaluation-task":
            discoverable = (path.parent / "case.json").is_file() and (path.parent / "agent-task.json").is_file()
        elif role_id == "corpus-instruction":
            discoverable = (path.parent / "manifest.json").is_file()
        elif role_id == "evaluation-suite-document":
            discoverable = (path.parents[1] / "README.md").is_file() if path.name != "README.md" else True
        elif role_id == "example-local-instruction":
            discoverable = True
        if role.get("humanAuthored") and not discoverable:
            errors.append(f"{rel}: role-aware discoverability owner did not resolve")
        release = None
        parts = PurePosixPath(rel).parts
        if role_id in {"implementation-plan", "validation-report", "validation-release-index", "verification-run-report"}:
            release = next((part for part in parts if re.fullmatch(r"\d+\.\d+(?:\.\d+){1,2}", part)), None)
        doc = doc_by_path.get(rel)
        entries.append({
            "path": rel,
            "role": role_id,
            "lifecycle": role.get("lifecycle"),
            "status": role.get("status"),
            "humanAuthored": bool(role.get("humanAuthored")),
            "canonicalDocumentId": doc.id if doc else None,
            "release": release,
            "sourceOwner": role.get("discoverabilityOwner"),
            "discoverabilityOwner": role.get("discoverabilityOwner"),
            "discoverable": discoverable,
            "inboundDocumentRefs": inbound.get(rel, []),
            "machineRefs": machine_refs.get(rel, []),
            "bytes": path.stat().st_size,
            "digest": sha256_file(path),
        })

    root_observed = sorted(path.name for path in ROOT.glob("*.md"))
    root_allowed = sorted(policy["rootMarkdownAllowlist"])
    if root_observed != root_allowed:
        errors.append(f"root Markdown whitelist mismatch: observed={root_observed}, allowed={root_allowed}")
    plan_paths = {rel for rel, entry in zip(markdown_rels, entries) if entry["role"] == "implementation-plan"}
    if plan_paths != registered_plans:
        errors.append(f"planning registry mismatch: unregistered={sorted(plan_paths-registered_plans)}, missing={sorted(registered_plans-plan_paths)}")

    canonical_basenames: dict[str, list[str]] = defaultdict(list)
    for doc in documents:
        if PurePosixPath(doc.rel).name != "index.md":
            canonical_basenames[PurePosixPath(doc.rel).name].append(f"docs/{doc.rel}")
    for basename, paths in sorted(canonical_basenames.items()):
        if len(paths) > 1:
            errors.append(f"canonical basename collision {basename}: {', '.join(paths)}")
    for doc in documents:
        estimated = int(doc.meta["agent"]["estimated_tokens"])
        calculated = deterministic_token_estimate(doc.body)
        tolerance = max(64, int(calculated * 0.20))
        if abs(estimated - calculated) > tolerance:
            errors.append(f"docs/{doc.rel}: estimated_tokens {estimated} differs from deterministic estimate {calculated}")
        if doc.meta.get("domain") not in CONTROLLED_DOMAINS:
            errors.append(f"docs/{doc.rel}: uncontrolled domain {doc.meta.get('domain')}")
        if doc.meta.get("kind") not in CONTROLLED_KINDS:
            errors.append(f"docs/{doc.rel}: uncontrolled kind {doc.meta.get('kind')}")
        text = doc.path.read_text(encoding="utf-8").rstrip()
        if text.count(CANONICAL_FOOTER) != 1 or not text.endswith(CANONICAL_FOOTER):
            errors.append(f"docs/{doc.rel}: canonical footer is not unique and terminal")
        if PATCH_MARKER_RE.search(text):
            errors.append(f"docs/{doc.rel}: release patch append marker remains")

    migration_result = validate_path_migrations(documents, require_redirects=require_redirects)
    errors.extend(migration_result["errors"])
    relationship_result = build_document_relationship_audit(
        documents, entries=entries, markdown_paths=markdown_paths
    )
    errors.extend(relationship_result["errors"])
    inventory = {
        "schema": "https://schemas.aixem.org/documentation/repository-document-inventory/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "summary": {
            "markdownFiles": len(entries),
            "humanAuthored": sum(1 for item in entries if item["humanAuthored"]),
            "discoverable": sum(1 for item in entries if item["discoverable"]),
            "orphans": sum(1 for item in entries if item["humanAuthored"] and not item["discoverable"]),
            "unknownRoles": role_counts.get("unknown", 0),
            "byRole": dict(sorted(role_counts.items())),
        },
        "documents": entries,
    }
    return {
        "valid": not errors,
        "documents": len(entries),
        "humanAuthored": inventory["summary"]["humanAuthored"],
        "orphans": inventory["summary"]["orphans"],
        "unknownRoles": inventory["summary"]["unknownRoles"],
        "roles": inventory["summary"]["byRole"],
        "inventory": inventory,
        "pathMigrations": migration_result,
        "relationships": relationship_result,
        "errors": errors,
        "warnings": warnings,
    }

def validate_repository_english() -> dict[str, Any]:
    """Verify that shipped textual content follows the English-only release policy."""
    errors: list[str] = []
    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".wasm", ".bin", ".zip"}:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"VERSION", "Makefile", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        match = CJK_RE.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{rel}:{line}: English-only policy violation")
    return {"valid": not errors, "filesScanned": scanned, "errors": errors}


def validate_json_schema(instance: Any, schema_path: Path, label: str) -> list[str]:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        pointer = "/" + "/".join(str(p) for p in error.absolute_path)
        errors.append(f"{label}{pointer}: {error.message}")
    return errors


def resolve_markdown_link(doc: Document, target: str, by_path: dict[str, Document]) -> tuple[str | None, str | None]:
    split = urlsplit(target)
    if split.scheme or split.netloc or target.startswith("mailto:"):
        return None, None
    raw_path = unquote(split.path)
    fragment = unquote(split.fragment)
    if not raw_path:
        return doc.rel, fragment
    if raw_path.startswith("/"):
        return None, fragment
    base = PurePosixPath(doc.rel).parent
    normalized = PurePosixPath(os.path.normpath((base / raw_path).as_posix()))
    rel = normalized.as_posix()
    if rel.startswith("../") or rel == "..":
        # Site-only assets intentionally live outside canonical source.
        if "/assets/" in f"/{rel}":
            return None, fragment
        return rel, fragment
    if rel.endswith(".html"):
        rel = rel[:-5] + ".md"
    if raw_path.endswith("/"):
        rel = (normalized / "index.md").as_posix()
    return rel, fragment


def validate_documents(documents: list[Document], *, strict_links: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    by_id, by_path = document_maps(documents)
    schema_path = META / "schema" / "document-metadata.schema.json"
    requirement_defs: dict[str, tuple[Document, Requirement]] = {}
    alias_owner: dict[str, str] = {}

    for doc in documents:
        errors.extend(validate_json_schema(doc.meta, schema_path, doc.rel))
        if doc.meta.get("language") != "en":
            errors.append(f"{doc.rel}: language must be en")
        if CJK_RE.search(doc.path.read_text(encoding="utf-8")):
            errors.append(f"{doc.rel}: English-only policy violation (CJK/Hangul character found)")
        if not DOC_ID_RE.fullmatch(doc.id):
            errors.append(f"{doc.rel}: invalid document ID {doc.id}")
        if not doc.headings or doc.headings[0].level != 1:
            errors.append(f"{doc.rel}: first content heading must be level 1")
        elif doc.headings[0].text != str(doc.meta.get("title")):
            warnings.append(f"{doc.rel}: H1 differs from metadata title")
        for field in ("depends_on", "related"):
            for target in doc.meta.get(field, []):
                if target not in by_id:
                    errors.append(f"{doc.rel}: unresolved {field} document ID {target}")
                if target == doc.id:
                    errors.append(f"{doc.rel}: self reference in {field}")
        for term in [str(doc.meta.get("title", "")), *doc.meta.get("aliases", [])]:
            key = normalize_term(term)
            if not key:
                continue
            previous = alias_owner.get(key)
            if previous and previous != doc.id:
                warnings.append(f"alias collision {term!r}: {previous}, {doc.id}; generated resolver keeps explicit authored alias precedence")
            else:
                alias_owner[key] = doc.id
        meta_requirements = doc.meta.get("requirements", [])
        meta_requirement_ids = [str(item.get("id")) for item in meta_requirements]
        body_requirement_ids = [item.id for item in doc.requirements]
        if meta_requirement_ids != body_requirement_ids:
            errors.append(f"{doc.rel}: front-matter and body requirement IDs differ: metadata={meta_requirement_ids}, body={body_requirement_ids}")
        if meta_requirements and doc.meta.get("status") != "normative":
            errors.append(f"{doc.rel}: informative or non-normative document declares requirements")
        for req in doc.requirements:
            if doc.meta.get("status") != "normative":
                errors.append(f"{doc.rel}: requirement definition {req.id} is not in a normative document")
            if req.id in requirement_defs:
                previous = requirement_defs[req.id][0]
                errors.append(f"duplicate requirement definition {req.id}: {previous.rel}, {doc.rel}")
            requirement_defs[req.id] = (doc, req)
            if req.id not in doc.anchors:
                errors.append(f"{doc.rel}: requirement anchor missing for {req.id}")
            if not req.statement:
                errors.append(f"{doc.rel}: requirement {req.id} has no statement")

        if strict_links:
            text = doc.body
            targets = LINK_RE.findall(text) + RAW_LINK_RE.findall(text)
            for target in targets:
                if target.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
                    continue
                rel, fragment = resolve_markdown_link(doc, target, by_path)
                if rel is None:
                    continue
                target_doc = by_path.get(rel)
                if target_doc is None:
                    # Raw site assets are validated after publication.
                    if "assets/" in target:
                        continue
                    errors.append(f"{doc.rel}: unresolved internal link {target}")
                    continue
                if fragment and fragment not in target_doc.anchors:
                    errors.append(f"{doc.rel}: unresolved anchor {target_doc.rel}#{fragment}")

    nav = load_yaml(META / "navigation.yaml")
    errors.extend(validate_json_schema(nav, META / "schema" / "navigation.schema.json", "docs/_meta/navigation.yaml"))
    nav_ids: list[str] = []
    for section in nav.get("sections", []):
        for key in [section.get("index"), *section.get("items", [])]:
            if key not in by_id:
                errors.append(f"navigation: unresolved document ID {key}")
            else:
                nav_ids.append(key)
    missing_nav = sorted(set(by_id) - set(nav_ids))
    if missing_nav:
        errors.append("navigation: canonical documents missing from navigation: " + ", ".join(missing_nav))
    duplicate_nav = [k for k, count in Counter(nav_ids).items() if count > 1]
    if duplicate_nav:
        errors.append("navigation: documents listed more than once: " + ", ".join(sorted(duplicate_nav)))

    aliases = load_yaml(META / "aliases.yaml")
    for alias, target in aliases.get("aliases", {}).items():
        if target not in by_id:
            errors.append(f"aliases: {alias} resolves to unknown document {target}")

    conformance = load_yaml(META / "conformance.yaml")
    errors.extend(validate_json_schema(conformance, META / "schema" / "conformance-map.schema.json", "docs/_meta/conformance.yaml"))
    for rid in sorted(requirement_defs):
        if rid not in conformance.get("requirements", {}):
            errors.append(f"conformance: missing requirement mapping {rid}")
    for rid in conformance.get("requirements", {}):
        if rid not in requirement_defs:
            errors.append(f"conformance: mapping has no normative requirement definition {rid}")

    result = {
        "valid": not errors,
        "documents": len(documents),
        "normativeDocuments": sum(1 for d in documents if d.meta.get("status") == "normative"),
        "requirements": len(requirement_defs),
        "totalBytes": sum(d.bytes for d in documents),
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }
    return result


def load_routes() -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for path in sorted((META / "routes").glob("*.yaml")):
        route = load_yaml(path)
        route["_source"] = path.relative_to(ROOT).as_posix()
        routes.append(route)
    return routes


def validate_routes(routes: list[dict[str, Any]], documents: list[Document]) -> dict[str, Any]:
    """Validate simple document routes and ordered composite route chains."""
    errors: list[str] = []
    warnings: list[str] = []
    by_id, _ = document_maps(documents)
    schema_path = META / "schema" / "task-route.schema.json"
    route_ids: set[str] = set()
    route_by_id: dict[str, dict[str, Any]] = {}
    intents: dict[str, str] = {}
    aliases: dict[str, str] = {}
    validator_ids = set(load_yaml(META / "conformance.yaml").get("validators", {}))

    # Validate shape and collect identifiers before resolving composite children.
    for route in routes:
        source = route.pop("_source", None)
        errors.extend(validate_json_schema(route, schema_path, source or route.get("id", "route")))
        if source is not None:
            route["_source"] = source
        rid = str(route.get("id", ""))
        if rid in route_ids:
            errors.append(f"duplicate route ID {rid}")
        route_ids.add(rid)
        route_by_id[rid] = route
        intent = normalize_term(str(route.get("intent", "")))
        if intent in intents:
            errors.append(f"duplicate route intent {intent}: {intents[intent]}, {rid}")
        intents[intent] = rid
        for raw in [route.get("intent", ""), *route.get("aliases", [])]:
            key = normalize_term(str(raw))
            if not key:
                errors.append(f"{rid}: empty normalized alias {raw!r}")
                continue
            previous = aliases.get(key)
            if previous and previous != rid:
                errors.append(f"route alias collision {raw!r}: {previous}, {rid}")
            aliases[key] = rid
        for validator in route.get("validators", []):
            if validator not in validator_ids:
                errors.append(f"{rid}: unknown validator {validator}")
        writes = route.get("writes")
        if writes:
            for key in ("artifacts", "derived", "prohibited"):
                for pattern in writes.get(key, []):
                    normalized = str(pattern).replace("\\", "/")
                    if normalized.startswith("/") or ".." in normalized.split("/") or re.match(r"^[A-Za-z]:", normalized):
                        errors.append(f"{rid}: unsafe write-scope pattern {pattern!r}")
            for constraint in writes.get("constraints", []):
                pattern = str(constraint.get("pattern", "")).replace("\\", "/")
                if pattern.startswith("/") or ".." in pattern.split("/") or re.match(r"^[A-Za-z]:", pattern):
                    errors.append(f"{rid}: unsafe write-scope constraint {pattern!r}")
        for code in route.get("remediation", {}).get("acceptsDiagnostics", []):
            if not re.fullmatch(r"AIXEM-DIAG-[A-Z0-9-]+", str(code)):
                errors.append(f"{rid}: invalid accepted diagnostic code {code!r}")

    for route in routes:
        rid = route.get("id")
        kind = route.get("kind", "simple")
        budget = route.get("budget", {})
        if kind == "composite":
            writes = route.get("writes") or {}
            if writes.get("authority") or writes.get("artifacts"):
                errors.append(f"{rid}: composite routes must not declare broad authoritative write scope; child stage owns scope")
            stages = route.get("stages", [])
            orders = [stage.get("order") for stage in stages]
            if orders != list(range(1, len(stages) + 1)):
                errors.append(f"{rid}: composite stage order must be contiguous from 1")
            seen_children: set[str] = set()
            for stage in stages:
                child_id = stage.get("route")
                if child_id == rid:
                    errors.append(f"{rid}: composite route cannot include itself")
                if child_id not in route_by_id:
                    errors.append(f"{rid}: unresolved child route {child_id}")
                if child_id in seen_children:
                    warnings.append(f"{rid}: child route {child_id} appears more than once")
                seen_children.add(str(child_id))
            route["_computedBytes"] = 0
            route["_computedDocuments"] = 0
        else:
            steps = route.get("steps", [])
            orders = [step.get("order") for step in steps]
            if orders != list(range(1, len(steps) + 1)):
                errors.append(f"{rid}: step order must be contiguous from 1")
            if len(steps) > budget.get("max_documents", 0):
                errors.append(f"{rid}: {len(steps)} steps exceed max_documents budget")
            total_bytes = 0
            for step in steps:
                target = by_id.get(step.get("document"))
                if not target:
                    errors.append(f"{rid}: unresolved route document {step.get('document')}")
                    continue
                total_bytes += target.bytes
                section = step.get("section")
                if section and section not in target.anchors:
                    errors.append(f"{rid}: unresolved section {target.id}#{section}")
                if not step.get("required") and not step.get("condition"):
                    errors.append(f"{rid}: optional step {step.get('order')} requires a condition")
            if total_bytes > budget.get("max_bytes", 0):
                errors.append(f"{rid}: route reads {total_bytes} bytes and exceeds max_bytes")
            route["_computedBytes"] = total_bytes
            route["_computedDocuments"] = len(steps)

    # Composite routes may chain other composites, but cycles are forbidden.
    graph = {
        str(route.get("id")): [str(stage.get("route")) for stage in route.get("stages", [])]
        for route in routes if route.get("kind", "simple") == "composite"
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node) if node in stack else 0
            errors.append("composite route cycle: " + " -> ".join(stack[start:] + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for child in graph.get(node, []):
            if child in graph:
                visit(child)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return {"valid": not errors, "routes": len(routes), "aliases": len(aliases), "errors": errors, "warnings": sorted(set(warnings))}


def detect_dependency_cycles(documents: list[Document]) -> list[list[str]]:
    by_id, _ = document_maps(documents)
    graph = {doc.id: [x for x in doc.meta.get("depends_on", []) if x in by_id] for doc in documents}
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        if node in visiting:
            if node in stack:
                i = stack.index(node)
                cycles.append(stack[i:] + [node])
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for nxt in graph.get(node, []):
            dfs(nxt)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        dfs(node)
    unique = []
    seen = set()
    for cycle in cycles:
        key = tuple(cycle)
        if key not in seen:
            seen.add(key)
            unique.append(cycle)
    return unique


def build_document_index(documents: list[Document]) -> dict[str, Any]:
    previous_paths: dict[str, list[str]] = defaultdict(list)
    for migration in load_path_migrations().get("migrations", []):
        previous_paths[str(migration["document"])].append(str(migration["from"]))
    entries = []
    for doc in sorted(documents, key=lambda d: d.id):
        agent = dict(doc.meta.get("agent", {}))
        agent["computedEstimatedTokens"] = deterministic_token_estimate(doc.body)
        entries.append({
            "id": doc.id,
            "path": f"docs/{doc.rel}",
            "sitePath": doc.site_path,
            "title": doc.meta["title"],
            "status": doc.meta["status"],
            "version": str(doc.meta["version"]),
            "language": doc.meta["language"],
            "domain": doc.meta["domain"],
            "kind": doc.meta["kind"],
            "summary": doc.meta["summary"],
            "authority": doc.meta.get("authority", []),
            "aliases": doc.meta.get("aliases", []),
            "agent": agent,
            "previousPaths": sorted(previous_paths.get(doc.id, [])),
            "dependsOn": doc.meta.get("depends_on", []),
            "related": doc.meta.get("related", []),
            "headings": [dataclasses.asdict(h) for h in doc.headings],
            "requirements": [dataclasses.asdict(r) for r in doc.requirements],
            "bytes": doc.bytes,
            "digest": doc.sha256,
        })
    return {
        "schema": "https://schemas.aixem.org/documentation/document-index/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "documents": entries,
    }


def build_route_index(routes: list[dict[str, Any]], documents: list[Document]) -> dict[str, Any]:
    by_id, _ = document_maps(documents)
    exact: dict[str, str] = {}
    route_by_id = {route["id"]: route for route in routes}
    compiled = []
    for route in sorted(routes, key=lambda r: r["id"]):
        for term in [route["intent"], *route.get("aliases", [])]:
            exact[normalize_term(term)] = route["id"]
        kind = route.get("kind", "simple")
        base = {
            "id": route["id"],
            "kind": kind,
            "intent": route["intent"],
            "aliases": route.get("aliases", []),
            "summary": route["summary"],
            "budget": route["budget"],
            "completion": route["completion"],
            "expectedInputs": route.get("expected_inputs", []),
            "expectedOutputs": route["expected_outputs"],
            "validators": route["validators"],
            **({"writes": route["writes"]} if route.get("writes") is not None else {}),
            **({"remediation": route["remediation"]} if route.get("remediation") is not None else {}),
            "source": route.get("_source"),
            "taskPacket": f"docs/_meta/generated/task-packets/{route['id']}.json",
        }
        if kind == "composite":
            stages = []
            aggregate_documents = 0
            aggregate_bytes = 0
            for stage in route.get("stages", []):
                child = route_by_id[stage["route"]]
                aggregate_documents += int(child.get("_computedDocuments", len(child.get("steps", []))))
                aggregate_bytes += int(child.get("_computedBytes", 0))
                stages.append({
                    **stage,
                    "childIntent": child["intent"],
                    "childSource": child.get("_source"),
                    "taskPacket": f"docs/_meta/generated/task-packets/{child['id']}.json",
                    **({"writes": child["writes"]} if child.get("writes") is not None else {}),
                    **({"remediation": child["remediation"]} if child.get("remediation") is not None else {}),
                })
            base.update({
                "stages": stages,
                "computed": {
                    "documents": 0,
                    "bytes": 0,
                    "maxDepth": route["budget"]["max_depth"],
                    "aggregateStageDocuments": aggregate_documents,
                    "aggregateStageBytes": aggregate_bytes,
                    "budgetScope": "per-stage",
                },
            })
        else:
            steps = []
            total_bytes = 0
            for step in route["steps"]:
                doc = by_id[step["document"]]
                total_bytes += doc.bytes
                item = dict(step)
                item.update({"path": f"docs/{doc.rel}", "sitePath": doc.site_path, "bytes": doc.bytes, "digest": doc.sha256})
                steps.append(item)
            base.update({
                "steps": steps,
                "computed": {"documents": len(steps), "bytes": total_bytes, "maxDepth": route["budget"]["max_depth"]},
            })
        compiled.append(base)
    return {
        "schema": "https://schemas.aixem.org/documentation/route-index/1",
        "formatVersion": "1.2",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "policy": {"exactRouteFirst": True, "defaultMaxDocuments": 7, "defaultMaxBytes": 98304, "defaultMaxDepth": 3, "remoteFetch": "deny", "compositeBudgetScope": "per-stage"},
        "exact": dict(sorted(exact.items())),
        "routes": compiled,
    }


def build_task_packets(routes: list[dict[str, Any]], documents: list[Document]) -> tuple[dict[str, Any], dict[str, Path]]:
    """Compile compact, non-authoritative route execution packets."""
    packet_dir = GENERATED / "task-packets"
    if packet_dir.exists():
        shutil.rmtree(packet_dir)
    packet_dir.mkdir(parents=True, exist_ok=True)
    by_id, _ = document_maps(documents)
    route_by_id = {route["id"]: route for route in routes}
    packet_paths: dict[str, Path] = {}
    index_entries: list[dict[str, Any]] = []
    for route in sorted(routes, key=lambda item: item["id"]):
        source_path = ROOT / str(route.get("_source"))
        kind = route.get("kind", "simple")
        packet: dict[str, Any] = {
            "schema": "https://schemas.aixem.org/documentation/task-packet/1",
            "formatVersion": "1.0",
            "release": RELEASE_ID,
            "generatedAt": FIXED_TIME,
            "id": route["id"],
            "kind": kind,
            "intent": route["intent"],
            "summary": route["summary"],
            "source": route.get("_source"),
            "sourceDigest": sha256_file(source_path),
            "budget": route["budget"],
            "expectedInputs": route.get("expected_inputs", []),
            "expectedOutputs": route["expected_outputs"],
            "completion": route["completion"],
            "validators": route["validators"],
            **({"writes": route["writes"]} if route.get("writes") is not None else {}),
            **({"remediation": route["remediation"]} if route.get("remediation") is not None else {}),
            "authority": "derived-navigation-only",
        }
        if kind == "composite":
            packet["stages"] = [
                {
                    **stage,
                    "taskPacket": f"docs/_meta/generated/task-packets/{stage['route']}.json",
                    "sourceDigest": sha256_file(ROOT / str(route_by_id[stage["route"]].get("_source"))),
                    **({"writes": route_by_id[stage["route"]]["writes"]} if route_by_id[stage["route"]].get("writes") is not None else {}),
                    **({"remediation": route_by_id[stage["route"]]["remediation"]} if route_by_id[stage["route"]].get("remediation") is not None else {}),
                }
                for stage in route.get("stages", [])
            ]
        else:
            packet["documents"] = [
                {
                    "order": step["order"],
                    "document": step["document"],
                    "section": step.get("section"),
                    "purpose": step["purpose"],
                    "required": step["required"],
                    **({"condition": step["condition"]} if step.get("condition") else {}),
                    "path": f"docs/{by_id[step['document']].rel}",
                    "bytes": by_id[step["document"]].bytes,
                    "digest": by_id[step["document"]].sha256,
                }
                for step in route.get("steps", [])
            ]
        path = packet_dir / f"{route['id']}.json"
        write_json(path, packet)
        packet_paths[route["id"]] = path
        index_entries.append({"id": route["id"], "kind": kind, "path": path.relative_to(ROOT).as_posix(), "digest": sha256_file(path)})
    index = {
        "schema": "https://schemas.aixem.org/documentation/task-packet-index/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "packets": index_entries,
    }
    return index, packet_paths


def tokenize(value: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(value.lower()) if token not in STOPWORDS and len(token) > 1]


def build_inverted_index(documents: list[Document]) -> dict[str, Any]:
    postings: dict[str, dict[str, int]] = defaultdict(dict)
    records = []
    for doc in sorted(documents, key=lambda d: d.id):
        high = " ".join([doc.meta["title"], *doc.meta.get("aliases", []), *doc.meta.get("agent", {}).get("intents", [])])
        medium = " ".join([doc.meta["summary"], *[h.text for h in doc.headings]])
        low = re.sub(r"<[^>]+>", " ", doc.body)
        weights = Counter(tokenize(high))
        weights.update({k: v * 2 for k, v in Counter(tokenize(medium)).items()})
        weights.update(Counter(tokenize(low)))
        for token, weight in weights.items():
            postings[token][doc.id] = min(weight, 255)
        records.append({"id": doc.id, "title": doc.meta["title"], "path": f"docs/{doc.rel}", "sitePath": doc.site_path, "summary": doc.meta["summary"], "status": doc.meta["status"], "domain": doc.meta["domain"]})
    return {
        "schema": "https://schemas.aixem.org/documentation/inverted-index/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "documents": records,
        "terms": {term: [{"document": doc_id, "weight": weight} for doc_id, weight in sorted(items.items(), key=lambda x: (-x[1], x[0]))] for term, items in sorted(postings.items())},
    }


def build_dependency_graph(documents: list[Document]) -> dict[str, Any]:
    cycles = detect_dependency_cycles(documents)
    if cycles:
        raise AixemDocsError("dependency cycles: " + "; ".join(" -> ".join(c) for c in cycles))
    nodes = [{"id": d.id, "title": d.meta["title"], "status": d.meta["status"], "domain": d.meta["domain"], "path": f"docs/{d.rel}"} for d in sorted(documents, key=lambda x: x.id)]
    edges = []
    for doc in sorted(documents, key=lambda x: x.id):
        for target in doc.meta.get("depends_on", []):
            edges.append({"from": doc.id, "to": target, "type": "depends-on"})
        for target in doc.meta.get("related", []):
            edges.append({"from": doc.id, "to": target, "type": "related"})
    return {"schema": "https://schemas.aixem.org/documentation/dependency-graph/1", "formatVersion": "1.0", "release": RELEASE_ID, "generatedAt": FIXED_TIME, "acyclicDependencies": True, "nodes": nodes, "edges": edges}


def build_artifact_map(documents: list[Document]) -> dict[str, Any]:
    by_id, _ = document_maps(documents)
    authored = load_yaml(META / "artifact-ownership.yaml")
    errors = validate_json_schema(authored, META / "schema" / "artifact-ownership.schema.json", "docs/_meta/artifact-ownership.yaml")
    validators = set(load_yaml(META / "conformance.yaml").get("validators", {}))
    rules = []
    seen_authority: dict[str, str] = {}
    for item in authored.get("rules", []):
        owner = item["owner"]
        if owner not in by_id:
            errors.append(f"artifact ownership: unknown owner {owner} for {item['pattern']}")
        for validator in item.get("validators", []):
            if validator not in validators:
                errors.append(f"artifact ownership: unknown validator {validator} for {item['pattern']}")
        authority = item["authority"]
        # Multiple patterns may share a broad class, but duplicate exact authority is suspicious.
        if authority in seen_authority and seen_authority[authority] != item["pattern"]:
            errors.append(f"artifact ownership collision for authority {authority}: {seen_authority[authority]}, {item['pattern']}")
        seen_authority[authority] = item["pattern"]
        rules.append(item)
    if errors:
        raise AixemDocsError("\n".join(errors))
    return {"schema": "https://schemas.aixem.org/documentation/artifact-map/1", "formatVersion": "1.0", "release": RELEASE_ID, "generatedAt": FIXED_TIME, "rules": rules}


def build_traceability(documents: list[Document]) -> dict[str, Any]:
    by_id, _ = document_maps(documents)
    conformance = load_yaml(META / "conformance.yaml")
    definitions: dict[str, tuple[Document, Requirement]] = {}
    for doc in documents:
        for req in doc.requirements:
            definitions[req.id] = (doc, req)
    records = []
    errors = []
    for rid, (doc, req) in sorted(definitions.items()):
        mapping = conformance.get("requirements", {}).get(rid)
        if not mapping:
            errors.append(f"missing conformance mapping for {rid}")
            continue
        validators = mapping.get("validators", [])
        tests = mapping.get("tests", [])
        evidence = mapping.get("evidence", [])
        if not validators and not tests and mapping.get("status") not in {"not-applicable", "planned"}:
            errors.append(f"{rid} has no validator/test coverage")
        for validator in validators:
            if validator not in conformance.get("validators", {}):
                errors.append(f"{rid}: unknown validator {validator}")
        for test in tests:
            if test not in conformance.get("tests", {}):
                errors.append(f"{rid}: unknown test {test}")
        records.append({
            "id": rid,
            "title": req.title,
            "statement": req.statement,
            "source": {"document": doc.id, "path": f"docs/{doc.rel}", "anchor": req.anchor, "sitePath": f"{doc.site_path}#{req.anchor}", "line": req.line},
            "coverage": mapping,
        })
    for rid in conformance.get("requirements", {}):
        if rid not in definitions:
            errors.append(f"mapping without definition: {rid}")
    if errors:
        raise AixemDocsError("\n".join(errors))
    counts = Counter(record["coverage"]["status"] for record in records)
    return {
        "schema": "https://schemas.aixem.org/documentation/requirement-traceability/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "summary": {"requirements": len(records), "byStatus": dict(sorted(counts.items())), "silentGaps": 0},
        "validators": conformance.get("validators", {}),
        "tests": conformance.get("tests", {}),
        "requirements": records,
    }


def build_docs_manifest(documents: list[Document], products: dict[str, Path]) -> dict[str, Any]:
    files = []
    for doc in sorted(documents, key=lambda d: d.rel):
        files.append({"path": f"docs/{doc.rel}", "role": "canonical-document", "bytes": doc.bytes, "digest": doc.sha256})
    for path in sorted([p for p in META.rglob("*") if p.is_file() and "generated" not in p.relative_to(META).parts]):
        files.append({"path": path.relative_to(ROOT).as_posix(), "role": "authored-metadata", "bytes": path.stat().st_size, "digest": sha256_file(path)})
    for role, path in sorted(products.items()):
        if path.exists() and path.name != "manifest.json":
            files.append({"path": path.relative_to(ROOT).as_posix(), "role": role, "bytes": path.stat().st_size, "digest": sha256_file(path)})
    return {
        "schema": "https://schemas.aixem.org/documentation/manifest/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "canonicalRoot": "docs/",
        "fileCount": len(files),
        "files": files,
    }


def compile_generated() -> dict[str, Any]:
    GENERATED.mkdir(parents=True, exist_ok=True)
    documents = load_documents()
    docs_validation = validate_documents(documents)
    routes = load_routes()
    routes_validation = validate_routes(routes, documents)
    repository_audit = audit_repository_documents(documents)
    if not docs_validation["valid"] or not routes_validation["valid"] or not repository_audit["valid"]:
        errors = docs_validation["errors"] + routes_validation["errors"] + repository_audit["errors"]
        raise AixemDocsError("documentation validation failed:\n" + "\n".join(errors))
    products_data = {
        "document-index.json": build_document_index(documents),
        "route-index.json": build_route_index(routes, documents),
        "inverted-index.json": build_inverted_index(documents),
        "dependency-graph.json": build_dependency_graph(documents),
        "artifact-map.json": build_artifact_map(documents),
        "requirement-traceability.json": build_traceability(documents),
        "repository-document-inventory.json": repository_audit["inventory"],
        "document-relationship-audit.json": repository_audit["relationships"],
        "path-migration-index.json": build_path_migration_index(documents),
    }
    products: dict[str, Path] = {}
    for name, data in products_data.items():
        path = GENERATED / name
        write_json(path, data)
        products[name.removesuffix(".json")] = path
    packet_index, packet_paths = build_task_packets(routes, documents)
    packet_schema = META / "schema" / "task-packet.schema.json"
    packet_index_schema = META / "schema" / "task-packet-index.schema.json"
    packet_errors: list[str] = []
    for route_id, path in sorted(packet_paths.items()):
        packet_errors.extend(validate_json_schema(read_json(path), packet_schema, path.relative_to(ROOT).as_posix()))
    packet_errors.extend(validate_json_schema(packet_index, packet_index_schema, "docs/_meta/generated/task-packet-index.json"))
    if packet_errors:
        raise AixemDocsError("task packet validation failed:\n" + "\n".join(packet_errors))
    packet_index_path = GENERATED / "task-packet-index.json"
    write_json(packet_index_path, packet_index)
    products_data["task-packet-index.json"] = packet_index
    products["task-packet-index"] = packet_index_path
    for route_id, path in packet_paths.items():
        products[f"task-packet-{route_id}"] = path
    manifest = build_docs_manifest(documents, products)
    write_json(GENERATED / "manifest.json", manifest)
    return {
        "documents": documents,
        "routes": routes,
        "docsValidation": docs_validation,
        "routesValidation": routes_validation,
        "repositoryDocumentAudit": repository_audit,
        "products": products_data,
        "taskPackets": packet_index,
    }


def card_path_for(doc: Document) -> str:
    name = PurePosixPath(doc.rel).with_suffix("").as_posix().replace("/index", "/overview")
    return f"reference/cards/{name}.aixcard.json"


def build_legacy_reference() -> dict[str, Any]:
    if not GENERATED.exists() or not (GENERATED / "document-index.json").exists():
        compile_generated()
    documents = load_documents()
    routes = load_routes()
    by_id, _ = document_maps(documents)
    if REFERENCE.exists():
        shutil.rmtree(REFERENCE)
    (REFERENCE / "cards").mkdir(parents=True)
    (REFERENCE / "routes").mkdir(parents=True)
    (REFERENCE / "domains").mkdir(parents=True)
    (REFERENCE / "indexes").mkdir(parents=True)
    cards_by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    card_paths: dict[str, str] = {}
    for doc in sorted(documents, key=lambda d: d.id):
        path_rel = card_path_for(doc)
        card_paths[doc.id] = path_rel
        rules = [{"id": r.id, "level": "must", "text": r.statement} for r in doc.requirements]
        if not rules:
            rules = [{"id": f"{doc.id}.read", "level": "should", "text": str(doc.meta["summary"])}]
        card = {
            "schema": "https://schemas.aixem.org/reference/aixcard/1",
            "formatVersion": "1.0",
            "card": {
                "id": doc.id,
                "title": doc.meta["title"],
                "domain": doc.meta["domain"],
                "kind": doc.meta["kind"],
                "summary": doc.meta["summary"],
                "keywords": sorted(set([*doc.meta.get("aliases", []), *doc.meta.get("agent", {}).get("intents", []), doc.meta["title"]])),
                "aliases": doc.meta.get("aliases", []),
                "priority": {"critical": 1000, "high": 900, "normal": 500, "low": 100}.get(doc.meta.get("agent", {}).get("priority"), 500),
                "estimatedReadBytes": doc.bytes,
                "rules": rules,
                "sourceRefs": [{"path": f"docs/{doc.rel}", "documentId": doc.id, "authority": "canonical"}],
                "ownerArtifacts": [],
                "readNext": doc.meta.get("depends_on", []),
                "inputs": [],
                "outputs": [],
                "appliesTo": doc.meta.get("authority", []),
                "metadata": {"release": RELEASE_ID, "generatedAt": FIXED_TIME, "path": path_rel, "sourceDigest": doc.sha256},
            },
        }
        out = ROOT / path_rel
        write_json(out, card)
        cards_by_domain[doc.meta["domain"]].append({"id": doc.id, "title": doc.meta["title"], "path": path_rel, "summary": doc.meta["summary"]})

    route_entries = []
    route_by_id = {route["id"]: route for route in routes}
    for route in sorted(routes, key=lambda r: r["id"]):
        out_rel = f"reference/routes/{route['intent']}.aixroute.json"
        steps = []
        if route.get("kind", "simple") == "composite":
            for stage in route.get("stages", []):
                child = route_by_id[stage["route"]]
                steps.append({
                    "order": stage["order"],
                    "id": f"stage-{stage['order']}",
                    "purpose": stage["purpose"],
                    "read": [f"reference/routes/{child['intent']}.aixroute.json"],
                    "required": stage.get("required", True),
                    "produces": stage.get("outputs", []),
                    "exitCheck": stage["exit"],
                })
        else:
            for step in route["steps"]:
                doc = by_id[step["document"]]
                item = {
                    "order": step["order"],
                    "id": f"step-{step['order']}",
                    "purpose": step["purpose"],
                    "read": [card_paths[doc.id]],
                    "required": step["required"],
                    "produces": [],
                    "exitCheck": route["completion"][min(step["order"] - 1, len(route["completion"]) - 1)],
                }
                if step.get("condition"):
                    item["when"] = step["condition"]
                steps.append(item)
        payload = {
            "schema": "https://schemas.aixem.org/reference/aixroute/1",
            "formatVersion": "1.0",
            "route": {
                "id": route["intent"],
                "title": route["summary"],
                "intents": [route["intent"]],
                "aliases": route.get("aliases", []),
                "budget": {"maxDocuments": route["budget"]["max_documents"], "maxBytes": route["budget"]["max_bytes"], "maxDepth": route["budget"]["max_depth"], "fallbackDocuments": 2},
                "steps": steps,
                "conditionalReads": [],
                "stopConditions": route["completion"],
                "outputs": route["expected_outputs"],
                "validators": route["validators"],
                "metadata": {"release": RELEASE_ID, "generatedAt": FIXED_TIME, "exactRoutePreferred": True, "source": route.get("_source"), "kind": route.get("kind", "simple")},
            },
        }
        write_json(ROOT / out_rel, payload)
        route_entries.append({"intent": route["intent"], "route": out_rel, "aliases": route.get("aliases", []), "priority": 900})

    domain_entries = []
    for domain, cards in sorted(cards_by_domain.items()):
        rel = f"reference/domains/{domain}/index.aixdomain.json"
        payload = {
            "schema": "https://schemas.aixem.org/reference/aixdomain/1",
            "formatVersion": "1.0",
            "domain": {"id": domain, "title": domain.replace("-", " ").title(), "description": f"Generated canonical-document cards for the {domain} domain.", "cards": sorted(cards, key=lambda x: x["id"]), "metadata": {"release": RELEASE_ID, "generatedAt": FIXED_TIME}},
        }
        write_json(ROOT / rel, payload)
        domain_entries.append({"id": domain, "title": payload["domain"]["title"], "index": rel, "description": payload["domain"]["description"]})

    root_index = {
        "schema": "https://schemas.aixem.org/reference/aixref-root/1",
        "formatVersion": "1.0",
        "referenceRoot": {
            "id": "aixem.schematic-reference",
            "version": VERSION,
            "release": RELEASE_ID,
            "description": "Generated route-first compatibility reference compiled from canonical English documentation.",
            "policies": {"defaultMaxDocuments": 7, "defaultMaxBytes": 98304, "maxDepth": 3, "failClosedOnDigestMismatch": True, "exactRouteFirst": True, "remoteFetch": "deny"},
            "entrypoints": route_entries,
            "domains": domain_entries,
            "indexes": {
                "manifest": "reference/indexes/manifest.aixmanifest.json",
                "invertedIndex": "reference/indexes/inverted-index.json",
                "dependencyGraph": "reference/indexes/dependency-graph.json",
                "artifactMap": "reference/indexes/artifact-map.aixmap.json",
                "capabilities": "reference/indexes/capabilities.aixcap.json",
            },
            "metadata": {"generatedAt": FIXED_TIME, "canonicalRoot": "docs/", "generator": "tools/docs/build_legacy_reference.py"},
        },
    }
    write_json(REFERENCE / "index.aixref.json", root_index)
    shutil.copy2(GENERATED / "inverted-index.json", REFERENCE / "indexes/inverted-index.json")
    shutil.copy2(GENERATED / "dependency-graph.json", REFERENCE / "indexes/dependency-graph.json")
    artifact_map = read_json(GENERATED / "artifact-map.json")
    write_json(REFERENCE / "indexes/artifact-map.aixmap.json", {"schema": "https://schemas.aixem.org/reference/aixmap/1", "formatVersion": "1.0", "artifactMap": {"release": RELEASE_ID, "generatedAt": FIXED_TIME, "rules": artifact_map["rules"]}})
    capabilities = {
        "schema": "https://schemas.aixem.org/reference/aixcap/1", "formatVersion": "1.0",
        "capabilityIndex": {"release": RELEASE_ID, "generatedAt": FIXED_TIME, "capabilities": [
            {"id": r["intent"], "route": r["route"], "available": True} for r in route_entries
        ]},
    }
    write_json(REFERENCE / "indexes/capabilities.aixcap.json", capabilities)
    files = []
    for path in sorted(REFERENCE.rglob("*")):
        if path.is_file() and path.name != "manifest.aixmanifest.json":
            files.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "digest": sha256_file(path)})
    ref_manifest = {"schema": "https://schemas.aixem.org/reference/aixmanifest/1", "formatVersion": "1.0", "manifest": {"release": RELEASE_ID, "generatedAt": FIXED_TIME, "files": files}}
    write_json(REFERENCE / "indexes/manifest.aixmanifest.json", ref_manifest)
    return {"cards": len(documents), "routes": len(routes), "domains": len(cards_by_domain), "files": len(files) + 1}


class SiteRenderer(mistune.HTMLRenderer):
    def __init__(self) -> None:
        super().__init__(escape=False)
        self.used: dict[str, int] = {}

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        base = slugify(text)
        idx = self.used.get(base, 0)
        self.used[base] = idx + 1
        anchor = base if idx == 0 else f"{base}-{idx}"
        return f'<h{level} id="{html.escape(anchor)}">{text}<a class="heading-anchor" href="#{html.escape(anchor)}" aria-label="Link to this section">#</a></h{level}>\n'

    def link(self, text: str, url: str, title: str | None = None) -> str:
        split = urlsplit(url)
        if not split.scheme and split.path.endswith(".md"):
            url = split.path[:-3] + ".html" + (("#" + split.fragment) if split.fragment else "")
        title_attr = f' title="{html.escape(title)}"' if title else ""
        return f'<a href="{html.escape(url, quote=True)}"{title_attr}>{text}</a>'


def relative_url(from_site_path: str, to_site_path: str) -> str:
    start = PurePosixPath(from_site_path).parent.as_posix()
    return os.path.relpath(to_site_path, start=start or ".").replace(os.sep, "/")


def make_breadcrumbs(doc: Document, by_path: dict[str, Document]) -> list[tuple[str, str]]:
    crumbs = [("Documentation", relative_url(doc.site_path, "index.html"))]
    parts = PurePosixPath(doc.rel).parts
    if len(parts) > 1:
        section_rel = f"{parts[0]}/index.md"
        section = by_path.get(section_rel)
        if section and section.id != doc.id:
            crumbs.append((section.meta["title"], relative_url(doc.site_path, section.site_path)))
    if doc.rel != "index.md":
        crumbs.append((doc.meta["title"], ""))
    return crumbs


def clean_plaintext(markdown_body: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown_body, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[#*`_~>|\[\]()]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _site_css() -> str:
    return r''':root{
  --ink:#17231d;--muted:#637168;--line:#dce3df;--soft:#f4f7f5;--paper:#fff;
  --brand:#163f31;--brand-2:#225d48;--accent:#cde8d9;--code:#10221a;--warn:#855500;
  --danger:#8f2d2d;--max:860px
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);background:var(--paper);font:15.5px/1.68 Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
body.nav-open{overflow:hidden}
.skip{position:fixed;left:12px;top:-60px;z-index:70;padding:8px 12px;background:#fff;color:#000;border:2px solid var(--brand)}
.skip:focus{top:12px}
.topbar{height:58px;background:var(--brand);color:#fff;display:flex;align-items:center;position:sticky;top:0;z-index:50;border-bottom:1px solid #0c2d22}
.brand{display:flex;align-items:center;gap:11px;padding:0 22px;min-width:284px;font-weight:760;letter-spacing:.02em}
.brand-mark{display:grid;place-items:center;width:29px;height:29px;border:1px solid #86af99;font:700 11px/1 ui-monospace,monospace}
.brand small{display:block;color:#bcd4c6;font-size:10px;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.top-actions{margin-left:auto;display:flex;align-items:center;gap:10px;padding:0 18px}
.version{border:1px solid #628a76;padding:3px 8px;font:600 11px/1.4 ui-monospace,monospace}
.search-open,.menu-open{border:1px solid #6f9783;background:#0f3428;color:#fff;padding:7px 11px;cursor:pointer}
.menu-open{display:none}
kbd{font:10px/1.2 ui-monospace,monospace;border:1px solid #6f9783;padding:1px 4px;background:#173c30}
.layout{display:grid;grid-template-columns:284px minmax(0,1fr) 240px;min-height:calc(100vh - 58px)}
.sidebar{border-right:1px solid var(--line);background:#f8faf9;padding:18px 12px 40px;position:sticky;top:58px;height:calc(100vh - 58px);overflow:auto}
.sidebar h2{font-size:11px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted);padding:0 10px;margin:13px 0 5px}
.sidebar a{display:block;color:#33423a;text-decoration:none;padding:5px 10px;border-left:2px solid transparent;font-size:13px}
.sidebar a:hover{background:#edf3ef;color:#0f3d2e}
.sidebar a.active{background:#e2eee7;color:#0d3d2d;border-left-color:var(--brand-2);font-weight:700}
.sidebar .section-index{font-weight:660}
.content-wrap{min-width:0;padding:0 46px 72px}
.content{max-width:var(--max);margin:0 auto}
.breadcrumbs{display:flex;gap:7px;align-items:center;padding:20px 0 12px;color:var(--muted);font-size:12px;flex-wrap:wrap}
.breadcrumbs a{color:var(--brand-2);text-decoration:none}
.doc-head{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:28px}
.eyebrow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.badge{font:650 10px/1.4 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;border:1px solid var(--line);padding:2px 6px}
.badge.normative{background:#e3f1e9;border-color:#b6d4c3;color:#124d37}
.badge.informative{background:#f1f4f2;color:#536158}
.badge.draft{background:#fff6db;color:#765700}
.badge.deprecated{background:#fdeaea;border-color:#e3b2b2;color:var(--danger)}
.doc-id{font:11px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--muted)}
.doc-head h1{font-size:38px;line-height:1.18;letter-spacing:-.025em;margin:0 0 10px}
.lead{font-size:17px;line-height:1.65;color:#4f5e56;margin:0;max-width:740px}
.article h1:first-child{display:none}
.article h2{font-size:26px;line-height:1.3;margin:45px 0 13px;padding-top:6px;border-top:1px solid #edf0ee}
.article h3{font-size:19px;line-height:1.38;margin:31px 0 9px}
.article h4{font-size:16px;margin-top:24px}
.heading-anchor{opacity:0;text-decoration:none;color:#91a69b;font-size:.65em;margin-left:8px}
.article h2:hover .heading-anchor,.article h3:hover .heading-anchor,.heading-anchor:focus{opacity:1}
.article a{color:#126044;text-decoration-thickness:1px;text-underline-offset:2px}
.article code{font:13px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace;background:#edf2ef;padding:1px 4px;border-radius:2px}
.article pre{background:var(--code);color:#e3eee8;padding:17px 19px;overflow:auto;border:1px solid #284136}
.article pre code{background:none;padding:0;color:inherit}
.article blockquote{margin:22px 0;padding:8px 18px;border-left:3px solid #95b8a5;background:#f4f8f6;color:#45554c}
.article table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px}
.article th,.article td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
.article th{background:#f0f4f2}
.article img,.article iframe{max-width:100%}
.article iframe{width:100%;height:620px;border:1px solid #bac7c0;background:#fff}
.meta-panel{margin-top:48px;padding:17px;border:1px solid var(--line);background:var(--soft)}
.meta-panel h2{border:0;margin:0 0 10px;padding:0;font-size:15px}
.meta-list{display:grid;grid-template-columns:140px 1fr;gap:5px 12px;font-size:13px}
.meta-list dt{color:var(--muted)}
.meta-list dd{margin:0;min-width:0;overflow-wrap:anywhere}
.related{display:flex;flex-wrap:wrap;gap:6px}
.related a{background:#e9f1ec;padding:3px 7px;text-decoration:none}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:30px}
.pager a{border:1px solid var(--line);padding:12px;text-decoration:none;color:var(--ink)}
.pager a:last-child{text-align:right}
.pager small{display:block;color:var(--muted);text-transform:uppercase;font-size:10px;letter-spacing:.08em}
.toc{border-left:1px solid var(--line);padding:26px 18px;position:sticky;top:58px;height:calc(100vh - 58px);overflow:auto}
.toc h2{font-size:11px;text-transform:uppercase;letter-spacing:.11em;color:var(--muted);margin:0 0 9px}
.toc a{display:block;color:#59675f;text-decoration:none;font-size:12px;padding:3px 0}
.toc a.level-3{padding-left:11px}
.toc a:hover{color:#0e5139}
.footer{border-top:1px solid var(--line);margin-top:45px;padding-top:18px;color:var(--muted);font-size:12px}
.search-dialog{border:0;width:min(720px,92vw);padding:0;box-shadow:0 20px 80px #0005}
.search-dialog::backdrop{background:#07120dbb}
.search-box{padding:18px;background:#fff}
.search-box header{display:flex;gap:10px}
.search-box input{flex:1;padding:11px 12px;border:1px solid #8fa096;font-size:16px}
.search-box button{border:1px solid var(--line);background:#f4f6f5;padding:0 12px}
.results{max-height:65vh;overflow:auto;margin-top:10px}
.result{display:block;padding:11px;border-top:1px solid var(--line);text-decoration:none;color:var(--ink)}
.result:hover{background:#f2f7f4}
.result strong{display:block}
.result span{font-size:12px;color:var(--muted)}
.schema-browser{border:1px solid var(--line);padding:14px;background:#f7faf8;margin:20px 0}
.schema-catalog td:first-child{white-space:nowrap}
.schema-catalog code{font-size:11px}
.home-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px;margin:23px 0}
.home-card{border:1px solid var(--line);padding:17px;text-decoration:none!important;color:var(--ink)!important;background:#fff}
.home-card:hover{border-color:#759a86;background:#f5f9f7}
.home-card b{display:block;font-size:16px}
.home-card span{color:var(--muted);font-size:13px}
.req-backlink{font:11px/1.4 ui-monospace,monospace;background:#e8f3ed;padding:2px 5px;margin-left:5px}
.requirement-record{border-top:1px solid var(--line);padding-top:8px}
.requirement-record dl{display:grid;grid-template-columns:95px 1fr;gap:4px 10px}
.requirement-record dd{margin:0;overflow-wrap:anywhere}
@media(max-width:1120px){
  .layout{grid-template-columns:248px minmax(0,1fr)}
  .toc{display:none}.brand{min-width:248px}.content-wrap{padding:0 30px 60px}
}
@media(max-width:760px){
  .topbar{height:52px}.brand{min-width:0;padding:0 13px}.brand small,.version,kbd{display:none}.menu-open{display:inline-block}
  .layout{display:block}.content-wrap{padding:0 18px 50px}.doc-head h1{font-size:30px}.breadcrumbs{padding-top:15px}.article iframe{height:470px}.pager,.home-grid{grid-template-columns:1fr}.meta-list,.requirement-record dl{grid-template-columns:1fr}.meta-list dt,.requirement-record dt{font-weight:700}.top-actions{padding-right:10px;gap:6px}
  .sidebar{display:block;position:fixed;z-index:60;top:52px;left:0;width:min(88vw,320px);height:calc(100vh - 52px);transform:translateX(-105%);transition:transform .18s ease;box-shadow:10px 0 30px #0002}
  body.nav-open .sidebar{transform:translateX(0)}
  body.nav-open::after{content:"";position:fixed;z-index:55;inset:52px 0 0;background:#07120d88}
}
@media print{
  .topbar,.sidebar,.toc,.pager,.search-dialog{display:none!important}.layout{display:block}.content-wrap{padding:0}.content{max-width:none}.article a{color:#000}.heading-anchor{display:none}
}
'''


def _site_js() -> str:
    return r'''(()=>{
  const dialog=document.getElementById('search-dialog');
  const input=document.getElementById('site-search');
  const results=document.getElementById('search-results');
  const open=document.getElementById('search-open');
  const close=document.getElementById('search-close');
  const menu=document.getElementById('menu-open');
  const sidebar=document.getElementById('site-sidebar');
  const dataScript=[...document.scripts].find(s=>/\/search-data\.js(?:$|\?)/.test(s.src));
  const siteRoot=dataScript?new URL('../',dataScript.src):new URL('./',location.href);
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const resultUrl=url=>new URL(url,siteRoot).href;
  function run(){
    const q=input.value.trim().toLowerCase();
    const tokens=q.split(/[^a-z0-9+#.-]+/).filter(Boolean);
    if(!q){results.innerHTML='<div class="result"><span>Type an intent, title, document ID, requirement ID, or engineering term.</span></div>';return;}
    const scored=(window.AIXEM_SEARCH||[]).map(d=>{
      const text=(d.id+' '+d.title+' '+d.summary+' '+d.aliases.join(' ')+' '+d.intents.join(' ')+' '+d.headings.join(' ')+' '+d.requirements.join(' ')).toLowerCase();
      let score=0;
      for(const t of tokens){
        if(d.id.toLowerCase()===t)score+=40;
        if(d.title.toLowerCase().includes(t))score+=12;
        if(d.aliases.some(x=>x.toLowerCase().includes(t)))score+=10;
        if(d.intents.some(x=>x.toLowerCase().includes(t)))score+=10;
        if(text.includes(t))score+=2;
      }
      return [score,d];
    }).filter(x=>x[0]>0).sort((a,b)=>b[0]-a[0]||a[1].title.localeCompare(b[1].title)).slice(0,15);
    results.innerHTML=scored.length
      ?scored.map(([,d])=>`<a class="result" href="${esc(resultUrl(d.url))}"><strong>${esc(d.title)}</strong><span>${esc(d.id)} · ${esc(d.summary)}</span></a>`).join('')
      :'<div class="result"><span>No canonical document matched this query.</span></div>';
  }
  function closeNav(){document.body.classList.remove('nav-open');menu?.setAttribute('aria-expanded','false');}
  menu?.addEventListener('click',()=>{const next=!document.body.classList.contains('nav-open');document.body.classList.toggle('nav-open',next);menu.setAttribute('aria-expanded',String(next));});
  sidebar?.addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
  open?.addEventListener('click',()=>{dialog.showModal();input.focus();run();});
  close?.addEventListener('click',()=>dialog.close());
  input?.addEventListener('input',run);
  window.addEventListener('keydown',e=>{
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();dialog.showModal();input.focus();run();}
    if(e.key==='Escape'){if(dialog?.open)dialog.close();closeNav();}
  });
  document.addEventListener('click',e=>{if(document.body.classList.contains('nav-open')&&!sidebar?.contains(e.target)&&e.target!==menu)closeNav();});
})();'''

def build_site() -> dict[str, Any]:
    documents = load_documents()
    by_id, by_path = document_maps(documents)
    nav = load_yaml(META / "navigation.yaml")
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True)
    (SITE / "assets" / "data").mkdir(parents=True)
    (SITE / "assets" / "examples" / "controller").mkdir(parents=True)
    (SITE / "assets" / "schemas").mkdir(parents=True)
    (SITE / "assets" / "site.css").write_text(_site_css(), encoding="utf-8", newline="\n")
    (SITE / "assets" / "site.js").write_text(_site_js(), encoding="utf-8", newline="\n")
    for path in sorted(GENERATED.glob("*.json")):
        shutil.copy2(path, SITE / "assets" / "data" / path.name)
    example_render = ROOT / "examples" / "electronics-grid-controller" / "render"
    if example_render.exists():
        for path in example_render.glob("*"):
            if path.is_file():
                shutil.copy2(path, SITE / "assets" / "examples" / "controller" / path.name)

    # Flatten navigation and preserve authored order.
    ordered_ids: list[str] = []
    for section in nav["sections"]:
        ordered_ids.extend([section["index"], *section["items"]])
    ordered_docs = [by_id[x] for x in ordered_ids]
    prev_next = {doc.id: (ordered_docs[i - 1] if i else None, ordered_docs[i + 1] if i + 1 < len(ordered_docs) else None) for i, doc in enumerate(ordered_docs)}

    search_records = []
    for doc in documents:
        search_records.append({
            "id": doc.id,
            "title": doc.meta["title"],
            "summary": doc.meta["summary"],
            "aliases": doc.meta.get("aliases", []),
            "intents": doc.meta.get("agent", {}).get("intents", []),
            "headings": [h.text for h in doc.headings],
            "requirements": [r.id for r in doc.requirements],
            "url": doc.site_path,
        })
    (SITE / "assets" / "search-data.js").write_text("window.AIXEM_SEARCH=" + json.dumps(sorted(search_records, key=lambda x: x["id"]), ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")

    for doc in documents:
        renderer = SiteRenderer()
        markdown = mistune.create_markdown(renderer=renderer, plugins=["table", "strikethrough", "task_lists", "url"])
        article = markdown(doc.body)
        if doc.id == "AIXEM-CONF-REQUIREMENTS-001":
            trace = read_json(GENERATED / "requirement-traceability.json")
            catalog_parts = ['<section class="requirement-catalog"><h2 id="complete-requirement-catalog">Complete requirement catalog</h2><p>This generated catalog links every normative requirement to its canonical source, validator, test, and evidence record.</p>']
            for record in trace.get("requirements", []):
                coverage = record.get("coverage", {})
                validators = ", ".join(coverage.get("validators", [])) or "None"
                tests = ", ".join(coverage.get("tests", [])) or "None"
                evidence = ", ".join(coverage.get("evidence", [])) or "None"
                source = record.get("source", {})
                source_url = relative_url(doc.site_path, source.get("sitePath", "index.html"))
                catalog_parts.append(
                    f'<article class="requirement-record" id="{html.escape(record["id"])}"><h3>{html.escape(record["id"])} — {html.escape(record["title"])}</h3>'
                    f'<p>{html.escape(record["statement"])}</p><dl><dt>Source</dt><dd><a href="{html.escape(source_url)}">{html.escape(source.get("document", ""))}</a></dd>'
                    f'<dt>Validators</dt><dd><code>{html.escape(validators)}</code></dd><dt>Tests</dt><dd><code>{html.escape(tests)}</code></dd>'
                    f'<dt>Evidence</dt><dd><code>{html.escape(evidence)}</code></dd></dl></article>'
                )
            catalog_parts.append('</section>')
            article += ''.join(catalog_parts)
        if doc.id == "AIXEM-SPEC-SCHEMAS-001":
            rows = []
            schema_root = DOCS / "specifications" / "schemas"
            for schema_path in sorted(schema_root.rglob("*.json")):
                rel = schema_path.relative_to(schema_root).as_posix()
                data = json.loads(schema_path.read_text(encoding="utf-8"))
                target = f"specifications/schemas/{rel}.html"
                url = relative_url(doc.site_path, target)
                family = PurePosixPath(rel).parts[0] if len(PurePosixPath(rel).parts) > 1 else "root"
                rows.append(f'<tr><td>{html.escape(family)}</td><td><a href="{html.escape(url)}"><code>{html.escape(rel)}</code></a></td><td>{html.escape(str(data.get("title") or "Machine-readable contract"))}</td></tr>')
            article += '<section><h2 id="generated-schema-catalog">Generated schema catalog</h2><p>Each entry opens a readable static schema page and links to the exact JSON asset shipped with this release.</p><table class="schema-catalog"><thead><tr><th>Family</th><th>Schema</th><th>Title</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></section>'
        # Transform the canonical iframe source to the site-local asset path.
        article = article.replace('../../assets/examples/controller/workbench.html', relative_url(doc.site_path, 'assets/examples/controller/workbench.html'))
        # Add requirement traceability links after normative requirement headings.
        trace_url = relative_url(doc.site_path, "conformance/requirements.html")
        article = re.sub(r"(<h3[^>]*>\s*(AIXEM-REQ-[A-Z0-9-]+-\d{4})\b)", rf'\1 <a class="req-backlink" href="{trace_url}#\2">trace</a>', article)

        css = relative_url(doc.site_path, "assets/site.css")
        js = relative_url(doc.site_path, "assets/site.js")
        search_data = relative_url(doc.site_path, "assets/search-data.js")
        sidebar_parts = []
        for section in nav["sections"]:
            section_doc = by_id[section["index"]]
            sidebar_parts.append(f'<h2>{html.escape(section["title"])}</h2>')
            for target_id in [section["index"], *section["items"]]:
                target = by_id[target_id]
                cls = "active" if target.id == doc.id else ""
                if target.id == section_doc.id:
                    cls += " section-index"
                sidebar_parts.append(f'<a class="{cls.strip()}" href="{html.escape(relative_url(doc.site_path, target.site_path))}">{html.escape(target.meta["title"])}</a>')
        crumbs = make_breadcrumbs(doc, by_path)
        breadcrumb_html = "<span>›</span>".join(f'<a href="{html.escape(url)}">{html.escape(label)}</a>' if url else f'<span>{html.escape(label)}</span>' for label, url in crumbs)
        toc_items = [h for h in doc.headings if h.level in (2, 3)]
        toc_html = "".join(f'<a class="level-{h.level}" href="#{html.escape(h.anchor)}">{html.escape(h.text)}</a>' for h in toc_items) or '<span style="font-size:12px;color:#748078">Overview page</span>'
        related = [by_id[x] for x in doc.meta.get("related", []) if x in by_id]
        dependencies = [by_id[x] for x in doc.meta.get("depends_on", []) if x in by_id]
        related_html = "".join(f'<a href="{html.escape(relative_url(doc.site_path, d.site_path))}">{html.escape(d.meta["title"])}</a>' for d in related) or "None"
        dependency_html = "".join(f'<a href="{html.escape(relative_url(doc.site_path, d.site_path))}">{html.escape(d.meta["title"])}</a>' for d in dependencies) or "None"
        previous, nxt = prev_next.get(doc.id, (None, None))
        pager = "<div class=\"pager\">"
        pager += (f'<a href="{html.escape(relative_url(doc.site_path, previous.site_path))}"><small>Previous</small>{html.escape(previous.meta["title"])}</a>' if previous else '<span></span>')
        pager += (f'<a href="{html.escape(relative_url(doc.site_path, nxt.site_path))}"><small>Next</small>{html.escape(nxt.meta["title"])}</a>' if nxt else '<span></span>')
        pager += "</div>"
        intents = ", ".join(doc.meta.get("agent", {}).get("intents", [])) or "None"
        authority = ", ".join(doc.meta.get("authority", [])) or "Informative guidance"
        body_class = "home" if doc.rel == "index.md" else ""
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(doc.meta['summary'], quote=True)}"><meta name="aixem-document-id" content="{html.escape(doc.id)}"><meta name="aixem-release" content="{RELEASE_ID}"><title>{html.escape(doc.meta['title'])} — AIXEM Documentation</title><link rel="stylesheet" href="{css}"></head><body class="{body_class}"><a class="skip" href="#main">Skip to main content</a><header class="topbar"><div class="brand"><span class="brand-mark">AX</span><span>AIXEM<small>Schematic Reference Platform</small></span></div><div class="top-actions"><span class="version">v{VERSION}</span><button class="menu-open" id="menu-open" type="button" aria-controls="site-sidebar" aria-expanded="false">Menu</button><button class="search-open" id="search-open" type="button">Search <kbd>⌘K</kbd></button></div></header><div class="layout"><nav class="sidebar" id="site-sidebar" aria-label="Documentation navigation">{''.join(sidebar_parts)}</nav><main class="content-wrap" id="main"><div class="content"><div class="breadcrumbs">{breadcrumb_html}</div><header class="doc-head"><div class="eyebrow"><span class="badge {html.escape(doc.meta['status'])}">{html.escape(doc.meta['status'])}</span><span class="doc-id">{html.escape(doc.id)} · v{html.escape(str(doc.meta['version']))}</span></div><h1>{html.escape(doc.meta['title'])}</h1><p class="lead">{html.escape(doc.meta['summary'])}</p></header><article class="article">{article}</article><section class="meta-panel"><h2>Document metadata</h2><dl class="meta-list"><dt>Authority</dt><dd>{html.escape(authority)}</dd><dt>Agent intents</dt><dd>{html.escape(intents)}</dd><dt>Dependencies</dt><dd><span class="related">{dependency_html}</span></dd><dt>Related documents</dt><dd><span class="related">{related_html}</span></dd><dt>Canonical source</dt><dd><code>docs/{html.escape(doc.rel)}</code></dd><dt>Source digest</dt><dd><code>{html.escape(doc.sha256)}</code></dd></dl></section>{pager}<footer class="footer">AIXEM {VERSION} · Canonical English documentation · Generated from <code>docs/</code> without a runtime backend.</footer></div></main><aside class="toc" aria-label="On this page"><h2>On this page</h2>{toc_html}</aside></div><dialog class="search-dialog" id="search-dialog" aria-label="Documentation search"><div class="search-box"><header><input id="site-search" type="search" autocomplete="off" placeholder="Search documents, intents, IDs, and requirements"><button type="button" id="search-close">Close</button></header><div class="results" id="search-results"></div></div></dialog><script src="{search_data}"></script><script src="{js}"></script></body></html>'''
        out = SITE / doc.site_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")

    # Generate readable pages for JSON schemas while retaining source JSON under assets.
    schema_count = 0
    for schema_path in sorted((DOCS / "specifications" / "schemas").rglob("*.json")):
        rel = schema_path.relative_to(DOCS / "specifications" / "schemas")
        asset = SITE / "assets" / "schemas" / rel
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(schema_path, asset)
        out_rel = PurePosixPath("specifications/schemas") / PurePosixPath(rel.as_posix() + ".html")
        out = SITE / out_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        css = relative_url(out_rel.as_posix(), "assets/site.css")
        source_url = relative_url(out_rel.as_posix(), (PurePosixPath("assets/schemas") / PurePosixPath(rel.as_posix())).as_posix())
        back_url = relative_url(out_rel.as_posix(), "specifications/schemas/index.html")
        data = json.loads(schema_path.read_text(encoding="utf-8"))
        title = data.get("title") or rel.name
        page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — AIXEM Schema</title><link rel="stylesheet" href="{css}"></head><body><header class="topbar"><div class="brand"><span class="brand-mark">AX</span><span>AIXEM<small>Schema Reference</small></span></div></header><main class="content-wrap" style="padding-top:24px"><div class="content"><div class="breadcrumbs"><a href="{back_url}">Schema Catalog</a><span>›</span><span>{html.escape(rel.as_posix())}</span></div><header class="doc-head"><div class="eyebrow"><span class="badge normative">JSON Schema</span><span class="doc-id">{html.escape(str(data.get('$schema','')))}</span></div><h1>{html.escape(title)}</h1><p class="lead">Machine-readable contract distributed with AIXEM {VERSION}.</p></header><div class="schema-browser"><a href="{source_url}">Open raw JSON schema</a></div><article class="article"><pre><code>{html.escape(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))}</code></pre></article></div></main></body></html>'''
        out.write_text(page, encoding="utf-8", newline="\n")
        schema_count += 1

    # Generated reference explorer page.
    route_index = read_json(GENERATED / "route-index.json")
    route_sections: list[str] = []
    for route in route_index["routes"]:
        if route.get("kind", "simple") == "composite":
            step_items = "".join(
                f'<li><code>{html.escape(stage["route"])}</code> — {html.escape(stage["purpose"])}'
                f'<br><small>Exit: {html.escape(stage["exit"])}</small></li>'
                for stage in route.get("stages", [])
            )
            budget_text = (
                f'{route["computed"]["aggregateStageDocuments"]} aggregate stage documents · '
                f'{route["computed"]["aggregateStageBytes"]} aggregate bytes · '
                f'depth {route["computed"]["maxDepth"]} · budget enforced per stage'
            )
        else:
            step_items = "".join(
                f'<li><code>{html.escape(step["document"])}</code> — {html.escape(step["purpose"])}</li>'
                for step in route.get("steps", [])
            )
            budget_text = (
                f'{route["computed"]["documents"]} documents · '
                f'{route["computed"]["bytes"]} bytes · depth {route["computed"]["maxDepth"]}'
            )
        route_sections.append(
            f'<section><h2 id="{slugify(route["intent"])}">{html.escape(route["intent"])}</h2>'
            f'<p>{html.escape(route["summary"])}</p>'
            f'<p><b>Kind:</b> {html.escape(route.get("kind", "simple"))}<br><b>Budget:</b> {budget_text}</p>'
            f'<ol>{step_items}</ol></section>'
        )
    routes_markup = "".join(route_sections)
    explorer = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agent Route Explorer — AIXEM</title><link rel="stylesheet" href="assets/site.css"></head><body><header class="topbar"><div class="brand"><span class="brand-mark">AX</span><span>AIXEM<small>Agent Route Explorer</small></span></div></header><main class="content-wrap" style="padding-top:24px"><div class="content"><header class="doc-head"><div class="eyebrow"><span class="badge informative">Generated</span><span class="doc-id">{RELEASE_ID}</span></div><h1>Agent Route Explorer</h1><p class="lead">Compiled route-first plans derived from authored route YAML and canonical document metadata.</p></header><article class="article">{routes_markup}</article></div></main></body></html>'''
    (SITE / "reference-explorer.html").write_text(explorer, encoding="utf-8", newline="\n")

    redirect_count = 0
    for migration in build_path_migration_index(documents)["migrations"]:
        old_site = str(migration["fromSitePath"])
        new_site = str(migration["toSitePath"])
        out = SITE / old_site
        out.parent.mkdir(parents=True, exist_ok=True)
        relative_target = relative_url(old_site, new_site)
        redirect = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url={html.escape(relative_target, quote=True)}"><link rel="canonical" href="{html.escape(relative_target, quote=True)}"><title>Moved - AIXEM Documentation</title></head><body data-target="{html.escape(new_site, quote=True)}"><main><h1>Document moved</h1><p>The canonical document moved without changing identity. <a href="{html.escape(relative_target, quote=True)}">Open the current path</a>.</p></main></body></html>'''
        out.write_text(redirect, encoding="utf-8", newline="\n")
        redirect_count += 1
    return {"pages": len(documents) + schema_count + 1 + redirect_count, "canonicalPages": len(documents), "schemaPages": schema_count, "redirectPages": redirect_count, "assets": sum(1 for p in (SITE / "assets").rglob("*") if p.is_file())}


def validate_site() -> dict[str, Any]:
    """Validate generated HTML in two passes so every page is parsed exactly once."""
    errors: list[str] = []
    files = sorted(p for p in SITE.rglob("*.html") if p.is_file())
    site_root = SITE.resolve()
    soup_cache: dict[Path, BeautifulSoup] = {}
    anchor_cache: dict[Path, set[str]] = {}

    # Parse all pages first. Forward fragment references therefore reuse the same
    # soup/anchor record instead of reparsing a target before its normal turn.
    for page in files:
        resolved = page.resolve()
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        soup_cache[resolved] = soup
        anchor_cache[resolved] = {str(tag.get("id")) for tag in soup.find_all(attrs={"id": True})}
        if not soup.html or soup.html.get("lang") != "en":
            errors.append(f"{page.relative_to(ROOT)}: missing html lang=en")

    for page in files:
        soup = soup_cache[page.resolve()]
        for tag in soup.find_all(["a", "link", "script", "img", "iframe"]):
            attr = "href" if tag.name in {"a", "link"} else "src"
            value = tag.get(attr)
            if not value or value.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
                continue
            split = urlsplit(value)
            target = (page.parent / unquote(split.path)).resolve() if split.path else page.resolve()
            try:
                target.relative_to(site_root)
            except ValueError:
                errors.append(f"{page.relative_to(ROOT)}: path escapes site root: {value}")
                continue
            if split.path and not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing local target {value}")
                continue
            if split.fragment and target.suffix.lower() == ".html" and split.fragment not in anchor_cache.get(target, set()):
                errors.append(f"{page.relative_to(ROOT)}: missing fragment {value}")

    required = [SITE / "index.html", SITE / "assets/site.css", SITE / "assets/site.js", SITE / "assets/search-data.js", SITE / "reference-explorer.html"]
    for path in required:
        if not path.is_file():
            errors.append(f"missing site output {path.relative_to(ROOT)}")
    return {"valid": not errors, "pages": len(files), "errors": errors}


def route_query(query: str, *, allow_fallback: bool = True) -> dict[str, Any]:
    index = read_json(GENERATED / "route-index.json")
    normalized = normalize_term(query)
    route_id = index["exact"].get(normalized)
    if route_id:
        route = next(r for r in index["routes"] if r["id"] == route_id)
        return {"query": query, "normalized": normalized, "match": "exact", "route": route, "fallbackUsed": False}
    # Substring intent/alias match before document fallback.
    candidates = []
    q_tokens = set(tokenize(query))
    for route in index["routes"]:
        terms = [route["intent"], *route.get("aliases", [])]
        score = max((len(q_tokens.intersection(tokenize(term))) for term in terms), default=0)
        # A single generic token (for example, "visual") is too weak to
        # override document fallback. Exact normalized intent/alias matches
        # are handled above; token routing therefore requires two terms.
        if score >= 2:
            candidates.append((score, route["id"], route))
    if candidates:
        candidates.sort(key=lambda x: (-x[0], x[1]))
        if len(candidates) == 1 or candidates[0][0] > candidates[1][0]:
            return {"query": query, "normalized": normalized, "match": "route-token", "route": candidates[0][2], "fallbackUsed": False}
    if not allow_fallback:
        return {"query": query, "normalized": normalized, "match": "none", "route": None, "fallbackUsed": False}
    inverted = read_json(GENERATED / "inverted-index.json")
    scores: Counter[str] = Counter()
    for token in tokenize(query):
        for posting in inverted.get("terms", {}).get(token, []):
            scores[posting["document"]] += posting["weight"]
    docs = {d["id"]: d for d in inverted["documents"]}
    results = [{**docs[doc_id], "score": score} for doc_id, score in scores.most_common(7) if doc_id in docs]
    return {"query": query, "normalized": normalized, "match": "fallback" if results else "none", "route": None, "fallbackUsed": bool(results), "documents": results}


def validate_migration_inventory() -> dict[str, Any]:
    """Validate exact baseline coverage and target-resolution integrity."""
    inv = ROOT / "validation" / "evidence" / "pass-01" / "baseline-inventory.json"
    migration = ROOT / "validation" / "evidence" / "pass-01" / "migration-map.json"
    audit_path = ROOT / "validation" / "evidence" / "pass-01" / "declared-artifact-audit.json"
    errors: list[str] = []
    if not inv.is_file() or not migration.is_file() or not audit_path.is_file():
        return {"valid": False, "errors": ["baseline inventory, migration map, or declared-artifact audit missing"]}

    inv_data = read_json(inv)
    map_data = read_json(migration)
    audit = read_json(audit_path)
    inventory = inv_data.get("files", [])
    mappings = map_data.get("mappings", [])
    inv_paths = [str(x.get("path", "")) for x in inventory]
    map_paths = [str(x.get("source", "")) for x in mappings]
    inv_set = set(inv_paths)
    map_set = set(map_paths)

    if len(inv_paths) != len(inv_set):
        errors.append("baseline inventory contains duplicate paths")
    if len(map_paths) != len(map_set):
        errors.append("migration map contains duplicate source paths")
    if inv_set != map_set:
        errors.append(
            f"migration coverage mismatch: inventory={len(inv_set)}, mappings={len(map_set)}, "
            f"missing={len(inv_set-map_set)}, extra={len(map_set-inv_set)}"
        )
    if inv_data.get("summary", {}).get("files") != len(inventory):
        errors.append("baseline inventory summary file count mismatch")
    if map_data.get("summary", {}).get("mappings") != len(mappings):
        errors.append("migration map summary count mismatch")

    inventory_by_path = {str(item.get("path")): item for item in inventory}
    canonical_ids = {doc.id for doc in load_documents()}
    allowed_nonexistent_targets = {
        "docs/", "docs/specifications/", "docs/_meta/generated/", "reference/", "validation/",
        "tools/docs/", "examples/electronics-grid-controller/",
    }
    for item in inventory:
        rel = str(item.get("path", ""))
        digest = str(item.get("digest", ""))
        if not rel or PurePosixPath(rel).is_absolute() or ".." in PurePosixPath(rel).parts:
            errors.append(f"unsafe or empty inventory path {rel!r}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            errors.append(f"invalid inventory digest {rel}")
        if not isinstance(item.get("bytes"), int) or item.get("bytes", -1) < 0:
            errors.append(f"invalid inventory byte count {rel}")

    for item in mappings:
        source = str(item.get("source", ""))
        baseline_item = inventory_by_path.get(source)
        if not item.get("disposition"):
            errors.append(f"missing disposition {source}")
        if not item.get("rationale"):
            errors.append(f"missing rationale {source}")
        if not isinstance(item.get("target"), list):
            errors.append(f"target must be an array {source}")
            targets: list[str] = []
        else:
            targets = [str(x) for x in item.get("target", [])]
        ids = [str(x) for x in item.get("canonicalDocumentIds", [])]
        if not ids:
            errors.append(f"missing canonical document identity {source}")
        for document_id in ids:
            if document_id not in canonical_ids:
                errors.append(f"unknown canonical document ID {document_id} for {source}")
        if baseline_item and item.get("sourceDigest") != baseline_item.get("digest"):
            errors.append(f"source digest mismatch in migration map {source}")
        for target in targets:
            pure = PurePosixPath(target.split("#", 1)[0])
            if pure.is_absolute() or ".." in pure.parts:
                errors.append(f"unsafe migration target {target} for {source}")
                continue
            target_path = ROOT / pure.as_posix()
            if target in allowed_nonexistent_targets or target.endswith("/"):
                if not target_path.exists():
                    errors.append(f"migration target directory missing {target} for {source}")
            elif not target_path.exists():
                errors.append(f"migration target missing {target} for {source}")

    if not audit.get("valid") or not audit.get("targetResolutionValid"):
        errors.append("0.4 declared-artifact audit is not resolved in the 0.5 target")
    unresolved = audit.get("unresolvedInTarget", [])
    if unresolved:
        errors.append("unresolved historical declared artifacts: " + ", ".join(unresolved))
    for target in audit.get("resolvedInTarget", []):
        if not (ROOT / target).exists():
            errors.append(f"historical artifact marked resolved but absent: {target}")

    return {
        "valid": not errors,
        "inventoryFiles": len(inv_set),
        "mappedFiles": len(map_set),
        "canonicalIdsResolved": sum(bool(x.get("canonicalDocumentIds")) for x in mappings),
        "historicalDeclaredMissing": len(audit.get("missing", [])),
        "historicalResolvedInTarget": len(audit.get("resolvedInTarget", [])),
        "errors": errors,
    }


def validate_artifact_existence() -> dict[str, Any]:
    """Verify authored artifact declarations and ownership patterns against the package."""
    errors: list[str] = []
    checked = 0
    rules = load_yaml(META / "artifact-ownership.yaml").get("rules", [])
    all_paths = [p for p in ROOT.rglob("*") if p.exists() and "__pycache__" not in p.parts]
    rel_paths = [p.relative_to(ROOT).as_posix() for p in all_paths]

    def has_match(pattern: str) -> bool:
        base = pattern.split("#", 1)[0]
        if "/" not in base and not any(ch in base for ch in "*?["):
            # Registry identifiers are not file-system paths.
            return True
        if base.endswith("/"):
            return (ROOT / base.rstrip("/")).is_dir()
        if any(ch in base for ch in "*?["):
            return any(fnmatch.fnmatch(rel, base) for rel in rel_paths)
        return (ROOT / base).exists()

    for item in rules:
        pattern = str(item.get("pattern", ""))
        checked += 1
        if not has_match(pattern):
            errors.append(f"declared artifact has no package target: {pattern}")

    # Per-document exact owned/consumed paths are also release declarations.
    for doc in load_documents():
        artifacts = doc.meta.get("artifacts", {})
        for role in ("owns", "consumes"):
            for raw in artifacts.get(role, []):
                target = str(raw).split("#", 1)[0]
                if not target or any(ch in target for ch in "*?["):
                    continue
                if "/" not in target:
                    continue
                checked += 1
                if not (ROOT / target.rstrip("/")).exists():
                    errors.append(f"{doc.rel}: declared {role} artifact missing: {raw}")
    return {"valid": not errors, "declarationsChecked": checked, "errors": sorted(set(errors))}


def validate_requirement_evidence() -> dict[str, Any]:
    """Verify release evidence files for every normative requirement."""
    trace_path = GENERATED / "requirement-traceability.json"
    if not trace_path.is_file():
        return {"valid": False, "requirements": 0, "evidenceFiles": 0, "errors": ["requirement traceability index missing"]}
    trace = read_json(trace_path)
    errors: list[str] = []
    evidence_files = 0
    for record in trace.get("requirements", []):
        rid = record.get("id")
        coverage = record.get("coverage", {})
        evidence = coverage.get("evidence", [])
        if not evidence:
            errors.append(f"{rid}: no evidence path declared")
        for rel in evidence:
            evidence_files += 1
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"{rid}: evidence file missing: {rel}")
                continue
            try:
                data = read_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{rid}: invalid evidence JSON {rel}: {exc}")
                continue
            if data.get("requirement") != rid:
                errors.append(f"{rid}: evidence requirement mismatch in {rel}")
            if data.get("release") != RELEASE_ID:
                errors.append(f"{rid}: evidence release mismatch in {rel}")
            if data.get("status") != "pass":
                errors.append(f"{rid}: evidence status is not pass in {rel}")
            expected_validators = set(coverage.get("validators", []))
            observed_validators = set(data.get("validators", []))
            if not expected_validators.issubset(observed_validators):
                errors.append(f"{rid}: evidence omits mapped validators in {rel}")
            expected_tests = set(coverage.get("tests", []))
            observed_tests = set(data.get("tests", []))
            if not expected_tests.issubset(observed_tests):
                errors.append(f"{rid}: evidence omits mapped tests in {rel}")
            source = data.get("source", {})
            if source.get("document") != record.get("source", {}).get("document"):
                errors.append(f"{rid}: evidence source document mismatch in {rel}")
    return {
        "valid": not errors,
        "requirements": len(trace.get("requirements", [])),
        "evidenceFiles": evidence_files,
        "errors": errors,
    }


def validate_051_baseline_evidence() -> dict[str, Any]:
    """Verify the exact 0.5.0 baseline inventory and non-destructive 0.5.1 diff."""
    inventory_path = ROOT / "validation" / "evidence" / "pass-01" / "baseline-0.5.0-inventory.json"
    diff_path = ROOT / "validation" / "evidence" / "pass-01" / "baseline-0.5.0-diff.json"
    errors: list[str] = []
    if not inventory_path.is_file() or not diff_path.is_file():
        return {"valid": False, "errors": ["0.5.0 baseline inventory or diff is missing"]}
    try:
        inventory = read_json(inventory_path)
        diff = read_json(diff_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"invalid 0.5.0 baseline evidence: {exc}"]}
    accepted_baseline_releases = {
        "AIXEM-SRP-0.5.1-2026-08-11",
        "AIXEM-SRP-0.5.2-2026-08-11",
        RELEASE_ID,
    }
    if inventory.get("release") not in accepted_baseline_releases or diff.get("release") not in accepted_baseline_releases:
        errors.append("0.5.0 baseline evidence release is not a recognized preserved release")
    if inventory.get("baselineVersion") != "0.5.0" or diff.get("baselineVersion") != "0.5.0":
        errors.append("baseline version is not 0.5.0")
    files = inventory.get("files", [])
    if not files or inventory.get("summary", {}).get("files") != len(files):
        errors.append("baseline inventory file count mismatch")
    paths = [str(item.get("path", "")) for item in files]
    if len(paths) != len(set(paths)):
        errors.append("baseline inventory contains duplicate paths")
    for item in files:
        rel = str(item.get("path", ""))
        pure = PurePosixPath(rel)
        if not rel or pure.is_absolute() or ".." in pure.parts:
            errors.append(f"unsafe baseline path {rel!r}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(item.get("digest", ""))):
            errors.append(f"invalid baseline digest {rel}")
    if diff.get("valid") is not True:
        errors.append("baseline diff is not valid")
    if diff.get("removed"):
        errors.append("0.5.1 worktree removes files from the 0.5.0 baseline")
    return {
        "valid": not errors,
        "baselineFiles": len(files),
        "added": diff.get("summary", {}).get("added", 0),
        "modified": diff.get("summary", {}).get("modified", 0),
        "removed": diff.get("summary", {}).get("removed", 0),
        "errors": errors,
    }


def validate_authoring_readiness_evidence() -> dict[str, Any]:
    """Verify machine evidence for the 0.5.1 authoring-readiness target."""
    paths = {
        "contract": ROOT / "validation" / "evidence" / "pass-01" / "authoring-contract-closure.json",
        "authoring": ROOT / "validation" / "evidence" / "pass-02" / "authoring-validation.json",
        "evals": ROOT / "validation" / "agent-evals" / "results" / "0.5.1-fixture-results.json",
        "review": ROOT / "validation" / "evidence" / "pass-02" / "authoring-visual-review.json",
    }
    errors: list[str] = []
    data: dict[str, Any] = {}
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"authoring readiness evidence missing: {path.relative_to(ROOT)}")
            continue
        try:
            data[name] = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid authoring readiness evidence {path.relative_to(ROOT)}: {exc}")
    accepted_authoring_releases = {
        None,
        "AIXEM-SRP-0.5.1-2026-08-11",
        "AIXEM-SRP-0.5.2-2026-08-11",
        "AIXEM-SRP-0.5.5-2026-08-11",
        RELEASE_ID,
    }
    for name, value in data.items():
        if value.get("release") not in accepted_authoring_releases:
            errors.append(f"{name} evidence release is not a recognized preserved release")
        if value.get("valid") is not True:
            errors.append(f"{name} evidence is not valid")
    coverage = data.get("authoring", {}).get("referenceCoverage", {})
    examples = data.get("authoring", {}).get("examples", {})
    eval_summary = data.get("evals", {}).get("summary", {})
    if coverage and coverage.get("coverage") != 1.0:
        errors.append("authoring schema/reference coverage is not 100%")
    if examples and examples.get("examples", 0) < 8:
        errors.append("fewer than eight executable authoring examples were validated")
    if eval_summary:
        if eval_summary.get("tasks") != 8 or eval_summary.get("failed") != 0:
            errors.append("fixture-backed agent evaluation did not pass all eight tasks")
        if eval_summary.get("normalTaskRepositoryWideSearches") != 0:
            errors.append("agent evaluation used repository-wide search")
        if eval_summary.get("normalTaskRendererSourceInspections") != 0:
            errors.append("agent evaluation used renderer source inspection")
    return {
        "valid": not errors,
        "referenceCoverage": coverage.get("coverage"),
        "examples": examples.get("examples"),
        "evaluationTasks": eval_summary.get("tasks"),
        "errors": errors,
    }


def validate_refinement_pass_evidence() -> dict[str, Any]:
    """Verify all three 0.5.1 refinement passes have durable PASS evidence."""
    required = {
        "pass-01": [
            "validation/releases/0.5.1/pass-01-authoring-contract-closure.md",
            "validation/evidence/pass-01/baseline-0.5.0-inventory.json",
            "validation/evidence/pass-01/baseline-0.5.0-diff.json",
            "validation/evidence/pass-01/authoring-contract-closure.json",
            "validation/evidence/pass-01/schema-reference-coverage.json",
            "validation/evidence/pass-01/renderer-contract-validation.json",
        ],
        "pass-02": [
            "validation/releases/0.5.1/pass-02-agent-usability-and-drawing-quality.md",
            "validation/evidence/pass-02/authoring-validation.json",
            "validation/evidence/pass-02/route-corpus-results.json",
            "validation/evidence/pass-02/reproducibility.json",
            "validation/evidence/pass-02/authoring-visual-review.json",
            "validation/agent-evals/results/0.5.1-fixture-results.json",
        ],
        "pass-03": [
            "validation/releases/0.5.1/pass-03-release-integrity-and-regression.md",
            "validation/evidence/pass-03/site-validation.json",
            "validation/evidence/pass-03/render-determinism.json",
            "validation/evidence/pass-03/test-results.json",
            "validation/evidence/pass-03/visual-capture.json",
            "validation/evidence/pass-03/site-home-desktop.png",
            "validation/evidence/pass-03/site-home-narrow.png",
            "validation/evidence/pass-03/authoring-home-desktop.png",
            "validation/evidence/pass-03/authoring-passive-workbench.png",
            "validation/evidence/pass-03/authoring-ic-workbench.png",
            "validation/evidence/pass-03/authoring-junction-workbench.png",
        ],
    }
    errors: list[str] = []
    status: dict[str, Any] = {}
    for pass_id, members in required.items():
        members = [*members, f"validation/evidence/{pass_id}/hierarchical-verification.json"]
        pass_errors: list[str] = []
        for rel in members:
            path = ROOT / rel
            if not path.is_file():
                pass_errors.append(f"missing {rel}")
                continue
            if path.suffix == ".json":
                try:
                    data = read_json(path)
                    if data.get("valid") is False or data.get("successful") is False:
                        pass_errors.append(f"non-passing evidence: {rel}")
                except (OSError, json.JSONDecodeError) as exc:
                    pass_errors.append(f"invalid JSON evidence {rel}: {exc}")
            elif path.suffix == ".md" and "Status: **PASS**" not in path.read_text(encoding="utf-8"):
                pass_errors.append(f"pass report does not declare PASS: {rel}")
        status[pass_id] = {"valid": not pass_errors, "artifacts": len(members), "errors": pass_errors}
        errors.extend(f"{pass_id}: {error}" for error in pass_errors)
    return {"valid": not errors, "passes": status, "errors": errors}


def validate_test_results() -> dict[str, Any]:
    path = ROOT / "validation" / "test-results.json"
    if not path.is_file():
        return {"valid": False, "testsRun": 0, "errors": ["validation/test-results.json missing"]}
    data = read_json(path)
    errors: list[str] = []
    if not data.get("successful"):
        errors.append("repository conformance test run was not successful")
    if int(data.get("testsRun", 0)) < 8:
        errors.append(f"expected at least 8 tests, observed {data.get('testsRun', 0)}")
    if data.get("failures") or data.get("errors"):
        errors.append("test result contains failures or errors")
    return {"valid": not errors, "testsRun": data.get("testsRun", 0), "durationSeconds": data.get("durationSeconds"), "errors": errors}

def render_example() -> dict[str, Any]:
    script = ROOT / "implementation" / "schematic" / "render_project.py"
    project = ROOT / "examples" / "electronics-grid-controller" / "project.aixproj.json"
    proc = subprocess.run([sys.executable, str(script), str(project)], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        raise AixemDocsError(f"schematic render failed:\n{proc.stdout}\n{proc.stderr}")
    render_dir = project.parent / "render"
    digests = {p.name: sha256_file(p) for p in sorted(render_dir.iterdir()) if p.is_file()}
    return {"returnCode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip(), "digests": digests}


def check_render_determinism() -> dict[str, Any]:
    first = render_example()
    first_digests = first["digests"]
    second = render_example()
    second_digests = second["digests"]
    return {"valid": first_digests == second_digests, "first": first_digests, "second": second_digests, "stdout": second["stdout"]}


def generated_digest_map() -> dict[str, str]:
    roots = [GENERATED, REFERENCE, SITE]
    result = {}
    for base in roots:
        if base.exists():
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    result[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return result


def check_generated_freshness() -> dict[str, Any]:
    before = generated_digest_map()
    compile_generated()
    build_legacy_reference()
    build_site()
    after = generated_digest_map()
    changed = sorted(set(before) | set(after))
    changed = [p for p in changed if before.get(p) != after.get(p)]
    return {"valid": not changed, "files": len(after), "changed": changed}


def build_release_manifest() -> dict[str, Any]:
    """Create exact SHA-256 coverage for every shipped file except self-referential artifacts."""
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    excluded = {
        "release/manifest.json",
        "release/archive-verification.json",
    }
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in excluded or rel.startswith(".git/") or rel.endswith(".pyc") or "/__pycache__/" in f"/{rel}/":
            continue
        files.append({"path": rel, "bytes": path.stat().st_size, "digest": sha256_file(path)})
    manifest = {
        "schema": "https://schemas.aixem.org/release/manifest/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "version": VERSION,
        "generatedAt": FIXED_TIME,
        "canonicalDocumentationRoot": "docs/",
        "hashAlgorithm": "SHA-256",
        "excludedFromHashCoverage": sorted(excluded),
        "fileCount": len(files),
        "totalBytes": sum(x["bytes"] for x in files),
        "files": files,
    }
    write_json(RELEASE_DIR / "manifest.json", manifest)
    return manifest

def verify_release_manifest(root: Path = ROOT) -> dict[str, Any]:
    """Verify manifest metadata, member safety, digest coverage, and exact file-set closure."""
    path = root / "release" / "manifest.json"
    if not path.is_file():
        return {"valid": False, "errors": ["release/manifest.json missing"], "files": 0}
    manifest = read_json(path)
    errors: list[str] = []
    if manifest.get("release") != RELEASE_ID:
        errors.append(f"manifest release mismatch: {manifest.get('release')}")
    if manifest.get("version") != VERSION:
        errors.append(f"manifest version mismatch: {manifest.get('version')}")
    if manifest.get("hashAlgorithm") not in {None, "SHA-256"}:
        errors.append("manifest hashAlgorithm must be SHA-256")

    excluded = set(manifest.get("excludedFromHashCoverage", []))
    expected_excluded = {"release/manifest.json", "release/archive-verification.json"}
    if excluded != expected_excluded:
        errors.append(f"manifest exclusion set mismatch: {sorted(excluded)}")

    records = manifest.get("files", [])
    listed_paths = [str(item.get("path", "")) for item in records]
    if len(listed_paths) != len(set(listed_paths)):
        errors.append("manifest contains duplicate paths")
    for rel in listed_paths:
        pure = PurePosixPath(rel)
        if not rel or pure.is_absolute() or ".." in pure.parts:
            errors.append(f"unsafe manifest path {rel!r}")

    for item in records:
        rel = str(item.get("path", ""))
        target = root / rel
        if not target.is_file():
            errors.append(f"missing manifest member {rel}")
            continue
        if target.stat().st_size != item.get("bytes"):
            errors.append(f"byte count mismatch {rel}")
        digest = str(item.get("digest", ""))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            errors.append(f"invalid manifest digest format {rel}")
        elif sha256_file(target) != digest:
            errors.append(f"digest mismatch {rel}")

    actual_paths: set[str] = set()
    for target in root.rglob("*"):
        if not target.is_file():
            continue
        rel = target.relative_to(root).as_posix()
        if rel in excluded or rel.startswith(".git/") or rel.endswith(".pyc") or "/__pycache__/" in f"/{rel}/":
            continue
        actual_paths.add(rel)
    listed_set = set(listed_paths)
    if listed_set != actual_paths:
        missing = sorted(actual_paths - listed_set)
        extra = sorted(listed_set - actual_paths)
        if missing:
            errors.append("manifest omits shipped files: " + ", ".join(missing[:20]))
        if extra:
            errors.append("manifest lists non-shipped files: " + ", ".join(extra[:20]))

    if len(records) != manifest.get("fileCount"):
        errors.append("manifest fileCount mismatch")
    observed_total = sum(int(item.get("bytes", 0)) for item in records)
    if observed_total != manifest.get("totalBytes"):
        errors.append("manifest totalBytes mismatch")
    final_report = f"validation/releases/{VERSION}/final-validation.md"
    for required in ("AGENTS.md", "README.md", "docs/index.md", "site/index.html", final_report):
        if required not in listed_set:
            errors.append(f"required release member missing from manifest: {required}")
    return {"valid": not errors, "files": len(records), "totalBytes": observed_total, "errors": errors}

def run_full_validation(*, check_freshness: bool = True) -> dict[str, Any]:
    documents = load_documents()
    routes = load_routes()
    docs_result = validate_documents(documents)
    routes_result = validate_routes(routes, documents)
    repository_docs_result = audit_repository_documents(documents, require_redirects=SITE.exists())
    cycles = detect_dependency_cycles(documents)
    site_result = validate_site() if SITE.exists() else {"valid": False, "errors": ["site not built"], "pages": 0}
    migration_result = validate_migration_inventory()
    baseline_051_result = validate_051_baseline_evidence()
    authoring_result = validate_authoring_readiness_evidence()
    artifact_result = validate_artifact_existence()
    evidence_result = validate_requirement_evidence()
    passes_result = validate_refinement_pass_evidence()
    tests_result = validate_test_results()
    english_result = validate_repository_english()
    manifest_result = verify_release_manifest() if (RELEASE_DIR / "manifest.json").exists() else {"valid": False, "errors": ["release manifest not built"], "files": 0}
    trace = read_json(GENERATED / "requirement-traceability.json") if (GENERATED / "requirement-traceability.json").exists() else {"summary": {"silentGaps": 1}}
    freshness = check_generated_freshness() if check_freshness else {"valid": True, "skipped": True, "changed": []}
    checks = {
        "canonicalDocumentation": docs_result,
        "repositoryDocumentGovernance": repository_docs_result,
        "englishOnlyRelease": english_result,
        "taskRoutes": routes_result,
        "dependencyGraph": {"valid": not cycles, "cycles": cycles},
        "traceability": {"valid": trace.get("summary", {}).get("silentGaps") == 0, "summary": trace.get("summary", {})},
        "requirementEvidence": evidence_result,
        "artifactExistence": artifact_result,
        "staticSite": site_result,
        "legacyMigrationCoverage": migration_result,
        "baseline050Inventory": baseline_051_result,
        "agentAuthoringReadiness": authoring_result,
        "threeRefinementPasses": passes_result,
        "repositoryTests": tests_result,
        "generatedFreshness": freshness,
        "releaseManifest": manifest_result,
    }
    valid = all(bool(value.get("valid")) for value in checks.values())
    return {
        "schema": "https://schemas.aixem.org/validation/release-validation/1",
        "formatVersion": "1.0",
        "release": RELEASE_ID,
        "generatedAt": FIXED_TIME,
        "valid": valid,
        "summary": {
            "canonicalDocuments": docs_result.get("documents", 0),
            "repositoryMarkdown": repository_docs_result.get("documents", 0),
            "documentOrphans": repository_docs_result.get("orphans", 0),
            "normativeDocuments": docs_result.get("normativeDocuments", 0),
            "requirements": docs_result.get("requirements", 0),
            "routes": routes_result.get("routes", 0),
            "sitePages": site_result.get("pages", 0),
            "testsRun": tests_result.get("testsRun", 0),
            "manifestFiles": manifest_result.get("files", 0),
        },
        "checks": checks,
    }

def deterministic_zip(source_root: Path, output: Path) -> dict[str, Any]:
    """Create a one-root ZIP with fixed timestamps, stable order, and deterministic POSIX modes."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    epoch = (2026, 8, 12, 0, 0, 0)
    base_name = source_root.name
    files = [
        p
        for p in sorted(source_root.rglob("*"))
        if p.is_file()
        and ".git" not in p.parts
        and "__pycache__" not in p.parts
        and not p.name.endswith(".pyc")
    ]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            arcname = f"{base_name}/{path.relative_to(source_root).as_posix()}"
            info = zipfile.ZipInfo(arcname, date_time=epoch)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            executable = bool(path.stat().st_mode & 0o111)
            if not executable:
                try:
                    executable = path.read_bytes()[:2] == b"#!"
                except OSError:
                    executable = False
            mode = 0o100755 if executable else 0o100644
            info.external_attr = (mode & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        members = archive.namelist()
        duplicates = [name for name, count in Counter(members).items() if count > 1]
    if bad:
        raise AixemDocsError(f"ZIP integrity failure at {bad}")
    if duplicates:
        raise AixemDocsError("ZIP contains duplicate members: " + ", ".join(duplicates))
    return {"path": str(output), "bytes": output.stat().st_size, "digest": sha256_file(output), "members": len(members), "sourceFiles": len(files)}

def verify_archive(archive_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    names: list[str] = []
    if not archive_path.is_file():
        return {"valid": False, "archive": archive_path.name, "bytes": 0, "digest": None, "members": 0, "errors": ["archive does not exist"]}
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"container integrity failure: {bad}")
        names = archive.namelist()
        duplicates = [name for name, count in Counter(names).items() if count > 1]
        if duplicates:
            errors.append("duplicate archive members: " + ", ".join(duplicates))
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts or not pure.parts:
                errors.append(f"unsafe archive member: {name}")
        top_names = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
        if len(top_names) != 1:
            errors.append(f"archive must contain one top-level directory, observed {sorted(top_names)}")
        if not errors:
            top = next(iter(top_names))
            with tempfile.TemporaryDirectory(prefix="aixem-archive-") as tmp:
                archive.extractall(tmp)
                extracted = Path(tmp) / top
                result = verify_release_manifest(extracted)
                if not result["valid"]:
                    errors.extend(result["errors"])
                required = [
                    extracted / "AGENTS.md",
                    extracted / "site" / "index.html",
                    extracted / "validation" / "releases" / VERSION / "final-validation.md",
                ]
                for target in required:
                    if not target.is_file():
                        errors.append(f"required extracted member missing: {target.relative_to(extracted)}")
    return {"valid": not errors, "archive": archive_path.name, "bytes": archive_path.stat().st_size, "digest": sha256_file(archive_path), "members": len(names), "errors": errors}


def command_audit_repository_docs(args: argparse.Namespace) -> int:
    result = audit_repository_documents(require_redirects=args.require_redirects)
    output = {key: value for key, value in result.items() if key != "inventory"}
    print(canonical_json(output), end="")
    return 0 if result["valid"] else 2

def command_build_all(_: argparse.Namespace) -> int:
    compiled = compile_generated()
    reference = build_legacy_reference()
    site = build_site()
    print(json.dumps({"documents": len(compiled["documents"]), "routes": len(compiled["routes"]), "reference": reference, "site": site}, indent=2))
    return 0


def command_validate_docs(_: argparse.Namespace) -> int:
    result = validate_documents(load_documents())
    print(canonical_json(result), end="")
    return 0 if result["valid"] else 2


def command_build_index(_: argparse.Namespace) -> int:
    compile_generated()
    print(GENERATED / "document-index.json")
    return 0


def command_build_routes(_: argparse.Namespace) -> int:
    documents = load_documents(); routes = load_routes(); result = validate_routes(routes, documents)
    if not result["valid"]:
        print(canonical_json(result), file=sys.stderr); return 2
    write_json(GENERATED / "route-index.json", build_route_index(routes, documents))
    print(GENERATED / "route-index.json")
    return 0


def command_build_graphs(_: argparse.Namespace) -> int:
    documents = load_documents()
    write_json(GENERATED / "dependency-graph.json", build_dependency_graph(documents))
    write_json(GENERATED / "artifact-map.json", build_artifact_map(documents))
    print(GENERATED / "dependency-graph.json")
    return 0


def command_build_traceability(_: argparse.Namespace) -> int:
    write_json(GENERATED / "requirement-traceability.json", build_traceability(load_documents()))
    print(GENERATED / "requirement-traceability.json")
    return 0


def command_build_manifest(_: argparse.Namespace) -> int:
    manifest = build_release_manifest()
    print(json.dumps({"files": manifest["fileCount"], "bytes": manifest["totalBytes"]}, indent=2))
    return 0


def command_build_reference(_: argparse.Namespace) -> int:
    print(json.dumps(build_legacy_reference(), indent=2)); return 0


def command_build_site(_: argparse.Namespace) -> int:
    print(json.dumps(build_site(), indent=2)); return 0


def command_query(args: argparse.Namespace) -> int:
    print(canonical_json(route_query(args.query)), end=""); return 0


def command_check_release(args: argparse.Namespace) -> int:
    result = run_full_validation(check_freshness=not args.no_freshness)
    print(canonical_json(result), end="")
    return 0 if result["valid"] else 2


def command_verify_archive(args: argparse.Namespace) -> int:
    result = verify_archive(args.archive.resolve())
    print(canonical_json(result), end="")
    return 0 if result["valid"] else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    commands = {
        "build-all": command_build_all,
        "validate-docs": command_validate_docs,
        "build-index": command_build_index,
        "build-routes": command_build_routes,
        "build-graphs": command_build_graphs,
        "build-traceability": command_build_traceability,
        "build-manifest": command_build_manifest,
        "build-reference": command_build_reference,
        "build-site": command_build_site,
    }
    for name, func in commands.items():
        p = sub.add_parser(name); p.set_defaults(func=func)
    p = sub.add_parser("audit-repository-docs"); p.add_argument("--require-redirects", action="store_true"); p.set_defaults(func=command_audit_repository_docs)
    p = sub.add_parser("query-route"); p.add_argument("query"); p.set_defaults(func=command_query)
    p = sub.add_parser("check-release"); p.add_argument("--no-freshness", action="store_true"); p.set_defaults(func=command_check_release)
    p = sub.add_parser("verify-archive"); p.add_argument("archive", type=Path); p.set_defaults(func=command_verify_archive)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (AixemDocsError, OSError, ValueError, KeyError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
