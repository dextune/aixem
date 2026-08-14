#!/usr/bin/env python3
"""Build the L001-L012 cold-start Agent Evaluation 3 corpus."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "validation" / "agent-evals-3"
CASES = CORPUS / "cases"
FIXED_TIME = "2026-08-12T00:00:00Z"
RELEASE_DATE = "2026-08-12"
CANONICAL_LIBRARY_DIR = "library/electronics/authoring"
CANONICAL_LIBRARY_FILE = f"{CANONICAL_LIBRARY_DIR}/authoring-components.aixlib.json"


def repository_release() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return f"AIXEM-SRP-{version}-{RELEASE_DATE}"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value), encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def stable_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def project_file(workspace: Path) -> Path:
    projects = sorted(workspace.glob("*.aixproj.json"))
    if len(projects) != 1:
        raise RuntimeError(f"expected one top-level project in {workspace}, got {len(projects)}")
    return projects[0]


def copy_start(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if any(part in {"render", "evidence", ".aixem-agent", "__pycache__"} for part in rel.parts):
            continue
        if path.is_dir():
            (destination / rel).mkdir(parents=True, exist_ok=True)
        elif path.is_file() and path.name not in {"README.md", "case.json"}:
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def refresh_locks(workspace: Path) -> None:
    project_path = project_file(workspace)
    project = read_json(project_path)
    project_root = project_path.parent
    for library_path in sorted(workspace.rglob("*.aixlib.json")):
        if any(part in {"render", "evidence"} for part in library_path.relative_to(workspace).parts):
            continue
        library = read_json(library_path)
        changed = False
        for component in library.get("library", {}).get("components", []):
            for presentation in component.get("presentations", []):
                asset = presentation.get("asset", {})
                rel = asset.get("path")
                if not rel:
                    continue
                target = (project_root / PurePosixPath(str(rel))).resolve()
                if target.is_file():
                    observed = sha256_file(target)
                    if asset.get("digest") != observed:
                        asset["digest"] = observed
                        changed = True
        if changed:
            stable_json(library_path, library)
    body = project.get("project", {})
    for ref in body.get("libraries", []):
        target = (project_root / PurePosixPath(ref["path"])).resolve()
        if target.is_file():
            ref["digest"] = sha256_file(target)
    if project.get("schema", "").endswith("/aixproj/2"):
        for sheet in body.get("sheets", []):
            for key in ("source", "layout"):
                target = (project_root / PurePosixPath(sheet[key]["path"])).resolve()
                if target.is_file():
                    sheet[key]["digest"] = sha256_file(target)
    else:
        for key in ("source", "layout"):
            target = (project_root / PurePosixPath(body[key]["path"])).resolve()
            if target.is_file():
                body[key]["digest"] = sha256_file(target)
    stable_json(project_path, project)


def replace_text_tree(root: Path, replacements: dict[str, str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".aixem"}:
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")


def completed_render_digests(source: Path) -> list[str]:
    names = {"resolved-scene.json", "resolved-project-scene.json", "drawing.svg", "project-composite.svg"}
    return sorted({sha256_file(path) for path in source.rglob("*") if path.is_file() and path.name in names})


def invariant(inv_id: str, predicate: str, description: str, arguments: dict[str, Any], required: bool = True) -> dict[str, Any]:
    if predicate in {"validator-pass", "render-deterministic"}:
        basis = [{"type": "task", "pointer": "/completionCriteria/3"}]
    elif predicate == "authority-digest-unchanged":
        basis = [{"type": "task", "pointer": "/writeConstraints/writableAuthorities"}]
    else:
        basis = [{"type": "task", "pointer": "/facts"}]
    return {"id": inv_id, "predicate": predicate, "description": description, "required": required, "arguments": arguments, "basis": basis}


def common_invariants(case_id: str, project: str = "project.aixproj.json") -> list[dict[str, Any]]:
    return [
        invariant(f"{case_id}-VALID", "validator-pass", "The actual final workspace passes full project validation.", {"route": "validate-project", "project": project}),
        invariant(f"{case_id}-RENDER", "render-deterministic", "The actual final workspace renders deterministically three times.", {"project": project, "repeats": 3}),
    ]


def task(
    case_id: str,
    title: str,
    operation: str,
    route: str,
    prompt: str,
    facts: dict[str, Any],
    writable_authorities: list[str],
    writable_paths: list[str],
    expected: list[str],
    project: str = "project.aixproj.json",
) -> dict[str, Any]:
    return {
        "schema": "https://schemas.aixem.org/agent/task/1",
        "formatVersion": "1.0",
        "id": case_id,
        "title": title,
        "operation": operation,
        "routingMode": "fixed",
        "entryRoute": route,
        "activeRoute": route,
        "project": project,
        "prompt": prompt,
        "facts": facts,
        "writeConstraints": {
            "writableAuthorities": writable_authorities,
            "writablePaths": writable_paths,
            "prohibitedPaths": ["render/**", "evidence/**"],
            "requiredValidators": ["agent.live_stage", "agent.evaluation_invariants"],
        },
        "completionCriteria": [
            "Use AGENTS.md and the compiled route packet before editing.",
            "Edit only the authoritative files allowed by the active route.",
            "Run prepare, check, authority-local repair, and close.",
            "Leave zero blocking diagnostics, zero scope violations, and deterministic render evidence.",
        ],
        "expectedArtifacts": expected,
    }


def task_markdown(value: dict[str, Any]) -> str:
    facts = "\n".join(f"- **{key}:** `{json.dumps(item, ensure_ascii=False)}`" for key, item in value["facts"].items())
    criteria = "\n".join(f"- {item}" for item in value["completionCriteria"])
    return f"""# {value['id']} — {value['title']}

{value['prompt']}

## Supplied facts

{facts}

## Required closure

{criteria}

The task file is a request envelope, not a grant of write authority. The active route packet remains authoritative for permitted edits.
"""


def make_case(
    case_id: str,
    title: str,
    category: str,
    source: str,
    task_doc: dict[str, Any],
    mutate: Callable[[Path], None],
    invariants: list[dict[str, Any]],
    expected_diagnostics: list[str],
) -> dict[str, Any]:
    source_path = ROOT / source
    root = CASES / case_id
    root.mkdir(parents=True, exist_ok=True)
    start = root / "start"
    copy_start(source_path, start)
    mutate(start)
    case_doc = {
        "schema": "https://schemas.aixem.org/validation/agent-eval-3-case/1",
        "formatVersion": "1.0",
        "id": case_id,
        "title": title,
        "category": category,
        "startSource": source,
        "generatedAt": FIXED_TIME,
        "expectedInitialDiagnostics": expected_diagnostics,
        "forbiddenCompletedDigests": completed_render_digests(source_path),
        "agentVisible": ["agent-task.json", "TASK.md", "start/**", "compiled reference pack"],
        "evaluatorOnly": ["evaluator/invariants.json", "case.json", "scoring metadata"],
        "completedTargetBundled": False,
    }
    write_json(root / "case.json", case_doc)
    write_json(root / "agent-task.json", task_doc)
    (root / "TASK.md").write_text(task_markdown(task_doc), encoding="utf-8", newline="\n")
    write_json(root / "evaluator" / "invariants.json", {
        "schema": "https://schemas.aixem.org/agent/evaluation-invariant/1",
        "formatVersion": "1.0",
        "caseId": case_id,
        "invariants": invariants,
        "authority": "evaluator-only",
    })
    return {"id": case_id, "title": title, "category": category, "case": f"validation/agent-evals-3/cases/{case_id}/case.json", "task": f"validation/agent-evals-3/cases/{case_id}/agent-task.json", "invariants": f"validation/agent-evals-3/cases/{case_id}/evaluator/invariants.json"}


def mutate_l001(root: Path) -> None:
    replace_text_tree(root, {"authoring:resistor": "live:resistor-l001", "R1": "RX41", "R2": "RX42", "10k": "13k", "22k": "47k", "net link": "net synth_link_41", '"link"': '"synth_link_41"'})
    shutil.rmtree(root / "library", ignore_errors=True)


def mutate_l002(root: Path) -> None:
    replace_text_tree(root, {"authoring:connector-6": "live:connector-l002", "J1": "JX62"})
    shutil.rmtree(root / "library", ignore_errors=True)


def mutate_l003(root: Path) -> None:
    replace_text_tree(root, {"authoring:controller-12": "live:controller-l003", "U1": "UX12", "AXC12": "LVC12"})
    shutil.rmtree(root / "library", ignore_errors=True)


def mutate_l004(root: Path) -> None:
    path = root / "parameterized_variant.aixlayout.json"
    doc = read_json(path)
    placement = doc["layout"]["placements"][1]
    placement["variant"] = "missing-live-variant"
    placement["parameters"] = {"body-height": 12.5}
    stable_json(path, doc)
    refresh_locks(root)


def mutate_l005(root: Path) -> None:
    replace_text_tree(root, {"net bus": "net fabric_l005", '"bus"': '"fabric_l005"', "BUS": "FABRIC-L005"})
    path = root / "multi_terminal_junction.aixlayout.json"
    doc = read_json(path)
    doc["layout"]["connections"][0]["paths"] = doc["layout"]["connections"][0]["paths"][:2]
    stable_json(path, doc)
    refresh_locks(root)


def mutate_l006(root: Path) -> None:
    path = project_file(root)
    doc = read_json(path)
    doc["project"]["projectNets"] = []
    doc["project"]["metadata"]["case"] = "L006"
    stable_json(path, doc)


def mutate_l007(root: Path) -> None:
    path = project_file(root)
    doc = read_json(path)
    doc["project"]["projectNets"] = []
    doc["project"]["metadata"]["case"] = "L007"
    stable_json(path, doc)


def mutate_l008(root: Path) -> None:
    source = ROOT / "examples" / "authoring" / "08-visual-repair" / "fixtures" / "broken-lead-port.aixsym.json"
    broken = read_json(source)
    broken["symbol"]["id"] = "authoring:resistor"
    stable_json(root / CANONICAL_LIBRARY_DIR / "repaired-resistor.aixsym.json", broken)
    refresh_locks(root)


def mutate_l009(root: Path) -> None:
    source = root / "two_terminal_route.aixem"
    source.write_text(source.read_text(encoding="utf-8") + "\nnet misbound_l009 = T1.1 T2.1\n", encoding="utf-8", newline="\n")
    refresh_locks(root)


def mutate_l010(root: Path) -> None:
    path = root / "two_terminal_route.aixlayout.json"
    doc = read_json(path)
    doc["layout"]["connections"][0]["paths"][0]["via"][1][0] = 82.5
    stable_json(path, doc)
    refresh_locks(root)


def mutate_l011(root: Path) -> None:
    path = project_file(root)
    doc = read_json(path)
    members = doc["project"]["projectNets"][0]["members"]
    members.append(dict(members[0]))
    doc["project"]["metadata"]["case"] = "L011"
    stable_json(path, doc)


def mutate_l012(root: Path) -> None:
    path = root / CANONICAL_LIBRARY_DIR / "repaired-resistor.aixsym.json"
    doc = read_json(path)
    for node in doc["symbol"].get("graphics", []):
        if node.get("type") == "text" and node.get("field") in {"reference", "value"}:
            node["x"] = 0
            node["y"] = 0
    stable_json(path, doc)
    refresh_locks(root)


def main() -> int:
    shutil.rmtree(CASES, ignore_errors=True)
    CASES.mkdir(parents=True)
    entries: list[dict[str, Any]] = []

    entries.append(make_case(
        "L001", "New two-pin passive", "creation", "examples/authoring/01-two-pin-passive",
        task("L001", "New two-pin passive", "create", "create-symbol",
             "Create the missing two-pin passive symbol and presentation binding for the supplied RX41/RX42 divider skeleton. Preserve the supplied semantic endpoint intent.",
             {"componentType": "live:resistor-l001", "ports": ["1", "2"], "references": ["RX41", "RX42"], "values": ["13k", "47k"], "semanticNet": "synth_link_41", "gridMm": 2.5},
             ["symbol", "component-library", "project"], ["library/electronics/authoring/resistor.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"],
             ["library/electronics/authoring/resistor.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"]),
        mutate_l001,
        common_invariants("L001") + [
            invariant("L001-PORTS", "symbol-port-set", "The authored passive exposes exactly two electrical ports.", {"path": "library/electronics/authoring/resistor.aixsym.json", "ports": ["1", "2"], "mode": "exact"}),
            invariant("L001-ENTITY", "entity-present", "RX41 remains a semantic resistor instance.", {"source": "two_pin_passive.aixem", "entity": "RX41", "componentType": "live:resistor-l001"}),
            invariant("L001-NET", "local-net-members", "The supplied divider link is preserved.", {"source": "two_pin_passive.aixem", "net": "synth_link_41", "members": ["RX41.2", "RX42.1"], "mode": "exact"}),
        ], ["AIXEM-DIAG-BINDING-ASSET-DIGEST"]))

    entries.append(make_case(
        "L002", "Six-pin connector", "creation", "examples/authoring/02-connector",
        task("L002", "Six-pin connector", "create", "create-symbol",
             "Create the missing six-pin connector symbol and total presentation binding for JX62. Use a 5 mm pin pitch and preserve all supplied endpoints.",
             {"componentType": "live:connector-l002", "reference": "JX62", "pinCount": 6, "ports": ["1", "2", "3", "4", "5", "6"], "pinPitchMm": 5},
             ["symbol", "component-library", "project"], ["library/electronics/authoring/connector-6.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"],
             ["library/electronics/authoring/connector-6.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"]),
        mutate_l002,
        common_invariants("L002") + [
            invariant("L002-PORTS", "symbol-port-set", "The connector exposes all six ports exactly once.", {"path": "library/electronics/authoring/connector-6.aixsym.json", "ports": ["1", "2", "3", "4", "5", "6"], "mode": "exact"}),
            invariant("L002-ENTITY", "entity-present", "JX62 resolves to the requested connector type.", {"source": "connector_6.aixem", "entity": "JX62", "componentType": "live:connector-l002"}),
        ], ["AIXEM-DIAG-BINDING-ASSET-DIGEST"]))

    entries.append(make_case(
        "L003", "Twelve-pin controller", "creation", "examples/authoring/03-multi-pin-ic",
        task("L003", "Twelve-pin controller", "create", "create-symbol",
             "Create the missing twelve-pin controller symbol and complete presentation binding for UX12. Group power, control, signal, and no-connect pins without changing endpoint identities.",
             {"componentType": "live:controller-l003", "reference": "UX12", "value": "LVC12", "pinCount": 12, "ports": [str(i) for i in range(1, 13)], "pinPitchMm": 5},
             ["symbol", "component-library", "project"], ["library/electronics/authoring/controller-12.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"],
             ["library/electronics/authoring/controller-12.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"]),
        mutate_l003,
        common_invariants("L003") + [
            invariant("L003-PORTS", "symbol-port-set", "The controller exposes the complete 1-12 endpoint set.", {"path": "library/electronics/authoring/controller-12.aixsym.json", "ports": [str(i) for i in range(1, 13)], "mode": "exact"}),
            invariant("L003-ENTITY", "entity-present", "UX12 resolves to the requested controller type.", {"source": "controller_12.aixem", "entity": "UX12", "componentType": "live:controller-l003"}),
        ], ["AIXEM-DIAG-BINDING-ASSET-DIGEST"]))

    entries.append(make_case(
        "L004", "Parameterized variant instance", "creation", "examples/authoring/04-parameterized-variant",
        task("L004", "Parameterized variant instance", "modify", "create-schematic",
             "Repair the invalid placement selection by using the existing IEC variant for R2 with body-height 12.5. Do not alter the reusable symbol, component library, or semantic source.",
             {"entity": "R2", "variant": "iec", "parameters": {"body-height": 12.5}, "precedence": "placement overrides variant defaults"},
             ["layout", "project"], ["parameterized_variant.aixlayout.json", "project.aixproj.json"], ["parameterized_variant.aixlayout.json", "project.aixproj.json"]),
        mutate_l004,
        common_invariants("L004") + [
            invariant("L004-PRESERVE", "authority-digest-unchanged", "Semantic, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "symbol", "component-library"]}),
        ], ["AIXEM-DIAG-UNSUPPORTED-CAPABILITY"]))

    entries.append(make_case(
        "L005", "Three-terminal semantic net", "creation", "examples/authoring/07-multi-terminal-junction",
        task("L005", "Three-terminal semantic net", "modify", "route-nets",
             "Complete the missing branch for semantic net fabric_l005 with an explicit junction. Preserve the separate crossing net and do not infer connectivity from geometry.",
             {"net": "fabric_l005", "members": ["T1.1", "T2.1", "T3.1"], "junction": [75, 50], "crossingNet": "cross"},
             ["layout", "project"], ["multi_terminal_junction.aixlayout.json", "project.aixproj.json"], ["multi_terminal_junction.aixlayout.json", "project.aixproj.json"]),
        mutate_l005,
        common_invariants("L005") + [
            invariant("L005-NET", "local-net-members", "Semantic membership remains exactly the supplied three terminals.", {"source": "multi_terminal_junction.aixem", "net": "fabric_l005", "members": ["T1.1", "T2.1", "T3.1"], "mode": "exact"}),
            invariant("L005-PRESERVE", "authority-digest-unchanged", "Semantic, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "symbol", "component-library"]}),
        ], ["AIXEM-DIAG-ROUTE-ENDPOINT-CLOSURE"]))

    entries.append(make_case(
        "L006", "Two-sheet hierarchical composition", "creation", "validation/corpus/hierarchical-project-1/cases/H001-two-sheet-power-+-control",
        task("L006", "Two-sheet hierarchical composition", "modify", "compose-project",
             "Create the three missing explicit project nets for the existing power and control leaf sheets. Use the supplied interface memberships; never connect by equal names or geometry.",
             {"projectNets": {"rail_live_56": ["power@VCC", "control@VCC"], "return_live_56": ["power@GND", "control@GND"], "command_live_56": ["power@OUT", "control@IN"]}},
             ["project"], ["project.aixproj.json"], ["project.aixproj.json"]),
        mutate_l006,
        common_invariants("L006") + [
            invariant("L006-RAIL", "project-net-members", "The supply project net binds both explicit VCC interfaces.", {"project": "project.aixproj.json", "net": "rail_live_56", "members": ["power@VCC", "control@VCC"], "mode": "exact"}),
            invariant("L006-RETURN", "project-net-members", "The return project net binds both explicit GND interfaces.", {"project": "project.aixproj.json", "net": "return_live_56", "members": ["power@GND", "control@GND"], "mode": "exact"}),
            invariant("L006-CMD", "project-net-members", "The command project net binds OUT to IN.", {"project": "project.aixproj.json", "net": "command_live_56", "members": ["power@OUT", "control@IN"], "mode": "exact"}),
            invariant("L006-PRESERVE", "authority-digest-unchanged", "Leaf semantic, layout, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "layout", "symbol", "component-library"]}),
        ], []))

    entries.append(make_case(
        "L007", "Same-name local nets", "creation", "validation/corpus/hierarchical-project-1/cases/H004-same-name-local-nets-not-connected",
        task("L007", "Same-name local nets", "modify", "compose-project",
             "Add only the explicit common_return_77 project net between alpha.GND and beta.GND. Keep the same-name local vcc nets namespace-isolated and do not create a VCC project net.",
             {"projectNet": "common_return_77", "members": ["alpha@GND", "beta@GND"], "mustRemainLocal": ["alpha:vcc", "beta:vcc"]},
             ["project"], ["project.aixproj.json"], ["project.aixproj.json"]),
        mutate_l007,
        common_invariants("L007") + [
            invariant("L007-RETURN", "project-net-members", "Only explicit GND interfaces are joined by the requested project net.", {"project": "project.aixproj.json", "net": "common_return_77", "members": ["alpha@GND", "beta@GND"], "mode": "exact"}),
            invariant("L007-ALPHA", "local-net-members", "Alpha vcc remains local to alpha.", {"source": "circuits/alpha.aixem", "net": "vcc", "members": ["U1.9", "@VCC"], "mode": "exact"}),
            invariant("L007-BETA", "local-net-members", "Beta vcc remains local to beta.", {"source": "circuits/beta.aixem", "net": "vcc", "members": ["U1.9", "@VCC"], "mode": "exact"}),
            invariant("L007-PRESERVE", "authority-digest-unchanged", "Leaf semantic, layout, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "layout", "symbol", "component-library"]}),
        ], []))

    entries.append(make_case(
        "L008", "Broken lead and port", "repair", "examples/authoring/08-visual-repair",
        task("L008", "Broken lead and port", "repair", "create-symbol",
             "Repair the symbol lead endpoint so the visible lead and electrical port coincide. Modify only symbol authority and required digest locks.",
             {"diagnostic": "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH", "symbol": "library/electronics/authoring/repaired-resistor.aixsym.json"},
             ["symbol", "component-library", "project"], ["library/electronics/authoring/repaired-resistor.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"], ["library/electronics/authoring/repaired-resistor.aixsym.json", "project.aixproj.json"]),
        mutate_l008,
        common_invariants("L008") + [
            invariant("L008-DIAG", "diagnostic-absent", "The lead/port mismatch diagnostic is absent.", {"route": "create-symbol", "project": "project.aixproj.json", "code": "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH"}),
            invariant("L008-PRESERVE", "authority-digest-unchanged", "Semantic and layout authorities remain unchanged.", {"authorities": ["semantic", "layout"]}),
        ], ["AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH"]))

    entries.append(make_case(
        "L009", "Correct-looking route on wrong semantic net", "repair", "examples/authoring/06-two-terminal-route",
        task("L009", "Correct-looking route on wrong semantic net", "repair", "create-schematic",
             "Remove the contradictory semantic membership misbound_l009 while preserving the valid signal net and existing layout geometry.",
             {"diagnostic": "AIXEM-DIAG-SEMANTIC-NET-CLOSURE", "validNet": "signal", "invalidNet": "misbound_l009", "members": ["T1.1", "T2.1"]},
             ["semantic", "project"], ["two_terminal_route.aixem", "project.aixproj.json"], ["two_terminal_route.aixem", "project.aixproj.json"]),
        mutate_l009,
        common_invariants("L009") + [
            invariant("L009-DIAG", "diagnostic-absent", "The semantic closure diagnostic is absent.", {"route": "create-schematic", "project": "project.aixproj.json", "code": "AIXEM-DIAG-SEMANTIC-NET-CLOSURE"}),
            invariant("L009-NET", "local-net-members", "The valid semantic signal membership is preserved.", {"source": "two_terminal_route.aixem", "net": "signal", "members": ["T1.1", "T2.1"], "mode": "exact"}),
            invariant("L009-PRESERVE", "authority-digest-unchanged", "Layout, symbol, and library authorities remain unchanged.", {"authorities": ["layout", "symbol", "component-library"]}),
        ], ["AIXEM-DIAG-SEMANTIC-NET-CLOSURE"]))

    entries.append(make_case(
        "L010", "Off-grid non-orthogonal route", "repair", "examples/authoring/06-two-terminal-route",
        task("L010", "Off-grid non-orthogonal route", "repair", "route-nets",
             "Repair the non-orthogonal route using grid-aligned layout geometry. Do not change semantic net membership or component presentation.",
             {"diagnostic": "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL", "gridMm": 2.5, "net": "signal"},
             ["layout", "project"], ["two_terminal_route.aixlayout.json", "project.aixproj.json"], ["two_terminal_route.aixlayout.json", "project.aixproj.json"]),
        mutate_l010,
        common_invariants("L010") + [
            invariant("L010-DIAG", "diagnostic-absent", "The non-orthogonal route diagnostic is absent.", {"route": "route-nets", "project": "project.aixproj.json", "code": "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL"}),
            invariant("L010-PRESERVE", "authority-digest-unchanged", "Semantic, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "symbol", "component-library"]}),
        ], ["AIXEM-DIAG-ROUTE-NON-ORTHOGONAL"]))

    entries.append(make_case(
        "L011", "Duplicate project-net member", "repair", "validation/corpus/hierarchical-project-1/cases/H001-two-sheet-power-+-control",
        task("L011", "Duplicate project-net member", "repair", "compose-project",
             "Remove the duplicated project-net member without changing any leaf circuit, sheet layout, or other project-net membership.",
             {"diagnostic": "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER", "projectNet": "vcc_5v"},
             ["project"], ["project.aixproj.json"], ["project.aixproj.json"]),
        mutate_l011,
        common_invariants("L011") + [
            invariant("L011-DIAG", "diagnostic-absent", "The duplicate-member diagnostic is absent.", {"route": "compose-project", "project": "project.aixproj.json", "code": "AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER"}),
            invariant("L011-VCC", "project-net-members", "The VCC project net retains exactly its two intended members.", {"project": "project.aixproj.json", "net": "vcc_5v", "members": ["power@VCC", "control@VCC"], "mode": "exact"}),
            invariant("L011-PRESERVE", "authority-digest-unchanged", "Leaf semantic, layout, symbol, and library authorities remain unchanged.", {"authorities": ["semantic", "layout", "symbol", "component-library"]}),
        ], ["AIXEM-DIAG-PROJECT-NET-DUPLICATE-MEMBER"]))

    entries.append(make_case(
        "L012", "Field and body overlap", "repair", "examples/authoring/08-visual-repair",
        task("L012", "Field and body overlap", "repair", "create-symbol",
             "Move reference and value fields outside the body according to the symbol design profile. Preserve all endpoint semantics and route geometry.",
             {"diagnostic": "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP", "fields": ["reference", "value"], "symbol": "library/electronics/authoring/repaired-resistor.aixsym.json"},
             ["symbol", "component-library", "project"], ["library/electronics/authoring/repaired-resistor.aixsym.json", "library/electronics/authoring/authoring-components.aixlib.json", "project.aixproj.json"], ["library/electronics/authoring/repaired-resistor.aixsym.json", "project.aixproj.json"]),
        mutate_l012,
        common_invariants("L012") + [
            invariant("L012-DIAG", "diagnostic-absent", "The field/body overlap diagnostic is absent.", {"route": "create-symbol", "project": "project.aixproj.json", "code": "AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP"}),
            invariant("L012-PRESERVE", "authority-digest-unchanged", "Semantic and layout authorities remain unchanged.", {"authorities": ["semantic", "layout"]}),
        ], ["AIXEM-DIAG-SYMBOL-FIELD-BODY-OVERLAP"]))

    manifest = {
        "schema": "https://schemas.aixem.org/validation/agent-eval-3-corpus/1",
        "formatVersion": "1.1",
        "id": "agent-evals-3",
        "corpusId": "agent-evals-3",
        "corpusRevision": "1.1",
        "baselineRelease": "AIXEM-SRP-0.5.8.1-2026-08-12",
        "protocolVersion": "1.0",
        "release": repository_release(),
        "repositoryRelease": repository_release(),
        "generatedAt": FIXED_TIME,
        "cases": entries,
        "summary": {"cases": len(entries), "creation": sum(item["category"] == "creation" for item in entries), "repair": sum(item["category"] == "repair" for item in entries)},
        "completedTargetsBundled": False,
        "evaluatorDataStaged": False,
        "tierAProtocolAvailable": True,
        "tierBRequiresExplicitExternalExecutor": True,
        "liveExternalAgentExecuted": False,
    }
    write_json(CORPUS / "manifest.json", manifest)
    case_links = "\n".join(
        f"- [{item['id']} — {item['title']}](cases/{item['id']}/TASK.md)"
        for item in entries
    )
    readme = f"""# Agent Evaluation 3 — Cold-Start Corpus

L001-L012 are incomplete, fresh-start authoring tasks. `agent-task.json`, `TASK.md`, and `start/` are agent-visible inputs. `evaluator/invariants.json` and `case.json` remain evaluator-only and are never copied into a cold-start stage.

The corpus contains no completed target workspace or completed target render. Creation tasks are L001-L007; repair tasks are L008-L012. Agent Evaluation 2 remains historical deterministic Tier A replay and is not reused as live evidence.

## Registered Cases

{case_links}

The links above are part of the repository root reference chain. The corpus builder MUST reproduce them so rebuilding the suite cannot isolate any human-authored `TASK.md`.
"""
    (CORPUS / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    print(json.dumps(manifest["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
