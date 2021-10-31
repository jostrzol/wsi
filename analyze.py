# by Jakub Ostrzołek

from io import TextIOWrapper
import json
from typing import Dict, List, Optional
from matplotlib import pyplot as plt
from dataclasses import dataclass, field
import numpy as np
from collections import Counter


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
        f"Mean result={np.array([r.result for r in record.runs]).mean()}")


def plot_fitness_scatter(record: BenchmarkRecord, dot_scale=50, **plt_format):
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

    plt.scatter(x, y, **plt_format, s=s)

    plt.xlabel("Generation number")
    plt.ylabel("Population fitness score")

    generate_title("Population fitness", record)

    plt.tight_layout()


def plot_fitness_mean_std_dev(record: BenchmarkRecord, **plt_format):
    gens = np.array(record.aggregate_generations())

    x = list(range(len(gens)))
    y = gens.mean(1)
    std_dev = gens.std(1)

    plt.errorbar(x, y, yerr=std_dev, fmt="ob",  elinewidth=0.5, **plt_format)

    plt.xlabel("Generation number")
    plt.ylabel("Population fitness score")

    generate_title("Population fitness mean and standard deviation", record)

    plt.tight_layout()


def plot_compare(benchmark: Benchmark,
                 size: Optional[int] = None,
                 iterations: Optional[int] = None,
                 mutation_prob: Optional[int] = None,
                 crossover_prob: Optional[int] = None,
                 results_format: Optional[dict] = None,
                 times_format: Optional[dict] = None,
                 **plt_format):
    if results_format is None:
        results_format = {}
    if times_format is None:
        times_format = {}

    err = ValueError("Exactly one parameter (size, iterations, "
                     "mutation_prob, crossover_prob) must be None")

    params = [size, iterations, mutation_prob, crossover_prob]
    param_names = ["Size", "Iterations",
                   "Mutation probability", "Crossover probability"]
    param_names_in_code = ["size", "iterations",
                           "mutation_prob", "crossover_prob"]
    try:
        i_none = params.index(None)
    except ValueError:
        raise err

    if not all(param is not None for i, param in
               enumerate(params) if i != i_none):
        raise err

    sub_b = benchmark
    for param in params[:i_none]:
        sub_b = sub_b[param]

    param_values = list(sub_b.keys())
    subs_b = list(sub_b.values())

    for param in params[i_none+1:]:
        subs_b = [sub_b[param] for sub_b in subs_b]

    records: List[BenchmarkRecord] = subs_b

    to_sort = list(zip(param_values, records))
    to_sort.sort()
    param_values, records = zip(*to_sort)

    ax1 = plt.axes()
    ax2 = ax1.twinx()

    for i, record in enumerate(records):
        results = np.array(record.aggregate_results())
        times = np.array(record.aggregate_times()) * 1000

        results_mean = results.mean()
        times_mean = times.mean()
        results_std_dev = results.std()
        times_std_dev = times.std()

        ax1.errorbar(i - 0.05, results_mean, results_std_dev,
                     fmt="ob", **plt_format, **results_format)
        ax2.errorbar(i + 0.05, times_mean, times_std_dev,
                     fmt="or", **plt_format, **times_format)

    plt.xticks(range(len(records)), param_values)

    ax1.set_xlabel(param_names[i_none])
    ax1.set_ylabel("Result fitness score")
    ax2.set_ylabel("Time [ms]")

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


# if __name__ == "__main__":
#     parser = ArgumentParser()
#     parser.add_argument(
#         "benchmark", type=open,
#         help="A JSON file generated by pytest-benchmark "
#         "(run pytest --benchmark-json=<filename>.json to get the file)")
#     parser.add_argument(
#         "plots", type=Path, default="plots",
#         help="Generate plots in the given directory")
#     parser.add_argument(
#         "-s", action="store_true", help="Generate step plots")
#     parser.add_argument(
#         "-c", action="store_true", help="Generate compare plots")

#     args = parser.parse_args()

#     benchmark = generate_benchmark(args.benchmark)

#     if args.s:
#         for learn_coef, learn_coef_b in benchmark["f"].items():
#             for start_pnt, plot_benchmark in learn_coef_b.items():
#                 plot_steps_3d(f, plot_benchmark["steps_taken"])
#                 filename = label_steps(
#                     start_pnt, learn_coef, plot_benchmark)
#                 dest_path: Path = args.plots / "f" / "steps"
#                 dest_path.mkdir(parents=True, exist_ok=True)
#                 plt.subplots_adjust(top=0.85)
#                 plt.savefig(dest_path / filename)
#                 plt.close()

#         for learn_coef, learn_coef_b in benchmark["g"].items():
#             for start_pnt, plot_benchmark in learn_coef_b.items():
#                 plot_steps_2d(g, plot_benchmark["steps_taken"])
#                 filename = label_steps(
#                     start_pnt, learn_coef, plot_benchmark)
#                 dest_path: Path = args.plots / "g" / "steps"
#                 dest_path.mkdir(parents=True, exist_ok=True)
#                 plt.subplots_adjust(top=0.85)
#                 plt.savefig(dest_path / filename)
#                 plt.close()

#     if args.c:
#         for f_name, f_benchmark in benchmark.items():
#             for start_pnt in list(f_benchmark.values())[0]:
#                 plot_performance_vs_learn_coef(f_benchmark, start_pnt)
#                 filename = label_performance_vs_learn_coef(start_pnt)
#                 dest_path: Path = args.plots / f_name / "performance"
#                 dest_path.mkdir(parents=True, exist_ok=True)
#                 plt.subplots_adjust(top=0.85)
#                 plt.savefig(dest_path / filename)
#                 plt.close()

#         for f_name, f_benchmark in benchmark.items():
#             for learn_coef in f_benchmark.keys():
#                 plot_performance_vs_start_pnts(f_benchmark, learn_coef)
#                 filename = label_performance_vs_start_pnt(learn_coef)
#                 dest_path: Path = args.plots / f_name / "performance"
#                 dest_path.mkdir(parents=True, exist_ok=True)
#                 plt.subplots_adjust(top=0.85)
#                 plt.savefig(dest_path / filename)
#                 plt.close()
