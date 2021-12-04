# by Jakub Ostrzołek

from __future__ import annotations
from typing import Any, Iterable, Optional, Union
from math import log
from collections import Counter

import pandas as pd
import numpy as np


class ID3Node:
    def __init__(self,
                 attribute: str,
                 mapped_values: Iterable[int],
                 next_nodes: Iterable[Union[ID3Node, int]]):

        self._decision_dict = {
            value: next_node
            for value, next_node in zip(mapped_values, next_nodes)}
        self._attribute = attribute

    def predict(self, row: pd.Series):
        value = row[self._attribute]
        try:
            next = self._decision_dict[value]
            return next.predict(row) if isinstance(
                next, ID3Node) else next
        except KeyError:
            # node unfit for the given value
            # return the most frequent class returned by all children
            classes = [
                next.predict(row) if isinstance(next, ID3Node)
                else next for next in self._decision_dict.values()]
            return Counter(classes).most_common(n=1)[0][0]


def _entropy(y: pd.Series):
    class_counts = y.value_counts()
    total = class_counts.sum()

    def partial(count: int):
        frequency = count / total
        return -frequency * log(frequency)
    return class_counts.apply(partial).sum()


def _division_entropy(X: pd.DataFrame, y: pd.Series,
                      division_label: Any):
    div_attr_counts = X[division_label].value_counts()
    total = div_attr_counts.sum()

    def partial(attr_value: int):
        count = div_attr_counts[attr_value]
        mask = X[division_label] == attr_value
        return count / total * _entropy(y[mask])
    return sum(div_attr_counts.index.map(partial))


def _division_info_gain(X: pd.DataFrame, y: pd.Series,
                        division_label: Any):
    return _entropy(y) - \
        _division_entropy(X, y, division_label)


class ID3Tree:
    def __init__(self, max_depth: int):
        self._max_depth = max_depth
        self._root: Optional[ID3Node] = None

    def get_max_depth(self):
        return self._max_depth

    def _fit(self, X: pd.DataFrame, y: pd.Series, depth: int):
        class_counts = y.value_counts()
        if class_counts.size == 1 or depth == 0 or X.shape[1] == 0:
            return class_counts.index[0]

        best_label = max(
            X.columns,
            key=lambda c: _division_info_gain(X, y, c))

        uniques = X[best_label].unique()
        next_nodes = [self._fit(
            X[X[best_label] == value].drop(best_label, axis=1),
            y[X[best_label] == value],
            depth - 1) for value in uniques]
        return ID3Node(
            best_label,
            uniques,
            next_nodes)

    def fit(self, X: Union[pd.DataFrame, np.ndarray],
            y: Union[pd.Series, np.ndarray]):
        X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        y = y if isinstance(y, pd.Series) else pd.Series(y)
        X.index = y.index
        self._root = self._fit(X, y, self._max_depth)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        if self._root is None:
            raise RuntimeError("Cannot predict using unfit model")
        X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        root = self._root
        return X.apply(
            lambda row: root.predict(row) if isinstance(
                root, ID3Node) else root,
            axis=1)
