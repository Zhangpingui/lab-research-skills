"""Validate structural invariants for manuscript-review agent packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


SCHEMA = "manuscript-review-packet-v1"
ROLES = {"structure-reviewer", "evidence-reviewer", "domain-reviewer"}
ROLE_PREFIXES = {
    "structure-reviewer": "S",
    "evidence-reviewer": "E",
    "domain-reviewer": "D",
}
PRIORITIES = {"critical", "major", "minor"}
CATEGORIES = {
    "factual_error",
    "evidence_gap",
    "novelty_risk",
    "logic",
    "reproducibility",
    "domain_boundary",
    "citation",
    "presentation",
    "ethics",
}
CLAIM_RELEVANT_CATEGORIES = {
    "factual_error",
    "evidence_gap",
    "novelty_risk",
    "reproducibility",
    "domain_boundary",
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_packet(packet: Any, known_claim_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]

    if packet.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must equal {SCHEMA!r}")
    role = packet.get("role")
    if role not in ROLES:
        errors.append(f"role must be one of {sorted(ROLES)}")
    if not _nonempty_string(packet.get("manuscript_id")):
        errors.append("manuscript_id must be a non-empty string")

    read_scope = packet.get("read_scope")
    if not isinstance(read_scope, list) or any(not _nonempty_string(item) for item in read_scope):
        errors.append("read_scope must be a list of non-empty strings")

    issues = packet.get("issues")
    if not isinstance(issues, list):
        errors.append("issues must be a list")
        issues = []

    seen_ids: set[str] = set()
    for index, issue in enumerate(issues):
        path = f"issues[{index}]"
        if not isinstance(issue, dict):
            errors.append(f"{path} must be an object")
            continue
        expected_prefix = ROLE_PREFIXES.get(role)
        issue_id = issue.get("issue_id")
        if (
            not isinstance(issue_id, str)
            or expected_prefix is None
            or not re.fullmatch(rf"{expected_prefix}\d+", issue_id)
        ):
            errors.append(
                f"{path}.issue_id must use the {expected_prefix or '?'} prefix for role {role!r}"
            )
        elif issue_id in seen_ids:
            errors.append(f"{path}.issue_id duplicates {issue_id!r}")
        else:
            seen_ids.add(issue_id)

        if issue.get("priority") not in PRIORITIES:
            errors.append(f"{path}.priority must be one of {sorted(PRIORITIES)}")
        category = issue.get("category")
        if category not in CATEGORIES:
            errors.append(f"{path}.category must be one of {sorted(CATEGORIES)}")
        for field in ("location", "problem", "evidence", "impact", "action"):
            if not _nonempty_string(issue.get(field)):
                errors.append(f"{path}.{field} must be a non-empty string")

        claim_ids = issue.get("claim_ids")
        if not isinstance(claim_ids, list) or any(
            not isinstance(item, str) or not re.fullmatch(r"C\d+", item)
            for item in claim_ids
        ):
            errors.append(f"{path}.claim_ids must be a list of Cxx strings")
            claim_ids = []
        if category in CLAIM_RELEVANT_CATEGORIES and not claim_ids:
            errors.append(f"{path}.claim_ids is required for category {category!r}")
        if known_claim_ids is not None:
            unknown = sorted(item for item in claim_ids if item not in known_claim_ids)
            if unknown:
                errors.append(f"{path}.claim_ids references unknown claims: {unknown}")

    open_questions = packet.get("open_questions")
    if not isinstance(open_questions, list) or any(
        not _nonempty_string(question) for question in open_questions
    ):
        errors.append("open_questions must be a list of non-empty strings")
    return errors


def _load_claim_ids(path: Path) -> set[str]:
    claims = json.loads(path.read_text(encoding="utf-8"))
    records = claims.get("claims") if isinstance(claims, dict) else None
    if not isinstance(records, list):
        raise ValueError("top-level claims must be a list")
    return {
        item.get("claim_id")
        for item in records
        if isinstance(item, dict)
        and isinstance(item.get("claim_id"), str)
        and re.fullmatch(r"C\d+", item["claim_id"])
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, help="Optional claims.json for Cxx validation")
    parser.add_argument("packets", nargs="+", type=Path)
    args = parser.parse_args()

    try:
        known_claim_ids = _load_claim_ids(args.claims) if args.claims else None
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
