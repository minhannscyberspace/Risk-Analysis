#!/usr/bin/env python3
"""
Prepare a returns CSV for Risk-Analysis from public price CSV files.

Usage example:
  python tools/prepare_returns_csv.py \
    --input data/SPY.csv --input data/QQQ.csv --input data/TLT.csv --input data/GLD.csv \
    --ticker SPY --ticker QQQ --ticker TLT --ticker GLD \
    --date-column Date --price-column Adj Close \
    --output backend/data/sample_returns_public.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert price CSV files to aligned daily returns CSV.")
    parser.add_argument("--input", action="append", required=True, help="Path to one price CSV file.")
    parser.add_argument("--ticker", action="append", required=True, help="Ticker/column name for each input file.")
    parser.add_argument("--date-column", default="Date", help="Date column name in input CSV (default: Date).")
    parser.add_argument(
        "--price-column",
        default="Adj Close",
        help="Price column name in input CSV (default: Adj Close).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output returns CSV.",
    )
    return parser.parse_args()


def load_price_series(csv_path: Path, date_col: str, price_col: str, ticker: str) -> pd.Series:
    frame = pd.read_csv(csv_path)
    if date_col not in frame.columns or price_col not in frame.columns:
        raise ValueError(
            f"{csv_path} missing required columns. Found: {list(frame.columns)}; "
            f"expected date='{date_col}', price='{price_col}'."
        )

    temp = frame[[date_col, price_col]].copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna(subset=[date_col, price_col]).sort_values(date_col)
    temp = temp.drop_duplicates(subset=[date_col], keep="last")
    return temp.set_index(date_col)[price_col].rename(ticker)


def main() -> None:
    args = parse_args()
    if len(args.input) != len(args.ticker):
        raise ValueError("Number of --input and --ticker arguments must match.")

    series_list: list[pd.Series] = []
    for csv_path, ticker in zip(args.input, args.ticker):
        series = load_price_series(
            csv_path=Path(csv_path),
            date_col=args.date_column,
            price_col=args.price_column,
            ticker=ticker,
        )
        series_list.append(series)

    prices = pd.concat(series_list, axis=1).dropna(how="any")
    returns = prices.pct_change().dropna(how="any")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    returns.to_csv(output_path, index=False)
    print(f"Wrote returns CSV: {output_path} ({len(returns)} rows, {len(returns.columns)} columns)")


if __name__ == "__main__":
    main()
