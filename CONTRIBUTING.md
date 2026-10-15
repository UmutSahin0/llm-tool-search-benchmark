# Contributing

Thanks for improving the benchmark. Small, focused pull requests are easiest to review.

1. Create a virtual environment and install `requirements.txt`.
2. Make one focused change and run `python -m compileall benchmark analyze_results.py compare_experiments.py`.
3. If benchmark behavior changes, include the exact command, provider/model, catalog sizes, prices, and a short sanitized result summary in the pull request.

## Benchmark invariants

- Keep `expected_tool` evaluation-only; never send it to a model, retriever, or tool-search request.
- Preserve the controlled ablation: eager and deferred modes may differ only in business-tool `defer_loading`.
- Add a task only when it has one clear expected tool and a natural-language prompt that does not name that tool.

## Safety and data

Never commit `.env`, API keys, private prompts, or unredacted experiment output. Bug reports should include the provider, model ID, reproducible command, and only sanitized `raw_runs.csv` rows.
