"""Behavior checks for the multi-agent handoff packet validator."""

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/lab-research/scripts/validate_agent_packet.py"
SPEC = importlib.util.spec_from_file_location("validate_agent_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_packet():
    return {
        "schema_version": "lab-research-agent-packet-v1",
        "paper_sha256": "a" * 64,
        "role": "evidence",
        "read_scope": {"pdf_pages": [7, 11], "visual_pages": [11]},
        "findings": [
            {
                "finding_id": "E01",
                "kind": "author_claim",
                "statement": "The paper reports a deformable grouping ablation.",
                "locators": [{"pdf_page": 11, "anchor": "Table VII"}],
                "evidence_status": "supports",
                "confidence": "high",
                "depends_on": [],
            }
        ],
        "open_questions": ["Was the split isolated by original scene?"],
    }


class PacketValidationTests(unittest.TestCase):
    def test_valid_packet_passes(self):
        self.assertEqual(MODULE.validate_packet(valid_packet()), [])

    def test_source_claim_requires_locator(self):
        packet = valid_packet()
        packet["findings"][0]["locators"] = []
        self.assertTrue(any("locators is required" in item for item in MODULE.validate_packet(packet)))

    def test_locator_must_be_in_read_scope(self):
        packet = valid_packet()
        packet["findings"][0]["locators"][0]["pdf_page"] = 12
        self.assertTrue(any("outside read_scope" in item for item in MODULE.validate_packet(packet)))

    def test_visual_pages_must_be_subset(self):
        packet = valid_packet()
        packet["read_scope"]["visual_pages"] = [12]
        self.assertTrue(any("must be a subset" in item for item in MODULE.validate_packet(packet)))

    def test_idea_requires_claim_dependency(self):
        packet = valid_packet()
        packet["role"] = "idea"
        packet["findings"][0].update(
            {"finding_id": "I01", "kind": "idea", "locators": [], "depends_on": []}
        )
        self.assertTrue(any("at least one Cxx" in item for item in MODULE.validate_packet(packet)))

    def test_role_prefix_must_be_unique_by_role(self):
        packet = valid_packet()
        packet["role"] = "falsifier"
        packet["findings"][0]["finding_id"] = "F01"
        self.assertTrue(any("R prefix" in item for item in MODULE.validate_packet(packet)))

    def test_unknown_claim_dependency_fails_when_ledger_is_provided(self):
        packet = valid_packet()
        packet["role"] = "idea"
        packet["findings"][0].update(
            {"finding_id": "I01", "kind": "idea", "locators": [], "depends_on": ["C99"]}
        )
        self.assertTrue(
            any("unknown claims" in item for item in MODULE.validate_packet(packet, {"C01"}))
        )

    def test_duplicate_finding_ids_fail(self):
        packet = valid_packet()
        packet["findings"].append(dict(packet["findings"][0]))
        self.assertTrue(any("duplicates" in item for item in MODULE.validate_packet(packet)))


if __name__ == "__main__":
    unittest.main()
