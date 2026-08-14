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
from render_project import GridProjectRenderer  # noqa: E402


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


def relock_layout(project_root: Path, layout_path: Path) -> None:
    project_path = project_root / "project.aixproj.json"
    project = read_json(project_path)
    expected_path = layout_path.relative_to(project_root).as_posix()
    layout_ref = project["project"]["layout"]
    if layout_ref["path"] != expected_path:
        raise AssertionError(f"project layout path {layout_ref['path']} != {expected_path}")
    layout_ref["digest"] = sha256_file(layout_path)
    write_json(project_path, project)


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

    def test_schematic_uniform_scaling_rebinds_route_endpoint(self) -> None:
        source = AUTHORING / "01-two-pin-passive"
        baseline = GridProjectRenderer(source / "project.aixproj.json", SCHEMA_ROOT)
        baseline_route = baseline.layout["connections"][0]["paths"][0]
        baseline_start = baseline._resolve_route_end(baseline_route["from"])

        with tempfile.TemporaryDirectory(prefix="aixem-uniform-scale-") as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(source, root)
            layout_path = root / "two_pin_passive.aixlayout.json"
            layout = read_json(layout_path)
            placement = next(item for item in layout["layout"]["placements"] if item["entity"] == "R1")
            placement["scaleX"] = 1.5
            placement["scaleY"] = 1.5
            write_json(layout_path, layout)
            relock_layout(root, layout_path)

            scaled = GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
            route = scaled.layout["connections"][0]["paths"][0]
            scaled_start = scaled._resolve_route_end(route["from"])
            self.assertEqual(scaled_start, scaled.bindings["R1"].port_positions["2"])
            self.assertNotEqual(scaled_start, baseline_start)
            origin_x = float(placement["x"])
            self.assertAlmostEqual(scaled_start[0] - origin_x, (baseline_start[0] - origin_x) * 1.5)
            self.assertAlmostEqual(scaled_start[1], baseline_start[1])
            svg, _scene = scaled.build_svg()
            self.assertIn('data-entity="R1"', svg)

    def test_grid_renderer_rejects_nonuniform_or_negative_scale_without_restricting_core_affine_support(self) -> None:
        source = AUTHORING / "01-two-pin-passive"
        with tempfile.TemporaryDirectory(prefix="aixem-scale-policy-") as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(source, root)
            layout_path = root / "two_pin_passive.aixlayout.json"
            layout = read_json(layout_path)
            placement = next(item for item in layout["layout"]["placements"] if item["entity"] == "R1")
            placement["scaleX"] = 1.5
            placement["scaleY"] = 1.0
            write_json(layout_path, layout)
            relock_layout(root, layout_path)

            core = ProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
            self.assertEqual(core.bindings["R1"].placement["scaleX"], 1.5)
            with self.assertRaisesRegex(Exception, "uniform component scaling"):
                GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)

            layout = read_json(layout_path)
            placement = next(item for item in layout["layout"]["placements"] if item["entity"] == "R1")
            placement["scaleX"] = -1.0
            placement["scaleY"] = -1.0
            write_json(layout_path, layout)
            relock_layout(root, layout_path)
            with self.assertRaisesRegex(Exception, "finite positive uniform component scaling"):
                GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)

    def test_scaled_endpoint_keeps_explicit_vias_authored_and_fails_closed_until_rerouted(self) -> None:
        source = AUTHORING / "01-two-pin-passive"
        with tempfile.TemporaryDirectory(prefix="aixem-scale-reroute-") as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(source, root)
            layout_path = root / "two_pin_passive.aixlayout.json"

            baseline = GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
            baseline_route = baseline.layout["connections"][0]["paths"][0]
            start = baseline._resolve_route_end(baseline_route["from"])
            end = baseline._resolve_route_end(baseline_route["to"])

            layout = read_json(layout_path)
            route = layout["layout"]["connections"][0]["paths"][0]
            escape_y = start[1] + 5.0
            route["via"] = [[start[0], escape_y], [end[0], escape_y]]
            write_json(layout_path, layout)
            relock_layout(root, layout_path)
            GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)

            layout = read_json(layout_path)
            placement = next(item for item in layout["layout"]["placements"] if item["entity"] == "R1")
            placement["scaleX"] = 1.5
            placement["scaleY"] = 1.5
            write_json(layout_path, layout)
            relock_layout(root, layout_path)

            core = ProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
            moved_start = core.bindings["R1"].port_positions["2"]
            with self.assertRaisesRegex(Exception, "orthogonal routes"):
                GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)

            layout = read_json(layout_path)
            route = layout["layout"]["connections"][0]["paths"][0]
            route["via"][0][0] = moved_start[0]
            write_json(layout_path, layout)
            relock_layout(root, layout_path)
            repaired = GridProjectRenderer(root / "project.aixproj.json", SCHEMA_ROOT)
            self.assertEqual(repaired._resolve_route_end(route["from"]), moved_start)

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
