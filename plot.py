import json

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from itertools import product

from typing import Dict, Generator, List, Optional, Set, Tuple
from io import TextIOWrapper

BENCHMARK_FILENAME = 'benchmark.json'


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

    def str_params(self, exclude=None) -> Dict[str, str]:
        exclude = [] if exclude is None else exclude
        return {k: v for k, v in {
            "size": f'size={self.size}',
            "p1_depth": f'p1_depth={self.p1_depth}',
            "p2_depth": f'p2_depth={self.p2_depth}',
        }.items() if k not in exclude}

    def __str__(self):
        return ", ".join(self.str_params().values())

    def __repr__(self):
        return ",".join(self.str_params().values())


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


def plot_progress(record: Record):
    n_bars = 3
    width = 1 / (n_bars + 1)
    offset = (width * i for i in range(n_bars))

    scores = np.array(record.scores)
    values = np.array(record.values)

    common = {
        "edgecolor": "green"
    }

    # values
    x_p1 = np.array([
        i + 1 for i in range(len(values)) if values[i][0] == record.p1_char])
    y_p1 = [int(v) for c, v in values if c == record.p1_char]
    x_p2 = np.array([
        i + 1 for i in range(len(values)) if values[i][0] == record.p2_char])
    y_p2 = [int(v) for c, v in values if c == record.p2_char]

    values_offset = next(offset)
    plt.bar(x_p1 + values_offset, y_p1, width,
            color='lightcoral', **common,
            label="1. player's move pred. value")
    plt.bar(x_p2 + values_offset, y_p2, width,
            color='cornflowerblue', **common,
            label="2. player's move pred. value")

    # scores
    x = np.arange(len(record.scores))
    y_p1 = scores[:, 0]
    y_p2 = scores[:, 1]

    common['edgecolor'] = 'grey'

    plt.bar(x + next(offset), y_p1, width,
            color='red', **common, label="1. player score")
    plt.bar(x + next(offset), y_p2, width,
            color='blue', **common, label="2. player score")

    plt.legend()

    plt.xlabel("Turn number")
    plt.ylabel("Score / value")
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    plt.title(str(record))


def plot_compare(benchmark: Benchmark, size: int):
    records: List[Record] = list(benchmark.get_records([size]))

    width = 0.5

    y = [r.scores[-1][0] - r.scores[-1][1] for r in records]
    x = np.arange(len(records))

    plt.bar(x, y, width, edgecolor='grey')

    plt.xlabel("p2_depth")
    plt.xticks(x, [r.p2_depth for r in records])
    plt.ylabel("1. player score - 2. player score")

    plt.title(', '.join(records[0].str_params('p2_depth').values()))


if __name__ == "__main__":
    with open(BENCHMARK_FILENAME) as f:
        benchmark = Benchmark(f)

    # plt.figure(figsize=(12, 6))
    # plot_progress(benchmark.get_record(2, 6, 8))
    # plt.show()

    plot_compare(benchmark, 5)
    plt.show()
