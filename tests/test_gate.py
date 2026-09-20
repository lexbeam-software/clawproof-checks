import json
import subprocess
import sys
import copy
import unittest
from pathlib import Path

from scripts.clawproof_gate import InputError, evaluate, load_json, score_band


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "clawproof_gate.py"


class GateCliTests(unittest.TestCase):
    def run_gate(self, fixture: str, fmt: str = "json") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLI),
                "gate",
                str(ROOT / "examples" / fixture),
                "--format",
                fmt,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_pass_requires_all_yes_with_evidence(self):
        completed = self.run_gate("gate-pass.json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["review_items"], [])

    def test_critical_failure_blocks_despite_high_score(self):
        completed = self.run_gate("gate-block.json")
        self.assertEqual(completed.returncode, 3, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["score"], 95)
        self.assertEqual(result["blockers"][0]["question_id"], "05a")

    def test_omissions_and_missing_evidence_require_review(self):
        completed = self.run_gate("gate-review.json")
        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["decision"], "REVIEW")
        self.assertTrue(any(item["question_id"] == "02a" for item in result["review_items"]))
        self.assertTrue(any(item["question_id"] == "10b" for item in result["review_items"]))

    def test_malformed_answer_is_invalid(self):
        completed = self.run_gate("gate-invalid.json")
        self.assertEqual(completed.returncode, 4)
        self.assertIn("invalid input", completed.stderr)

    def test_markdown_output_is_stable_and_explicit(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "gate",
                str(ROOT / "examples" / "gate-block.json"),
                "--format",
                "markdown",
                "--target",
                "agent-x",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("**Target:** agent-x", completed.stdout)
        self.assertIn("**Decision:** BLOCK", completed.stdout)
        self.assertIn("`05a`: critical control explicitly failed", completed.stdout)
        self.assertIn("does not inspect or certify", completed.stdout)

    def test_policy_ids_match_bundled_check_contract(self):
        policy = json.loads((ROOT / "policy" / "clawproof-gate.v1.json").read_text())
        packaged_policy = json.loads(
            (
                ROOT
                / "skills"
                / "clawproof-audit"
                / "policy"
                / "clawproof-gate.v1.json"
            ).read_text()
        )
        bundle = json.loads(
            (ROOT / "skills" / "clawproof-audit" / "checks.json").read_text()
        )
        verification_ids = [
            item["id"]
            for check in bundle["checks"]
            for item in check["verification"]
        ]
        verification_questions = {
            item["id"]: item["question"]
            for check in bundle["checks"]
            for item in check["verification"]
        }
        self.assertEqual(policy["question_ids"], verification_ids)
        self.assertEqual(policy["questions"], verification_questions)
        self.assertEqual(policy, packaged_policy)
        self.assertEqual(len(verification_ids), len(set(verification_ids)))
        self.assertTrue(
            set(policy["critical_question_ids"]).issubset(verification_ids)
        )

    def test_block_takes_precedence_over_review(self):
        policy = load_json(ROOT / "policy" / "clawproof-gate.v1.json")
        declaration = load_json(ROOT / "examples" / "gate-block.json")
        declaration["answers"]["01b"] = {"value": "partial", "evidence": []}
        result = evaluate(declaration, policy)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(result["review_items"])

    def test_omitted_critical_answer_requires_review(self):
        policy = load_json(ROOT / "policy" / "clawproof-gate.v1.json")
        declaration = load_json(ROOT / "examples" / "gate-pass.json")
        del declaration["answers"]["01a"]
        result = evaluate(declaration, policy)
        self.assertEqual(result["decision"], "REVIEW")
        self.assertEqual(result["blockers"], [])

    def test_blank_evidence_and_unexpected_answer_fields_are_invalid(self):
        policy = load_json(ROOT / "policy" / "clawproof-gate.v1.json")
        declaration = load_json(ROOT / "examples" / "gate-pass.json")
        declaration["answers"]["01a"]["evidence"] = ["   "]
        with self.assertRaises(InputError):
            evaluate(declaration, policy)

        declaration = load_json(ROOT / "examples" / "gate-pass.json")
        declaration["answers"]["01a"]["note"] = "typo bait"
        with self.assertRaises(InputError):
            evaluate(declaration, policy)

    def test_malformed_policy_is_invalid_not_a_traceback(self):
        policy = load_json(ROOT / "policy" / "clawproof-gate.v1.json")
        declaration = load_json(ROOT / "examples" / "gate-pass.json")
        malformed = copy.deepcopy(policy)
        del malformed["questions"]
        with self.assertRaisesRegex(InputError, "missing required keys"):
            evaluate(declaration, malformed)

    def test_score_band_boundaries(self):
        policy = load_json(ROOT / "policy" / "clawproof-gate.v1.json")
        expected = {
            0: "at-risk",
            39: "at-risk",
            40: "foundational",
            64: "foundational",
            65: "controlled-with-gaps",
            84: "controlled-with-gaps",
            85: "mature-controls",
            100: "mature-controls",
        }
        for score, band_id in expected.items():
            with self.subTest(score=score):
                self.assertEqual(score_band(policy, score)["id"], band_id)


if __name__ == "__main__":
    unittest.main()
