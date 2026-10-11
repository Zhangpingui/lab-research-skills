"""Behavior checks for manuscript-review packet validation."""

import importlib.util
from pathlib import Path
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/lab-research/scripts/validate_manuscript_review_packet.py"
)
SPEC = importlib.util.spec_from_file_location("validate_manuscript_review_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_packet():
    return {
        "schema_version": "manuscript-review-packet-v1",
        "role": "evidence-reviewer",
        "manuscript_id": "draft-v03",
        "read_scope": ["Abstract", "Section IV-B", "Fig. 3"],
        "issues": [
            {
                "issue_id": "E01",
                "priority": "major",
                "category": "evidence_gap",
                "location": "Section IV-B, Fig. 3",
                "problem": "The cross-sensor claim uses a single-source test.",
                "evidence": "Fig. 3 reports only sensor A.",
                "impact": "The evidence does not support cross-sensor generalization.",
                "action": "Add an independent sensor split or narrow the claim.",
                "claim_ids": ["C03"],
            }
        ],
        "open_questions": ["Is sensor B available for evaluation?"],
    }


class ManuscriptPacketValidationTests(unittest.TestCase):
    def test_valid_packet_passes(self):
        self.assertEqual(MODULE.validate_packet(valid_packet(), {"C03"}), [])

    def test_role_controls_issue_prefix(self):
        packet = valid_packet()
        packet["role"] = "structure-reviewer"
        self.assertTrue(any("S prefix" in item for item in MODULE.validate_packet(packet)))

    def test_evidence_issue_requires_claim(self):
        packet = valid_packet()
        packet["issues"][0]["claim_ids"] = []
        self.assertTrue(any("claim_ids is required" in item for item in MODULE.validate_packet(packet)))

    def test_presentation_issue_can_have_no_claim(self):
        packet = valid_packet()
        packet["issues"][0].update(
            {"category": "presentation", "claim_ids": [], "problem": "The legend is unreadable."}
        )
        self.assertEqual(MODULE.validate_packet(packet), [])

    def test_unknown_claim_fails(self):
        packet = valid_packet()
        self.assertTrue(
            any("unknown claims" in item for item in MODULE.validate_packet(packet, {"C01"}))
        )

    def test_duplicate_issue_id_fails(self):
        packet = valid_packet()
        packet["issues"].append(dict(packet["issues"][0]))
        self.assertTrue(any("duplicates" in item for item in MODULE.validate_packet(packet)))


if __name__ == "__main__":
    unittest.main()
