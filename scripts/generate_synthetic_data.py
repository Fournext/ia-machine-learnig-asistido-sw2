"""Generate reproducible, as-of customer snapshots and future renewal labels.

Attendance is simulated only for observation_date and the preceding 59 days.
Renewal outcomes are simulated afterwards and never included in the features.
This is demonstration data, not evidence of performance on real gym customers.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "datasets" / "synthetic_gym_churn.csv"


def generate_dataset(rows: int = 3600, seed: int = 42) -> pd.DataFrame:
    if rows < 1200:
        raise ValueError("Generate at least 1,200 customers.")
    rng = np.random.default_rng(seed)
    records = []
    for index in range(rows):
        observation = pd.Timestamp("2022-01-01") + pd.Timedelta(
            days=int(rng.integers(0, 1096))
        )
        membership = str(rng.choice(["Mensual", "Trimestral", "Anual"], p=[.55, .28, .17]))
        duration = {"Mensual": 30, "Trimestral": 90, "Anual": 365}[membership]
        remaining = int(rng.integers(-10, min(duration, 61)))
        renewals = int(min(rng.geometric(.35) - 1, 12))
        seniority = max(60, renewals * duration + duration - remaining)
        commitment = float(rng.beta(2.8, 2.0))
        baseline = float(rng.uniform(1.2, 5.5))
        declining = rng.random() < .33
        change = float(rng.uniform(.12, .55) if declining else rng.uniform(.75, 1.35))
        # Index 0 is 59 days ago; index 59 is the observation date.
        rates = np.r_[np.full(30, baseline / 7), np.full(30, baseline * change / 7)]
        visits = (rng.random(60) < np.clip(rates, 0, .95)).astype(int)
        if declining:
            visits[60 - int(rng.integers(2, 22)):] = 0
        last_7 = int(visits[-7:].sum())
        last_30 = int(visits[-30:].sum())
        previous_30 = int(visits[:30].sum())
        attended = np.flatnonzero(visits)
        since_last = int(59 - attended[-1]) if attended.size else 60
        # Eight complete trailing seven-day windows.
        empty_weeks = float(np.mean(visits[-56:].reshape(8, 7).sum(axis=1) == 0))
        longest, current = 0, 0
        for visit in visits:
            current = 0 if visit else current + 1
            longest = max(longest, current)
        compliance = float(np.clip(
            .55 * min(last_30 / max(baseline * 30 / 7, 1), 1)
            + .45 * commitment + rng.normal(0, .06), 0, 1
        ))
        variation = (last_30 - previous_30) * 7 / 30
        trend = (last_30 - previous_30) / max(previous_30, 1)
        # Risk uses only past/current covariates plus unobserved customer noise.
        logit = (
            -2.05 + .075 * since_last + 1.05 * empty_weeks
            - .65 * compliance - .09 * min(renewals, 6)
            - .65 * variation + .32 * (membership == "Mensual")
            - .35 * (membership == "Anual") + rng.normal(0, .35)
        )
        probability = 1 / (1 + np.exp(-logit))
        will_miss_deadline = rng.random() < probability
        expiration = observation + pd.Timedelta(days=remaining)
        deadline = expiration + pd.Timedelta(days=30)
        if will_miss_deadline:
            renewal_date = deadline + pd.Timedelta(days=int(rng.integers(1, 91)))
        else:
            earliest = max(observation + pd.Timedelta(days=1), expiration)
            renewal_date = earliest + pd.Timedelta(
                days=int(rng.integers(0, (deadline - earliest).days + 1))
            )
        records.append({
            "client_id": str(uuid5(NAMESPACE_URL, f"gym-synthetic/{seed}/{index}")),
            "observation_date": observation.strftime("%Y-%m-%d"),
            "membership_type": membership,
            "duration_days": duration,
            "days_until_expiration": remaining,
            "previous_renewals_count": renewals,
            "client_seniority_days": seniority,
            "attendances_last_7d": last_7,
            "attendances_last_30d": last_30,
            "attendances_last_60d": last_30 + previous_30,
            "days_since_last_attendance": since_last,
            "weekly_frequency": round(last_30 * 7 / 30, 6),
            "frequency_variation": round(variation, 6),
            "attendance_trend": round(trend, 6),
            "pct_weeks_without_visit": empty_weeks,
            "inactivity_max_days": longest,
            "routine_compliance_score": round(compliance, 6),
            "churn_30d": int(renewal_date > deadline),
        })
    data = pd.DataFrame(records).sort_values("observation_date", kind="stable")
    return data.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=3600)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = generate_dataset(args.rows, args.seed)
    if not .20 <= data.churn_30d.mean() <= .35:
        raise ValueError("Sample churn is outside 20%-35%; choose more rows or another seed.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.output, index=False)
    print(data.groupby("membership_type").agg(
        customers=("client_id", "size"), churn_rate=("churn_30d", "mean"),
        mean_weekly_visits=("weekly_frequency", "mean"),
    ).to_string(float_format=lambda value: f"{value:.4f}"))
    print(f"\nRows: {len(data):,} | Churn: {data.churn_30d.mean():.2%}")
    print(f"Observation dates: {data.observation_date.min()} to {data.observation_date.max()}")
    print(f"Saved: {args.output.resolve()}")


if __name__ == "__main__":
    main()
