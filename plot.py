# by Jakub Ostrzołek

import json

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from copy import copy

from typing import Dict, Generator, Iterable, List, Optional, Set, Tuple, Union
from io import TextIOWrapper

BENCHMARK_FILENAME = 'benchmark.json'
PLOTS_DIRECTORY = 'plots'


@dataclass
class Record:
    time: float
    p1_char: str
    p2_char: str
    scores: List[Tuple[int, int]]
    values: List[Tuple[str, int]]
    size: int
    p1_depth: int
    p2_depth: int

    def str_params(
            self, exclude: Optional[List[str]] = None) -> Dict[str, str]:
        exclude = [] if exclude is None else exclude
        return {k: v for k, v in {
            "size": f'size={self.size}',
            "p1_depth": f'p1_depth={self.p1_depth}',
            "p2_depth": f'p2_depth={self.p2_depth}',
        }.items() if k not in exclude}

    def str_params_combined(
            self, exclude: Optional[List[str]] = None, separator: str = ", "
    ) -> str:
        return separator.join(self.str_params(exclude).values())

    def __str__(self):
        return self.str_params_combined()

    def __repr__(self):
        return self.str_params_combined(separator=",")


class Benchmark:
    def __init__(self, file: TextIOWrapper):
        parsed = json.load(file)

        self.benchmark: Dict[Record] = {}

        self.sizes: Set[int] = set()
        self.p1_depths: Set[int] = set()
        self.p2_depths: Set[int] = set()

        for b in parsed["benchmarks"]:
            params = b['params']

            size = params['size']
            p1_depth = params['p1_depth']
            p2_depth = params['p2_depth']

            self.sizes.add(size)
            self.p1_depths.add(p1_depth)
            self.p2_depths.add(p2_depth)

            extra = b["extra_info"]
            self.benchmark[(size, p1_depth, p2_depth)] = Record(
                time=b["stats"]["mean"],
                p1_char=extra["p1_char"],
                p2_char=extra["p2_char"],
                scores=[tuple(pair) for pair in extra["scores"]],
                values=[(c, int(v)) for c, v in extra["values"]],
                size=size,
                p1_depth=p1_depth,
                p2_depth=p2_depth,
            )

    def all_params(self):
        return [self.sizes, self.p1_depths, self.p2_depths]

    def get_records(
            self,
            sizes: Optional[int] = None,
            p1_depths: Optional[int] = None,
            p2_depths: Optional[int] = None) -> Generator[Record, None, None]:

        params = [sizes, p1_depths, p2_depths]
        for i, (param, all_params) in enumerate(
                zip(params, self.all_params())):
            if param is None:
                params[i] = list(all_params)

        for record_params in product(*params):
            try:
                yield self.benchmark[record_params]
            except KeyError:
                pass

    def get_record(self, size: int, p1_depth: int, p2_depth: int):
        return self.benchmark[(size, p1_depth, p2_depth)]


def prepare_bars(n_bars: int, x: Iterable[float],
                 xtickslbls: Iterable[Union[str, int, float]] = None):
    width = 1 / (n_bars + 1)
    offset = (width * i for i in range(n_bars))
    if xtickslbls is None:
        xtickslbls = copy(x)
    tick_offset = - width / 2 + (n_bars / 2 * width)
    tick_positions = {l: xx for xx, l in zip(x + tick_offset, xtickslbls)}
    plt.xticks(list(tick_positions.values()), xtickslbls)
    return (width, offset, tick_positions)


def plot_progress(record: Record):
    x = np.arange(len(record.scores))
    width, offset, _ = prepare_bars(3, x)

    scores = np.array(record.scores)
    values = np.array(record.values)

    # values
    x_p1 = np.array([
        i + 1 for i in range(len(values)) if values[i][0] == record.p1_char])
    y_p1 = [int(v) for c, v in values if c == record.p1_char]
    x_p2 = np.array([
        i + 1 for i in range(len(values)) if values[i][0] == record.p2_char])
    y_p2 = [int(v) for c, v in values if c == record.p2_char]

    common = {"width": width}

    values_offset = next(offset)
    plt.bar(x_p1 + values_offset, y_p1,
            color='lightcoral', **common,
            label="1. player's move pred. value")
    plt.bar(x_p2 + values_offset, y_p2,
            color='cornflowerblue', **common,
            label="2. player's move pred. value")

    # scores
    y_p1 = scores[:, 0]
    y_p2 = scores[:, 1]

    common['edgecolor'] = 'grey'

    plt.bar(x + next(offset), y_p1,
            color='red', **common, label="1. player score")
    plt.bar(x + next(offset), y_p2,
            color='blue', **common, label="2. player score")

    plt.legend()

    plt.xlabel("Turn number")
    plt.ylabel("Score / value")
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    plt.title("Game progress\n" + str(record))
    return repr(record)


def plot_compare(benchmark: Benchmark, size: int, p1_depth: int):
    records: List[Record] = list(benchmark.get_records([size], [p1_depth]))

    x = np.arange(len(records))
    width, offset, tp = prepare_bars(2, x, [r.p2_depth for r in records])

    # final scores
    y_p1 = [r.scores[-1][0] for r in records]
    y_p2 = [r.scores[-1][1] for r in records]

    common = {"edgecolor": "grey", "width": width}

    plt.bar(x + next(offset), y_p1, color='red', **common, label="1. player")
    plt.bar(x + next(offset), y_p2, color='blue', **common, label="2. player")

    y_min, y_max = plt.ylim()
    plt.vlines(tp[p1_depth], y_min, y_max, color='silver', linestyles='dashed')

    plt.legend()

    plt.xlabel("p2_depth")
    plt.ylabel("Final score")

    plt.title("Final score\n" +
              records[0].str_params_combined("p2_depth", ", "))
    return records[0].str_params_combined("p2_depth", ",")


if __name__ == "__main__":
    with open(BENCHMARK_FILENAME) as f:
        benchmark = Benchmark(f)

    plots_dir = Path(PLOTS_DIRECTORY)

    widths = {
        2: 8,
        3: 10,
        4: 12,
        5: 14,
    }
    dir = plots_dir / 'progress'
    dir.mkdir(parents=True, exist_ok=True)

    # for record in benchmark.get_records():
    #     width = widths[record.size]
    #     plt.figure(figsize=(width, 6))
    #     basename = plot_progress(record)
    #     plt.savefig(dir / (basename + '.jpg'))
    #     plt.close()

    dir = plots_dir / 'compare'
    dir.mkdir(parents=True, exist_ok=True)

    for size in benchmark.sizes:
        for p1_depth in benchmark.p1_depths:
            try:
                next(benchmark.get_records([size], [p1_depth]))
            except StopIteration:
                continue
            basename = plot_compare(benchmark, size, p1_depth)
            plt.savefig(dir / (basename + '.jpg'))
            plt.close()
