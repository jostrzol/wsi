# by Jakub Ostrzołek

from io import TextIOWrapper
from typing import Callable, List, Optional, Tuple
from main import f, g
from argparse import ArgumentParser
import json
from matplotlib import pyplot as plt
import numpy as np
from math import sqrt
from pathlib import Path


GRAPH_RESOLUTION = 500


def plot_steps_2d(function: Callable[[float], float],
                  steps_taken: List[Tuple[float]],
                  half_range: Optional[float] = None):
    """
    Plots the steps taken to calculate a minimum of a function.
    Works only in 2D.
    """
    ax = plt.axes()

    xs = [x[0] for x in steps_taken]
    ys = [function(*x) for x in steps_taken]
    ax.plot(xs, ys, "D-", zorder=100)

    if half_range is None:
        xlim = ax.get_xlim()
    else:
        xlim = (-half_range, half_range)
    xs = np.arange(xlim[0], xlim[1], (xlim[1] - xlim[0]) / GRAPH_RESOLUTION)
    ys = [function(x) for x in xs]
    ax.plot(xs, ys, zorder=10)

    plt.xlabel("X")
    plt.ylabel("Y")

    return ax


def plot_steps_3d(
        function: Callable[[float, float], float],
        steps_taken: List[Tuple[float, float]],
        half_range: Optional[float] = None):
    """
    Plots the steps taken to calculate a minimum of a function.
    Works only in 3D.
    """
    ax = plt.axes()

    xs = [x[0] for x in steps_taken]
    ys = [x[1] for x in steps_taken]
    ax.plot(xs, ys, "D-", zorder=100)

    if half_range is None:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
    else:
        xlim = (-half_range, half_range)
        ylim = (-half_range, half_range)

    xs = np.arange(
        xlim[0],
        xlim[1],
        (xlim[1] - xlim[0]) / sqrt(GRAPH_RESOLUTION))
    ys = np.arange(
        ylim[0],
        ylim[1],
        (ylim[1] - ylim[0]) / sqrt(GRAPH_RESOLUTION))
    xxs, yys = np.meshgrid(xs, ys)
    zs = [[function(x, y) for x in xs]for y in ys]
    ax.contour(xxs, yys, zs, zorder=10)

    plt.xlabel("X")
    plt.ylabel("Y")

    return ax


def label_steps(start_pnt: Tuple[float, ...], learn_coef: float,
                plot_benchmark: dict):
    """Labels plots generated by plot_steps_2d or plot_steps_2d"""
    if len(start_pnt) > 1:
        start_pnt_str = rf"$x=({','.join(str(x) for x in start_pnt)})$"
    else:
        start_pnt_str = rf"$x={start_pnt[0]}$"
    start_pnt_ascii = start_pnt_str.replace("$", "")
    learn_coef_str = fr"$\alpha={learn_coef}$"
    learn_coef_ascii = f"a={learn_coef}"
    plt.title(f"Starting point: {start_pnt_str}\n"
              f"Initial learning coefficient: {learn_coef_str}\n"
              f"Steps taken: {len(plot_benchmark['steps_taken']) - 1} "
              f"Iterations: {plot_benchmark['iterations']}")
    filename = f"{start_pnt_ascii},{learn_coef_ascii}.svg"
    return filename


def plot_performance_vs_learn_coef(
        f_benchmark: dict, start_pnt: Tuple[float, ...], bar_width=0.25):
    """
    Plots a bar chart showing the corelation between the
    initial learning coefficient and performance of the algorithm
    """
    ax = plt.axes()

    xs = list(f_benchmark.keys())
    ys1 = [len(learn_coef_b[start_pnt]["steps_taken"]) - 1
           for learn_coef_b in f_benchmark.values()]
    ys2 = [learn_coef_b[start_pnt]["iterations"]
           for learn_coef_b in f_benchmark.values()]
    ys3 = [learn_coef_b[start_pnt]["time"] * 1000
           for learn_coef_b in f_benchmark.values()]
    xs1 = np.arange(len(ys1))
    xs2 = xs1 + bar_width
    xs3 = xs2 + bar_width

    ax.bar(xs1, ys1, edgecolor="grey", width=bar_width, label="Steps")
    ax.bar(xs2, ys2, edgecolor="grey",
           width=bar_width, label="Iterations")
    ax.set_xlabel(r"Initial learning coefficient $\alpha$")
    ax.set_ylabel("Count")

    ax_time = ax.twinx()
    ax_time.bar(xs3, ys3, edgecolor="grey",
                width=bar_width, label="Time", color="red")
    ax_time.set_ylabel("Time [ms]")

    handles, lables = ax.get_legend_handles_labels()
    handles_time, lables_time = ax_time.get_legend_handles_labels()
    handles, lables = (handles + handles_time, lables + lables_time)
    plt.legend(handles, lables)

    plt.xticks([np.average(x) for x in zip(xs1, xs2, xs3)], xs)


def label_performance_vs_learn_coef(start_pnt: Tuple[float, ...]):
    """Labels plots generated by plot_performance_vs_learn_coef"""
    if len(start_pnt) > 1:
        start_pnt_str = rf"$x=({','.join(str(x) for x in start_pnt)})$"
    else:
        start_pnt_str = rf"$x={start_pnt[0]}$"
    start_pnt_ascii = start_pnt_str.replace("$", "")
    plt.title("Compare steps counts, iterations and time\n"
              "vs initial learning coefficient\n"
              f"Starting point: {start_pnt_str}")
    filename = f"{start_pnt_ascii}.svg"
    return filename


def plot_performance_vs_start_pnts(
        f_benchmark: dict, learn_coef: float, bar_width=0.25):
    """
    Plots a bar chart showing the corelation between the
    starting point and performance of the algorithm
    """
    ax = plt.axes()

    xs = list(f_benchmark[learn_coef].keys())
    if len(xs[0]) == 1:
        xs = [x[0] for x in xs]
    ys1 = [len(start_pnt_b["steps_taken"]) - 1
           for start_pnt_b in f_benchmark[learn_coef].values()]
    ys2 = [start_pnt_b["iterations"]
           for start_pnt_b in f_benchmark[learn_coef].values()]
    ys3 = [start_pnt_b["time"] * 1000
           for start_pnt_b in f_benchmark[learn_coef].values()]
    xs1 = np.arange(len(ys1))
    xs2 = xs1 + bar_width
    xs3 = xs2 + bar_width

    ax.bar(xs1, ys1, edgecolor="grey", width=bar_width, label="Steps")
    ax.bar(xs2, ys2, edgecolor="grey",
           width=bar_width, label="Iterations")
    ax.set_xlabel("Starting point")
    ax.set_ylabel("Count")

    ax_time = ax.twinx()
    ax_time.bar(xs3, ys3, edgecolor="grey",
                width=bar_width, label="Time", color="red")
    ax_time.set_ylabel("Time [ms]")

    handles, lables = ax.get_legend_handles_labels()
    handles_time, lables_time = ax_time.get_legend_handles_labels()
    handles, lables = (handles + handles_time, lables + lables_time)
    plt.legend(handles, lables)

    plt.xticks([np.average(x) for x in zip(xs1, xs2, xs3)], xs)


def label_performance_vs_start_pnt(learn_coef: float):
    """Labels plots generated by plot_performance_vs_learn_coef"""
    learn_coef_str = rf"$\alpha={learn_coef}$"
    learn_coef_ascii = f"a={learn_coef}"
    plt.title("Compare steps counts, iterations and time\n"
              "vs starting point\n"
              f"Initial learning coefficient: {learn_coef_str}")
    filename = f"{learn_coef_ascii}.svg"
    return filename


def generate_benchmark(json_file: TextIOWrapper):
    """
    Generates a benchmark dictionary using a benchmark file
    generated with test_benchmark. Run
    `pytest --benchmark-json=FILENAME`
    to get said file.
    """
    benchmark = {}
    parsed = json.load(json_file)
    for b in parsed["benchmarks"]:
        func_b = benchmark.setdefault(b["extra_info"]["function"], {})
        learn_coef_b = func_b.setdefault(b["params"]["learn_coef"], {})
        learn_coef_b[tuple(b["params"]["start_pnt"])] = {
            "time": b["stats"]["mean"],
            "steps_taken": b["extra_info"]["steps_taken"],
            "iterations": b["extra_info"]["iterations"],
            "found": b["extra_info"]["found"],
        }
    return benchmark


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "benchmark", help="A JSON file generated by benchmark", type=open)
    parser.add_argument(
        "plots", help="Generate plots in the given directionary",
        type=Path)
    parser.add_argument(
        "-s", action="store_true", help="Generate step plots")
    parser.add_argument(
        "-c", action="store_true", help="Generate compare plots")

    args = parser.parse_args()

    benchmark = generate_benchmark(args.benchmark)

    if args.s:
        for learn_coef, learn_coef_b in benchmark["f"].items():
            for start_pnt, plot_benchmark in learn_coef_b.items():
                plot_steps_3d(f, plot_benchmark["steps_taken"])
                filename = label_steps(
                    start_pnt, learn_coef, plot_benchmark)
                dest_path: Path = args.plots / "f" / "steps"
                dest_path.mkdir(parents=True, exist_ok=True)
                plt.subplots_adjust(top=0.8)
                plt.savefig(dest_path / filename, transparent=True)
                plt.close()

        for learn_coef, learn_coef_b in benchmark["g"].items():
            for start_pnt, plot_benchmark in learn_coef_b.items():
                plot_steps_2d(g, plot_benchmark["steps_taken"])
                filename = label_steps(
                    start_pnt, learn_coef, plot_benchmark)
                dest_path: Path = args.plots / "g" / "steps"
                dest_path.mkdir(parents=True, exist_ok=True)
                plt.subplots_adjust(top=0.8)
                plt.savefig(dest_path / filename, transparent=True)
                plt.close()

    if args.c:
        for f_name, f_benchmark in benchmark.items():
            for start_pnt in list(f_benchmark.values())[0]:
                plot_performance_vs_learn_coef(f_benchmark, start_pnt)
                filename = label_performance_vs_learn_coef(start_pnt)
                dest_path: Path = args.plots / f_name / "performance"
                dest_path.mkdir(parents=True, exist_ok=True)
                plt.subplots_adjust(top=0.8)
                plt.savefig(dest_path / filename, transparent=True)
                plt.close()

        for f_name, f_benchmark in benchmark.items():
            for learn_coef in f_benchmark.keys():
                plot_performance_vs_start_pnts(f_benchmark, learn_coef)
                filename = label_performance_vs_start_pnt(learn_coef)
                dest_path: Path = args.plots / f_name / "performance"
                dest_path.mkdir(parents=True, exist_ok=True)
                plt.subplots_adjust(top=0.8)
                plt.savefig(dest_path / filename, transparent=True)
                plt.close()
