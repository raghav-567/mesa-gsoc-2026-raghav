import argparse
import csv
import statistics
import time
from pathlib import Path

from model import MixedEcosystem


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


def parse_number_list(raw: str, cast_type, field_name: str) -> list[int] | list[float]:
    values = []
    for part in raw.split(","):
        stripped = part.strip()
        if not stripped:
            continue
        try:
            values.append(cast_type(stripped))
        except (ValueError, argparse.ArgumentTypeError) as exc:
            raise ValueError(
                f"Invalid value '{stripped}' in --{field_name}; "
                "use comma-separated numeric values."
            ) from exc
    if not values:
        raise ValueError(f"--{field_name} cannot be empty.")
    return values


def run_once(
    steps: int,
    width: int,
    height: int,
    num_sheep: int,
    num_wolves: int,
    latency_ms: float,
    seed: int,
) -> dict:
    model = MixedEcosystem(
        width=width,
        height=height,
        num_sheep=num_sheep,
        num_wolves=num_wolves,
        simulated_latency_ms=latency_ms,
        seed=seed,
    )

    start = time.perf_counter()
    for _ in range(steps):
        model.step()
    total_runtime_ms = (time.perf_counter() - start) * 1000

    wolves = model.get_wolves()
    if wolves:
        wolf_avg_total_ms = [
            sum(wolf.latency_log_ms) / len(wolf.latency_log_ms) for wolf in wolves
        ]
        wolf_avg_parse_ms = [
            sum(wolf.parse_log_ms) / len(wolf.parse_log_ms) for wolf in wolves
        ]
        avg_wolf_total_ms = statistics.mean(wolf_avg_total_ms)
        avg_wolf_parse_ms = statistics.mean(wolf_avg_parse_ms)
    else:
        avg_wolf_total_ms = 0.0
        avg_wolf_parse_ms = 0.0

    return {
        "seed": seed,
        "steps": steps,
        "num_sheep": num_sheep,
        "num_wolves": num_wolves,
        "total_agents": num_sheep + num_wolves,
        "latency_ms_config": latency_ms,
        "total_runtime_ms": round(total_runtime_ms, 6),
        "avg_model_step_ms": round(total_runtime_ms / steps, 6),
        "avg_wolf_total_step_ms": round(avg_wolf_total_ms, 6),
        "avg_wolf_parse_ms": round(avg_wolf_parse_ms, 6),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark mixed-agent latency model.")
    parser.add_argument("--steps", type=positive_int, default=100)
    parser.add_argument("--width", type=positive_int, default=20)
    parser.add_argument("--height", type=positive_int, default=20)
    parser.add_argument("--sheep-list", type=str, default="20,50")
    parser.add_argument("--wolf-list", type=str, default="2,5,10")
    parser.add_argument("--latency-list", type=str, default="10,50,100")
    parser.add_argument("--runs", type=positive_int, default=3)
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("benchmark_results.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        sheep_values = parse_number_list(
            args.sheep_list, non_negative_int, "sheep-list"
        )
        wolf_values = parse_number_list(
            args.wolf_list, non_negative_int, "wolf-list"
        )
        latency_values = parse_number_list(
            args.latency_list, non_negative_float, "latency-list"
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    rows = []
    for sheep in sheep_values:
        for wolves in wolf_values:
            for latency in latency_values:
                for run_idx in range(args.runs):
                    rows.append(
                        run_once(
                            steps=args.steps,
                            width=args.width,
                            height=args.height,
                            num_sheep=sheep,
                            num_wolves=wolves,
                            latency_ms=latency,
                            seed=args.base_seed + run_idx,
                        )
                    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    model_step_times = [row["avg_model_step_ms"] for row in rows]
    wolf_total_times = [row["avg_wolf_total_step_ms"] for row in rows]
    print(f"Saved benchmark rows to: {args.output}")
    print(
        "Summary | "
        f"avg_model_step_ms mean={statistics.mean(model_step_times):.4f}, "
        f"stdev={statistics.pstdev(model_step_times):.4f} | "
        f"avg_wolf_total_step_ms mean={statistics.mean(wolf_total_times):.4f}"
    )


if __name__ == "__main__":
    main()
