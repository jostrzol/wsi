# by Jakub Ostrzołek

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import KBinsDiscretizer

from matplotlib import pyplot as plt

from argparse import ArgumentParser
from math import inf

import pandas as pd

from id3 import ID3Tree
from plot import get_metrics, plot_model


def constrain(min=-inf, max=inf, type=float):
    def wrapped_type(string: str):
        result = type(string)
        if result < min or result > max:
            raise ValueError(f"not in range [{min}, {max}]")
        return result
    return wrapped_type


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("n_bins", type=constrain(2, type=int),
                        help="number of bins to divide continouous data into")
    parser.add_argument("depth", type=constrain(0, type=int),
                        help="maximal tree depth")

    args = parser.parse_args()

    # prepare data

    df: pd.DataFrame = load_iris(as_frame=True)['frame']

    X = df.drop(['target'], axis=1)
    y = df['target']

    encoder = KBinsDiscretizer(
        args.n_bins,
        encode="ordinal",
        strategy="quantile")
    encoder.fit_transform(X)
    # back to dataframe after encoding
    X = pd.DataFrame(X, index=y.index)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    tree = ID3Tree(args.depth)

    tree.fit(X_train, y_train)
    y_train_pred = tree.predict(X_train)
    y_test_pred = tree.predict(X_test)

    metrics_train, cm_train = get_metrics(y_train, y_train_pred)
    metrics_test, cm_test = get_metrics(y_test, y_test_pred)

    plot_model(
        (metrics_train, metrics_test),
        (cm_train, cm_test),
        ('train', 'test'),
        f'n_bins = {encoder.n_bins}, depth = {tree.get_max_depth()}')

    plt.show()
    plt.close()
