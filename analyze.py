# by Jakub Ostrzołek

from io import TextIOWrapper
import json
from typing import Dict, List, Optional, Tuple
from matplotlib import pyplot as plt
from dataclasses import dataclass, field
from matplotlib.axes import Axes
import numpy as np
from collections import Counter
from argparse import ArgumentParser
from pathlib import Path
from main import probability, iterations, size


class AnalyzeError(ValueError):
    def __init__(self, msg: str):
        super().__init__(msg)


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


def plot_compare(benchmark: Benchmark,
                 size_iterations: List[Tuple[float, float]],
                 mutation_prob: List[float],
                 crossover_prob: List[float],
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

    params = [size_iterations, mutation_prob, crossover_prob]
    param_names = ["(Size, Iterations)",
                   "Mutation probability", "Crossover probability"]
    param_code_names = [("size", "iterations"),
                        ("mutation_prob",), ("crossover_prob",)]

    n_records = None
    variable_param_values = None
    variable_param_name = None
    params_no_varying = list(zip(params, param_code_names))
    for i, (param, name) in enumerate(zip(params, param_names)):
        if len(param) == 1:
            continue
        elif len(param) >= 1:
            if n_records is None:
                n_records = len(param)
                variable_param_values = param
                variable_param_name = name
                params_no_varying.pop(i)
            else:
                raise AnalyzeError("Expected exactly one parameter "
                                   "with >= 1 number of values")
        else:
            raise AnalyzeError("All parameters must have at least one value")

    size, iterations = zip(*size_iterations)
    params = [size, iterations, *params[1:]]

    params = [param * n_records if len(param)
              == 1 else param for param in params]

    try:
        records = [benchmark[s][i][mp][cm] for s, i, mp, cm in zip(*params)]
    except KeyError:
        raise AnalyzeError("Given benchmark does not exist")

    to_sort = list(zip(variable_param_values, records))
    to_sort.sort()
    param_values, records = zip(*to_sort)
    param_values: List[float]
    records: List[BenchmarkRecord]

    ax_results = plt.axes()
    ax_time: Axes = ax_results.twinx()

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

    ax_results.set_xlabel(variable_param_name)
    ax_results.set_ylabel("Result fitness score")
    ax_time.set_ylabel("Time [ms]")

    title = "Results comparison for "
    separators = iter([" ", "\n", " "])
    for i, (values, names) in enumerate(params_no_varying):
        values = np.array(values).reshape(-1)
        for value, name in zip(values, names):
            title += f"{name}={value}," + next(separators)
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
    try:
        sub_b = benchmark[size]
        sub_b = sub_b[iterations]
        sub_b = sub_b[mutation_prob]
        return sub_b[crossover_prob]
    except KeyError:
        raise AnalyzeError("Given benchmark does not exist")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "benchmark", type=open,
        help="A JSON file generated by pytest-benchmark "
        "(run pytest --benchmark-json=<filename>.json to get the file)")
    parser.add_argument(
        "plot_type", choices=["scatter", "mean-std", "compare"],
        help="Choose plot type. 'scatter' and 'mean-std' require "
        "1 of all 4 algorithm parameters, while 'compare' > 1 for "
        "one chosen parameter and 1 for other 3")
    parser.add_argument(
        "-d", "--plots-dir", type=Path, default=Path("plots"),
        help="Generate plots in the given directory")
    params = parser.add_argument_group("Algorithm parameters")
    params.add_argument(
        "-s", "--size", nargs="+", required=True,
        type=size, help="Population size")
    params.add_argument(
        "-i", "--iterations", nargs="+", required=True,
        type=iterations, help="Iterations")
    params.add_argument(
        "-m", "--mutation-prob", nargs="+", required=True,
        type=probability, help="Mutation probability")
    params.add_argument(
        "-c", "--crossover-prob", nargs="+", required=True,
        type=probability, help="Crossover probability")
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

    def handle_scatter_mean_std():
        if any(len(param) != 1 for param in params):
            raise AnalyzeError("Expected one of each parameter")
        record = get_record(benchmark, args.size[0], args.iterations[0],
                            args.mutation_prob[0], args.crossover_prob[0])
        fnc = plot_fitness_scatter if args.plot_type == "scatter" \
            else plot_fitness_mean_std_dev
        fnc(record, height=args.height, width=args.width,
            **args.pyplot_kwargs)

    def handle_compare():
        plot_compare(benchmark, list(zip(args.size, args.iterations)),
                     args.mutation_prob, args.crossover_prob,
                     height=args.height, width=args.width,
                     **args.pyplot_kwargs)

    plot_types_map = {
        "scatter": handle_scatter_mean_std,
        "mean-std": handle_scatter_mean_std,
        "compare": handle_compare
    }

    try:
        plot_types_map[args.plot_type]()
    except AnalyzeError as e:
        print(f"Error: {e}")
        exit(1)

    param_short_names = ["s", "i", "m", "c"]
    values_str = [str(values[0]) if len(values) == 1 else
                  f"[{','.join(str(v) for v in values)}]" for values in params]
    filename = ",".join(
        [short + "=" + value
         for short, value in zip(param_short_names, values_str)]) + ".png"

    path = args.plots_dir / args.plot_type
    path.mkdir(parents=True, exist_ok=True)
    plt.savefig(path / filename, bbox_inches='tight')
