# by Jakub Ostrzołek

from math import inf
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

from typing import Dict, Iterable, List, Tuple, Union, Optional
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


def get_metrics(y: pd.Series, y_pred: pd.Series
                ) -> Tuple[Dict[str, float], np.ndarray]:
    """calculates metrics and confusion matrix"""
    common = {'average': 'macro',
              'zero_division': 0}
    return (
        {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, **common),
            'recall': recall_score(y, y_pred, **common),
            'f1': f1_score(y, y_pred, **common)
        },
        confusion_matrix(y, y_pred)
    )


def plot_model(
        set_metrics: List[Dict[str, float]],
        set_conf_mat: List[np.ndarray],
        set_names: List[str],
        title: str) -> List[float]:
    n_sets = len(set_metrics)

    fig = plt.figure(figsize=(10, 6))
    gs = gridspec.GridSpec(ncols=n_sets + 1, nrows=n_sets, figure=fig)

    ax_bar: plt.Axes = fig.add_subplot(gs[:, 1:])

    x_bar = np.arange(len(set_metrics[0]))
    width, offset, _ = prepare_bars(
        n_sets, x_bar, set_metrics[0].keys(), ax=ax_bar)

    for i, (metrics, conf_mat, set_name) in enumerate(
            zip(set_metrics, set_conf_mat, set_names)):
        ax: plt.Axes = fig.add_subplot(gs[i, 0])
        ax.set_aspect('equal')
        ax.set_title(set_name)

        heatmap(conf_mat, ax=ax, annot=True)

        x_cur = x_bar + next(offset)
        y_bar = list(metrics.values())
        ax_bar.bar(
            x_cur,
            y_bar,
            label=set_name,
            width=width,
            edgecolor='black')
        for xx, yy in zip(x_cur, y_bar):
            ax_bar.text(xx, yy - 0.02, f'{yy:.3f}', color='white',
                        horizontalalignment='center',
                        verticalalignment='top')

    ax_bar.set_ylim(0, 1)
    ax_bar.set_title('metrics')
    ax_bar.legend(loc='lower right')
    plt.suptitle(title)

    plt.tight_layout(h_pad=2)
    return


if __name__ == "__main__":
    df: pd.DataFrame = load_iris(as_frame=True)['frame']

    X = df.drop(['target'], axis=1)
    y = df['target']

    encoders = {
        n: KBinsDiscretizer(
            n_bins=n,
            encode="ordinal",
            strategy="quantile") for n in [2, 3, 5, 7]}
    for encoder in encoders.values():
        encoder.fit(X)

    X_rest, X_test, y_rest, y_test = train_test_split(X, y, test_size=0.2)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25)

    trees = {i: ID3Tree(i) for i in range(5)}

    plot_dir = Path(PLOT_DIR)
    plot_dir.mkdir(exist_ok=True, parents=True)

    best_encoder: KBinsDiscretizer = None
    best_tree: ID3Tree = None
    best_metrics_sum = -inf

    for encoder in encoders.values():
        X_train_e = encoder.transform(X_train)
        X_val_e = encoder.transform(X_val)

        # back to dataframes
        X_train_e = pd.DataFrame(X_train_e, index=y_train.index)
        X_val_e = pd.DataFrame(X_val_e, index=y_val.index)

        for depth, tree in trees.items():
            tree.fit(X_train_e, y_train)
            y_train_pred = tree.predict(X_train_e)
            y_val_pred = tree.predict(X_val_e)

            metrics_train, cm_train = get_metrics(y_train, y_train_pred)
            metrics_val, cm_val = get_metrics(y_val, y_val_pred)

            metrics_sum = sum(metrics_val.values())
            if metrics_sum > best_metrics_sum:
                best_encoder = encoder
                best_tree = tree
                best_metrics_sum = metrics_sum

            plot_model(
                (metrics_train, metrics_val),
                (cm_train, cm_val),
                ('train', 'validate'),
                f'n_bins = {encoder.n_bins}, depth = {depth}')

            filename = f'b={encoder.n_bins}&d={depth}.jpg'
            plt.savefig(plot_dir / filename)

            plt.close()

    # plot test set for the best one
    X_train_e = best_encoder.transform(X_train)
    X_test_e = best_encoder.transform(X_test)

    # back to dataframes
    X_train_e = pd.DataFrame(X_train_e, index=y_train.index)
    X_test_e = pd.DataFrame(X_test_e, index=y_test.index)

    best_tree.fit(X_train_e, y_train)
    y_train_pred = best_tree.predict(X_train_e)
    y_test_pred = best_tree.predict(X_test_e)

    metrics_train, cm_train = get_metrics(y_train, y_train_pred)
    metrics_test, cm_test = get_metrics(y_test, y_test_pred)

    plot_model(
        (metrics_train, metrics_test),
        (cm_train, cm_test),
        ('train', 'test'),
        f'n_bins = {best_encoder.n_bins}, depth = {best_tree.get_max_depth()}')

    filename = 'test-best.jpg'
    plt.savefig(plot_dir / filename)

    plt.close()
