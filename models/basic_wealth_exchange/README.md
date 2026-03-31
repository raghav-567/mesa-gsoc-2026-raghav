# Basic Wealth Exchange Model

### What the model does and why I chose it
This is a foundational model where agents move randomly around a grid and give one unit of wealth to a neighbor if they share a cell. I built this model first to ensure I fundamentally understood Mesa's core architecture before attempting to introduce external Large Language Models. 

### What Mesa features it uses
* `mesa.space.MultiGrid`
* `model.agents.shuffle_do("step")` (Mesa 3+ activation path)
* `grid.get_cell_list_contents()` for agent interaction.

### What I learned building it
This model taught me how Mesa's simulation loop depends on fast, non-blocking `step()` functions. It also helped me migrate a legacy scheduler-style implementation to Mesa 3-compatible activation (`AgentSet.shuffle_do`).

### What was hard, what surprised me, what I'd do differently
**The Takeaway:** Building this made me realize how delicate the main simulation thread is. Because standard ABM agents execute their logic in microseconds, introducing an LLM agent that takes seconds to respond (via API) will completely stall the activation loop. 
**Next Steps:** This realization directly informed my second model (`mixed_agent_latency`), where I began testing the actual friction points of integrating LLMs into this fast-paced deterministic loop.

### Reproducibility
Run one deterministic simulation:
```bash
conda run -n ml2-env python model.py --steps 20 --num-agents 50 --seed 42
```

Run benchmark sweep and save CSV:
```bash
conda run -n ml2-env python run_benchmark.py --steps 200 --num-agents 100 --runs 5
```
