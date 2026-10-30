"""Check snapshot consistency, temporal isolation and persisted predictions."""

import importlib.util
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_script("generate_synthetic_data")
trainer = load_script("train_and_evaluate")


@pytest.fixture(scope="module")
def data():
    return generator.generate_dataset()


def test_reproducible_dataset():
    first = generator.generate_dataset(1200)
    pd.testing.assert_frame_equal(first, generator.generate_dataset(1200))
    assert .20 <= first.churn_30d.mean() <= .35
    with pytest.raises(ValueError, match="1,200"):
        generator.generate_dataset(100)


def test_snapshot_constraints(data):
    assert len(data) >= 1200
    assert data.client_id.is_unique
    assert not data.isna().any().any()
    assert .20 <= data.churn_30d.mean() <= .35
    assert set(data.columns) == set(trainer.FEATURES + ["client_id", "observation_date", "churn_30d"])
    assert data.duration_days.eq(data.membership_type.map(
        {"Mensual": 30, "Trimestral": 90, "Anual": 365})).all()
    assert (data.attendances_last_7d <= data.attendances_last_30d).all()
    assert (data.attendances_last_30d <= data.attendances_last_60d).all()
    assert data.attendances_last_7d.between(0, 7).all()
    assert data.attendances_last_30d.between(0, 30).all()
    assert data.attendances_last_60d.between(0, 60).all()
    assert data.days_since_last_attendance.between(0, 60).all()
    assert (data.inactivity_max_days >= data.days_since_last_attendance).all()
    assert (data.inactivity_max_days <= 60).all()
    for days, feature in [(7, "attendances_last_7d"), (30, "attendances_last_30d"),
                          (60, "attendances_last_60d")]:
        assert (data.loc[data.days_since_last_attendance >= days, feature] == 0).all()
    for feature in ["pct_weeks_without_visit", "routine_compliance_score"]:
        assert data[feature].between(0, 1).all()
    np.testing.assert_allclose(data.weekly_frequency, data.attendances_last_30d * 7 / 30, atol=1e-6)
    np.testing.assert_allclose(data.frequency_variation,
                               (2 * data.attendances_last_30d - data.attendances_last_60d) * 7 / 30,
                               atol=1e-6)


def test_temporal_label_isolation(data):
    dated = data.copy()
    dated.observation_date = pd.to_datetime(dated.observation_date)
    train, val, test = trainer.temporal_split(dated)
    assert train.observation_date.max() < val.observation_date.min()
    assert val.observation_date.max() < test.observation_date.min()
    for earlier, later in [(train, val), (val, test)]:
        deadlines = earlier.observation_date + pd.to_timedelta(earlier.days_until_expiration + 30, unit="D")
        assert deadlines.max() < later.observation_date.min()
        assert set(earlier.client_id).isdisjoint(later.client_id)
    assert len(train) + len(val) + len(test) < len(data)


def test_input_validation(data, tmp_path):
    path = tmp_path / "bad.csv"
    for invalid in [data.drop(columns="membership_type"),
                    data.assign(churn_30d=2), data.assign(client_id="duplicate"),
                    data.assign(weekly_frequency=float("inf"))]:
        invalid.to_csv(path, index=False)
        with pytest.raises(ValueError):
            trainer.load_dataset(path)
    dated = data.copy()
    dated.observation_date = pd.Timestamp("2024-01-01")
    with pytest.raises(ValueError, match="ten distinct"):
        trainer.temporal_split(dated)


def test_training_and_serialization(data, tmp_path):
    path = tmp_path / "data.csv"
    data.to_csv(path, index=False)
    output = tmp_path / "artifacts"
    metadata = trainer.run_training(path, output)
    model = joblib.load(output / "model.joblib")
    assert isinstance(model, Pipeline)
    assert (output / "metadata.json").is_file()
    assert len(metadata["transformed_feature_names"]) == 17
    assert metadata["feature_names"] == trainer.FEATURES
    assert set(metadata["permutation_importance"]) == set(trainer.FEATURES)
    assert sum(map(sum, metadata["metrics"]["confusion_matrix"])) == metadata["splits"]["test"]["rows"]
    for name, metric in metadata["metrics"].items():
        if name != "confusion_matrix":
            assert 0 <= metric <= 1
    dated = trainer.load_dataset(path)
    train, val, test = trainer.temporal_split(dated)
    scaler = model.named_steps["preprocessor"].named_transformers_["numeric"]
    np.testing.assert_allclose(scaler.mean_, train[trainer.NUMERIC_FEATURES].mean())
    assert not set(model.feature_names_in_) & {"client_id", "observation_date", "churn_30d"}
    probability = model.predict_proba(test[trainer.FEATURES])
    assert probability.shape == (len(test), 2)
    np.testing.assert_allclose(probability.sum(axis=1), 1)
    reloaded_metrics = trainer.evaluate(model, test)
    for name, value in reloaded_metrics.items():
        if name == "confusion_matrix":
            assert value == metadata["metrics"][name]
        else:
            assert value == pytest.approx(metadata["metrics"][name], abs=1e-12)
    # The calibrated RF retains only the training samples, never validation samples.
    calibrated = model.named_steps["classifier"].calibrated_classifiers_[0]
    assert calibrated.estimator.estimators_[0].tree_.n_node_samples[0] <= len(train)
    unknown = test[trainer.FEATURES].iloc[:1].copy()
    unknown["membership_type"] = "Nueva"
    assert np.isfinite(model.predict_proba(unknown)).all()
