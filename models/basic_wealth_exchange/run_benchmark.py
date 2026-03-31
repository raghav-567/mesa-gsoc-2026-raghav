import argparse
import csv
import statistics
import time
from pathlib import Path

from model import WealthModel


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def gini(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumulative = 0
    for i, value in enumerate(sorted_values, start=1):
        cumulative += i * value
    total = sum(sorted_values)
    if total == 0:
        return 0.0
    return (2 * cumulative) / (n * total) - (n + 1) / n


def run_once(steps: int, num_agents: int, width: int, height: int, seed: int) -> dict:
    model = WealthModel(
        num_agents=num_agents,
        width=width,
        height=height,
        seed=seed,
    )

    start = time.perf_counter()
    for _ in range(steps):
        model.step()
    total_ms = (time.perf_counter() - start) * 1000

    wealth_values = [agent.wealth for agent in model.agents]
    return {
        "seed": seed,
        "steps": steps,
        "num_agents": num_agents,
        "width": width,
        "height": height,
        "total_runtime_ms": round(total_ms, 6),
        "avg_step_ms": round(total_ms / steps, 6),
        "total_wealth": sum(wealth_values),
        "gini": round(gini(wealth_values), 6),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark the basic wealth model.")
    parser.add_argument("--steps", type=positive_int, default=200)
    parser.add_argument("--num-agents", type=positive_int, default=100)
    parser.add_argument("--width", type=positive_int, default=20)
    parser.add_argument("--height", type=positive_int, default=20)
    parser.add_argument("--runs", type=positive_int, default=5)
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("benchmark_results.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    for i in range(args.runs):
        seed = args.base_seed + i
        rows.append(
            run_once(
                steps=args.steps,
                num_agents=args.num_agents,
                width=args.width,
                height=args.height,
                seed=seed,
            )
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    step_times = [row["avg_step_ms"] for row in rows]
    ginis = [row["gini"] for row in rows]
    print(f"Saved benchmark rows to: {args.output}")
    print(
        "Summary | "
        f"avg_step_ms mean={statistics.mean(step_times):.4f}, "
        f"stdev={statistics.pstdev(step_times):.4f} | "
        f"gini mean={statistics.mean(ginis):.4f}"
    )


if __name__ == "__main__":
    main()
