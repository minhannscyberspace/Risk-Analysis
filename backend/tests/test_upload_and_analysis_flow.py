from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_run_and_fetch_analysis_flow() -> None:
    csv_payload = "asset_a,asset_b\n0.01,0.02\n-0.01,0.00\n0.03,0.01\n"
    upload_response = client.post(
        "/api/upload/file",
        files={"file": ("returns.csv", csv_payload, "text/csv")},
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert upload_body["rows"] == 3
    assert set(upload_body["columns"]) == {"asset_a", "asset_b"}

    run_response = client.post(
        "/api/analysis/run",
        json={"dataset_id": upload_body["dataset_id"], "confidence_level": 0.95},
    )
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["status"] == "completed"

    get_response = client.get(f"/api/analysis/{run_body['analysis_id']}")
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["status"] == "completed"
    assert get_body["dataset_id"] == upload_body["dataset_id"]
    assert "mean_return" in get_body["summary"]

    pca_response = client.get(f"/api/analysis/{run_body['analysis_id']}/pca")
    assert pca_response.status_code == 200
    assert "explained_variance_ratio" in pca_response.json()

    risk_response = client.get(f"/api/analysis/{run_body['analysis_id']}/risk")
    assert risk_response.status_code == 200
    assert "historical_var" in risk_response.json()

    metrics_response = client.get(f"/api/analysis/{run_body['analysis_id']}/metrics")
    assert metrics_response.status_code == 200
    assert "sharpe" in metrics_response.json()

    scenario_run_response = client.post(
        "/api/scenarios/run", json={"analysis_id": run_body["analysis_id"]}
    )
    assert scenario_run_response.status_code == 200
    scenario_id = scenario_run_response.json()["scenario_id"]

    scenario_get_response = client.get(f"/api/scenarios/{scenario_id}")
    assert scenario_get_response.status_code == 200
    assert "historical_crisis" in scenario_get_response.json()["scenarios"]

    report_gen_response = client.post(
        "/api/reports/generate", json={"analysis_id": run_body["analysis_id"]}
    )
    assert report_gen_response.status_code == 200
    report_id = report_gen_response.json()["report_id"]

    report_get_response = client.get(f"/api/reports/{report_id}")
    assert report_get_response.status_code == 200
    assert "highlights" in report_get_response.json()["report"]
