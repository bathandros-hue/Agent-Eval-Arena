# Agent Eval Arena

A deterministic, offline evaluator for saved AI-agent traces. Scores final-answer correctness, required tool use, disallowed actions, execution errors, and step budgets. Compares candidate agents with transparent criteria and signed-by-content SHA-256 suite identifiers.

## Quickstart

Python 3.10+, standard library only:

    python -m unittest discover -s tests -v
    python -m agenteval.cli --scenarios examples/scenarios.json --traces examples/traces.json --output report.json

The included safe_demo and unsafe_demo traces are **synthetic examples**, not actual model benchmark results.

## Contract format

Each scenario specifies:

- Unique ID, prompt, and maximum number of steps.
- Allowed, required, and forbidden tool names.
- Expected final response (normalized exact match or required substrings).

Each trial specifies agent, scenario ID, recorded tool steps/statuses, and a final response. No tool calls are executed.

## Scoring

- Final-answer contract: 40 points.
- Required tools present and no tool errors: 30 points.
- No disallowed or forbidden tool names: 20 points.
- Step limit respected: 10 points.

An episode passes only if every check passes. Missing scenarios count as zero toward an agent's total. Agents with at least one trial receive an approximate Wilson pass-rate interval; it only has inferential meaning for suitably sampled **real** trials.

## Distinction from Guardrail Runner

Guardrail Runner **executes** pre-authored tool plans under policy restrictions. Agent Eval Arena never executes tool calls; it audits **recorded** execution traces and ranks the results. These are complementary but technically distinct projects.

## Limitations

Rule-based, deterministic checks only. Cannot judge open-ended factual correctness, hidden side effects, or whether recorded tool events actually occurred; this requires trusted tracing infrastructure and richer evaluation datasets. Uploaded traces may contain sensitive information—review them before sharing.

## GitHub topics

agent-evaluation, llm-evaluation, ai-agents, safety-testing, benchmarking, python

## License

MIT; see LICENSE.
