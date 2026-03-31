# Mixed-Agent Latency & Observation Benchmark

### What the model does and why I chose it
This model simulates a basic mixed ecosystem where "mock" LLM-driven agents (Wolves) interact with standard, rule-based agents (Sheep). I built this specifically to benchmark the inference latency bottlenecks of LLM agents and to stress-test how well the experimental `mesa-llm` logic handles environments populated by non-LLM entities. Applying the same rigorous evaluation metrics used in my hybrid RAG and AQI data modeling projects, I wanted to quantify exactly how much an LLM call slows down a simulation loop to justify the architectural need for `asyncio`.

### What Mesa features it uses
* `mesa.space.MultiGrid` for spatial positioning.
* `model.agents.shuffle_do("step")` for Mesa 3+ activation.
* `grid.get_neighbors()` for spatial observation parsing.

### What I learned building it
I learned that synchronous (blocking) LLM calls are a fatal bottleneck for ABMs. Even with a simulated 50ms delay per LLM-like agent, the simulation slows significantly because each call blocks the main execution path. This reinforced that an `asyncio` batching pipeline is mandatory for production-ready `mesa-llm`.

### What was hard, what surprised me, what I'd do differently
**The Friction Point:** I was surprised to discover a critical interoperability flaw: if an LLM-like agent assumes every neighbor exposes `internal_state`, mixed simulations can break when standard Mesa agents are present.

**The Fix:** I used a duck-typing fallback in the observation loop (`getattr(...)`) that records a structured default payload for non-LLM neighbors. This prevents crashes without modifying standard agent classes.

**What I'd do differently:** 1. **Deterministic Parsing:** use strict schema-first payloads (for example with `Pydantic`) to reduce token costs and harden parser behavior. 2. **Scope Discipline:** keep Mesa-LLM work focused on Mesa 3.x stabilization first (current maintainer priority), and treat Mesa 4 compatibility as a stretch track only.

### Reproducibility
Run one deterministic latency experiment:
```bash
conda run -n ml2-env python model.py --steps 20 --num-sheep 20 --num-wolves 5 --latency-ms 50 --seed 42
```

Run benchmark sweep and save CSV:
```bash
conda run -n ml2-env python run_benchmark.py --steps 100 --runs 3 --sheep-list 20,50 --wolf-list 2,5,10 --latency-list 10,50,100
```
