from pathlib import Path

import pandas as pd

from app.services.analysis_store import SQLiteAnalysisStore


def test_sqlite_store_persists_records_across_instances(tmp_path: Path) -> None:
    db_file = tmp_path / "risk_analysis_test.db"
    store_a = SQLiteAnalysisStore(db_path=db_file)

    frame = pd.DataFrame({"asset_a": [0.01, 0.02], "asset_b": [0.0, -0.01]})
    dataset_id = store_a.save_dataset(frame)
    analysis_id = store_a.save_analysis(
        dataset_id=dataset_id,
        summary={"mean_return": 0.005, "volatility": 0.01, "historical_var": -0.01, "cvar": -0.015},
        pca={"feature_names": ["asset_a", "asset_b"], "explained_variance_ratio": [0.7, 0.3], "loadings": {}},
        risk={"historical_var": -0.01, "parametric_var": -0.008, "cvar": -0.015, "breach_frequency": 0.05, "confidence_level": 0.95},
        metrics={"mean_return": 0.005, "volatility": 0.01, "sharpe": 0.5, "sortino": 0.7, "max_drawdown": -0.03, "rolling_volatility": 0.01},
    )
    scenario_id = store_a.save_scenario_run(
        analysis_id=analysis_id,
        scenarios={"historical_crisis": {"mean_return": -0.02, "delta_vs_base": -0.025}},
    )
    report_id = store_a.save_report(
        analysis_id=analysis_id,
        report={"highlights": ["Persistence test"]},
    )

    # Re-open with a new store instance to verify persistence survives restarts.
    store_b = SQLiteAnalysisStore(db_path=db_file)
    loaded_dataset = store_b.get_dataset(dataset_id)
    loaded_analysis = store_b.get_analysis(analysis_id)
    loaded_scenario = store_b.get_scenario_run(scenario_id)
    loaded_report = store_b.get_report(report_id)

    assert not loaded_dataset.empty
    assert loaded_analysis["analysis_id"] == analysis_id
    assert loaded_scenario["analysis_id"] == analysis_id
    assert loaded_report["analysis_id"] == analysis_id
    assert loaded_report["report"]["highlights"] == ["Persistence test"]
