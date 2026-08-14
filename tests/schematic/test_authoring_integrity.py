"""Focused AIXEM 0.5.9 authoring-integrity conformance tests."""
from __future__ import annotations

import copy
import json
import unittest

from implementation.schematic.authoring_integrity import (
    DIAG_ERC_CONNECTED_NOCONNECT,
    DIAG_ERC_OUTPUT_CONFLICT,
    DIAG_ERC_POWER_OUTPUT_CONFLICT,
    DIAG_LAYOUT_GRID_PROFILE_MISMATCH,
    DIAG_LIBRARY_COMPONENT_SEMANTIC_CLONE,
    DIAG_LIBRARY_DOMAIN_UNKNOWN,
    DIAG_LIBRARY_NAME_INVALID,
    DIAG_LIBRARY_PART_INTENT_REVIEW_INCOMPLETE,
    DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING,
    DIAG_LIBRARY_PART_PROVENANCE_INVALID,
    DIAG_LIBRARY_PART_SOURCE_REQUIRED,
    DIAG_LIBRARY_PATH_NONCANONICAL,
    DIAG_PIN_DIFFERENTIAL_PAIR_INCOMPLETE,
    DIAG_PIN_NOCONNECT_CONTRADICTION,
    DIAG_PIN_SEMANTICS_PROFILE_INVALID,
    PIN_SEMANTICS_PROFILE,
    aggregate_validation_claims,
    bounded_compatibility_precheck,
    ceil_to_grid,
    choose_existing_namespace,
    component_signatures,
    detect_semantic_clones,
    minimum_pin_group_span,
    validate_circuit_intent_review,
    validate_component,
    validate_component_pin_semantics,
    validate_layout_profile_grid,
    validate_library_artifact_path,
    validate_library_document,
    validate_minimum_component_contract,
    validate_part_provenance,
    validate_part_review_evidence,
    validate_pin_semantics,
)


def generic_component(component_id: str = "aixem:resistor") -> dict:
    return {
        "id": component_id,
        "displayName": "Generic resistor",
        "kind": "passive",
        "description": "Generic two-terminal resistor template.",
        "classification": [],
        "metadata": {
            "semanticReady": True,
            "partProvenance": {"status": "generic-template"},
        },
        "ports": [
            {"id": "1", "name": "1", "terminal": "1", "type": "passive", "required": False},
            {"id": "2", "name": "2", "terminal": "2", "type": "passive", "required": False},
        ],
        "properties": [
            {"id": "refdes", "type": "string", "required": False},
            {"id": "value", "type": "string", "required": False},
        ],
        "presentations": [{
            "purpose": "primary-diagram",
            "asset": {
                "path": "library/electronics/passive/resistor/resistor-iec.aixsym.json",
                "digest": "sha256:" + "1" * 64,
                "symbolId": "aixem:resistor-iec",
                "revision": "1.0.0",
            },
            "portMap": {"1": "1", "2": "2"},
            "fieldMap": {"reference": "refdes", "value": "value"},
        }],
    }


def concrete_component(component_id: str = "vendor:abc123") -> dict:
    value = generic_component(component_id)
    value["displayName"] = "ABC123"
    value["description"] = "Concrete two-terminal source-backed device."
    value["metadata"] = {
        "semanticReady": True,
        "partProvenance": {
            "status": "datasheet-backed",
            "manufacturer": "Example Semiconductor",
            "partNumber": "ABC123",
            "sourceKind": "manufacturer-datasheet",
            "sourceUri": "https://vendor.example/datasheets/abc123.pdf",
            "sourceDigest": "sha256:" + "2" * 64,
        },
    }
    return value


def review_evidence(component: dict, library_digest: str = "sha256:" + "3" * 64) -> dict:
    return {
        "componentId": component["id"],
        "libraryDigest": library_digest,
        "symbolDigests": ["sha256:" + "1" * 64],
        "sourceUri": component["metadata"]["partProvenance"]["sourceUri"],
        "sourceDigest": component["metadata"]["partProvenance"]["sourceDigest"],
        "pinSemanticsProfile": PIN_SEMANTICS_PROFILE,
        "result": "PASS",
        "checks": {
            "identity": True,
            "pinNumbers": True,
            "pinNamesAndFunctions": True,
            "portTypes": True,
            "minimumProperties": True,
            "presentationBinding": True,
            "pinSemantics": True,
        },
    }


def intent_evidence(component: dict, library_digest: str = "sha256:" + "3" * 64) -> dict:
    return {
        "componentId": component["id"],
        "libraryDigest": library_digest,
        "result": "PASS",
        "checks": {
            "functionalRole": True,
            "intendedConnectedPins": True,
            "requiredPins": True,
            "deliberateNoConnects": True,
            "taskRelevantProperties": True,
            "endpointPreservingPresentation": True,
        },
    }


class LibraryPathTests(unittest.TestCase):
    def codes(self, path: str, **kwargs) -> set[str]:
        return {issue.code for issue in validate_library_artifact_path(path, **kwargs)}

    def test_lby001_new_electronics_path(self) -> None:
        self.assertEqual([], validate_library_artifact_path("library/electronics/passive/resistor/resistors.aixlib.json"))
        self.assertEqual([], validate_library_artifact_path("library/electronics/passive/resistor/resistor-iec.aixsym.json"))

    def test_lby002_new_architecture_path(self) -> None:
        self.assertEqual([], validate_library_artifact_path("library/architecture/opening/door/door-symbols.aixlib.json"))
        self.assertEqual([], validate_library_artifact_path("library/architecture/opening/door/single-leaf-door.aixsym.json"))

    def test_lby003_unknown_domain(self) -> None:
        self.assertIn(DIAG_LIBRARY_DOMAIN_UNKNOWN, self.codes("library/mechanical/fastener/bolts.aixlib.json"))

    def test_lby004_examples_location_rejected(self) -> None:
        self.assertIn(DIAG_LIBRARY_PATH_NONCANONICAL, self.codes("examples/parts/resistor.aixsym.json"))

    def test_lby004_fixture_owner_exception_still_requires_library_root(self) -> None:
        self.assertIn(DIAG_LIBRARY_PATH_NONCANONICAL, self.codes("examples/parts/resistor.aixsym.json", task_owns_fixture_area=True))

    def test_lby005_existing_legacy_repair(self) -> None:
        self.assertEqual([], validate_library_artifact_path("libraries/authoring.aixlib.json", operation="modified"))
        self.assertEqual([], validate_library_artifact_path("symbols/resistor.aixsym.json", operation="modified"))

    def test_lby006_new_legacy_root_rejected(self) -> None:
        self.assertIn(DIAG_LIBRARY_PATH_NONCANONICAL, self.codes("libraries/new-part.aixlib.json"))

    def test_lby007_invalid_namespace_and_filename(self) -> None:
        codes = self.codes("library/electronics/Power Parts/New_Resistor.aixsym.json")
        self.assertIn(DIAG_LIBRARY_NAME_INVALID, codes)

    def test_context_free_filename_rejected(self) -> None:
        self.assertIn(DIAG_LIBRARY_NAME_INVALID, self.codes("library/electronics/passive/library.aixlib.json"))

    def test_unsafe_path_rejected(self) -> None:
        self.assertIn(DIAG_LIBRARY_PATH_NONCANONICAL, self.codes("library/electronics/../parts/foo.aixlib.json"))

    def test_lby008_namespace_reuse(self) -> None:
        existing = ["passive/resistor", "integrated-circuit/microcontroller"]
        self.assertEqual("passive/resistor", choose_existing_namespace(existing, "passive-components/resistors"))

    def test_namespace_choice_is_deterministic(self) -> None:
        existing = ["passives/resistors", "passive/resistor"]
        first = choose_existing_namespace(existing, "passive-components/resistors")
        second = choose_existing_namespace(reversed(existing), "passive-components/resistors")
        self.assertEqual(first, second)


class SizingAndGridTests(unittest.TestCase):
    def test_outward_grid_quantization(self) -> None:
        self.assertEqual(12.5, ceil_to_grid(10.1, 2.5))
        self.assertEqual(10.0, ceil_to_grid(10.0, 2.5))

    def test_invalid_sizing_input_fails(self) -> None:
        with self.assertRaises(ValueError):
            ceil_to_grid(-1, 2.5)
        with self.assertRaises(ValueError):
            minimum_pin_group_span(0)

    def test_repeated_pin_group_span(self) -> None:
        self.assertEqual(30.0, minimum_pin_group_span(6, 5.0, 2.5))
        self.assertEqual(5.0, minimum_pin_group_span(1, 5.0, 2.5))

    def test_grid_profile_coherent(self) -> None:
        layout = {"layout": {"coordinateSystem": {"grid": 2.5}}}
        profile = {"styleProfile": {"grid": {"snap": 2.5, "minor": 2.5, "major": 10}, "symbol": {"pinPitch": 5}}}
        self.assertEqual([], validate_layout_profile_grid(layout, profile))

    def test_g005_grid_profile_mismatch(self) -> None:
        layout = {"layout": {"coordinateSystem": {"grid": 5}}}
        profile = {"styleProfile": {"grid": {"snap": 2.5, "minor": 2.5, "major": 10}, "symbol": {"pinPitch": 5}}}
        self.assertEqual(DIAG_LAYOUT_GRID_PROFILE_MISMATCH, validate_layout_profile_grid(layout, profile)[0].code)

    def test_non_integral_profile_ratios_fail(self) -> None:
        layout = {"layout": {"coordinateSystem": {"grid": 2.5}}}
        profile = {"styleProfile": {"grid": {"snap": 2.5, "minor": 2.5, "major": 9}, "symbol": {"pinPitch": 4}}}
        issues = validate_layout_profile_grid(layout, profile)
        self.assertEqual(1, len(issues))
        self.assertIn("not integral", issues[0].message)


class PartProvenanceTests(unittest.TestCase):
    def test_prt001_datasheet_backed_valid(self) -> None:
        self.assertEqual([], validate_part_provenance(concrete_component()))

    def test_prt002_concrete_part_without_source(self) -> None:
        component = concrete_component()
        del component["metadata"]["partProvenance"]["sourceUri"]
        self.assertIn(DIAG_LIBRARY_PART_SOURCE_REQUIRED, {item.code for item in validate_part_provenance(component)})

    def test_invalid_source_uri(self) -> None:
        component = concrete_component()
        component["metadata"]["partProvenance"]["sourceUri"] = "datasheet.pdf"
        self.assertIn(DIAG_LIBRARY_PART_SOURCE_REQUIRED, {item.code for item in validate_part_provenance(component)})

    def test_prt003_placeholder_valid_but_not_semantic_ready(self) -> None:
        component = concrete_component()
        component["metadata"] = {
            "semanticReady": False,
            "partProvenance": {"status": "placeholder", "placeholderReason": "Authoritative datasheet unavailable."},
        }
        self.assertEqual([], validate_part_provenance(component))
        claims = aggregate_validation_claims(component, structural_pass=True, semantic_issues=[])
        self.assertEqual("PLACEHOLDER", claims["partSemanticResult"])
        self.assertFalse(claims["semanticReady"])

    def test_placeholder_requires_reason(self) -> None:
        component = concrete_component()
        component["metadata"] = {"semanticReady": False, "partProvenance": {"status": "placeholder"}}
        self.assertIn(DIAG_LIBRARY_PART_PROVENANCE_INVALID, {item.code for item in validate_part_provenance(component)})

    def test_placeholder_cannot_be_semantic_ready(self) -> None:
        component = concrete_component()
        component["metadata"] = {"semanticReady": True, "partProvenance": {"status": "placeholder", "placeholderReason": "Missing source."}}
        self.assertTrue(validate_part_provenance(component))

    def test_prt004_generic_template(self) -> None:
        self.assertEqual([], validate_part_provenance(generic_component()))

    def test_generic_template_cannot_claim_exact_identity(self) -> None:
        component = generic_component()
        component["metadata"]["partProvenance"].update({"manufacturer": "Vendor", "partNumber": "X1"})
        self.assertIn(DIAG_LIBRARY_PART_PROVENANCE_INVALID, {item.code for item in validate_part_provenance(component)})

    def test_missing_provenance_fails(self) -> None:
        component = generic_component()
        component["metadata"].pop("partProvenance")
        self.assertIn(DIAG_LIBRARY_PART_PROVENANCE_INVALID, {item.code for item in validate_part_provenance(component)})

    def test_prt009_minimum_contract(self) -> None:
        self.assertEqual([], validate_minimum_component_contract(generic_component()))
        broken = generic_component()
        broken["ports"] = []
        self.assertTrue(validate_minimum_component_contract(broken))

    def test_total_portmap_required(self) -> None:
        broken = generic_component()
        broken["presentations"][0]["portMap"] = {"1": "1"}
        self.assertTrue(validate_minimum_component_contract(broken))


class SemanticIdentityTests(unittest.TestCase):
    def test_signature_is_key_order_independent(self) -> None:
        component = generic_component()
        shuffled = json.loads(json.dumps(component, sort_keys=False))
        shuffled["metadata"] = {"partProvenance": {"status": "generic-template"}, "semanticReady": True}
        self.assertEqual(component_signatures(component), component_signatures(shuffled))

    def test_prt005_geometry_only_id_multiplication(self) -> None:
        first = generic_component("aixem:r-a")
        second = copy.deepcopy(first)
        second["id"] = "aixem:r-b"
        second["displayName"] = "Another resistor"
        issues = detect_semantic_clones([first, second])
        self.assertEqual(DIAG_LIBRARY_COMPONENT_SEMANTIC_CLONE, issues[0].code)

    def test_prt006_shared_symbol_with_distinct_source_identity(self) -> None:
        first = concrete_component("vendor:abc123")
        second = copy.deepcopy(first)
        second["id"] = "vendor:abc124"
        second["displayName"] = "ABC124"
        second["metadata"]["partProvenance"]["partNumber"] = "ABC124"
        self.assertEqual([], detect_semantic_clones([first, second]))
        self.assertEqual(
            component_signatures(first)["presentationSignature"],
            component_signatures(second)["presentationSignature"],
        )


class PinSemanticsTests(unittest.TestCase):
    def valid_port(self) -> dict:
        return {
            "id": "reset-n",
            "name": "RESET_N",
            "terminal": "14",
            "type": "input",
            "required": True,
            "metadata": {"pinSemantics": {
                "profile": PIN_SEMANTICS_PROFILE,
                "signalClass": "digital",
                "functionalTags": ["reset"],
                "polarity": "active-low",
                "powerDomain": "vddio",
                "capabilities": [],
                "alternateFunctions": [],
            }},
        }

    def test_pin001_active_low_reset(self) -> None:
        self.assertEqual([], validate_pin_semantics(self.valid_port()))

    def test_invalid_profile(self) -> None:
        port = self.valid_port()
        port["metadata"]["pinSemantics"]["profile"] = "future-profile"
        self.assertIn(DIAG_PIN_SEMANTICS_PROFILE_INVALID, {item.code for item in validate_pin_semantics(port)})

    def test_invalid_function_tag(self) -> None:
        port = self.valid_port()
        port["metadata"]["pinSemantics"]["functionalTags"] = ["Reset Signal"]
        self.assertTrue(validate_pin_semantics(port))

    def test_pin002_differential_pair_complete(self) -> None:
        component = generic_component()
        component["ports"] = []
        for member in ("positive", "negative"):
            component["ports"].append({
                "id": f"usb-{member}", "name": f"USB_{member.upper()}", "terminal": member, "type": "bidirectional", "required": True,
                "metadata": {"pinSemantics": {
                    "profile": PIN_SEMANTICS_PROFILE, "signalClass": "digital", "functionalTags": ["usb-data"],
                    "polarity": member, "differentialPair": {"id": "usb2-data", "member": member},
                    "capabilities": [], "alternateFunctions": [],
                }},
            })
        component["presentations"][0]["portMap"] = {port["id"]: port["id"] for port in component["ports"]}
        self.assertEqual([], validate_component_pin_semantics(component))

    def test_pin003_duplicate_differential_member(self) -> None:
        component = generic_component()
        component["ports"] = []
        for index in range(2):
            component["ports"].append({
                "id": f"d{index}", "name": f"D{index}", "type": "bidirectional", "required": False,
                "metadata": {"pinSemantics": {
                    "profile": PIN_SEMANTICS_PROFILE, "signalClass": "digital", "functionalTags": ["usb-data"],
                    "polarity": "positive", "differentialPair": {"id": "usb2-data", "member": "positive"},
                    "capabilities": [], "alternateFunctions": [],
                }},
            })
        self.assertIn(DIAG_PIN_DIFFERENTIAL_PAIR_INCOMPLETE, {item.code for item in validate_component_pin_semantics(component)})

    def test_pin004_noconnect_contradiction(self) -> None:
        port = {"id": "nc", "name": "NC", "type": "no-connect", "required": True}
        self.assertIn(DIAG_PIN_NOCONNECT_CONTRADICTION, {item.code for item in validate_pin_semantics(port)})

    def test_pin005_alternate_functions(self) -> None:
        port = self.valid_port()
        port["metadata"]["pinSemantics"]["alternateFunctions"] = [
            {"name": "PA9", "functionalTags": ["gpio"]},
            {"name": "USART1_TX", "functionalTags": ["uart-tx"]},
        ]
        self.assertEqual([], validate_pin_semantics(port))

    def test_duplicate_alternate_function_fails(self) -> None:
        port = self.valid_port()
        port["metadata"]["pinSemantics"]["alternateFunctions"] = [
            {"name": "PA9", "functionalTags": ["gpio"]},
            {"name": "PA9", "functionalTags": ["uart-tx"]},
        ]
        self.assertTrue(validate_pin_semantics(port))


class ReviewAndClaimsTests(unittest.TestCase):
    def test_prt007_render_pass_does_not_bypass_review(self) -> None:
        component = concrete_component()
        result = validate_component(component, structural_pass=True)
        self.assertEqual("STRUCTURAL_PASS", result["claims"]["structuralResult"])
        self.assertEqual("INCOMPLETE", result["claims"]["partSemanticResult"])
        self.assertFalse(result["claims"]["semanticReady"])
        self.assertIn(DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING, {item["code"] for item in result["issues"]})

    def test_prt001_full_semantic_review(self) -> None:
        component = concrete_component()
        library_digest = "sha256:" + "3" * 64
        result = validate_component(
            component,
            review_evidence=review_evidence(component, library_digest),
            library_digest=library_digest,
            symbol_digests=["sha256:" + "1" * 64],
        )
        self.assertTrue(result["valid"], result)
        self.assertEqual("PART_SEMANTIC_PASS", result["claims"]["partSemanticResult"])

    def test_prt008_review_wrong_source(self) -> None:
        component = concrete_component()
        evidence = review_evidence(component)
        evidence["sourceUri"] = "https://wrong.example/part.pdf"
        issues = validate_part_review_evidence(component, evidence, library_digest=evidence["libraryDigest"], symbol_digests=evidence["symbolDigests"])
        self.assertEqual(DIAG_LIBRARY_PART_PINOUT_REVIEW_MISSING, issues[0].code)

    def test_review_wrong_library_digest(self) -> None:
        component = concrete_component()
        evidence = review_evidence(component)
        issues = validate_part_review_evidence(component, evidence, library_digest="sha256:" + "9" * 64, symbol_digests=evidence["symbolDigests"])
        self.assertTrue(issues)

    def test_prt010_circuit_intent_review(self) -> None:
        component = concrete_component()
        library_digest = "sha256:" + "3" * 64
        self.assertEqual([], validate_circuit_intent_review(component, intent_evidence(component, library_digest), library_digest=library_digest))

    def test_incomplete_circuit_intent(self) -> None:
        component = concrete_component()
        evidence = intent_evidence(component)
        evidence["checks"]["requiredPins"] = False
        issues = validate_circuit_intent_review(component, evidence, library_digest=evidence["libraryDigest"])
        self.assertEqual(DIAG_LIBRARY_PART_INTENT_REVIEW_INCOMPLETE, issues[0].code)

    def test_full_claim_separation(self) -> None:
        component = concrete_component()
        library_digest = "sha256:" + "3" * 64
        result = validate_component(
            component,
            review_evidence=review_evidence(component, library_digest),
            intent_evidence=intent_evidence(component, library_digest),
            library_digest=library_digest,
            symbol_digests=["sha256:" + "1" * 64],
            intent_review_requested=True,
        )
        self.assertEqual("STRUCTURAL_PASS", result["claims"]["structuralResult"])
        self.assertEqual("PART_SEMANTIC_PASS", result["claims"]["partSemanticResult"])
        self.assertEqual("CIRCUIT_INTENT_REVIEW_PASS", result["claims"]["circuitIntentResult"])
        self.assertFalse(result["claims"]["claimBoundary"]["renderProvesDatasheetTruth"])


class CompatibilityTests(unittest.TestCase):
    def result(self, *types: str) -> dict:
        return bounded_compatibility_precheck([{"id": str(index), "type": value} for index, value in enumerate(types)])

    def test_erc001_output_to_inputs(self) -> None:
        self.assertEqual("PASS", self.result("output", "input", "input")["status"])

    def test_erc002_output_conflict(self) -> None:
        result = self.result("output", "output", "input")
        self.assertEqual("ERROR", result["status"])
        self.assertEqual(DIAG_ERC_OUTPUT_CONFLICT, result["issues"][0]["code"])

    def test_erc003_power_output_to_inputs(self) -> None:
        self.assertEqual("PASS", self.result("power-output", "power-input", "power-input")["status"])

    def test_erc004_power_output_conflict(self) -> None:
        result = self.result("power-output", "power-output", "power-input")
        self.assertEqual("ERROR", result["status"])
        self.assertEqual(DIAG_ERC_POWER_OUTPUT_CONFLICT, result["issues"][0]["code"])

    def test_erc005_tristate_uncertain(self) -> None:
        self.assertEqual("WARN", self.result("tri-state", "tri-state", "input")["status"])

    def test_erc006_open_collector_uncertain(self) -> None:
        self.assertEqual("WARN", self.result("open-collector", "open-collector", "input")["status"])

    def test_erc007_connected_noconnect(self) -> None:
        result = self.result("output", "no-connect")
        self.assertEqual("ERROR", result["status"])
        self.assertEqual(DIAG_ERC_CONNECTED_NOCONNECT, result["issues"][0]["code"])

    def test_erc008_input_only(self) -> None:
        self.assertEqual("WARN", self.result("input", "input")["status"])

    def test_unspecified_not_evaluated(self) -> None:
        self.assertEqual("NOT_EVALUATED", self.result("output", "unspecified")["status"])

    def test_compatibility_never_claims_safety(self) -> None:
        result = self.result("output", "input")
        self.assertTrue(all(value is False for value in result["claimBoundary"].values()))


class LibraryDocumentTests(unittest.TestCase):
    def test_valid_generic_library_document(self) -> None:
        document = {"library": {"components": [generic_component()]}}
        result = validate_library_document(
            document,
            artifact_path="library/electronics/passive/resistor/resistors.aixlib.json",
            operation="added",
        )
        self.assertTrue(result["valid"], result)
        self.assertEqual("STRUCTURAL_PASS", result["structuralResult"])
        self.assertEqual("GENERIC_TEMPLATE_PASS", result["componentResults"][0]["claims"]["partSemanticResult"])

    def test_library_document_detects_clone_and_path(self) -> None:
        first = generic_component("aixem:r1")
        second = copy.deepcopy(first)
        second["id"] = "aixem:r2"
        result = validate_library_document(
            {"library": {"components": [first, second]}},
            artifact_path="libraries/parts.aixlib.json",
            operation="added",
        )
        self.assertFalse(result["valid"])
        codes = {item["code"] for item in result["issues"]}
        self.assertIn(DIAG_LIBRARY_PATH_NONCANONICAL, codes)
        self.assertIn(DIAG_LIBRARY_COMPONENT_SEMANTIC_CLONE, codes)


if __name__ == "__main__":
    unittest.main()
