import copy
import unittest

from agenteval import evaluate, grade_trial, wilson_interval
from agenteval.grader import stable_hash


SCENARIO = {
    "id": "task", "prompt": "Find result", "max_steps": 2,
    "allowed_tools": ["read"], "required_tools": ["read"],
    "forbidden_tools": ["shell"],
    "expected": {"kind": "contains", "values": ["answer", "source"]},
}
TRIAL = {
    "agent": "a", "scenario_id": "task",
    "steps": [{"tool": "read", "status": "ok"}],
    "final": "The Answer (source: test).",
}


class TestEvaluation(unittest.TestCase):
    def test_correct_trace(self):
        result = grade_trial(SCENARIO, TRIAL)
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 100)

    def test_forbidden_tool_detected(self):
        bad = copy.deepcopy(TRIAL)
        bad["steps"].append({"tool": "shell", "status": "ok"})
        result = grade_trial(SCENARIO, bad)
        self.assertIn("unsafe_or_disallowed_tools", result["reasons"])
        self.assertFalse(result["safe"])

    def test_missing_tool_and_wrong_answer(self):
        bad = dict(TRIAL, steps=[], final="not found")
        result = grade_trial(SCENARIO, bad)
        self.assertIn("missing_required_tools", result["reasons"])
        self.assertIn("final_answer_mismatch", result["reasons"])

    def test_budget(self):
        bad = dict(TRIAL, steps=[{"tool": "read"}] * 3)
        self.assertIn("step_budget_exceeded", grade_trial(SCENARIO, bad)["reasons"])

    def test_error_step(self):
        bad = dict(TRIAL, steps=[{"tool": "read", "status": "error"}])
        self.assertIn("tool_error", grade_trial(SCENARIO, bad)["reasons"])

    def test_missing_trials_not_ignored(self):
        extra = dict(SCENARIO, id="task2")
        result = evaluate([SCENARIO, extra], [TRIAL])
        agent = result["agents"][0]
        self.assertEqual(agent["scenarios_total"], 2)
        self.assertEqual(agent["passed"], 1)
        self.assertEqual(agent["pass_rate"], 0.5)
        self.assertEqual(agent["missing_scenarios"], ["task2"])

    def test_exact_answer(self):
        scenario = dict(SCENARIO, expected={"kind": "exact", "value": "42"})
        trial = dict(TRIAL, final=" 42 ")
        self.assertTrue(grade_trial(scenario, trial)["passed"])

    def test_duplicate_and_invalid(self):
        with self.assertRaises(ValueError):
            evaluate([SCENARIO, SCENARIO], [TRIAL])
        with self.assertRaises(ValueError):
            evaluate([SCENARIO], [TRIAL, TRIAL])
        with self.assertRaises(ValueError):
            grade_trial(SCENARIO, dict(TRIAL, scenario_id="other"))

    def test_wilson_and_deterministic_hash(self):
        low, high = wilson_interval(5, 10)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)
        self.assertEqual(stable_hash({"a": 1, "b": 2}), stable_hash({"b": 2, "a": 1}))
        with self.assertRaises(ValueError):
            wilson_interval(2, 1)

    def test_multiple_agents(self):
        bad = dict(TRIAL, agent="b", final="wrong")
        report = evaluate([SCENARIO], [TRIAL, bad])
        self.assertEqual([r["agent"] for r in report["agents"]], ["a", "b"])
        self.assertEqual([r["passed"] for r in report["agents"]], [1, 0])


if __name__ == "__main__":
    unittest.main()
