"""AIXEM 0.5.9 deterministic authoring-integrity helpers.

This module hardens *new authoring* without changing the core AIXEM schema
URIs.  It validates the canonical project-library path, component-level part
provenance, semantic component identity, Pin Electrical Semantics Profile 1,
source-bound review evidence, bounded electrical compatibility, grid/profile
coherence, and separately reported validation claims.

The module never mutates authoritative source artifacts and never claims full
ERC, simulation correctness, voltage safety, timing correctness, or production
readiness.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
import math
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlsplit

LOWER_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LIBRARY_FILENAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.aixlib\.json$")
SYMBOL_FILENAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.aixsym\.json$")
ALLOWED_LIBRARY_DOMAINS = frozenset({"electronics", "architecture"})
PART_PROVENANCE_STATUSES = frozenset({"datasheet-backed", "generic-template", "placeholder"})
PIN_SEMANTICS_PROFILE = "aixem-pin-semantics-1"
PIN_SIGNAL_CLASSES = frozenset({"analog", "digital", "mixed-signal", "power", "ground", "reference", "rf", "unspecified"})
PIN_POLARITIES = frozenset({"unspecified", "active-high", "active-low", "positive", "negative"})
DIFFERENTIAL_MEMBERS = frozenset({"positive", "negative"})
COMPATIBILITY_OUTCOMES = frozenset({"PASS", "WARN", "ERROR", "NOT_EVALUATED"})

# Diagnostic codes are stable public identifiers.  Rich agent diagnostics are
# registered in implementation.agent.diagnostics; these compact issues remain
# usable by focused validators without importing the agent subsystem.
DIAG_LIBRARY_PATH_NONCANONICAL = "AIXEM-DIAG-LIBRARY-PATH-NONCANONICAL"
DIAG_LIBRARY_DOMAIN_UNKNOWN = "AIXEM-DIAG-LIBRARY-DOMAIN-UNKNOWN"
DIAG_LIBRARY_NAME_INVALID = "AIXEM-DIAG-LIBRARY-NAME-INVALID"
DIAG_LIBRARY_PART_SOURCE_REQUIRED = "AIXEM-DIAG-LIBRARY-PART-SOURCE-REQUIRED"
DIAG_LIBRARY_PART_PLACEHOLDER_UNDECLARED = "AIXEM-DIAG-LIBRARY-PART-PLACEHOLDER-UNDECLARED"
DIAG_LIBRARY_PART_PROVENANCE_INVALID = "AIXEM-DIAG-LIBRARY-PART-PROVENANCE-INVALID"
DIAG_LIBRARY_COMPONENT_SEMANTIC_CLONE = "AIXEM-DIAG-LIBRARY-COMPONENT-SEMANTIC-CLONE"
DIAG_LIBRARY_PART_MINIMUM_ATTRIBUTES_MISSING = "AIXEM-DIAG-LIBRARY-PART-MINIMUM-ATTRIBUTES-MISSING"
DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING = "AIXEM-DIAG-LIBRARY-PART-PINOUT-REVIEW-MISSING"
DIAG_LIBRARY_PART_INTENT_REVIEW_INCOMPLETE = "AIXEM-DIAG-LIBRARY-PART-INTENT-REVIEW-INCOMPLETE"
DIAG_LAYOUT_GRID_PROFILE_MISMATCH = "AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH"
DIAG_PIN_SEMANTICS_PROFILE_INVALID = "AIXEM-DIAG-PIN-SEMANTICS-PROFILE-INVALID"
DIAG_PIN_SIGNAL_CLASS_INVALID = "AIXEM-DIAG-PIN-SIGNAL-CLASS-INVALID"
DIAG_PIN_FUNCTION_TAG_INVALID = "AIXEM-DIAG-PIN-FUNCTION-TAG-INVALID"
DIAG_PIN_POLARITY_INCONSISTENT = "AIXEM-DIAG-PIN-POLARITY-INCONSISTENT"
DIAG_PIN_DIFFERENTIAL_PAIR_INCOMPLETE = "AIXEM-DIAG-PIN-DIFFERENTIAL-PAIR-INCOMPLETE"
DIAG_PIN_ALTERNATE_FUNCTION_INVALID = "AIXEM-DIAG-PIN-ALTERNATE-FUNCTION-INVALID"
DIAG_PIN_SOURCE_REVIEW_INCOMPLETE = "AIXEM-DIAG-PIN-SOURCE-REVIEW-INCOMPLETE"
DIAG_PIN_NOCONNECT_CONTRADICTION = "AIXEM-DIAG-PIN-NOCONNECT-CONTRADICTION"
DIAG_ERC_OUTPUT_CONFLICT = "AIXEM-DIAG-ERC-OUTPUT-CONFLICT"
DIAG_ERC_POWER_OUTPUT_CONFLICT = "AIXEM-DIAG-ERC-POWER-OUTPUT-CONFLICT"
DIAG_ERC_CONNECTED_NOCONNECT = "AIXEM-DIAG-ERC-CONNECTED-NOCONNECT"
DIAG_ERC_INPUT_ONLY = "AIXEM-DIAG-ERC-INPUT-ONLY"
DIAG_ERC_UNCERTAIN_TOPOLOGY = "AIXEM-DIAG-ERC-UNCERTAIN-TOPOLOGY"


@dataclass(frozen=True)
class IntegrityIssue:
    """One deterministic authoring-integrity finding."""

    code: str
    message: str
    severity: str = "error"
    path: str = ""
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
            "evidence": dict(self.evidence),
        }


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def semantic_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool) and math.isfinite(float(value))


def _as_decimal(value: Any, *, field_name: str) -> Decimal:
    if not _is_finite_number(value):
        raise ValueError(f"{field_name} must be a finite number")
    return Decimal(str(value))


def ceil_to_grid(value: float | int | Decimal, grid: float | int | Decimal) -> float:
    """Round a non-negative required dimension outward to the next grid line."""
    dimension = _as_decimal(value, field_name="value")
    quantum = _as_decimal(grid, field_name="grid")
    if dimension < 0:
        raise ValueError("value must be non-negative")
    if quantum <= 0:
        raise ValueError("grid must be greater than zero")
    units = (dimension / quantum).to_integral_value(rounding=ROUND_CEILING)
    result = units * quantum
    return float(result)


def minimum_pin_group_span(count: int, pin_pitch: float = 5.0, grid: float = 2.5) -> float:
    """Return ``(N - 1)P + 2G`` for one repeated side pin group."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be an integer greater than zero")
    pitch = _as_decimal(pin_pitch, field_name="pin_pitch")
    quantum = _as_decimal(grid, field_name="grid")
    if pitch <= 0 or quantum <= 0:
        raise ValueError("pin_pitch and grid must be greater than zero")
    return float((Decimal(count - 1) * pitch) + (Decimal(2) * quantum))


def _safe_relative_path(path: str | PurePosixPath) -> PurePosixPath | None:
    raw = PurePosixPath(str(path).replace("\\", "/"))
    if raw.is_absolute() or not raw.parts or ".." in raw.parts or "." in raw.parts:
        return None
    return raw


def _compound_stem(name: str, suffix: str) -> str:
    return name[: -len(suffix)] if name.endswith(suffix) else name


def validate_library_artifact_path(
    path: str | PurePosixPath,
    *,
    operation: str = "added",
    task_owns_fixture_area: bool = False,
) -> list[IntegrityIssue]:
    """Validate the canonical location of a newly authored reusable asset.

    Existing historical artifacts are compatible: ``modified`` paths do not
    fail merely because they predate 0.5.9.  The path rule applies to new
    ``.aixlib.json`` and ``.aixsym.json`` files.
    """
    rendered = str(path).replace("\\", "/")
    if operation != "added":
        return []
    if not rendered.endswith((".aixlib.json", ".aixsym.json")):
        return []
    pure = _safe_relative_path(rendered)
    if pure is None:
        return [IntegrityIssue(DIAG_LIBRARY_PATH_NONCANONICAL, "New reusable library paths must be safe project-relative paths.", path=rendered)]
    parts = pure.parts
    if parts and parts[0] in {"examples", "validation", "render", "evidence", "docs"} and not task_owns_fixture_area:
        return [IntegrityIssue(
            DIAG_LIBRARY_PATH_NONCANONICAL,
            "Ordinary reusable-part authoring must not create assets in example, validation, render, evidence, or documentation areas.",
            path=pure.as_posix(),
        )]
    if len(parts) < 3 or parts[0] != "library":
        return [IntegrityIssue(
            DIAG_LIBRARY_PATH_NONCANONICAL,
            "New reusable library and symbol artifacts must be created below library/<electronics|architecture>/... .",
            path=pure.as_posix(),
        )]
    domain = parts[1]
    issues: list[IntegrityIssue] = []
    if domain not in ALLOWED_LIBRARY_DOMAINS:
        issues.append(IntegrityIssue(
            DIAG_LIBRARY_DOMAIN_UNKNOWN,
            f"Unknown first-level library domain {domain!r}; expected electronics or architecture.",
            path=pure.as_posix(),
            evidence={"domain": domain, "allowed": sorted(ALLOWED_LIBRARY_DOMAINS)},
        ))
    for segment in parts[2:-1]:
        if not LOWER_KEBAB_RE.fullmatch(segment):
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_NAME_INVALID,
                f"Library namespace segment {segment!r} is not lower-kebab-case.",
                path=pure.as_posix(),
                evidence={"segment": segment},
            ))
    filename = parts[-1]
    valid_filename = bool(
        LIBRARY_FILENAME_RE.fullmatch(filename)
        if filename.endswith(".aixlib.json")
        else SYMBOL_FILENAME_RE.fullmatch(filename)
    )
    if not valid_filename:
        issues.append(IntegrityIssue(
            DIAG_LIBRARY_NAME_INVALID,
            f"Reusable artifact filename {filename!r} is not a semantic lower-kebab compound filename.",
            path=pure.as_posix(),
            evidence={"filename": filename},
        ))
    stem = _compound_stem(filename, ".aixlib.json" if filename.endswith(".aixlib.json") else ".aixsym.json")
    if stem in {"library", "parts", "components", "new", "final"}:
        issues.append(IntegrityIssue(
            DIAG_LIBRARY_NAME_INVALID,
            f"Context-free reusable artifact filename {filename!r} is not permitted for new authoring.",
            path=pure.as_posix(),
        ))
    return issues


def _namespace_key(parts: Sequence[str]) -> tuple[str, ...]:
    """Derive a conservative synonym key for deterministic reuse guidance."""
    result: list[str] = []
    for raw in parts:
        token = raw.lower().replace("_", "-").strip("-")
        for suffix in ("-components", "-component", "-parts", "-part"):
            if token.endswith(suffix):
                token = token[: -len(suffix)]
        if token.endswith("s") and len(token) > 3:
            token = token[:-1]
        result.append(token)
    return tuple(result)


def choose_existing_namespace(existing: Iterable[str], requested: str) -> str | None:
    """Return an established namespace when it is an exact/conservative match."""
    safe_requested = _safe_relative_path(requested)
    if safe_requested is None:
        return None
    requested_key = _namespace_key(safe_requested.parts)
    candidates: list[str] = []
    for item in existing:
        safe = _safe_relative_path(item)
        if safe is not None and _namespace_key(safe.parts) == requested_key:
            candidates.append(safe.as_posix())
    return sorted(candidates, key=lambda value: (len(PurePosixPath(value).parts), value))[0] if candidates else None


def _absolute_source_uri(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or any(ch.isspace() for ch in value):
        return False
    split = urlsplit(value)
    if split.scheme in {"http", "https"}:
        return bool(split.netloc)
    if split.scheme == "urn":
        return bool(split.path)
    return False


def part_provenance(component: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = component.get("metadata")
    if not isinstance(metadata, Mapping):
        return {}
    value = metadata.get("partProvenance")
    return value if isinstance(value, Mapping) else {}


def validate_part_provenance(component: Mapping[str, Any]) -> list[IntegrityIssue]:
    component_id = str(component.get("id", ""))
    pointer = f"component:{component_id or '<unknown>'}/metadata/partProvenance"
    provenance = part_provenance(component)
    if not provenance:
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_PROVENANCE_INVALID,
            "New component IDs require metadata.partProvenance with a declared status.",
            path=pointer,
        )]
    status = provenance.get("status")
    issues: list[IntegrityIssue] = []
    if status not in PART_PROVENANCE_STATUSES:
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_PROVENANCE_INVALID,
            f"Unknown part provenance status {status!r}.",
            path=pointer,
            evidence={"allowed": sorted(PART_PROVENANCE_STATUSES)},
        )]
    manufacturer = provenance.get("manufacturer")
    part_number = provenance.get("partNumber") or provenance.get("productId")
    semantic_ready = bool((component.get("metadata") or {}).get("semanticReady", False)) if isinstance(component.get("metadata"), Mapping) else False
    if status == "datasheet-backed":
        missing = [name for name, value in (
            ("manufacturer", manufacturer),
            ("partNumber or productId", part_number),
            ("sourceKind", provenance.get("sourceKind")),
            ("sourceUri", provenance.get("sourceUri")),
        ) if not isinstance(value, str) or not value.strip()]
        if missing:
            code = DIAG_LIBRARY_PART_SOURCE_REQUIRED if "sourceUri" in missing else DIAG_LIBRARY_PART_PROVENANCE_INVALID
            issues.append(IntegrityIssue(
                code,
                "Datasheet-backed concrete parts require " + ", ".join(missing) + ".",
                path=pointer,
                evidence={"missing": missing},
            ))
        if provenance.get("sourceKind") not in {None, "manufacturer-datasheet"}:
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_PART_PROVENANCE_INVALID,
                "Datasheet-backed status requires sourceKind=manufacturer-datasheet.",
                path=pointer,
            ))
        if provenance.get("sourceUri") and not _absolute_source_uri(provenance.get("sourceUri")):
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_PART_SOURCE_REQUIRED,
                "sourceUri must be an absolute HTTP(S) or URN identifier.",
                path=pointer,
            ))
    elif status == "generic-template":
        if manufacturer and part_number:
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_PART_PROVENANCE_INVALID,
                "generic-template must not claim one exact manufacturer/orderable part identity.",
                path=pointer,
            ))
    elif status == "placeholder":
        reason = provenance.get("placeholderReason")
        if not isinstance(reason, str) or not reason.strip():
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_PART_PROVENANCE_INVALID,
                "placeholder status requires a non-empty placeholderReason.",
                path=pointer,
            ))
        if semantic_ready:
            issues.append(IntegrityIssue(
                DIAG_LIBRARY_PART_PLACEHOLDER_UNDECLARED,
                "A placeholder cannot set semanticReady=true.",
                path=f"component:{component_id}/metadata/semanticReady",
            ))
    return issues


def _unique_nonempty_strings(values: Any) -> bool:
    return isinstance(values, list) and all(isinstance(value, str) and value.strip() for value in values) and len(values) == len(set(values))


def _valid_token_list(values: Any) -> bool:
    return _unique_nonempty_strings(values) and all(LOWER_KEBAB_RE.fullmatch(value) for value in values)


def validate_pin_semantics(port: Mapping[str, Any]) -> list[IntegrityIssue]:
    port_id = str(port.get("id", "<unknown>"))
    base = f"port:{port_id}"
    issues: list[IntegrityIssue] = []
    if port.get("type") == "no-connect" and port.get("required") is True:
        issues.append(IntegrityIssue(
            DIAG_PIN_NOCONNECT_CONTRADICTION,
            "type=no-connect cannot be combined with required=true.",
            path=base,
        ))
    metadata = port.get("metadata")
    if not isinstance(metadata, Mapping) or "pinSemantics" not in metadata:
        return issues
    semantics = metadata.get("pinSemantics")
    if not isinstance(semantics, Mapping):
        issues.append(IntegrityIssue(DIAG_PIN_SEMANTICS_PROFILE_INVALID, "pinSemantics must be an object.", path=f"{base}/metadata/pinSemantics"))
        return issues
    if semantics.get("profile") != PIN_SEMANTICS_PROFILE:
        issues.append(IntegrityIssue(
            DIAG_PIN_SEMANTICS_PROFILE_INVALID,
            f"pinSemantics.profile must be {PIN_SEMANTICS_PROFILE!r}.",
            path=f"{base}/metadata/pinSemantics/profile",
        ))
    signal_class = semantics.get("signalClass")
    if signal_class not in PIN_SIGNAL_CLASSES:
        issues.append(IntegrityIssue(
            DIAG_PIN_SIGNAL_CLASS_INVALID,
            f"Unknown signalClass {signal_class!r}.",
            path=f"{base}/metadata/pinSemantics/signalClass",
        ))
    tags = semantics.get("functionalTags", [])
    if not _valid_token_list(tags):
        issues.append(IntegrityIssue(
            DIAG_PIN_FUNCTION_TAG_INVALID,
            "functionalTags must be a unique list of lower-kebab tokens.",
            path=f"{base}/metadata/pinSemantics/functionalTags",
        ))
    polarity = semantics.get("polarity", "unspecified")
    if polarity not in PIN_POLARITIES:
        issues.append(IntegrityIssue(
            DIAG_PIN_POLARITY_INCONSISTENT,
            f"Unknown polarity {polarity!r}.",
            path=f"{base}/metadata/pinSemantics/polarity",
        ))
    pair = semantics.get("differentialPair")
    if pair is not None:
        if not isinstance(pair, Mapping) or not LOWER_KEBAB_RE.fullmatch(str(pair.get("id", ""))) or pair.get("member") not in DIFFERENTIAL_MEMBERS:
            issues.append(IntegrityIssue(
                DIAG_PIN_DIFFERENTIAL_PAIR_INCOMPLETE,
                "differentialPair requires a lower-kebab id and member positive|negative.",
                path=f"{base}/metadata/pinSemantics/differentialPair",
            ))
        elif polarity in {"positive", "negative"} and polarity != pair.get("member"):
            issues.append(IntegrityIssue(
                DIAG_PIN_POLARITY_INCONSISTENT,
                "Differential member and positive/negative polarity contradict each other.",
                path=f"{base}/metadata/pinSemantics",
            ))
    domain = semantics.get("powerDomain")
    if domain is not None and (not isinstance(domain, str) or not LOWER_KEBAB_RE.fullmatch(domain)):
        issues.append(IntegrityIssue(
            DIAG_PIN_FUNCTION_TAG_INVALID,
            "powerDomain must be a lower-kebab semantic token.",
            path=f"{base}/metadata/pinSemantics/powerDomain",
        ))
    capabilities = semantics.get("capabilities", [])
    if not _valid_token_list(capabilities):
        issues.append(IntegrityIssue(
            DIAG_PIN_FUNCTION_TAG_INVALID,
            "capabilities must be a unique list of source-backed lower-kebab tokens.",
            path=f"{base}/metadata/pinSemantics/capabilities",
        ))
    alternates = semantics.get("alternateFunctions", [])
    if not isinstance(alternates, list):
        issues.append(IntegrityIssue(
            DIAG_PIN_ALTERNATE_FUNCTION_INVALID,
            "alternateFunctions must be an array.",
            path=f"{base}/metadata/pinSemantics/alternateFunctions",
        ))
    else:
        names: list[str] = []
        for index, item in enumerate(alternates):
            item_path = f"{base}/metadata/pinSemantics/alternateFunctions/{index}"
            if not isinstance(item, Mapping) or not isinstance(item.get("name"), str) or not item.get("name", "").strip():
                issues.append(IntegrityIssue(DIAG_PIN_ALTERNATE_FUNCTION_INVALID, "Each alternate function requires a stable non-empty name.", path=item_path))
                continue
            names.append(str(item["name"]))
            if not _valid_token_list(item.get("functionalTags", [])):
                issues.append(IntegrityIssue(DIAG_PIN_ALTERNATE_FUNCTION_INVALID, "Alternate-function functionalTags must be unique lower-kebab tokens.", path=item_path))
        if len(names) != len(set(names)):
            issues.append(IntegrityIssue(DIAG_PIN_ALTERNATE_FUNCTION_INVALID, "Alternate-function names must be unique on one physical terminal.", path=f"{base}/metadata/pinSemantics/alternateFunctions"))
    return issues


def validate_component_pin_semantics(component: Mapping[str, Any]) -> list[IntegrityIssue]:
    issues: list[IntegrityIssue] = []
    ports = component.get("ports")
    if not isinstance(ports, list):
        return issues
    pair_members: dict[str, list[tuple[str, str]]] = {}
    for port in ports:
        if not isinstance(port, Mapping):
            continue
        issues.extend(validate_pin_semantics(port))
        semantics = ((port.get("metadata") or {}).get("pinSemantics") if isinstance(port.get("metadata"), Mapping) else None)
        pair = semantics.get("differentialPair") if isinstance(semantics, Mapping) else None
        if isinstance(pair, Mapping) and pair.get("id") and pair.get("member"):
            pair_members.setdefault(str(pair["id"]), []).append((str(port.get("id", "")), str(pair["member"])))
    for pair_id, members in sorted(pair_members.items()):
        member_values = [member for _port, member in members]
        if sorted(member_values) != ["negative", "positive"]:
            issues.append(IntegrityIssue(
                DIAG_PIN_DIFFERENTIAL_PAIR_INCOMPLETE,
                f"Differential pair {pair_id!r} must contain exactly one positive and one negative physical member.",
                path=f"component:{component.get('id', '<unknown>')}/ports",
                evidence={"pair": pair_id, "members": members},
            ))
    return issues


def validate_minimum_component_contract(component: Mapping[str, Any]) -> list[IntegrityIssue]:
    component_id = str(component.get("id", "<unknown>"))
    missing: list[str] = []
    for key in ("id", "displayName", "kind", "description"):
        if not isinstance(component.get(key), str) or not str(component.get(key, "")).strip():
            missing.append(key)
    ports = component.get("ports")
    if not isinstance(ports, list) or not ports:
        missing.append("ports")
    else:
        ids = [port.get("id") for port in ports if isinstance(port, Mapping)]
        if len(ids) != len(ports) or any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
            missing.append("unique stable port IDs")
        for port in ports:
            if not isinstance(port, Mapping):
                continue
            for key in ("name", "type"):
                if not isinstance(port.get(key), str) or not port.get(key):
                    missing.append(f"port {port.get('id', '?')} {key}")
    if not isinstance(component.get("properties"), list):
        missing.append("properties")
    presentations = component.get("presentations")
    if not isinstance(presentations, list) or not presentations:
        missing.append("presentations")
    elif isinstance(ports, list):
        port_ids = {str(port.get("id")) for port in ports if isinstance(port, Mapping) and port.get("id") is not None}
        for index, presentation in enumerate(presentations):
            port_map = presentation.get("portMap") if isinstance(presentation, Mapping) else None
            if not isinstance(port_map, Mapping) or set(map(str, port_map.keys())) != port_ids:
                missing.append(f"presentation {index} total portMap")
    if not part_provenance(component):
        missing.append("metadata.partProvenance")
    if not missing:
        return []
    return [IntegrityIssue(
        DIAG_LIBRARY_PART_MINIMUM_ATTRIBUTES_MISSING,
        "Component semantic contract is incomplete: " + ", ".join(sorted(set(missing))) + ".",
        path=f"component:{component_id}",
        evidence={"missing": sorted(set(missing))},
    )]


def _normalized_ports(component: Mapping[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for port in component.get("ports", []) if isinstance(component.get("ports"), list) else []:
        if not isinstance(port, Mapping):
            continue
        result.append({
            "id": port.get("id"),
            "name": port.get("name"),
            "terminal": port.get("terminal"),
            "type": port.get("type"),
            "required": bool(port.get("required", False)),
            "pinSemantics": ((port.get("metadata") or {}).get("pinSemantics") if isinstance(port.get("metadata"), Mapping) else None),
        })
    return sorted(result, key=lambda item: (str(item.get("id")), str(item.get("terminal"))))


def component_signatures(component: Mapping[str, Any]) -> dict[str, str]:
    """Derive deterministic review/deduplication signatures.

    Component ID and display text are intentionally excluded from the semantic
    basis so ID-only or label-only multiplication is detectable.
    """
    properties = []
    for item in component.get("properties", []) if isinstance(component.get("properties"), list) else []:
        if isinstance(item, Mapping):
            properties.append(dict(item))
    properties = sorted(properties, key=lambda item: str(item.get("id", "")))
    provenance = dict(part_provenance(component))
    presentations = []
    for item in component.get("presentations", []) if isinstance(component.get("presentations"), list) else []:
        if not isinstance(item, Mapping):
            continue
        asset = item.get("asset") if isinstance(item.get("asset"), Mapping) else {}
        presentations.append({
            "purpose": item.get("purpose"),
            "asset": {key: asset.get(key) for key in ("symbolId", "revision", "path", "digest")},
            "portMap": dict(sorted((item.get("portMap") or {}).items())) if isinstance(item.get("portMap"), Mapping) else None,
            "fieldMap": dict(sorted((item.get("fieldMap") or {}).items())) if isinstance(item.get("fieldMap"), Mapping) else None,
        })
    presentations = sorted(presentations, key=lambda item: (str(item.get("purpose")), json.dumps(item, sort_keys=True)))
    port_signature = semantic_digest(_normalized_ports(component))
    property_signature = semantic_digest(properties)
    provenance_signature = semantic_digest(provenance)
    presentation_signature = semantic_digest(presentations)
    semantic_basis = {
        "kind": component.get("kind"),
        "ports": port_signature,
        "properties": property_signature,
        "provenance": provenance_signature,
    }
    return {
        "portSignature": port_signature,
        "propertySignature": property_signature,
        "provenanceSignature": provenance_signature,
        "presentationSignature": presentation_signature,
        "semanticBasisSignature": semantic_digest(semantic_basis),
    }


def detect_semantic_clones(components: Sequence[Mapping[str, Any]]) -> list[IntegrityIssue]:
    groups: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for component in components:
        signatures = component_signatures(component)
        groups.setdefault(signatures["semanticBasisSignature"], []).append((str(component.get("id", "")), signatures))
    issues: list[IntegrityIssue] = []
    for signature, members in sorted(groups.items()):
        ids = sorted(component_id for component_id, _signatures in members)
        if len(ids) < 2:
            continue
        issues.append(IntegrityIssue(
            DIAG_LIBRARY_COMPONENT_SEMANTIC_CLONE,
            "Multiple component IDs have no distinct pin/property/provenance basis; shared geometry alone cannot justify semantic IDs.",
            path="components",
            evidence={"componentIds": ids, "semanticBasisSignature": signature},
        ))
    return issues


def validate_part_review_evidence(
    component: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
    *,
    library_digest: str | None = None,
    symbol_digests: Sequence[str] = (),
) -> list[IntegrityIssue]:
    provenance = part_provenance(component)
    status = provenance.get("status")
    component_id = str(component.get("id", "<unknown>"))
    if status != "datasheet-backed":
        return []
    if not isinstance(evidence, Mapping):
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING,
            "Datasheet-backed semantic-ready status requires source-bound pinout review evidence.",
            path=f"component:{component_id}",
        )]
    mismatches: list[str] = []
    expected = {
        "componentId": component_id,
        "sourceUri": provenance.get("sourceUri"),
    }
    if library_digest is not None:
        expected["libraryDigest"] = library_digest
    if provenance.get("sourceDigest"):
        expected["sourceDigest"] = provenance.get("sourceDigest")
    for key, value in expected.items():
        if evidence.get(key) != value:
            mismatches.append(key)
    expected_symbols = sorted(set(symbol_digests))
    if expected_symbols and sorted(set(evidence.get("symbolDigests", []))) != expected_symbols:
        mismatches.append("symbolDigests")
    if evidence.get("result") != "PASS":
        mismatches.append("result")
    checks = evidence.get("checks")
    required_checks = {
        "identity",
        "pinNumbers",
        "pinNamesAndFunctions",
        "portTypes",
        "minimumProperties",
        "presentationBinding",
        "pinSemantics",
    }
    if not isinstance(checks, Mapping) or any(checks.get(key) is not True for key in required_checks):
        mismatches.append("checks")
    if evidence.get("pinSemanticsProfile") not in {None, PIN_SEMANTICS_PROFILE}:
        mismatches.append("pinSemanticsProfile")
    if mismatches:
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING,
            "Part semantic review is incomplete or bound to different component/source/digest authority.",
            path=f"component:{component_id}",
            evidence={"mismatches": sorted(set(mismatches))},
        )]
    return []


def validate_circuit_intent_review(
    component: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
    *,
    library_digest: str | None = None,
) -> list[IntegrityIssue]:
    component_id = str(component.get("id", "<unknown>"))
    if not isinstance(evidence, Mapping):
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_INTENT_REVIEW_INCOMPLETE,
            "Circuit-intent approval requires an exact component-bound review record.",
            path=f"component:{component_id}",
        )]
    mismatches: list[str] = []
    if evidence.get("componentId") != component_id:
        mismatches.append("componentId")
    if library_digest is not None and evidence.get("libraryDigest") != library_digest:
        mismatches.append("libraryDigest")
    if evidence.get("result") != "PASS":
        mismatches.append("result")
    checks = evidence.get("checks")
    required = {
        "functionalRole",
        "intendedConnectedPins",
        "requiredPins",
        "deliberateNoConnects",
        "taskRelevantProperties",
        "endpointPreservingPresentation",
    }
    if not isinstance(checks, Mapping) or any(checks.get(key) is not True for key in required):
        mismatches.append("checks")
    if mismatches:
        return [IntegrityIssue(
            DIAG_LIBRARY_PART_INTENT_REVIEW_INCOMPLETE,
            "Circuit-intent review is incomplete or bound to different component/library authority.",
            path=f"component:{component_id}",
            evidence={"mismatches": sorted(set(mismatches))},
        )]
    return []


def validate_source_reviewed_pin_semantics(
    component: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
) -> list[IntegrityIssue]:
    provenance = part_provenance(component)
    if provenance.get("status") != "datasheet-backed":
        return []
    has_semantics = any(
        isinstance(port, Mapping)
        and isinstance(port.get("metadata"), Mapping)
        and "pinSemantics" in port.get("metadata", {})
        for port in component.get("ports", []) if isinstance(component.get("ports"), list)
    )
    if not has_semantics:
        return []
    if not isinstance(evidence, Mapping):
        return [IntegrityIssue(
            DIAG_PIN_SOURCE_REVIEW_INCOMPLETE,
            "Datasheet-backed detailed pin semantics require source-bound review evidence.",
            path=f"component:{component.get('id', '<unknown>')}/ports",
        )]
    checks = evidence.get("checks") if isinstance(evidence.get("checks"), Mapping) else {}
    if checks.get("pinSemantics") is not True or evidence.get("sourceUri") != provenance.get("sourceUri"):
        return [IntegrityIssue(
            DIAG_PIN_SOURCE_REVIEW_INCOMPLETE,
            "Pin semantic claims are not reviewed against the component source URI.",
            path=f"component:{component.get('id', '<unknown>')}/ports",
        )]
    return []


def bounded_compatibility_precheck(endpoints: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Run the conservative static compatibility matrix for one closed net."""
    types = [str(item.get("type", "unspecified")) for item in endpoints]
    issues: list[IntegrityIssue] = []
    counts = {kind: types.count(kind) for kind in sorted(set(types))}
    status = "PASS"
    if "no-connect" in types:
        status = "ERROR"
        issues.append(IntegrityIssue(DIAG_ERC_CONNECTED_NOCONNECT, "A no-connect endpoint participates in a connected net.", evidence={"types": types}))
    elif counts.get("power-output", 0) > 1:
        status = "ERROR"
        issues.append(IntegrityIssue(DIAG_ERC_POWER_OUTPUT_CONFLICT, "Multiple power-output sources share one local net.", evidence={"types": types}))
    elif counts.get("output", 0) > 1:
        status = "ERROR"
        issues.append(IntegrityIssue(DIAG_ERC_OUTPUT_CONFLICT, "Multiple ordinary output drivers share one local net.", evidence={"types": types}))
    elif "unspecified" in types or not endpoints:
        status = "NOT_EVALUATED"
        issues.append(IntegrityIssue(DIAG_ERC_UNCERTAIN_TOPOLOGY, "Unspecified or empty endpoint behavior prevents a compatibility PASS.", severity="warning", evidence={"types": types}))
    elif counts.get("tri-state", 0) > 1 or counts.get("open-collector", 0) > 1 or counts.get("open-emitter", 0) > 1 or counts.get("bidirectional", 0) > 1:
        status = "WARN"
        issues.append(IntegrityIssue(DIAG_ERC_UNCERTAIN_TOPOLOGY, "Multi-driver topology requires higher-level enable, bias, or protocol review.", severity="warning", evidence={"types": types}))
    elif types and all(kind in {"input", "power-input"} for kind in types):
        status = "WARN"
        issues.append(IntegrityIssue(DIAG_ERC_INPUT_ONLY, "The local net contains only receiving endpoints; a hierarchical or external source may be missing.", severity="warning", evidence={"types": types}))
    result = {
        "status": status,
        "valid": status != "ERROR",
        "endpointCount": len(endpoints),
        "typeCounts": counts,
        "issues": [issue.to_dict() for issue in issues],
        "claimBoundary": {
            "electricalSafety": False,
            "voltageCompatibility": False,
            "timingCorrectness": False,
            "simulationCorrectness": False,
            "productionReadiness": False,
        },
    }
    assert result["status"] in COMPATIBILITY_OUTCOMES
    return result


def _ratio_integral(numerator: Decimal, denominator: Decimal) -> bool:
    if denominator <= 0:
        return False
    value = numerator / denominator
    return value == value.to_integral_value()


def validate_layout_profile_grid(layout: Mapping[str, Any], style_profile: Mapping[str, Any]) -> list[IntegrityIssue]:
    layout_obj = layout.get("layout") if isinstance(layout.get("layout"), Mapping) else layout
    profile_obj = style_profile.get("styleProfile") if isinstance(style_profile.get("styleProfile"), Mapping) else style_profile
    coordinate = layout_obj.get("coordinateSystem") if isinstance(layout_obj, Mapping) else None
    grid = profile_obj.get("grid") if isinstance(profile_obj, Mapping) else None
    symbol = profile_obj.get("symbol") if isinstance(profile_obj, Mapping) else None
    if not isinstance(coordinate, Mapping) or not isinstance(grid, Mapping) or not isinstance(symbol, Mapping):
        return [IntegrityIssue(DIAG_LAYOUT_GRID_PROFILE_MISMATCH, "Layout coordinate system and active style grid/symbol profile must be present.")]
    try:
        layout_grid = _as_decimal(coordinate.get("grid"), field_name="layout.coordinateSystem.grid")
        snap = _as_decimal(grid.get("snap"), field_name="styleProfile.grid.snap")
        minor = _as_decimal(grid.get("minor"), field_name="styleProfile.grid.minor")
        major = _as_decimal(grid.get("major"), field_name="styleProfile.grid.major")
        pin_pitch = _as_decimal(symbol.get("pinPitch"), field_name="styleProfile.symbol.pinPitch")
    except ValueError as exc:
        return [IntegrityIssue(DIAG_LAYOUT_GRID_PROFILE_MISMATCH, str(exc))]
    mismatches: list[str] = []
    if layout_grid != snap:
        mismatches.append("layout.grid != profile.snap")
    if minor != snap:
        mismatches.append("profile.minor != profile.snap")
    if not _ratio_integral(major, snap):
        mismatches.append("profile.major/profile.snap is not integral")
    if not _ratio_integral(pin_pitch, snap):
        mismatches.append("profile.pinPitch/profile.snap is not integral")
    if mismatches:
        return [IntegrityIssue(
            DIAG_LAYOUT_GRID_PROFILE_MISMATCH,
            "Grid Schematic Profile 1 coherence failed: " + "; ".join(mismatches) + ".",
            evidence={"layoutGrid": float(layout_grid), "snap": float(snap), "minor": float(minor), "major": float(major), "pinPitch": float(pin_pitch)},
        )]
    return []


def aggregate_validation_claims(
    component: Mapping[str, Any],
    *,
    structural_pass: bool,
    semantic_issues: Sequence[IntegrityIssue],
    review_issues: Sequence[IntegrityIssue] = (),
    intent_issues: Sequence[IntegrityIssue] = (),
    intent_review_requested: bool = False,
) -> dict[str, Any]:
    status = part_provenance(component).get("status")
    semantic_errors = [issue for issue in [*semantic_issues, *review_issues] if issue.severity == "error"]
    if status == "placeholder":
        part_result = "PLACEHOLDER"
        semantic_ready = False
    elif semantic_errors:
        part_result = "INCOMPLETE"
        semantic_ready = False
    elif status == "generic-template":
        part_result = "GENERIC_TEMPLATE_PASS"
        semantic_ready = True
    elif status == "datasheet-backed":
        part_result = "PART_SEMANTIC_PASS"
        semantic_ready = True
    else:
        part_result = "INCOMPLETE"
        semantic_ready = False
    if not intent_review_requested:
        intent_result = "NOT_REVIEWED"
    elif any(issue.severity == "error" for issue in intent_issues):
        intent_result = "INCOMPLETE"
    else:
        intent_result = "CIRCUIT_INTENT_REVIEW_PASS"
    return {
        "structuralResult": "STRUCTURAL_PASS" if structural_pass else "STRUCTURAL_FAIL",
        "partSemanticResult": part_result,
        "semanticReady": semantic_ready and structural_pass,
        "circuitIntentResult": intent_result,
        "claimBoundary": {
            "renderProvesDatasheetTruth": False,
            "partSemanticPassProvesFullElectricalSafety": False,
            "circuitIntentReviewProvesSimulationCorrectness": False,
        },
    }


def validate_component(
    component: Mapping[str, Any],
    *,
    review_evidence: Mapping[str, Any] | None = None,
    intent_evidence: Mapping[str, Any] | None = None,
    library_digest: str | None = None,
    symbol_digests: Sequence[str] = (),
    structural_pass: bool = True,
    intent_review_requested: bool = False,
) -> dict[str, Any]:
    semantic_issues = [
        *validate_minimum_component_contract(component),
        *validate_part_provenance(component),
        *validate_component_pin_semantics(component),
        *validate_source_reviewed_pin_semantics(component, review_evidence),
    ]
    review_issues = validate_part_review_evidence(
        component,
        review_evidence,
        library_digest=library_digest,
        symbol_digests=symbol_digests,
    ) if part_provenance(component).get("status") == "datasheet-backed" else []
    intent_issues = validate_circuit_intent_review(component, intent_evidence, library_digest=library_digest) if intent_review_requested else []
    claims = aggregate_validation_claims(
        component,
        structural_pass=structural_pass,
        semantic_issues=semantic_issues,
        review_issues=review_issues,
        intent_issues=intent_issues,
        intent_review_requested=intent_review_requested,
    )
    issues = [*semantic_issues, *review_issues, *intent_issues]
    return {
        "valid": structural_pass and not any(issue.severity == "error" for issue in issues),
        "componentId": component.get("id"),
        "signatures": component_signatures(component),
        "claims": claims,
        "issues": [issue.to_dict() for issue in issues],
    }


def validate_library_document(
    document: Mapping[str, Any],
    *,
    artifact_path: str | None = None,
    operation: str = "modified",
    review_records: Mapping[str, Mapping[str, Any]] | None = None,
    intent_records: Mapping[str, Mapping[str, Any]] | None = None,
    structural_pass: bool = True,
) -> dict[str, Any]:
    library = document.get("library") if isinstance(document.get("library"), Mapping) else {}
    components = library.get("components") if isinstance(library.get("components"), list) else []
    issues: list[IntegrityIssue] = []
    if artifact_path:
        issues.extend(validate_library_artifact_path(artifact_path, operation=operation))
    issues.extend(detect_semantic_clones([item for item in components if isinstance(item, Mapping)]))
    component_results = []
    for component in components:
        if not isinstance(component, Mapping):
            continue
        component_id = str(component.get("id", ""))
        component_results.append(validate_component(
            component,
            review_evidence=(review_records or {}).get(component_id),
            intent_evidence=(intent_records or {}).get(component_id),
            structural_pass=structural_pass,
            intent_review_requested=component_id in (intent_records or {}),
        ))
    for item in component_results:
        for issue in item["issues"]:
            issues.append(IntegrityIssue(issue["code"], issue["message"], issue["severity"], issue["path"], issue.get("evidence", {})))
    valid = structural_pass and not any(issue.severity == "error" for issue in issues)
    return {
        "valid": valid,
        "structuralResult": "STRUCTURAL_PASS" if structural_pass else "STRUCTURAL_FAIL",
        "componentCount": len(component_results),
        "componentResults": component_results,
        "issues": [issue.to_dict() for issue in issues],
        "claimBoundary": "Structural/render PASS does not independently prove datasheet truth, semantic readiness, circuit suitability, or simulation correctness.",
    }


__all__ = [
    "ALLOWED_LIBRARY_DOMAINS",
    "COMPATIBILITY_OUTCOMES",
    "IntegrityIssue",
    "PART_PROVENANCE_STATUSES",
    "PIN_SEMANTICS_PROFILE",
    "aggregate_validation_claims",
    "bounded_compatibility_precheck",
    "ceil_to_grid",
    "choose_existing_namespace",
    "component_signatures",
    "detect_semantic_clones",
    "minimum_pin_group_span",
    "part_provenance",
    "semantic_digest",
    "validate_circuit_intent_review",
    "validate_component",
    "validate_component_pin_semantics",
    "validate_layout_profile_grid",
    "validate_library_artifact_path",
    "validate_library_document",
    "validate_minimum_component_contract",
    "validate_part_provenance",
    "validate_part_review_evidence",
    "validate_pin_semantics",
    "validate_source_reviewed_pin_semantics",
]
