"""Machine-readable diagnostics for the AIXEM agent authoring loop.

The module adapts existing validator issues and renderer exceptions into the
versioned Agent Diagnostic Contract 1.  Diagnostics are derived evidence only;
they never become circuit authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

DIAGNOSTIC_SCHEMA = "https://schemas.aixem.org/agent/diagnostic/1"
DIAGNOSTIC_FORMAT_VERSION = "1.0"

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
AUTHORITY_VALUES = {
    "semantic",
    "component-library",
    "symbol",
    "layout",
    "project",
    "project-routing",
    "renderer",
    "viewer",
    "workbench",
    "documentation",
    "agent-execution",
}
REPAIR_CLASS_VALUES = {
    "authoritative-source",
    "binding",
    "placement",
    "routing",
    "project-composition",
    "renderer-defect",
    "unsupported-capability",
    "manual-review",
    "execution-scope",
}


@dataclass(frozen=True)
class DiagnosticDefinition:
    authority: str
    remediation_route: str
    repair_class: str
    requirement: str
    summary: str


# The P0 registry deliberately covers the high-value failure classes listed in
# the 0.5.5 plan.  Additional execution-contract diagnostics are included at
# the end so the harness itself can fail closed without overloading prose.
DIAGNOSTIC_REGISTRY: dict[str, DiagnosticDefinition] = {
    "AIXEM-DIAG-SCHEMA-INVALID": DiagnosticDefinition(
        "documentation", "validate-project", "authoritative-source", "AIXEM-REQ-CONF-0001", "A declared JSON artifact does not satisfy its immutable schema."
    ),
    "AIXEM-DIAG-SEMANTIC-PORT-UNKNOWN": DiagnosticDefinition(
        "semantic", "create-schematic", "authoritative-source", "AIXEM-REQ-SYMBOL-0002", "A semantic endpoint refers to an unknown component or interface port."
    ),
    "AIXEM-DIAG-SEMANTIC-NET-ENDPOINT-UNKNOWN": DiagnosticDefinition(
        "semantic", "create-schematic", "authoritative-source", "AIXEM-REQ-ROUTE-0002", "A net contains an endpoint that cannot be resolved."
    ),
    "AIXEM-DIAG-SEMANTIC-NET-CLOSURE": DiagnosticDefinition(
        "semantic", "create-schematic", "authoritative-source", "AIXEM-REQ-ROUTE-0003", "Semantic net membership is incomplete, duplicated, or contradictory."
    ),
    "AIXEM-DIAG-COMPONENT-TYPE-UNKNOWN": DiagnosticDefinition(
        "component-library", "create-schematic", "binding", "AIXEM-REQ-SYMBOL-BINDING-0001", "An entity references a component type that no locked library provides."
    ),
    "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE": DiagnosticDefinition(
        "component-library", "create-symbol", "binding", "AIXEM-REQ-SYMBOL-BINDING-0001", "The semantic component port map is not total."
    ),
    "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN": DiagnosticDefinition(
        "component-library", "create-symbol", "binding", "AIXEM-REQ-SYMBOL-BINDING-0001", "A component presentation maps to an unknown symbol port."
    ),
    "AIXEM-DIAG-BINDING-ASSET-MISSING": DiagnosticDefinition(
        "component-library", "create-symbol", "binding", "AIXEM-REQ-PROJECT-0002", "A locked symbol or library asset is missing."
    ),
    "AIXEM-DIAG-BINDING-ASSET-DIGEST": DiagnosticDefinition(
        "component-library", "create-symbol", "binding", "AIXEM-REQ-PROJECT-0002", "A locked asset digest does not match the referenced file."
    ),
    "AIXEM-DIAG-SYMBOL-PORT-EXPRESSION": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-0020", "A symbol port coordinate or orientation expression cannot be resolved."
    ),
    "AIXEM-DIAG-SYMBOL-PORT-OFF-GRID": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-DESIGN-0001", "A symbol electrical port is not on the authoring grid."
    ),
    "AIXEM-DIAG-SYMBOL-PORT-ORIENTATION": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-DESIGN-0001", "A symbol electrical port orientation is not orthogonal."
    ),
    "AIXEM-DIAG-SYMBOL-LEAD-MISSING": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-DESIGN-0002", "A visible pin lead is missing or lacks machine association metadata."
    ),
    "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-DESIGN-0002", "A visible lead endpoint does not coincide with its electrical port."
    ),
    "AIXEM-DIAG-SYMBOL-PIN-PITCH": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-DESIGN-0003", "Related symbol pins do not use the declared standard pitch."
    ),
    "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP": DiagnosticDefinition(
        "symbol", "create-symbol", "authoritative-source", "AIXEM-REQ-SYMBOL-0016", "A required identity field overlaps symbol body geometry."
    ),
    "AIXEM-DIAG-LAYOUT-PLACEMENT-MISSING": DiagnosticDefinition(
        "layout", "create-schematic", "placement", "AIXEM-REQ-SCHEM-0005", "Semantic entities and layout placements do not have total closure."
    ),
    "AIXEM-DIAG-LAYOUT-PLACEMENT-OFF-GRID": DiagnosticDefinition(
        "layout", "create-schematic", "placement", "AIXEM-REQ-SCHEM-0004", "A placement origin is outside the active snap grid."
    ),
    "AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE": DiagnosticDefinition(
        "layout", "route-nets", "routing", "AIXEM-REQ-ROUTE-0002", "Layout routes do not close every semantic endpoint exactly."
    ),
    "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL": DiagnosticDefinition(
        "layout", "route-nets", "routing", "AIXEM-REQ-ROUTE-0004", "A local route contains a non-orthogonal segment."
    ),
    "AIXEM-DIAG-ROUTE-VIA-OFF-GRID": DiagnosticDefinition(
        "layout", "route-nets", "routing", "AIXEM-REQ-SCHEM-0003", "A free route bend does not land on the active grid."
    ),
    "AIXEM-DIAG-ROUTE-ZERO-LENGTH": DiagnosticDefinition(
        "layout", "route-nets", "routing", "AIXEM-REQ-ROUTE-0005", "A route contains a zero-length segment."
    ),
    "AIXEM-DIAG-JUNCTION-AMBIGUOUS": DiagnosticDefinition(
        "layout", "route-nets", "routing", "AIXEM-REQ-SCHEM-0006", "A branch or crossing does not have unambiguous junction semantics."
    ),
    "AIXEM-DIAG-PROJECT-SHEET-UNKNOWN": DiagnosticDefinition(
        "project", "compose-project", "project-composition", "AIXEM-REQ-HIER-0001", "A project reference names an unknown sheet."
    ),
    "AIXEM-DIAG-PROJECT-INTERFACE-UNKNOWN": DiagnosticDefinition(
        "project", "compose-project", "project-composition", "AIXEM-REQ-HIER-0004", "A project-net member names an unknown leaf interface port."
    ),
    "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER": DiagnosticDefinition(
        "project", "compose-project", "project-composition", "AIXEM-REQ-HIER-0007", "A project net repeats the same qualified interface member."
    ),
    "AIXEM-DIAG-PROJECT-NET-MULTIPLE-OWNERSHIP": DiagnosticDefinition(
        "project", "compose-project", "project-composition", "AIXEM-REQ-HIER-0008", "One qualified interface member belongs to more than one project net."
    ),
    "AIXEM-DIAG-PROJECT-ROUTE-NON-ORTHOGONAL": DiagnosticDefinition(
        "project-routing", "route-project-nets", "routing", "AIXEM-REQ-HIER-0012", "A derived project route contains a non-orthogonal segment."
    ),
    "AIXEM-DIAG-RENDERER-DETERMINISM": DiagnosticDefinition(
        "renderer", "render-review", "renderer-defect", "AIXEM-REQ-RENDERER-0005", "Equivalent locked inputs did not produce byte-identical renderer evidence."
    ),
    "AIXEM-DIAG-UNSUPPORTED-CAPABILITY": DiagnosticDefinition(
        "documentation", "change-architecture", "unsupported-capability", "AIXEM-REQ-AGENT-0032", "The task requires a capability outside the declared AIXEM contract."
    ),
    "AIXEM-DIAG-LIBRARY-PATH-NONCANONICAL": DiagnosticDefinition(
        "component-library", "create-symbol", "execution-scope", "AIXEM-REQ-LIBRARY-0001", "A newly authored reusable library artifact is outside the canonical project library tree."
    ),
    "AIXEM-DIAG-LIBRARY-DOMAIN-UNKNOWN": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-LIBRARY-0001", "A new library artifact uses an unsupported first-level domain."
    ),
    "AIXEM-DIAG-LIBRARY-NAME-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-LIBRARY-0001", "A new library namespace segment or reusable artifact filename violates the lower-kebab naming contract."
    ),
    "AIXEM-DIAG-LIBRARY-PART-SOURCE-REQUIRED": DiagnosticDefinition(
        "component-library", "create-symbol", "manual-review", "AIXEM-REQ-LIBRARY-0002", "A concrete real-part identity lacks its required authoritative source URI."
    ),
    "AIXEM-DIAG-LIBRARY-PART-PLACEHOLDER-UNDECLARED": DiagnosticDefinition(
        "component-library", "create-symbol", "manual-review", "AIXEM-REQ-LIBRARY-0002", "An unsupported concrete part identity was not declared as a placeholder."
    ),
    "AIXEM-DIAG-LIBRARY-PART-PROVENANCE-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-LIBRARY-0002", "Component-level provenance is incomplete or contradicts the declared provenance status."
    ),
    "AIXEM-DIAG-LIBRARY-COMPONENT-SEMANTIC-CLONE": DiagnosticDefinition(
        "component-library", "create-symbol", "manual-review", "AIXEM-REQ-LIBRARY-0003", "New component identities differ only by identity/display text without a distinct semantic contract."
    ),
    "AIXEM-DIAG-LIBRARY-PART-MINIMUM-ATTRIBUTES-MISSING": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-LIBRARY-0003", "A component does not provide the minimum identity, port, property, provenance, and presentation contract."
    ),
    "AIXEM-DIAG-LIBRARY-PART-PINOUT-REVIEW-MISSING": DiagnosticDefinition(
        "component-library", "validate-project", "manual-review", "AIXEM-REQ-LIBRARY-0005", "A datasheet-backed component lacks source-bound pinout review evidence."
    ),
    "AIXEM-DIAG-LIBRARY-PART-INTENT-REVIEW-INCOMPLETE": DiagnosticDefinition(
        "component-library", "validate-project", "manual-review", "AIXEM-REQ-LIBRARY-0005", "A circuit-intent review claim is incomplete or not bound to the exact component/source state."
    ),
    "AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH": DiagnosticDefinition(
        "layout", "create-schematic", "placement", "AIXEM-REQ-SCHEM-0003", "The serialized layout grid disagrees with the active style-profile snap authority."
    ),
    "AIXEM-DIAG-PIN-SEMANTICS-PROFILE-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0001", "A pin-semantics profile is missing, unsupported, or malformed."
    ),
    "AIXEM-DIAG-PIN-SIGNAL-CLASS-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0002", "A pin uses an unsupported signal-class value."
    ),
    "AIXEM-DIAG-PIN-FUNCTION-TAG-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0002", "A pin functional tag is not a stable lower-kebab semantic token."
    ),
    "AIXEM-DIAG-PIN-POLARITY-INCONSISTENT": DiagnosticDefinition(
        "component-library", "create-symbol", "manual-review", "AIXEM-REQ-PIN-0003", "A pin polarity declaration conflicts with the rest of its declared semantics."
    ),
    "AIXEM-DIAG-PIN-DIFFERENTIAL-PAIR-INCOMPLETE": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0003", "Differential-pair membership is incomplete, duplicated, or inconsistent."
    ),
    "AIXEM-DIAG-PIN-ALTERNATE-FUNCTION-INVALID": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0002", "An alternate-function entry is malformed or attempts to create an extra physical endpoint."
    ),
    "AIXEM-DIAG-PIN-SOURCE-REVIEW-INCOMPLETE": DiagnosticDefinition(
        "component-library", "validate-project", "manual-review", "AIXEM-REQ-PIN-0004", "Detailed pin semantics on a datasheet-backed part are not covered by source-bound review evidence."
    ),
    "AIXEM-DIAG-PIN-NOCONNECT-CONTRADICTION": DiagnosticDefinition(
        "component-library", "create-symbol", "authoritative-source", "AIXEM-REQ-PIN-0003", "A no-connect terminal has contradictory required/connectivity semantics."
    ),
    "AIXEM-DIAG-ERC-OUTPUT-CONFLICT": DiagnosticDefinition(
        "semantic", "validate-project", "manual-review", "AIXEM-REQ-PIN-0005", "A bounded static compatibility check found multiple ordinary output drivers."
    ),
    "AIXEM-DIAG-ERC-POWER-OUTPUT-CONFLICT": DiagnosticDefinition(
        "semantic", "validate-project", "manual-review", "AIXEM-REQ-PIN-0005", "A bounded static compatibility check found multiple local power-output sources."
    ),
    "AIXEM-DIAG-ERC-CONNECTED-NOCONNECT": DiagnosticDefinition(
        "semantic", "validate-project", "authoritative-source", "AIXEM-REQ-PIN-0005", "A terminal declared no-connect participates in a semantic net."
    ),
    "AIXEM-DIAG-ERC-INPUT-ONLY": DiagnosticDefinition(
        "semantic", "validate-project", "manual-review", "AIXEM-REQ-PIN-0005", "A local net contains only receiving endpoints and may be missing an explicit source."
    ),
    "AIXEM-DIAG-ERC-UNCERTAIN-TOPOLOGY": DiagnosticDefinition(
        "semantic", "validate-project", "manual-review", "AIXEM-REQ-PIN-0005", "A multi-driver or unspecified topology cannot receive a bounded compatibility PASS."
    ),
    "AIXEM-DIAG-AGENT-SCOPE-VIOLATION": DiagnosticDefinition(
        "agent-execution", "author-component-circuit", "execution-scope", "AIXEM-REQ-AGENT-AUTHORING-0001", "An agent changed an artifact outside the active route write scope."
    ),
    "AIXEM-DIAG-AGENT-GENERATED-OUTPUT-EDIT": DiagnosticDefinition(
        "agent-execution", "render-review", "execution-scope", "AIXEM-REQ-AGENT-VISUAL-QA-0002", "A generated output was edited before the harness render boundary."
    ),
    "AIXEM-DIAG-AGENT-STALLED-LOOP": DiagnosticDefinition(
        "agent-execution", "author-component-circuit", "manual-review", "AIXEM-REQ-AGENT-0020", "The same blocking diagnostic state survived a repair iteration unchanged."
    ),
    "AIXEM-DIAG-AGENT-OSCILLATING-LOOP": DiagnosticDefinition(
        "agent-execution", "author-component-circuit", "manual-review", "AIXEM-REQ-AGENT-0020", "The authoring loop returned to a previous authoritative/diagnostic state."
    ),
    "AIXEM-DIAG-AGENT-PATH-UNSAFE": DiagnosticDefinition(
        "agent-execution", "author-component-circuit", "execution-scope", "AIXEM-REQ-SEC-0001", "A staged path is unsafe, escapes the workspace, or uses a symbolic link."
    ),
}

RECOMMENDED_P0_CODES = {
    "AIXEM-DIAG-SCHEMA-INVALID",
    "AIXEM-DIAG-SEMANTIC-PORT-UNKNOWN",
    "AIXEM-DIAG-SEMANTIC-NET-ENDPOINT-UNKNOWN",
    "AIXEM-DIAG-SEMANTIC-NET-CLOSURE",
    "AIXEM-DIAG-COMPONENT-TYPE-UNKNOWN",
    "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE",
    "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN",
    "AIXEM-DIAG-BINDING-ASSET-MISSING",
    "AIXEM-DIAG-BINDING-ASSET-DIGEST",
    "AIXEM-DIAG-SYMBOL-PORT-EXPRESSION",
    "AIXEM-DIAG-SYMBOL-PORT-OFF-GRID",
    "AIXEM-DIAG-SYMBOL-PORT-ORIENTATION",
    "AIXEM-DIAG-SYMBOL-LEAD-MISSING",
    "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH",
    "AIXEM-DIAG-SYMBOL-PIN-PITCH",
    "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP",
    "AIXEM-DIAG-LAYOUT-PLACEMENT-MISSING",
    "AIXEM-DIAG-LAYOUT-PLACEMENT-OFF-GRID",
    "AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE",
    "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL",
    "AIXEM-DIAG-ROUTE-VIA-OFF-GRID",
    "AIXEM-DIAG-ROUTE-ZERO-LENGTH",
    "AIXEM-DIAG-JUNCTION-AMBIGUOUS",
    "AIXEM-DIAG-PROJECT-SHEET-UNKNOWN",
    "AIXEM-DIAG-PROJECT-INTERFACE-UNKNOWN",
    "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER",
    "AIXEM-DIAG-PROJECT-NET-MULTIPLE-OWNERSHIP",
    "AIXEM-DIAG-PROJECT-ROUTE-NON-ORTHOGONAL",
    "AIXEM-DIAG-RENDERER-DETERMINISM",
    "AIXEM-DIAG-LIBRARY-PATH-NONCANONICAL",
    "AIXEM-DIAG-LIBRARY-DOMAIN-UNKNOWN",
    "AIXEM-DIAG-LIBRARY-NAME-INVALID",
    "AIXEM-DIAG-LIBRARY-PART-SOURCE-REQUIRED",
    "AIXEM-DIAG-LIBRARY-PART-PROVENANCE-INVALID",
    "AIXEM-DIAG-LIBRARY-COMPONENT-SEMANTIC-CLONE",
    "AIXEM-DIAG-LIBRARY-PART-MINIMUM-ATTRIBUTES-MISSING",
    "AIXEM-DIAG-LIBRARY-PART-PINOUT-REVIEW-MISSING",
    "AIXEM-DIAG-LAYOUT-GRID-PROFILE-MISMATCH",
    "AIXEM-DIAG-PIN-SEMANTICS-PROFILE-INVALID",
    "AIXEM-DIAG-PIN-SIGNAL-CLASS-INVALID",
    "AIXEM-DIAG-PIN-DIFFERENTIAL-PAIR-INCOMPLETE",
    "AIXEM-DIAG-PIN-NOCONNECT-CONTRADICTION",
    "AIXEM-DIAG-ERC-OUTPUT-CONFLICT",
    "AIXEM-DIAG-ERC-POWER-OUTPUT-CONFLICT",
    "AIXEM-DIAG-ERC-CONNECTED-NOCONNECT",
    "AIXEM-DIAG-UNSUPPORTED-CAPABILITY",
}

LEGACY_CODE_MAP: dict[str, str] = {
    "schema": "AIXEM-DIAG-SCHEMA-INVALID",
    "port-expression": "AIXEM-DIAG-SYMBOL-PORT-EXPRESSION",
    "symbol-grid": "AIXEM-DIAG-SYMBOL-PORT-OFF-GRID",
    "port-orientation": "AIXEM-DIAG-SYMBOL-PORT-ORIENTATION",
    "lead-metadata": "AIXEM-DIAG-SYMBOL-LEAD-MISSING",
    "lead-missing": "AIXEM-DIAG-SYMBOL-LEAD-MISSING",
    "lead-port-mismatch": "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH",
    "pin-pitch": "AIXEM-DIAG-SYMBOL-PIN-PITCH",
    "field-body-overlap": "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP",
    "portmap-total": "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE",
    "portmap-direction": "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE",
    "portmap-target": "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN",
    "asset-missing": "AIXEM-DIAG-BINDING-ASSET-MISSING",
    "asset-digest": "AIXEM-DIAG-BINDING-ASSET-DIGEST",
    "fieldmap-source": "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN",
    "placement-missing": "AIXEM-DIAG-LAYOUT-PLACEMENT-MISSING",
    "placement-off-grid": "AIXEM-DIAG-LAYOUT-PLACEMENT-OFF-GRID",
    "route-endpoint": "AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE",
    "route-non-orthogonal": "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL",
    "route-via-off-grid": "AIXEM-DIAG-ROUTE-VIA-OFF-GRID",
    "route-zero-length": "AIXEM-DIAG-ROUTE-ZERO-LENGTH",
    "junction": "AIXEM-DIAG-JUNCTION-AMBIGUOUS",
    "render-drift": "AIXEM-DIAG-RENDERER-DETERMINISM",
    "render": "AIXEM-DIAG-UNSUPPORTED-CAPABILITY",
    "scope-violation": "AIXEM-DIAG-AGENT-SCOPE-VIOLATION",
    "generated-output-edit": "AIXEM-DIAG-AGENT-GENERATED-OUTPUT-EDIT",
    "unsafe-path": "AIXEM-DIAG-AGENT-PATH-UNSAFE",
}

# Order matters: specific renderer/project messages must win over broad terms.
EXCEPTION_RULES: Sequence[tuple[re.Pattern[str], str]] = (
    (re.compile(r"PROJECT_NET_DUPLICATE_MEMBER|repeats .*:@|projectNets/.*/members:.*non-unique", re.I), "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER"),
    (re.compile(r"PROJECT_NET_MEMBER_MULTIPLE_OWNERSHIP|multiple project nets|already belongs to project net", re.I), "AIXEM-DIAG-PROJECT-NET-MULTIPLE-OWNERSHIP"),
    (re.compile(r"PROJECT_NET_UNKNOWN_(?:PORT|INTERFACE)|unknown interface port|references unknown semantic port", re.I), "AIXEM-DIAG-PROJECT-INTERFACE-UNKNOWN"),
    (re.compile(r"PROJECT_(?:NET_)?UNKNOWN_SHEET|unknown parent|references .*sheet", re.I), "AIXEM-DIAG-PROJECT-SHEET-UNKNOWN"),
    (re.compile(r"project route.*non.?orthogonal|PROJECT_ROUTE.*ORTHOGONAL", re.I), "AIXEM-DIAG-PROJECT-ROUTE-NON-ORTHOGONAL"),
    (re.compile(r"unsupported required|unsupported schema URI|unsupported project routing mode", re.I), "AIXEM-DIAG-UNSUPPORTED-CAPABILITY"),
    (re.compile(r"digest mismatch", re.I), "AIXEM-DIAG-BINDING-ASSET-DIGEST"),
    (re.compile(r"symbol asset is missing|asset is missing|library is missing|source is missing|layout is missing", re.I), "AIXEM-DIAG-BINDING-ASSET-MISSING"),
    (re.compile(r"presentation portMap is not total", re.I), "AIXEM-DIAG-BINDING-PORTMAP-INCOMPLETE"),
    (re.compile(r"maps to unknown symbol port|mapped symbol port .* hidden", re.I), "AIXEM-DIAG-BINDING-PORTMAP-TARGET-UNKNOWN"),
    (re.compile(r"unresolved component type|duplicate component type", re.I), "AIXEM-DIAG-COMPONENT-TYPE-UNKNOWN"),
    (re.compile(r"placement closure mismatch|duplicate placement entity", re.I), "AIXEM-DIAG-LAYOUT-PLACEMENT-MISSING"),
    (re.compile(r"grid profile requires orthogonal routes", re.I), "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL"),
    (re.compile(r"route vias are off the .* grid", re.I), "AIXEM-DIAG-ROUTE-VIA-OFF-GRID"),
    (re.compile(r"zero-length", re.I), "AIXEM-DIAG-ROUTE-ZERO-LENGTH"),
    (re.compile(r"semantic nets have no layout connection|does not route all semantic endpoints|outside semantic net|route .* references endpoint", re.I), "AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE"),
    (re.compile(r"unknown interface endpoint", re.I), "AIXEM-DIAG-SEMANTIC-PORT-UNKNOWN"),
    (re.compile(r"endpoint owner does not exist|endpoint port does not exist|malformed endpoint", re.I), "AIXEM-DIAG-SEMANTIC-NET-ENDPOINT-UNKNOWN"),
    (re.compile(r"endpoint .* occurs in both|endpoints both connected and noconn|fewer than two endpoints", re.I), "AIXEM-DIAG-SEMANTIC-NET-CLOSURE"),
    (re.compile(r"schema|is a required property|is not valid under", re.I), "AIXEM-DIAG-SCHEMA-INVALID"),
)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    authority: str
    artifact: str
    location: Mapping[str, Any]
    requirement: str
    remediation_route: str
    repair_class: str
    message: str
    evidence: Mapping[str, Any] = field(default_factory=dict)
    id: str = ""

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "code": self.code,
            "severity": self.severity,
            "authority": self.authority,
            "artifact": self.artifact,
            "location": dict(self.location),
            "requirement": self.requirement,
            "remediationRoute": self.remediation_route,
            "repairClass": self.repair_class,
            "message": self.message,
            "evidence": dict(self.evidence),
        }
        return result


def validate_registry() -> list[str]:
    errors: list[str] = []
    missing = sorted(RECOMMENDED_P0_CODES - set(DIAGNOSTIC_REGISTRY))
    if missing:
        errors.append("missing P0 diagnostic definitions: " + ", ".join(missing))
    for code, definition in sorted(DIAGNOSTIC_REGISTRY.items()):
        if not re.fullmatch(r"AIXEM-DIAG-[A-Z0-9-]+", code):
            errors.append(f"invalid diagnostic code {code}")
        if definition.authority not in AUTHORITY_VALUES:
            errors.append(f"{code}: unknown authority {definition.authority}")
        if definition.repair_class not in REPAIR_CLASS_VALUES:
            errors.append(f"{code}: unknown repair class {definition.repair_class}")
        if not definition.remediation_route:
            errors.append(f"{code}: empty remediation route")
        if not definition.requirement:
            errors.append(f"{code}: empty requirement")
    return errors


def _safe_artifact(value: str | Path | None, workspace_root: Path | None = None) -> str:
    if value is None:
        return "."
    raw = Path(str(value))
    if workspace_root is not None:
        try:
            raw = raw.resolve().relative_to(workspace_root.resolve())
        except (ValueError, OSError):
            pass
    rendered = PurePosixPath(raw.as_posix()).as_posix()
    if rendered.startswith("/"):
        rendered = raw.name
    return rendered or "."


def _split_legacy_path(path_value: str, fallback_artifact: str) -> tuple[str, str | None]:
    """Split the common ``artifact/json/pointer`` legacy shape conservatively."""
    value = path_value.replace("\\", "/")
    if value.startswith("/"):
        return fallback_artifact, value
    known_suffixes = (".aixsym.json", ".aixlib.json", ".aixlayout.json", ".aixproj.json", ".json", ".aixem")
    for suffix in known_suffixes:
        index = value.find(suffix)
        if index >= 0:
            end = index + len(suffix)
            artifact = value[:end]
            pointer = value[end:] or None
            if pointer and not pointer.startswith("/"):
                pointer = "/" + pointer
            return artifact, pointer
    return value or fallback_artifact, None


def _definition(code: str) -> DiagnosticDefinition:
    try:
        return DIAGNOSTIC_REGISTRY[code]
    except KeyError as exc:
        raise ValueError(f"unknown AIXEM diagnostic code: {code}") from exc


def make_diagnostic(
    code: str,
    message: str,
    *,
    severity: str = "error",
    artifact: str | Path | None = None,
    json_pointer: str | None = None,
    object_kind: str | None = None,
    object_id: str | None = None,
    evidence: Mapping[str, Any] | None = None,
    workspace_root: Path | None = None,
) -> Diagnostic:
    definition = _definition(code)
    severity = severity.lower()
    if severity not in SEVERITY_ORDER:
        raise ValueError(f"unsupported diagnostic severity: {severity}")
    location: dict[str, Any] = {}
    if json_pointer:
        location["jsonPointer"] = json_pointer if json_pointer.startswith("/") else "/" + json_pointer
    if object_kind:
        location["objectKind"] = object_kind
    if object_id is not None:
        location["objectId"] = str(object_id)
    if not location:
        location["jsonPointer"] = ""
    return Diagnostic(
        code=code,
        severity=severity,
        authority=definition.authority,
        artifact=_safe_artifact(artifact, workspace_root),
        location=location,
        requirement=definition.requirement,
        remediation_route=definition.remediation_route,
        repair_class=definition.repair_class,
        message=str(message).strip() or definition.summary,
        evidence=dict(evidence or {}),
    )


def normalize_issue(
    issue: Mapping[str, Any] | Any,
    *,
    artifact: str | Path | None = None,
    workspace_root: Path | None = None,
    validator: str | None = None,
) -> Diagnostic:
    if hasattr(issue, "to_dict"):
        issue = issue.to_dict()
    if not isinstance(issue, Mapping):
        raise TypeError(f"issue must be a mapping, got {type(issue).__name__}")
    rich_fields = {
        "code", "severity", "authority", "artifact", "location", "requirement",
        "remediationRoute", "repairClass", "message", "evidence"
    }
    if rich_fields.issubset(issue) and str(issue.get("code")) in DIAGNOSTIC_REGISTRY:
        definition = _definition(str(issue["code"]))
        authority = str(issue["authority"])
        remediation = str(issue["remediationRoute"])
        repair_class = str(issue["repairClass"])
        requirement = str(issue["requirement"])
        if (authority, remediation, repair_class, requirement) != (
            definition.authority, definition.remediation_route, definition.repair_class, definition.requirement
        ):
            raise ValueError(f"diagnostic metadata contradicts registry for {issue['code']}")
        location = dict(issue.get("location") or {"jsonPointer": ""})
        return Diagnostic(
            code=str(issue["code"]),
            severity=str(issue["severity"]),
            authority=authority,
            artifact=_safe_artifact(str(issue["artifact"]), workspace_root),
            location=location,
            requirement=requirement,
            remediation_route=remediation,
            repair_class=repair_class,
            message=str(issue["message"]),
            evidence=dict(issue.get("evidence") or {}),
        )
    legacy_code = str(issue.get("code", "")).strip()
    code = legacy_code if legacy_code in DIAGNOSTIC_REGISTRY else LEGACY_CODE_MAP.get(legacy_code)
    if code is None:
        message = str(issue.get("message", legacy_code))
        code = exception_code(message)
    fallback_artifact = _safe_artifact(artifact, workspace_root)
    issue_path = str(issue.get("path", "")).strip()
    parsed_artifact, pointer = _split_legacy_path(issue_path, fallback_artifact) if issue_path else (fallback_artifact, None)
    location = issue.get("location") if isinstance(issue.get("location"), Mapping) else {}
    evidence = dict(issue.get("evidence", {})) if isinstance(issue.get("evidence"), Mapping) else {}
    if legacy_code:
        evidence.setdefault("legacyCode", legacy_code)
    if validator:
        evidence.setdefault("validator", validator)
    return make_diagnostic(
        code,
        str(issue.get("message", _definition(code).summary)),
        severity=str(issue.get("severity", "error")),
        artifact=parsed_artifact,
        json_pointer=str(location.get("jsonPointer", pointer or "")),
        object_kind=location.get("objectKind") or issue.get("objectKind"),
        object_id=location.get("objectId") or issue.get("objectId"),
        evidence=evidence,
        workspace_root=workspace_root,
    )


def exception_code(message: str) -> str:
    for pattern, code in EXCEPTION_RULES:
        if pattern.search(message):
            return code
    return "AIXEM-DIAG-UNSUPPORTED-CAPABILITY"


def normalize_exception(
    exc: BaseException | str,
    *,
    artifact: str | Path | None = None,
    workspace_root: Path | None = None,
    validator: str | None = None,
) -> Diagnostic:
    message = str(exc).strip()
    code = exception_code(message)
    evidence: dict[str, Any] = {"exceptionType": type(exc).__name__ if isinstance(exc, BaseException) else "message"}
    if validator:
        evidence["validator"] = validator
    # Production renderer schema messages commonly encode label:pointer: prose.
    pointer = None
    match = re.search(r"(?:^|\n)[^\n:]+:(/[^:]*|\$):\s", message)
    if match and match.group(1) != "$":
        pointer = match.group(1)
    return make_diagnostic(
        code,
        message,
        artifact=artifact,
        json_pointer=pointer,
        evidence=evidence,
        workspace_root=workspace_root,
    )


def assign_diagnostic_ids(diagnostics: Iterable[Diagnostic]) -> list[Diagnostic]:
    ordered = sorted(
        diagnostics,
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            item.code,
            item.artifact,
            json.dumps(dict(item.location), ensure_ascii=False, sort_keys=True),
            item.message,
            json.dumps(dict(item.evidence), ensure_ascii=False, sort_keys=True),
        ),
    )
    result: list[Diagnostic] = []
    seen: set[tuple[Any, ...]] = set()
    for item in ordered:
        key = (
            item.code,
            item.severity,
            item.authority,
            item.artifact,
            json.dumps(dict(item.location), ensure_ascii=False, sort_keys=True),
            item.requirement,
            item.remediation_route,
            item.repair_class,
            item.message,
            json.dumps(dict(item.evidence), ensure_ascii=False, sort_keys=True),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(
            Diagnostic(
                **{field_name: getattr(item, field_name) for field_name in (
                    "code", "severity", "authority", "artifact", "location", "requirement",
                    "remediation_route", "repair_class", "message", "evidence"
                )},
                id=f"diag-{len(result) + 1:04d}",
            )
        )
    return result


def normalize_issues(
    issues: Iterable[Mapping[str, Any] | Any],
    *,
    artifact: str | Path | None = None,
    workspace_root: Path | None = None,
    validator: str | None = None,
) -> list[Diagnostic]:
    return assign_diagnostic_ids(
        normalize_issue(item, artifact=artifact, workspace_root=workspace_root, validator=validator)
        for item in issues
    )


def diagnostics_to_dicts(diagnostics: Iterable[Diagnostic]) -> list[dict[str, Any]]:
    return [item.to_dict() for item in assign_diagnostic_ids(diagnostics)]


def blocking_diagnostics(diagnostics: Iterable[Diagnostic | Mapping[str, Any]]) -> list[Diagnostic | Mapping[str, Any]]:
    return [item for item in diagnostics if str(item.severity if isinstance(item, Diagnostic) else item.get("severity", "error")) == "error"]


def diagnostic_state_digest(diagnostics: Iterable[Diagnostic | Mapping[str, Any]]) -> str:
    records = []
    for item in diagnostics:
        value = item.to_dict() if isinstance(item, Diagnostic) else dict(item)
        if value.get("severity", "error") != "error":
            continue
        value.pop("id", None)
        records.append(value)
    records.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    payload = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def registry_as_records() -> list[dict[str, Any]]:
    return [
        {
            "code": code,
            "authority": item.authority,
            "remediationRoute": item.remediation_route,
            "repairClass": item.repair_class,
            "requirement": item.requirement,
            "summary": item.summary,
        }
        for code, item in sorted(DIAGNOSTIC_REGISTRY.items())
    ]
