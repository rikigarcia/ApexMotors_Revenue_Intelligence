from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def assign_temp(days: float) -> str:
    if days <= 7:
        return "Hot"
    if days <= 30:
        return "Warm"
    return "Cold"


def build_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()

    # Impute first so derived features cannot create NaNs.
    if "App_Engagement_Mins" in df.columns:
        df["App_Engagement_Mins"] = pd.to_numeric(df["App_Engagement_Mins"], errors="coerce")
        df["App_Engagement_Mins"] = df["App_Engagement_Mins"].fillna(df["App_Engagement_Mins"].median())

    df["Last_Contact_Days"] = pd.to_numeric(df["Last_Contact_Days"], errors="coerce").fillna(0)

    df["Engagement_Density"] = df["App_Engagement_Mins"] / (df["Last_Contact_Days"] + 1)
    df["High_Intent_Signal"] = (
        (df["Web_Configurator_Status"] == 1) & (df["Test_Drive_Completed"] == 1)
    ).astype(int)
    df["Lead_Temperature"] = df["Last_Contact_Days"].apply(assign_temp)
    df["Attrition_Risk"] = ((df["App_Engagement_Mins"] < 60) & (df["Last_Contact_Days"] > 30)).astype(int)

    df_final = pd.get_dummies(df, columns=["Lead_Source", "Lead_Temperature"], drop_first=True)

    for col in df_final.columns:
        if df_final[col].dtype == bool:
            df_final[col] = df_final[col].astype(int)

    numeric_cols = df_final.columns.drop(["Lead_ID"], errors="ignore")
    df_final[numeric_cols] = df_final[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df_final = df_final.fillna(df_final.median(numeric_only=True))

    return df_final


def write_schema_report(df: pd.DataFrame, output_path: Path) -> None:
    report = {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "null_counts": df.isna().sum().to_dict(),
        "dtypes": {k: str(v) for k, v in df.dtypes.to_dict().items()},
    }
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build ApexMotors processed dataset artifact.")
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("data/raw/apex_leads_v3.csv"),
        help="Path to raw input CSV.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/processed/apex_leads_final_v3.csv"),
        help="Path to processed output CSV.",
    )
    parser.add_argument(
        "--schema-out",
        type=Path,
        default=Path("data/processed/apex_leads_final_v3.schema.json"),
        help="Path to schema report JSON.",
    )
    args = parser.parse_args()

    if not args.raw.exists():
        raise FileNotFoundError(f"Raw dataset not found at {args.raw}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.schema_out.parent.mkdir(parents=True, exist_ok=True)

    df_raw = pd.read_csv(args.raw)
    df_processed = build_features(df_raw)

    if df_processed.isna().values.any():
        raise ValueError("Processed dataset still contains NaN values after cleaning.")

    df_processed.to_csv(args.out, index=False)
    write_schema_report(df_processed, args.schema_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

