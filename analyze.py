# by Jakub Ostrzołek

from io import TextIOWrapper
import json
from typing import Any, Dict, List, Optional
from matplotlib import pyplot as plt
from dataclasses import dataclass, field
import numpy as np
from collections import Counter
from argparse import ArgumentError, ArgumentParser
from pathlib import Path
from main import probability, iterations, size


@dataclass
class BenchmarkRun:
    generations: List[List[float]]
    result: float
    time: float


@dataclass
class BenchmarkRecord:
    runs: List[BenchmarkRun] = field(default_factory=lambda: [])
    size: int = 0
    iterations: int = 0
    mutation_prob: int = 0
    crossover_prob: int = 0

    def aggregate_times(self):
        return [r.time for r in self.runs]

    def aggregate_results(self):
        return [r.result for r in self.runs]

    def aggregate_generations(self):
        if not self.runs:
            return []
        result = self.runs[0].generations
        for r in self.runs[1:]:
            for aggregated_gen, generation in zip(result, r.generations):
                aggregated_gen.extend(generation)
        return result


Benchmark = Dict[str, Dict[str, Dict[str, Dict[str, BenchmarkRecord]]]]


def generate_title(title: str, record: BenchmarkRecord):
    plt.title(
        f"{title} for size={record.size}, "
        f"iterations={record.iterations},\n"
        f"mutation_prob={record.mutation_prob}, "
        f"crossover_prob={record.crossover_prob}. "
        f"Mean result={np.array([r.result for r in record.runs]).mean():.3f}")


def plot_fitness_scatter(
    record: BenchmarkRecord, height: float = 4.8, width: float = 6.4,
        dot_scale=1, **plt_format,):
    plt.figure(figsize=(width, height))

    gens = record.aggregate_generations()

    counters = (Counter(g) for g in gens)
    x = []
    y = []
    s = []

    for i, counter in enumerate(counters):
        y_extension = list(counter.keys())
        x.extend([i] * len(y_extension))
        y.extend(y_extension)
        for n_points in counter.values():
            s.append(dot_scale * n_points)

    plt.scatter(x, y, s=s, **plt_format)

    plt.xlabel("Generation number")
    plt.ylabel("Population fitness score")
    plt.xlim(-1, len(gens))

    generate_title("Population fitness", record)

    plt.tight_layout()


def plot_fitness_mean_std_dev(
        record: BenchmarkRecord, height: float = 4.8, width: float = 6.4,
        **plt_format,):
    plt.figure(figsize=(width, height))

    gens = np.array(record.aggregate_generations())

    x = list(range(len(gens)))
    y = gens.mean(1)
    std_dev = gens.std(1)

    # custom format must shadow default format
    kwargs = {"fmt": "ob", "markersize": 3,
              "elinewidth": 0.5, "ecolor": "y", **plt_format}
    plt.errorbar(x, y, yerr=std_dev, **kwargs)

    plt.xlabel("Generation number")
    plt.ylabel("Population fitness score")
    plt.xlim(-1, len(gens)+1)

    generate_title("Population fitness mean and std. deviation", record)

    plt.tight_layout()


class WrongNumberOfParamsError(ArgumentError):
    def __init__(self, expected_number: int):
        super().__init__(f"Exactly {expected_number} of parameters "
                         "(size, iterations, mutation_prob, crossover_prob) "
                         f"must be specified.")


class BenchmarkParamKeyError(KeyError):
    def __init__(self, param_name: str, param_value: Any):
        super().__init__(f"Benchmark not found for {param_name}={param_value}")


def plot_compare(benchmark: Benchmark,
                 size: Optional[int] = None,
                 iterations: Optional[int] = None,
                 mutation_prob: Optional[int] = None,
                 crossover_prob: Optional[int] = None,
                 results_format: Optional[dict] = None,
                 times_format: Optional[dict] = None,
                 height: float = 4.8,
                 width: float = 6.4,
                 **plt_format):
    plt.figure(figsize=(width, height))

    if results_format is None:
        results_format = {}
    if times_format is None:
        times_format = {}

    params = [size, iterations, mutation_prob, crossover_prob]
    param_names = ["Size", "Iterations",
                   "Mutation probability", "Crossover probability"]
    param_names_in_code = ["size", "iterations",
                           "mutation_prob", "crossover_prob"]
    try:
        i_none = params.index(None)
    except ValueError:
        raise WrongNumberOfParamsError(3)

    if not all(param is not None for i, param in
               enumerate(params) if i != i_none):
        raise WrongNumberOfParamsError(3)

    sub_b = benchmark
    param_names_iter = iter(param_names_in_code)
    current_name = next(param_names_iter)
    try:
        for param in params[:i_none]:
            sub_b = sub_b[param]
            current_name = next(param_names_iter)

        param_values = list(sub_b.keys())
        subs_b = list(sub_b.values())
        current_name = next(param_names_iter)

        for param in params[i_none+1:]:
            subs_b = [sub_b[param] for sub_b in subs_b]
            current_name = next(param_names_iter)
    except KeyError as e:
        raise BenchmarkParamKeyError(current_name, e.args[0])
    except StopIteration:
        pass

    records: List[BenchmarkRecord] = subs_b

    to_sort = list(zip(param_values, records))
    to_sort.sort()
    param_values, records = zip(*to_sort)

    ax_results = plt.axes()
    ax_time = ax_results.twinx()

    for i, record in enumerate(records):
        results = np.array(record.aggregate_results())
        times = np.array(record.aggregate_times()) * 1000

        results_mean = results.mean()
        times_mean = times.mean()
        results_std_dev = results.std()
        times_std_dev = times.std()

        # custom format must shadow default format
        kwargs_results = {"fmt": "ob", **plt_format, **results_format}
        kwargs_time = {"fmt": "or", **plt_format, **times_format}

        ax_results.errorbar(i - 0.05, results_mean,
                            results_std_dev, **kwargs_results)
        ax_time.errorbar(i + 0.05, times_mean, times_std_dev, **kwargs_time)

    plt.xticks(range(len(records)), param_values)

    ax_results.set_xlabel(param_names[i_none])
    ax_results.set_ylabel("Result fitness score")
    ax_time.set_ylabel("Time [ms]")

    title = "Results comparison for "
    for i, (name, value) in enumerate(zip(param_names_in_code, params)):
        if value is None:
            continue
        title += f"{name}={value},"
        if i == 1:
            title += "\n"
        else:
            title += " "
    title = title[:-2]

    plt.title(title)
    plt.tight_layout()


def generate_benchmark(json_file: TextIOWrapper):
    """
    Generates a benchmark dictionary using a benchmark file
    generated with test_benchmark. Run
    `pytest --benchmark-json=FILENAME`
    to get said file.
    """
    benchmark: Benchmark = {}
    parsed = json.load(json_file)
    for b in parsed["benchmarks"]:
        size: int = b["params"]["size"]
        iterations: int = b["params"]["iterations"]
        mutation_prob: int = b["params"]["mutation_prob"]
        crossover_prob: int = b["params"]["crossover_prob"]

        sub_b = benchmark.setdefault(size, {})
        sub_b = sub_b.setdefault(iterations, {})
        sub_b = sub_b.setdefault(mutation_prob, {})
        record: BenchmarkRecord = sub_b.setdefault(
            crossover_prob, BenchmarkRecord(
                [], size, iterations, mutation_prob, crossover_prob
            ))

        info = b["extra_info"]
        run = BenchmarkRun(
            info["generations"],
            info["result"],
            b["stats"]["mean"])

        record.runs.append(run)

    return benchmark


def get_record(benchmark,
               size: int,
               iterations: int,
               mutation_prob: int,
               crossover_prob: int):
    param_name = ""
    try:
        param_name = "size"
        sub_b = benchmark[size]
        param_name = "iterations"
        sub_b = sub_b[iterations]
        param_name = "mutation_prob"
        sub_b = sub_b[mutation_prob]
        param_name = "crossover_prob"
        return sub_b[crossover_prob]
    except KeyError as e:
        raise BenchmarkParamKeyError(param_name, e.args[0])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "benchmark", type=open,
        help="A JSON file generated by pytest-benchmark "
        "(run pytest --benchmark-json=<filename>.json to get the file)")
    parser.add_argument(
        "plot_type", choices=["scatter", "mean-std", "compare"],
        help="Choose plot type. 'scatter' and 'mean-std' require "
        "all 4 algorithm parameters, while 'compare' exactly 3")
    parser.add_argument(
        "-d", "--plots-dir", type=Path, default=Path("plots"),
        help="Generate plots in the given directory")
    params = parser.add_argument_group("Algorithm parameters")
    params.add_argument(
        "-s", "--size", default=None, type=size, help="Population size")
    params.add_argument(
        "-i", "--iterations", default=None, type=iterations, help="Iterations")
    params.add_argument(
        "-m", "--mutation-prob", default=None, type=probability,
        help="Mutation probability")
    params.add_argument(
        "-c", "--crossover-prob", default=None, type=probability,
        help="Crossover probability")
    parser.add_argument(
        "--pyplot-kwargs", default={}, type=json.loads,
        help="Keyword arguments given to pyplot in format "
        r'{"argument": value}')
    parser.add_argument(
        "--height", default=4.8, type=float,
        help="Height of the plot")
    parser.add_argument(
        "--width", default=6.4, type=float,
        help="Width of the plot")

    args = parser.parse_args()
    benchmark = generate_benchmark(args.benchmark)

    params = [args.size, args.iterations,
              args.mutation_prob, args.crossover_prob]

    def handle_scatter():
        if any(param is None for param in params):
            raise WrongNumberOfParamsError(4)
        record = get_record(benchmark, args.size, args.iterations,
                            args.mutation_prob, args.crossover_prob)
        plot_fitness_scatter(
            record, height=args.height, width=args.width, **args.pyplot_kwargs)

    def handle_mean_std():
        if any(param is None for param in params):
            raise WrongNumberOfParamsError(4)
        record = get_record(benchmark, args.size, args.iterations,
                            args.mutation_prob, args.crossover_prob)
        plot_fitness_mean_std_dev(
            record, height=args.height, width=args.width, **args.pyplot_kwargs)

    def handle_compare():
        plot_compare(benchmark, args.size, args.iterations,
                     args.mutation_prob, args.crossover_prob,
                     height=args.height, width=args.width,
                     **args.pyplot_kwargs)

    plot_types_map = {
        "scatter": handle_scatter,
        "mean-std": handle_mean_std,
        "compare": handle_compare
    }

    try:
        plot_types_map[args.plot_type]()
    except (BenchmarkParamKeyError, WrongNumberOfParamsError) as e:
        print(f"Error: {e}")
        exit(1)

    param_short_names = ["s", "i", "m", "c"]
    filename = ",".join([f"{short}={value}" for short, value in zip(
        param_short_names, params) if value is not None]) + ".png"

    path = args.plots_dir / args.plot_type
    path.mkdir(parents=True, exist_ok=True)
    plt.savefig(path / filename, bbox_inches='tight')
