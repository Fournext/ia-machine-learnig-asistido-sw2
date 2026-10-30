"""Train, temporally calibrate, evaluate and persist a gym churn pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
NUMERIC_FEATURES = [
    "duration_days", "days_until_expiration", "previous_renewals_count",
    "client_seniority_days", "attendances_last_7d", "attendances_last_30d",
    "attendances_last_60d", "days_since_last_attendance", "weekly_frequency",
    "frequency_variation", "attendance_trend", "pct_weeks_without_visit",
    "inactivity_max_days", "routine_compliance_score",
]
FEATURES = NUMERIC_FEATURES + ["membership_type"]
TARGET = "churn_30d"


def load_dataset(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = FEATURES + ["client_id", "observation_date", TARGET]
    missing = set(required) - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if data[required].isna().any().any():
        raise ValueError("Dataset contains missing values.")
    if not np.isfinite(data[NUMERIC_FEATURES].to_numpy(dtype=float)).all():
        raise ValueError("Numerical features must be finite.")
    if set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("Target must contain both binary classes.")
    if data.client_id.duplicated().any():
        raise ValueError("Expected one independent snapshot per client.")
    expected_duration = data.membership_type.map({"Mensual": 30, "Trimestral": 90, "Anual": 365})
    if expected_duration.isna().any() or not expected_duration.eq(data.duration_days).all():
        raise ValueError("Invalid membership type or duration.")
    data["observation_date"] = pd.to_datetime(data.observation_date, format="%Y-%m-%d")
    return data.sort_values("observation_date", kind="stable").reset_index(drop=True)


def temporal_split(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Keep date groups intact and purge labels unavailable at the next boundary."""
    dates = np.sort(data.observation_date.unique())
    if len(dates) < 10:
        raise ValueError("Need at least ten distinct observation dates.")
    val_start, test_start = pd.Timestamp(dates[int(.70 * len(dates))]), pd.Timestamp(
        dates[int(.85 * len(dates))]
    )
    label_available = data.observation_date + pd.to_timedelta(
        data.days_until_expiration + 30, unit="D"
    )
    if (label_available <= data.observation_date).any():
        raise ValueError("Snapshots must precede their renewal outcome deadline.")
    train = data[(data.observation_date < val_start) & (label_available < val_start)].copy()
    val = data[(data.observation_date >= val_start) & (data.observation_date < test_start)
               & (label_available < test_start)].copy()
    test = data[data.observation_date >= test_start].copy()
    for name, split in [("train", train), ("validation", val), ("test", test)]:
        if len(split) < 20 or split[TARGET].nunique() != 2:
            raise ValueError(f"{name} needs at least 20 rows and both classes after purging.")
    return train, val, test


def train_model(train: pd.DataFrame, val: pd.DataFrame) -> tuple[Pipeline, list[str], dict]:
    preprocessing = ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         ["membership_type"]),
    ])
    forest = RandomForestClassifier(
        n_estimators=150, max_depth=8, min_samples_split=5, min_samples_leaf=3,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )
    base = Pipeline([("preprocessor", preprocessing), ("classifier", forest)])
    base.fit(train[FEATURES], train[TARGET])
    # sklearn >=1.6 supports FrozenEstimator; older versions require cv='prefit'.
    try:
        from sklearn.frozen import FrozenEstimator
    except ImportError:
        calibrated = CalibratedClassifierCV(forest, method="sigmoid", cv="prefit")
        calibration_api = "cv=prefit"
    else:
        calibrated = CalibratedClassifierCV(FrozenEstimator(forest), method="sigmoid")
        calibration_api = "FrozenEstimator (prefitted classifier)"
    calibrated.fit(preprocessing.transform(val[FEATURES]), val[TARGET])
    model = Pipeline([("preprocessor", preprocessing), ("classifier", calibrated)])
    names = preprocessing.get_feature_names_out().tolist()
    importance = dict(zip(names, forest.feature_importances_.tolist()))
    return model, names, {"calibration_api": calibration_api, "impurity_importance": importance}


def evaluate(model: Pipeline, test: pd.DataFrame) -> dict:
    probability = model.predict_proba(test[FEATURES])[:, 1]
    prediction = (probability >= .5).astype(int)
    target = test[TARGET]
    return {
        "accuracy": float(accuracy_score(target, prediction)),
        "precision": float(precision_score(target, prediction, zero_division=0)),
        "recall": float(recall_score(target, prediction, zero_division=0)),
        "f1_score": float(f1_score(target, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(target, probability)),
        "pr_auc": float(average_precision_score(target, probability)),
        "brier_score": float(brier_score_loss(target, probability)),
        "confusion_matrix": confusion_matrix(target, prediction, labels=[0, 1]).tolist(),
    }


def run_training(dataset: Path, output: Path) -> dict:
    data = load_dataset(dataset)
    train, val, test = temporal_split(data)
    model, names, details = train_model(train, val)
    metrics = evaluate(model, test)
    permutation = permutation_importance(
        model, test[FEATURES], test[TARGET], scoring="roc_auc", n_repeats=5,
        random_state=42, n_jobs=1,
    )
    metadata = {
        "model_version": "1.0.0", "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(dataset.resolve()),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "library_versions": {"sklearn": sklearn.__version__, "pandas": pd.__version__,
                             "numpy": np.__version__, "joblib": joblib.__version__},
        "feature_names": FEATURES, "transformed_feature_names": names,
        "target": TARGET, "threshold": .5, "random_state": 42,
        "target_definition": "No renewal by membership expiration + 30 days",
        "data_kind": "synthetic; metrics do not establish real-world performance",
        "pr_auc_definition": "average precision (non-interpolated precision-recall area)",
        "confusion_matrix_labels": [0, 1], "metrics": metrics,
        "hyperparameters": {
            "n_estimators": 150, "max_depth": 8, "min_samples_split": 5,
            "min_samples_leaf": 3, "class_weight": "balanced", "random_state": 42,
        },
        "calibration": {"method": "sigmoid", "fit_split": "validation",
                        "api": details["calibration_api"]},
        "split_policy": "70/15/15 unique dates; purge train/validation labels crossing next boundary",
        "purged_rows": len(data) - len(train) - len(val) - len(test),
        "splits": {
            name: {"rows": len(split), "start": split.observation_date.min().isoformat(),
                   "end": split.observation_date.max().isoformat(),
                   "churn_rate": float(split[TARGET].mean())}
            for name, split in [("train", train), ("validation", val), ("test", test)]
        },
        "impurity_importance": details["impurity_importance"],
        "permutation_importance": {
            feature: {"mean": float(mean), "std": float(std)}
            for feature, mean, std in zip(FEATURES, permutation.importances_mean,
                                          permutation.importances_std)
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    model_path = output / "model.joblib"
    joblib.dump(model, model_path, compress=3)
    restored = joblib.load(model_path)
    np.testing.assert_allclose(restored.predict_proba(test[FEATURES]),
                               model.predict_proba(test[FEATURES]), rtol=1e-12, atol=1e-12)
    metadata["model_sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    print(pd.DataFrame(metadata["splits"]).T.to_string())
    print("\nIndependent test metrics (threshold=0.5):")
    for name, value in metrics.items():
        print(f"{name:20s}: {value:.6f}" if isinstance(value, float) else f"{name}: {value}")
    print("Confusion matrix: rows=true, columns=predicted, class order=[0, 1]")
    print("\nPermutation importance (mean decrease in test ROC-AUC):")
    print(pd.DataFrame(metadata["permutation_importance"]).T.sort_values(
        "mean", ascending=False).to_string(float_format=lambda value: f"{value:.6f}"))
    print(f"\nSaved and reload-verified: {model_path.resolve()}")
    print(f"Saved: {(output / 'metadata.json').resolve()}")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "datasets/synthetic_gym_churn.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/models/v1.0.0")
    args = parser.parse_args()
    run_training(args.dataset, args.output_dir)


if __name__ == "__main__":
    main()
