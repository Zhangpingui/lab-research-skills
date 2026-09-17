"""Validate structural invariants for lab-research agent handoff packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA = "lab-research-agent-packet-v1"
ROLES = {"mechanism", "evidence", "domain", "idea", "falsifier", "feasibility"}
ROLE_PREFIXES = {
    "mechanism": "M",
    "evidence": "E",
    "domain": "D",
    "idea": "I",
    "falsifier": "R",
    "feasibility": "X",
}
KINDS = {
    "source_fact",
    "author_claim",
    "interpretation",
    "critique",
    "hypothesis",
    "idea",
    "experiment",
}
LOCATOR_KINDS = {"source_fact", "author_claim", "interpretation", "critique"}
DEPENDENCY_KINDS = {"hypothesis", "idea", "experiment"}
EVIDENCE_STATUSES = {"supports", "partial", "contradicts", "unresolved", "not_applicable"}
CONFIDENCE = {"low", "medium", "high"}


def _positive_pages(value: Any, path: str, errors: list[str]) -> list[int]:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return []
    pages: list[int] = []
    for index, page in enumerate(value):
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            errors.append(f"{path}[{index}] must be a positive integer")
        else:
            pages.append(page)
    if len(pages) != len(set(pages)):
        errors.append(f"{path} must not contain duplicate pages")
    return pages


def validate_packet(packet: Any, known_claim_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]

    if packet.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must equal {SCHEMA!r}")
    paper_sha256 = packet.get("paper_sha256")
    if not isinstance(paper_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", paper_sha256):
        errors.append("paper_sha256 must be 64 lowercase hexadecimal characters")
    role = packet.get("role")
    if role not in ROLES:
        errors.append(f"role must be one of {sorted(ROLES)}")

    read_scope = packet.get("read_scope")
    if not isinstance(read_scope, dict):
        errors.append("read_scope must be an object")
        pdf_pages: list[int] = []
        visual_pages: list[int] = []
    else:
        pdf_pages = _positive_pages(read_scope.get("pdf_pages"), "read_scope.pdf_pages", errors)
        visual_pages = _positive_pages(read_scope.get("visual_pages"), "read_scope.visual_pages", errors)
        unexpected_visual = sorted(set(visual_pages) - set(pdf_pages))
        if unexpected_visual:
            errors.append(f"read_scope.visual_pages must be a subset of pdf_pages: {unexpected_visual}")

    findings = packet.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        findings = []
    seen_ids: set[str] = set()
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix} must be an object")
            continue
        finding_id = finding.get("finding_id")
        expected_prefix = ROLE_PREFIXES.get(role)
        if (
            not isinstance(finding_id, str)
            or expected_prefix is None
            or not re.fullmatch(rf"{expected_prefix}\d+", finding_id)
        ):
            errors.append(
                f"{prefix}.finding_id must use the {expected_prefix or '?'} prefix for role {role!r}"
            )
        elif finding_id in seen_ids:
            errors.append(f"{prefix}.finding_id duplicates {finding_id!r}")
        else:
            seen_ids.add(finding_id)
        kind = finding.get("kind")
        if kind not in KINDS:
            errors.append(f"{prefix}.kind must be one of {sorted(KINDS)}")
        statement = finding.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            errors.append(f"{prefix}.statement must be a non-empty string")
        if finding.get("evidence_status") not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status must be one of {sorted(EVIDENCE_STATUSES)}")
        if finding.get("confidence") not in CONFIDENCE:
            errors.append(f"{prefix}.confidence must be one of {sorted(CONFIDENCE)}")

        locators = finding.get("locators")
        if not isinstance(locators, list):
            errors.append(f"{prefix}.locators must be a list")
            locators = []
        if kind in LOCATOR_KINDS and not locators:
            errors.append(f"{prefix}.locators is required for kind {kind!r}")
        for locator_index, locator in enumerate(locators):
            locator_path = f"{prefix}.locators[{locator_index}]"
            if not isinstance(locator, dict):
                errors.append(f"{locator_path} must be an object")
                continue
            page = locator.get("pdf_page")
            if not isinstance(page, int) or isinstance(page, bool) or page < 1:
                errors.append(f"{locator_path}.pdf_page must be a positive integer")
            elif page not in pdf_pages:
                errors.append(f"{locator_path}.pdf_page {page} is outside read_scope.pdf_pages")
            anchor = locator.get("anchor")
            if not isinstance(anchor, str) or not anchor.strip():
                errors.append(f"{locator_path}.anchor must be a non-empty string")

        depends_on = finding.get("depends_on")
        if not isinstance(depends_on, list) or any(not isinstance(item, str) for item in depends_on):
            errors.append(f"{prefix}.depends_on must be a list of strings")
            depends_on = []
        if kind in DEPENDENCY_KINDS and not any(re.fullmatch(r"C\d+", item) for item in depends_on):
            errors.append(f"{prefix}.depends_on must reference at least one Cxx claim for kind {kind!r}")
        if known_claim_ids is not None:
            unknown_claims = sorted(
                item for item in depends_on if re.fullmatch(r"C\d+", item) and item not in known_claim_ids
            )
            if unknown_claims:
                errors.append(f"{prefix}.depends_on references unknown claims: {unknown_claims}")

    open_questions = packet.get("open_questions")
    if not isinstance(open_questions, list) or any(
        not isinstance(question, str) or not question.strip() for question in open_questions
    ):
        errors.append("open_questions must be a list of non-empty strings")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, help="Optional claims.json used to validate Cxx dependencies")
    parser.add_argument("packets", nargs="+", type=Path)
    args = parser.parse_args()
    known_claim_ids: set[str] | None = None
    if args.claims:
        try:
            claims = json.loads(args.claims.read_text(encoding="utf-8"))
            claim_records = claims.get("claims") if isinstance(claims, dict) else None
            if not isinstance(claim_records, list):
                raise ValueError("top-level claims must be a list")
            known_claim_ids = {
                item.get("claim_id")
                for item in claim_records
                if isinstance(item, dict) and isinstance(item.get("claim_id"), str)
            }
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            print(json.dumps({"claims": str(args.claims), "valid": False, "error": str(error)}))
            return 2
    failed = False
    results = []
    for path in args.packets:
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_packet(packet, known_claim_ids)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            errors = [f"could not read valid UTF-8 JSON: {error}"]
        results.append({"path": str(path), "valid": not errors, "errors": errors})
        failed = failed or bool(errors)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"schema_version": SCHEMA, "results": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
