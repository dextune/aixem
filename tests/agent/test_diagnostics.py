from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "implementation"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))

from agent.diagnostics import (  # noqa: E402
    DIAGNOSTIC_REGISTRY,
    RECOMMENDED_P0_CODES,
    assign_diagnostic_ids,
    diagnostic_state_digest,
    make_diagnostic,
    normalize_issue,
    registry_as_records,
    validate_registry,
)


class AgentDiagnosticContractTests(unittest.TestCase):
    def setUp(self) -> None:
        schema_path = ROOT / "docs/specifications/schemas/agent/aixem-agent-diagnostic-1.schema.json"
        self.validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))

    def test_registry_contains_complete_p0_set_and_valid_metadata(self) -> None:
        self.assertEqual([], validate_registry())
        self.assertTrue(RECOMMENDED_P0_CODES.issubset(DIAGNOSTIC_REGISTRY))
        self.assertGreaterEqual(len(DIAGNOSTIC_REGISTRY), 35)
        records = registry_as_records()
        self.assertEqual(sorted(DIAGNOSTIC_REGISTRY), [item["code"] for item in records])
        self.assertNotIn("render/*.svg", {item["authority"] for item in records})

    def test_diagnostic_serialization_is_schema_valid_and_stable(self) -> None:
        diagnostics = assign_diagnostic_ids([
            make_diagnostic(
                "AIXEM-DIAG-ROUTE-NON-ORTHOGONAL",
                "A route segment is diagonal.",
                artifact="control.aixlayout.json",
                json_pointer="/layout/connections/0/paths/0/via/0",
                object_kind="route-segment",
                object_id="net-a:0",
                evidence={"validator": "schematic.orthogonal"},
            ),
            make_diagnostic(
                "AIXEM-DIAG-SYMBOL-LEAD-PORT-MISMATCH",
                "Lead and port differ.",
                artifact="symbols/switch.aixsym.json",
            ),
        ])
        records = [item.to_dict() for item in diagnostics]
        for record in records:
            self.validator.validate(record)
        self.assertEqual(["diag-0001", "diag-0002"], [item["id"] for item in records])
        self.assertEqual(diagnostic_state_digest(records), diagnostic_state_digest(list(reversed(records))))

    def test_rich_diagnostic_round_trip_does_not_gain_legacy_evidence(self) -> None:
        record = assign_diagnostic_ids([
            make_diagnostic(
                "AIXEM-DIAG-BINDING-ASSET-DIGEST",
                "Digest mismatch.",
                artifact="libraries/main.aixlib.json",
                evidence={"validator": "schematic.authoring_binding"},
            )
        ])[0].to_dict()
        normalized = normalize_issue(record).to_dict()
        self.assertNotIn("legacyCode", normalized["evidence"])
        normalized["id"] = record["id"]
        self.assertEqual(record, normalized)

    def test_registry_metadata_cannot_be_contradicted(self) -> None:
        record = assign_diagnostic_ids([
            make_diagnostic("AIXEM-DIAG-ROUTE-ZERO-LENGTH", "bad", artifact="x.aixlayout.json")
        ])[0].to_dict()
        record["authority"] = "semantic"
        with self.assertRaises(ValueError):
            normalize_issue(record)


if __name__ == "__main__":
    unittest.main()
