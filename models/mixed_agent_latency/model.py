import argparse
import json
import time

import mesa


class StandardSheep(mesa.Agent):
    """Rule-based agent with no LLM-specific state."""

    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self.energy = 10

    def step(self) -> None:
        self.random_move()

    def random_move(self) -> None:
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


class MockLLMWolf(mesa.Agent):
    """LLM-like agent that simulates inference latency."""

    def __init__(self, model: mesa.Model, simulated_latency_ms: float = 50.0):
        super().__init__(model)
        self.internal_state = {"hunger": "high", "goal": "hunt"}
        self.simulated_latency_ms = simulated_latency_ms
        self.latency_log_ms: list[float] = []
        self.parse_log_ms: list[float] = []

    def step(self) -> None:
        start_time = time.perf_counter()
        parse_start = time.perf_counter()

        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False
        )

        parsed_observations = []
        for neighbor in neighbors:
            agent_desc = getattr(
                neighbor,
                "internal_state",
                {"entity_type": neighbor.__class__.__name__},
            )
            parsed_observations.append(agent_desc)

        parse_duration_ms = (time.perf_counter() - parse_start) * 1000
        self.parse_log_ms.append(parse_duration_ms)

        response_json = self.mock_blocking_llm_call(parsed_observations)
        parsed_action = json.loads(response_json).get("action", "move")
        if parsed_action == "move":
            self.random_move()

        total_duration_ms = (time.perf_counter() - start_time) * 1000
        self.latency_log_ms.append(total_duration_ms)

    def random_move(self) -> None:
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def mock_blocking_llm_call(self, context: list[dict]) -> str:
        """Simulates blocking API latency to model scheduler stalls."""
        _ = context
        time.sleep(self.simulated_latency_ms / 1000)
        return '{"action": "move"}'


class MixedEcosystem(mesa.Model):
    """Mixed world with rule-based and mock-LLM agents."""

    def __init__(
        self,
        width: int = 10,
        height: int = 10,
        num_sheep: int = 5,
        num_wolves: int = 2,
        simulated_latency_ms: float = 50.0,
        seed=None,
    ):
        super().__init__(seed=seed)
        self.grid = mesa.space.MultiGrid(width, height, torus=True)

        for _ in range(num_sheep):
            sheep = StandardSheep(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(sheep, (x, y))

        for _ in range(num_wolves):
            wolf = MockLLMWolf(self, simulated_latency_ms=simulated_latency_ms)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(wolf, (x, y))

    def step(self) -> None:
        self.agents.shuffle_do("step")

    def get_wolves(self) -> list[MockLLMWolf]:
        return [agent for agent in self.agents if isinstance(agent, MockLLMWolf)]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run mixed-agent latency benchmark.")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--num-sheep", type=int, default=5)
    parser.add_argument("--num-wolves", type=int, default=2)
    parser.add_argument("--latency-ms", type=float, default=50.0)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    print("Initializing Mixed-Agent Latency Benchmark...")
    model = MixedEcosystem(
        width=args.width,
        height=args.height,
        num_sheep=args.num_sheep,
        num_wolves=args.num_wolves,
        simulated_latency_ms=args.latency_ms,
        seed=args.seed,
    )

    print(f"Running {args.steps} steps to gather latency metrics...")
    for _ in range(args.steps):
        model.step()

    print("\n--- Evaluation Results ---")
    for wolf in model.get_wolves():
        avg_latency = sum(wolf.latency_log_ms) / len(wolf.latency_log_ms)
        avg_parse = sum(wolf.parse_log_ms) / len(wolf.parse_log_ms)
        print(
            f"LLM Agent {wolf.unique_id} | "
            f"Average total step latency: {avg_latency:.2f} ms | "
            f"Average parsing latency: {avg_parse:.4f} ms"
        )

    print(
        "\nBenchmark Complete: Mixed-agent observation parsing executed "
        "without requiring non-LLM agent state attributes."
    )
