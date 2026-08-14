"""Public renderer precedence and fail-closed binding contract tests."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "docs"))
sys.path.insert(0, str(ROOT / "implementation" / "schematic"))

from authoring_validation import AUTHORING, SCHEMA_ROOT, validate_renderer_contract_examples  # noqa: E402
from component_core import ProjectRenderer, sha256_file  # noqa: E402


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def relock_library(project_root: Path, library_path: Path) -> None:
    project_path = project_root / "project.aixproj.json"
    project = read_json(project_path)
    for entry in project["project"]["libraries"]:
        if entry["path"] == library_path.relative_to(project_root).as_posix():
            entry["digest"] = sha256_file(library_path)
    write_json(project_path, project)


def relock_symbol(project_root: Path, library_path: Path, symbol_path: Path) -> None:
    library = read_json(library_path)
    relative_symbol = symbol_path.relative_to(project_root).as_posix()
    for component in library["library"]["components"]:
        for presentation in component["presentations"]:
            if presentation["asset"]["path"] == relative_symbol:
                presentation["asset"]["digest"] = sha256_file(symbol_path)
    write_json(library_path, library)
    relock_library(project_root, library_path)


class RendererContractTests(unittest.TestCase):
    def test_variant_and_parameter_precedence(self) -> None:
        result = validate_renderer_contract_examples()
        self.assertTrue(result["valid"], result["issues"])
        scene = read_json(AUTHORING / "04-parameterized-variant" / "render" / "resolved-scene.json")
        entities = {item["key"]: item for item in scene["entities"]}
        self.assertEqual(entities["R1"]["variant"], "ansi")
        self.assertEqual(entities["R2"]["variant"], "iec")
        self.assertEqual(entities["R1"]["parameters"]["body-length"], 30)
        self.assertEqual(entities["R2"]["parameters"]["body-height"], 10)

    def test_field_precedence(self) -> None:
        root = AUTHORING / "05-field-and-port-binding"
        renderer = ProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
        fields = renderer.bindings["S1"].fields
        self.assertEqual(fields["reference"], "S1")
        self.assertEqual(fields["value"], "5V_OVERRIDE")
        self.assertEqual(fields["deviceLabel"], "TEMP")

    def test_port_map_direction_totality_and_visibility(self) -> None:
        root = AUTHORING / "05-field-and-port-binding"
        renderer = ProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
        binding = renderer.bindings["S1"]
        self.assertEqual(binding.presentation["portMap"], {"in": "p-left", "out": "p-right"})
        self.assertEqual(set(binding.port_positions), {"in", "out"})
        self.assertTrue(all(value is not None for value in binding.port_positions.values()))

    def test_fail_closed_binding_cases(self) -> None:
        source = AUTHORING / "05-field-and-port-binding"
        cases = []
        with tempfile.TemporaryDirectory(prefix="aixem-binding-cases-") as temporary:
            temp_root = Path(temporary)

            # Incomplete semantic port map.
            incomplete = temp_root / "incomplete"
            shutil.copytree(source, incomplete)
            library_path = incomplete / "library" / "electronics" / "authoring" / "authoring-components.aixlib.json"
            library = read_json(library_path)
            library["library"]["components"][0]["presentations"][0]["portMap"].pop("out")
            write_json(library_path, library)
            relock_library(incomplete, library_path)
            with self.assertRaises(Exception) as caught:
                ProjectRenderer(incomplete / "project.aixproj.json", SCHEMA_ROOT)
            cases.append(str(caught.exception))

            # Unknown symbol port target.
            unknown = temp_root / "unknown"
            shutil.copytree(source, unknown)
            library_path = unknown / "library" / "electronics" / "authoring" / "authoring-components.aixlib.json"
            library = read_json(library_path)
            library["library"]["components"][0]["presentations"][0]["portMap"]["out"] = "missing-port"
            write_json(library_path, library)
            relock_library(unknown, library_path)
            with self.assertRaises(Exception) as caught:
                ProjectRenderer(unknown / "project.aixproj.json", SCHEMA_ROOT)
            cases.append(str(caught.exception))

            # Required mapped port hidden by symbol state.
            hidden = temp_root / "hidden"
            shutil.copytree(source, hidden)
            library_path = hidden / "library" / "electronics" / "authoring" / "authoring-components.aixlib.json"
            symbol_path = hidden / "library" / "electronics" / "authoring" / "sensor.aixsym.json"
            symbol = read_json(symbol_path)
            target = next(port for port in symbol["symbol"]["ports"] if port["id"] == "p-right")
            target["visibleWhen"] = False
            write_json(symbol_path, symbol)
            relock_symbol(hidden, library_path, symbol_path)
            with self.assertRaises(Exception) as caught:
                ProjectRenderer(hidden / "project.aixproj.json", SCHEMA_ROOT)
            cases.append(str(caught.exception))

        combined = "\n".join(cases).lower()
        self.assertIn("portmap", combined)
        self.assertTrue("hidden" in combined or "visible" in combined)


if __name__ == "__main__":
    unittest.main()
