# Mesa GSoC Learning Space

This repository documents my hands-on preparation for Mesa GSoC, focused on Mesa-LLM stabilization and reproducible performance analysis.

## 2026 Alignment Snapshot

- Mesa GSoC 2026 emphasis: build models first, then propose scoped improvements with proof-of-concept artifacts.
- Mesa-LLM emphasis right now: maintenance and stabilization on Mesa 3.x are higher priority than broad Mesa 4 migration.
- This repo is intentionally organized around reproducible friction discovery (model code + benchmark CSV + implementation notes).

## Current Focus

I am using a two-model progression approach:

1. Baseline ABM model to establish deterministic non-LLM behavior and runtime baseline.
2. Mixed-agent latency model to quantify blocking LLM-like inference overhead and mixed-agent observation behavior.

This structure is aligned with Mesa GSoC guidance: build real models first, identify friction points, then propose targeted improvements.

## Models

### 1. Basic Wealth Exchange
- Path: `models/basic_wealth_exchange/`
- Purpose: baseline throughput and behavior sanity check.
- Key outputs:
  - deterministic run support (seeded)
  - benchmark CSV with runtime and Gini metrics

### 2. Mixed-Agent Latency Benchmark
- Path: `models/mixed_agent_latency/`
- Purpose: stress-test scheduler impact of blocking LLM-style calls in mixed agent populations.
- Key outputs:
  - seeded latency experiments
  - benchmark CSV across sheep/wolf counts and simulated latency settings
  - explicit parsing-latency vs total-step-latency separation

## Environment

All commands below are validated in:
- `conda` environment: `ml2-env`
- Python: `3.10.18`
- Mesa: `3.0.3`

For upstream `mesa-llm` contribution work, use a Python `3.12+` environment because the repository currently declares `requires-python = ">=3.12"` in its `pyproject.toml`.

## Quick Run

Run baseline model:
```bash
conda run -n ml2-env python models/basic_wealth_exchange/model.py --steps 20 --num-agents 50 --seed 42
```

Run mixed-agent model:
```bash
conda run -n ml2-env python models/mixed_agent_latency/model.py --steps 20 --num-sheep 20 --num-wolves 5 --latency-ms 50 --seed 42
```

## Benchmarks

Run baseline benchmark:
```bash
conda run -n ml2-env python models/basic_wealth_exchange/run_benchmark.py --steps 200 --num-agents 100 --runs 5
```

Output:
- `models/basic_wealth_exchange/benchmark_results.csv`

Run mixed-agent benchmark:
```bash
conda run -n ml2-env python models/mixed_agent_latency/run_benchmark.py --steps 100 --runs 3 --sheep-list 20,50 --wolf-list 2,5,10 --latency-list 10,50,100
```

Output:
- `models/mixed_agent_latency/benchmark_results.csv`

## Proposal-Oriented Artifacts

- Motivation: `motivation.md`
- Optimized approach and milestone plan: `proposal_optimized_approach.md`
- Upstream flow/requirements notes: `notes/mesa_llm_gsoc_2026_alignment.md`

## Why This Repo Exists

Mesa is a modeller-first library. I am using this space to:
- collect concrete evidence of API/performance friction points,
- convert those findings into scoped, testable proposal milestones,
- demonstrate readiness for collaborative open-source development.

## References

- [Mesa documentation](https://mesa.readthedocs.io/)
- [Mesa migration guide](https://mesa.readthedocs.io/latest/migration_guide.html)
- [Mesa contributing guide](https://github.com/mesa/mesa/blob/main/CONTRIBUTING.md)
- [Mesa discussions](https://github.com/mesa/mesa/discussions)
- [Mesa-LLM repository](https://github.com/mesa/mesa-llm)
- [Mesa GSoC 2026 guide](https://github.com/mesa/mesa/wiki/Google-Summer-of-Code-2026)
- [Mesa GSoC 2026 project ideas](https://github.com/mesa/mesa/wiki/GSoC-2026-Project-Ideas)
