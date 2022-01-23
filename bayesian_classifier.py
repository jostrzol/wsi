from typing import Any, Dict

import numpy as np
import pandas as pd


class BayesianClassifier:
    _y_probs: Dict[Any, float]
    # _y_probs: {
    #   label: P(y=label)
    # }
    _X_probs: Dict[Any, Dict[Any, Dict[Any, float]]]
    # _X_probs: {
    #   label: {
    #     column: {
    #       value: P(column=value|y=label)
    #     }
    #   }
    # }

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        y_counts = y.value_counts()
        n_samples = y.shape[0]
        self._y_probs = {
            label: count /
            n_samples for label,
            count in y_counts.items()}

        self._X_probs = {label: {} for label in y_counts.keys()}
        for column in X:
            for col_dict in self._X_probs.values():
                col_dict[column] = {}
            for value in X[column].unique():
                value_y_counts = {label: 0 for label in y_counts.keys()}
                mask = X[column] == value
                for label, count in y[mask].value_counts().items():
                    value_y_counts[label] = count

                for label, count in value_y_counts.items():
                    prob = count / y_counts[label]
                    self._X_probs[label][column][value] = prob

    def _predict_row(self, row: pd.Series):
        y_preds = {}
        for label, col_dict in self._X_probs.items():
            y_preds[label] = np.prod([
                col_dict[col][row[col]] for col in row.index
            ]) * self._y_probs[label]
        return max(y_preds, key=lambda label: y_preds[label])

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return X.apply(self._predict_row, axis=1)
