# Optimized Two-Model GSoC Approach (Mesa-LLM, 2026)

This document aligns the current two-model strategy with:
- Mesa GSoC 2026 candidate guidance,
- current `mesa-llm` issue and PR priorities,
- selection patterns from already accepted Mesa GSoC work (hands-on models + concrete PR proof).

## Ground Truth (as of March 31, 2026)

1. Mesa's official 2026 guide emphasizes model-building first, proof-of-concept artifacts, and visible community contributions.
2. Mesa's posted 2026 timeline says contributor proposals close on **March 31, 2026 (18:00 UTC)**.
3. `mesa-llm` migration tracker (#273) states that near-term priority is **Mesa 3.x maintenance/stabilization**, not broad Mesa 4 migration.
4. Several high-impact `mesa-llm` maintenance issues are still open across reliability, async safety, performance, and error handling.

## Current Proof-of-Concept Assets

### Model A: Baseline ABM Throughput
- Path: `models/basic_wealth_exchange/`
- Purpose: deterministic non-LLM baseline and throughput sanity checks.
- Evidence command:
  - `conda run -n ml2-env python models/basic_wealth_exchange/run_benchmark.py --steps 50 --num-agents 100 --runs 3 --base-seed 42`

### Model B: Mixed-Agent Latency Stress Test
- Path: `models/mixed_agent_latency/`
- Purpose: quantify blocking LLM-style overhead and mixed-agent observation robustness.
- Evidence command:
  - `conda run -n ml2-env python models/mixed_agent_latency/run_benchmark.py --steps 30 --runs 2 --sheep-list 20 --wolf-list 2,5 --latency-list 10,50 --base-seed 42`

## Why the Two-Model Structure Still Works

1. It is directly aligned with Mesa's "build models first" selection guidance.
2. It gives reproducible before/after metrics for any stabilization change.
3. It maps to active `mesa-llm` maintainer pain points (latency, reliability, reproducibility, tool safety).

## Winning Scope Adjustments (Recommended)

### Primary Scope (critical path: Mesa 3.x stabilization)
1. Reliability and async safety in stepping/reasoning paths.
2. Deterministic, schema-first tool execution and safer argument handling.
3. Reproducible benchmark + regression suite tied to real issue classes.
4. User-facing docs for performance/cost/error-handling workflows.

### Secondary Scope (only if primary is complete)
1. Targeted Mesa 4 compatibility experiments in isolated branches.
2. Additional example model and richer instrumentation.

### Explicit Non-Goals (for proposal clarity)
1. No large Mesa 4 migration in the critical path.
2. No broad API redesign without maintainer sign-off.
3. No feature-only expansion that lacks tests and benchmark evidence.

## Upstream Issue Buckets to Target

Prioritize unresolved, high-impact maintenance tickets. Suggested buckets:

1. **Reliability / concurrency**
   - #278, #220, #222, #137
2. **Error handling / first-run UX**
   - #266, #257, #244
3. **Performance / observability**
   - #200, #178
4. **Tooling validation hardening**
   - #279, #276 (already have active PRs #280 and #277; avoid duplicate work)

## PR Strategy for Selection Strength

1. Land 1-2 scoped bug-fix PRs on unresolved maintenance issues.
2. Every PR should include:
   - a failing test that reproduces the issue,
   - a minimal fix,
   - benchmark or behavior evidence before/after (when relevant),
   - updated docs/examples when user-facing behavior changes.
3. Keep PRs narrow and reviewable (single issue per PR where possible).

## Milestone Plan

### Community Bonding / Pre-selection
1. Expand benchmark matrix and define acceptance thresholds.
2. Submit small, test-backed maintenance fixes.
3. Share concise discussion updates linking evidence artifacts.

### Coding Phase 1
1. Land reliability + determinism fixes with regression tests.
2. Publish baseline-vs-improved benchmark report using Model A + Model B.
3. Improve first-run docs for provider errors and reproducibility.

### Coding Phase 2
1. Implement selected async/performance improvements and verify thresholds.
2. Add instrumentation for latency/token/cost observability.
3. Ship release-ready documentation and reproducible artifacts.

## Deliverables (175 vs 350 hours)

### 175-hour track
1. Stabilization patch set (reliability + tests).
2. Reproducible benchmark harness and report.
3. Focused documentation updates for usage and evaluation.

### 350-hour track
1. All 175-hour deliverables.
2. Deeper async/performance optimization pass.
3. Additional evaluated example model and expanded instrumentation.

## Risk Controls

1. Keep Mesa 4 work isolated from core delivery commitments.
2. Require benchmark-backed evidence for performance claims.
3. Prefer incremental PRs with clear rollback safety.
