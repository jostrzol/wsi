from matplotlib.figure import Figure
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix)
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import KBinsDiscretizer
from seaborn import heatmap

from matplotlib import pyplot as plt
from matplotlib import gridspec

from typing import Iterable, Union, Optional
from copy import copy
from pathlib import Path

import pandas as pd
import numpy as np

from id3 import ID3Tree

PLOT_DIR = "plots"


def prepare_bars(n_bars: int, x: Iterable[float],
                 xtickslbls: Iterable[Union[str, int, float]] = None,
                 ax: Optional[plt.Axes] = None):
    width = 1 / (n_bars + 1)
    offset = (width * i for i in range(n_bars))
    if xtickslbls is None:
        xtickslbls = copy(x)
    tick_offset = - width / 2 + (n_bars / 2 * width)
    tick_positions = {l: xx for xx, l in zip(x + tick_offset, xtickslbls)}
    if ax is not None:
        ax.set_xticks(list(tick_positions.values()))
        ax.set_xticklabels(xtickslbls)
    else:
        plt.xticks(list(tick_positions.values()), xtickslbls)
    return (width, offset, tick_positions)


def plot_model(
        tree: ID3Tree,
        Xs: Iterable[pd.DataFrame],
        ys: Iterable[pd.Series],
        setnames: Iterable[str],
        title: str) -> Figure:
    n_sets = len(Xs)

    fig = plt.figure(figsize=(10, 6))
    gs = gridspec.GridSpec(ncols=n_sets+1, nrows=n_sets, figure=fig)

    ax_bar: plt.Axes = fig.add_subplot(gs[:, 1:])

    common = {'average': 'macro',
              'zero_division': 0}
    metrics = {
        'accuracy': accuracy_score,
        'precision': lambda y, y_pred: precision_score(y, y_pred, **common),
        'recall': lambda y, y_pred: recall_score(y, y_pred, **common),
        'f1': lambda y, y_pred: f1_score(y, y_pred, **common)
    }
    x = np.arange(len(metrics))
    width, offset, _ = prepare_bars(n_sets, x, metrics.keys(), ax=ax_bar)

    for i, (X, y, setname) in enumerate(zip(Xs, ys, setnames)):
        y_pred = tree.predict(X)

        ax: plt.Axes = fig.add_subplot(gs[i, 0])
        ax.set_aspect('equal')
        ax.set_title(setname)

        heatmap(confusion_matrix(y, y_pred), ax=ax, annot=True)

        ax_bar.bar(
            x + next(offset),
            [score(y, y_pred) for score in metrics.values()],
            label=setname,
            width=width,
            edgecolor='black')

    ax_bar.set_ylim(0, 1)
    ax_bar.set_title('metrics')
    ax_bar.legend(loc='lower right')
    plt.suptitle(title)

    plt.tight_layout(h_pad=2)
    return fig


if __name__ == "__main__":
    df: pd.DataFrame = load_iris(as_frame=True)['frame']

    X = df.drop(['target'], axis=1)
    y = df['target']

    encoder = KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")
    X = encoder.fit_transform(X)

    X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25)

    # back to dataframes
    X_train = pd.DataFrame(X_train, index=y_train.index)
    X_val = pd.DataFrame(X_val, index=y_val.index)
    X_test = pd.DataFrame(X_test, index=y_test.index)

    trees = {i: ID3Tree(i) for i in range(5)}

    plot_dir = Path(PLOT_DIR)

    for depth, tree in trees.items():
        tree.fit(X_train, y_train)

        plot_model(
            tree,
            (X_train, X_val),
            (y_train, y_val),
            ('train', 'validate'),
            f'depth = {depth}')

        filename = f'd={depth}.jpg'
        plt.savefig(plot_dir / filename)

        plt.close()
