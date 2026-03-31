import argparse

import mesa


class WealthAgent(mesa.Agent):
    """Agent that starts with one unit of wealth and can exchange it."""

    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self.wealth = 1

    def move(self) -> None:
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self) -> None:
        if self.wealth <= 0:
            return
        cellmates = [
            agent
            for agent in self.model.grid.get_cell_list_contents([self.pos])
            if agent is not self
        ]
        if cellmates:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self) -> None:
        self.move()
        self.give_money()


class WealthModel(mesa.Model):
    """Simple random movement model with wealth exchange on shared cells."""

    def __init__(self, num_agents: int = 50, width: int = 10, height: int = 10, seed=None):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = mesa.space.MultiGrid(width, height, torus=True)

        for _ in range(self.num_agents):
            agent = WealthAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def step(self) -> None:
        self.agents.shuffle_do("step")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the basic wealth exchange model.")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--num-agents", type=int, default=50)
    parser.add_argument("--width", type=int, default=10)
    parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    print("Initializing Basic Wealth Model...")
    model = WealthModel(
        num_agents=args.num_agents,
        width=args.width,
        height=args.height,
        seed=args.seed,
    )
    for _ in range(args.steps):
        model.step()
    total_wealth = sum(agent.wealth for agent in model.agents)
    print(
        "Baseline simulation complete. "
        f"Steps={args.steps}, Agents={args.num_agents}, Total wealth={total_wealth}"
    )
