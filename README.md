# LLM Tool Search Benchmark

Does deferred tool loading save tokens without hurting tool-selection accuracy? This benchmark compares eager vs. deferred (`defer_loading`) tool schemas for LLM function calling across catalog sizes, reporting accuracy, tokens, latency and cost. It supports OpenAI and OpenRouter `tool_search`.

Reusable benchmark for comparing how an LLM routes requests across a large tool catalog:

- **Eager:** every business-tool schema is callable from the start.
- **Deferred:** business tools use `defer_loading` and are found through hosted tool search.

It records routing accuracy, token use, latency, estimated cost, cache savings, and callable-tool counts. `expected_tool` is evaluation-only and is never sent to the model or search tool.

## Quick start

Python 3.10+ and an OpenAI or OpenRouter API key are required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add a provider key and current per-million-token prices to `.env`, then run a small smoke test:

```powershell
python -m benchmark.run --provider openai --catalog-sizes 20 --max-tasks 3 --repetitions 1
python analyze_results.py
```

For OpenRouter, replace `--provider openai` with `--provider openrouter`; it reads `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` from `.env`. For OpenAI it reads `OPENAI_API_KEY` and `OPENAI_MODEL`. The committed `.env.example` documents every setting.

For a comparable result, keep model, task count, schema profile, catalog sizes, repetitions, and prices identical between runs:

```powershell
python -m benchmark.run --provider openai --model gpt-6-luna --catalog-sizes 20,40,80 --schema-profile rich --max-tasks 20 --repetitions 3
python analyze_results.py
```

Use `--provider openrouter` (and `OPENROUTER_API_KEY`) to run the same benchmark through OpenRouter. Each run is saved in `experiments/NNN/` with CSV data, metadata, a task snapshot, and charts. Compare runs with:

```powershell
python compare_experiments.py --experiments 031 033
```

## Example findings

The table below is from `experiments/033`: OpenAI `gpt-6-luna`, rich schemas, 20 tasks, and **one repetition**. It is an illustrative snapshot, not a general performance claim.

| Catalog | Condition | Accuracy | Mean total tokens | Mean cost | Mean latency |
| ---: | --- | ---: | ---: | ---: | ---: |
| 20 tools | Eager | 90% | 13,215 | $0.000280 | 5.00 s |
| 20 tools | Deferred | 50% | 2,754 | $0.000444 | 7.14 s |
| 40 tools | Eager | 75% | 25,681 | $0.000415 | 6.79 s |
| 40 tools | Deferred | 70% | 3,220 | $0.000349 | 8.37 s |
| 80 tools | Eager | 65% | 50,533 | $0.000886 | 8.51 s |
| 80 tools | Deferred | 55% | 4,397 | $0.000366 | 9.21 s |

Deferred loading sharply reduced token use in this run, while accuracy and latency varied. Run at least three repetitions before drawing conclusions.

## Contributing

Contributions are welcome—new routing tasks, provider support, analysis improvements, and reproducibility fixes are especially useful. Read [CONTRIBUTING.md](CONTRIBUTING.md), then open an issue or pull request.

Please never commit API keys, `.env`, or unredacted benchmark data. See [SECURITY.md](SECURITY.md) for reporting guidance. Licensed under [MIT](LICENSE).

## Author

**Umut Şahin**

- GitHub: [UmutSahin0](https://github.com/UmutSahin0)
- LinkedIn: [umutsahinn1](https://www.linkedin.com/in/umutsahinn1/)
- Medium: [@umutsahinn1](https://medium.com/@umutsahinn1)
