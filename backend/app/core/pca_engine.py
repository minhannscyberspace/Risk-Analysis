from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA


def compute_pca(returns_df: pd.DataFrame) -> dict[str, object]:
    pca = PCA()
    pca.fit(returns_df)

    loadings: dict[str, list[float]] = {}
    for idx, component in enumerate(pca.components_):
        loadings[f"PC{idx + 1}"] = [float(value) for value in component]

    return {
        "feature_names": list(returns_df.columns),
        "explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
        "loadings": loadings,
    }
