#!/usr/bin/env python3
"""Deterministic Clawproof PASS / REVIEW / BLOCK production gate.

The gate evaluates a versioned JSON declaration. It never uploads inputs, reads
referenced evidence files, or claims to certify the target environment.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policy" / "clawproof-gate.v1.json"
VALID_ANSWERS = {"yes", "partial", "no", "unknown"}
EXIT_CODES = {"PASS": 0, "REVIEW": 2, "BLOCK": 3, "INVALID": 4}
POLICY_KEYS = {
    "name",
    "version",
    "question_ids",
    "questions",
    "critical_question_ids",
    "answer_points",
    "score_bands",
    "decision_rules",
    "evaluation_rules",
    "disclaimer",
}


class InputError(ValueError):
    """Raised when the input cannot be evaluated safely."""


@dataclass(frozen=True)
class Finding:
    question_id: str
    reason: str


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except FileNotFoundError as exc:
        raise InputError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputError(f"Expected a JSON object in {path}")
    return data


def validate_policy(policy: dict[str, Any]) -> None:
    missing = sorted(POLICY_KEYS - set(policy))
    if missing:
        raise InputError(f"Policy is missing required keys: {', '.join(missing)}")
    if not isinstance(policy["version"], str) or not policy["version"].strip():
        raise InputError("Policy version must be a non-empty string")

    question_ids = policy["question_ids"]
    if (
        not isinstance(question_ids, list)
        or not question_ids
        or not all(isinstance(item, str) and item.strip() for item in question_ids)
        or len(question_ids) != len(set(question_ids))
    ):
        raise InputError("Policy question_ids must be a non-empty array of unique strings")

    questions = policy["questions"]
    if (
        not isinstance(questions, dict)
        or set(questions) != set(question_ids)
        or not all(isinstance(text, str) and text.strip() for text in questions.values())
    ):
        raise InputError("Policy questions must define non-empty text for every question id")

    critical_ids = policy["critical_question_ids"]
    if not isinstance(critical_ids, list) or not set(critical_ids).issubset(question_ids):
        raise InputError("Policy critical_question_ids must be a subset of question_ids")

    points = policy["answer_points"]
    if (
        not isinstance(points, dict)
        or set(points) != VALID_ANSWERS
        or not all(isinstance(value, int) and value >= 0 for value in points.values())
    ):
        raise InputError("Policy answer_points must define non-negative integers for every answer")

    max_score = len(question_ids) * points["yes"]
    bands = policy["score_bands"]
    if not isinstance(bands, list) or not bands:
        raise InputError("Policy score_bands must be a non-empty array")
    if not all(
        isinstance(band, dict)
        and isinstance(band.get("id"), str)
        and band["id"].strip()
        and isinstance(band.get("label"), str)
        and band["label"].strip()
        and isinstance(band.get("min"), int)
        and isinstance(band.get("max"), int)
        for band in bands
    ):
        raise InputError("Policy score_bands contain malformed entries")
    try:
        coverage = [
            sum(1 for band in bands if band["min"] <= score <= band["max"])
            for score in range(max_score + 1)
        ]
    except (KeyError, TypeError) as exc:
        raise InputError("Policy score_bands contain malformed entries") from exc
    if any(count != 1 for count in coverage):
        raise InputError(f"Policy score_bands must cover 0-{max_score} exactly once")

    if not isinstance(policy["decision_rules"], dict) or not isinstance(
        policy["evaluation_rules"], dict
    ):
        raise InputError("Policy decision_rules and evaluation_rules must be objects")
    if not isinstance(policy["disclaimer"], str) or not policy["disclaimer"].strip():
        raise InputError("Policy disclaimer must be a non-empty string")


def score_band(policy: dict[str, Any], score: int) -> dict[str, Any]:
    for band in policy["score_bands"]:
        if band["min"] <= score <= band["max"]:
            return band
    raise InputError(f"Policy has no score band for {score}")


def evaluate(declaration: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    validate_policy(policy)
    unexpected_root_keys = sorted(
        set(declaration) - {"policy_version", "target", "answers"}
    )
    if unexpected_root_keys:
        raise InputError(f"Unexpected declaration keys: {', '.join(unexpected_root_keys)}")

    policy_version = declaration.get("policy_version")
    if policy_version != policy["version"]:
        raise InputError(
            f"policy_version must be {policy['version']!r}, got {policy_version!r}"
        )

    answers = declaration.get("answers")
    if not isinstance(answers, dict):
        raise InputError("answers must be an object keyed by stable question id")

    target = declaration.get("target", "unnamed-agent")
    if not isinstance(target, str) or not target.strip():
        raise InputError("target must be a non-empty string when provided")
    target = target.strip()

    expected_ids = list(policy["question_ids"])
    unexpected = sorted(set(answers) - set(expected_ids))
    if unexpected:
        raise InputError(f"Unexpected question ids: {', '.join(unexpected)}")

    points = policy["answer_points"]
    critical_ids = set(policy["critical_question_ids"])
    score = 0
    normalized: dict[str, dict[str, Any]] = {}
    blockers: list[Finding] = []
    review_items: list[Finding] = []

    for question_id in expected_ids:
        raw = answers.get(question_id)
        if raw is None:
            value = "unknown"
            evidence: list[str] = []
            review_items.append(Finding(question_id, "answer omitted"))
        else:
            if not isinstance(raw, dict):
                raise InputError(f"answers.{question_id} must be an object")
            unexpected_answer_keys = sorted(set(raw) - {"value", "evidence"})
            if unexpected_answer_keys:
                raise InputError(
                    f"answers.{question_id} has unexpected keys: "
                    f"{', '.join(unexpected_answer_keys)}"
                )
            value = raw.get("value")
            evidence = raw.get("evidence", [])
            if value not in VALID_ANSWERS:
                raise InputError(
                    f"answers.{question_id}.value must be one of {sorted(VALID_ANSWERS)}"
                )
            if not isinstance(evidence, list) or not all(
                isinstance(item, str) and item.strip() for item in evidence
            ):
                raise InputError(
                    f"answers.{question_id}.evidence must be an array of non-empty strings"
                )
            evidence = [item.strip() for item in evidence]

        score += int(points[value])
        normalized[question_id] = {"value": value, "evidence": evidence}

        if question_id in critical_ids and value == "no":
            blockers.append(Finding(question_id, "critical control explicitly failed"))
        elif value != "yes" and raw is not None:
            review_items.append(Finding(question_id, f"answer is {value}"))

        if value == "yes" and not evidence:
            review_items.append(Finding(question_id, "yes answer has no evidence reference"))

    if blockers:
        decision = "BLOCK"
    elif review_items:
        decision = "REVIEW"
    else:
        decision = "PASS"

    band = score_band(policy, score)
    return {
        "schema": "clawproof.gate-result.v1",
        "policy_version": policy["version"],
        "target": target,
        "decision": decision,
        "score": score,
        "max_score": len(expected_ids) * int(points["yes"]),
        "band": {"id": band["id"], "label": band["label"]},
        "blockers": [finding.__dict__ for finding in blockers],
        "review_items": [finding.__dict__ for finding in review_items],
        "answers": normalized,
        "disclaimer": policy["disclaimer"],
    }


def render_markdown(result: dict[str, Any]) -> str:
    def markdown_cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")

    lines = [
        "# Clawproof Production Gate",
        "",
        f"**Target:** {result['target']}",
        f"**Policy:** {result['policy_version']}",
        f"**Decision:** {result['decision']}",
        f"**Coverage score:** {result['score']}/100 - {result['band']['label']}",
        "",
    ]

    if result["blockers"]:
        lines.extend(["## Blocking controls", ""])
        for item in result["blockers"]:
            lines.append(f"- `{item['question_id']}`: {item['reason']}")
        lines.append("")

    if result["review_items"]:
        lines.extend(["## Review required", ""])
        for item in result["review_items"]:
            lines.append(f"- `{item['question_id']}`: {item['reason']}")
        lines.append("")

    lines.extend(
        [
            "## Evidence declaration",
            "",
            "| Question | Answer | Evidence |",
            "|---|---|---|",
        ]
    )
    for question_id, answer in result["answers"].items():
        evidence = ", ".join(
            markdown_cell(item) for item in answer["evidence"]
        ) or "None declared"
        lines.append(f"| `{question_id}` | {answer['value']} | {evidence} |")

    lines.extend(["", f"_{result['disclaimer']}_", ""])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clawproof")
    subparsers = parser.add_subparsers(dest="command", required=True)
    gate = subparsers.add_parser("gate", help="Evaluate a gate declaration")
    gate.add_argument("input", type=Path, help="Path to a gate declaration JSON file")
    gate.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    gate.add_argument("--format", choices=("json", "markdown"), default="json")
    gate.add_argument("--target", help="Override the target name in the declaration")
    gate.add_argument("--output", type=Path, help="Write the report to a file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = load_json(args.policy)
        declaration = load_json(args.input)
        if args.target:
            declaration["target"] = args.target
        result = evaluate(declaration, policy)
        output = (
            json.dumps(result, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_markdown(result)
        )
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return EXIT_CODES[result["decision"]]
    except InputError as exc:
        sys.stderr.write(f"clawproof: invalid input: {exc}\n")
        return EXIT_CODES["INVALID"]


if __name__ == "__main__":
    raise SystemExit(main())
