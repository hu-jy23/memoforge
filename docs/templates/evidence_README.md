# Evidence Directory

Use one directory per task:

```text
workspace/evidence/{task_id}/
```

Suggested files:

- `commands.log`: commands run and exit codes
- `test.log`: test output
- `benchmark.csv`: metric results
- `profile-summary.md`: profiler findings
- `manual-inspection.md`: reviewer observations that cannot be automated

Evidence files contain raw or lightly summarized proof. Conclusions belong in `verify_result.json`, `promotion_decision.md`, and the learning entry.
