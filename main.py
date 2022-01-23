from typing import Dict, List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import KBinsDiscretizer

from bayesian_classifier import BayesianClassifier
from evaluate import get_metrics, plot_model

N_BINS = 5
TEST_SIZE = 0.2
N_SPLITS = 4


if __name__ == "__main__":
    X, y = load_wine(return_X_y=True, as_frame=True)

    discretizer = KBinsDiscretizer(
        n_bins=N_BINS, encode='ordinal', strategy='quantile')
    X = pd.DataFrame(
        discretizer.fit_transform(X),
        index=X.index,
        columns=X.columns,
        dtype=np.uint8)

    X_rest, X_test, y_rest, y_test = train_test_split(
        X, y, test_size=TEST_SIZE)

    kfold = KFold(n_splits=N_SPLITS)
    models: List[BayesianClassifier] = []
    metrics_train: List[Dict[str, float]] = []
    cms_train: List[np.ndarray] = []
    metrics_val: List[Dict[str, float]] = []
    cms_val: List[np.ndarray] = []
    for train_index, val_index in kfold.split(X_rest, y_rest):
        X_train = X_rest.iloc[train_index]
        y_train = y_rest.iloc[train_index]
        X_val = X_rest.iloc[val_index]
        y_val = y_rest.iloc[val_index]

        model = BayesianClassifier()
        model.fit(X_train, y_train)
        models.append(model)

        y_pred_train = model.predict(X_train)
        m_train, cm_train = get_metrics(y_train, y_pred_train)
        metrics_train.append(m_train)
        cms_train.append(cm_train)

        y_pred_val = model.predict(X_val)
        m_val, cm_val = get_metrics(y_val, y_pred_val)
        metrics_val.append(m_val)
        cms_val.append(cm_val)

    plot_model(
        metrics_val,
        cms_val,
        tuple(f'fold {i+1}' for i in range(len(models))),
        "BayesianClassifier validation sets metrics"
    )
    plt.show()

    best_i = max(range(len(models)),
                 key=lambda i: sum(metrics_val[i].values()))
    model = models[best_i]
    m_train = metrics_train[best_i]
    cm_train = cms_train[best_i]
    m_val = metrics_val[best_i]
    cm_val = cms_val[best_i]
    y_pred_test = model.predict(X_test)
    m_test, cm_test = get_metrics(y_test, y_pred_test)

    plot_model(
        (m_train, m_val, m_test),
        (cm_train, cm_val, cm_test),
        ("train", "validation", "test"),
        "BayesianClassifier best fold metrics"
    )
    plt.show()
