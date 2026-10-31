#!/usr/bin/env python3
"""Compare positive NAVs on common observation dates. No network or dependencies."""
import argparse
import csv
from datetime import date
import json
import math
from pathlib import Path
import sys


def compare(path, value_kind):
    products = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"product", "date", "nav"} <= set(reader.fieldnames or []):
            raise ValueError("CSV requires product,date,nav columns")
        for line, row in enumerate(reader, 2):
            name = row["product"].strip()
            if not name:
                raise ValueError(f"Empty product at line {line}")
            day = date.fromisoformat(row["date"])
            if day.isoformat() != row["date"]:
                raise ValueError(f"Use YYYY-MM-DD dates at line {line}")
            nav = float(row["nav"])
            if not math.isfinite(nav) or nav <= 0:
                raise ValueError(f"NAV must be finite and positive at line {line}")
            points = products.setdefault(name, {})
            if day in points:
                raise ValueError(f"Duplicate product/date at line {line}")
            points[day] = nav
    if len(products) < 2:
        raise ValueError("At least two products are required")
    days = sorted(set.intersection(*(set(points) for points in products.values())))
    if len(days) < 2:
        raise ValueError("At least two common observation dates are required")
    elapsed = (days[-1] - days[0]).days
    results = []
    for name, points in products.items():
        values = [points[day] for day in days]
        ratio = values[-1] / values[0]
        if not math.isfinite(ratio) or ratio <= 0:
            raise ValueError("NAV ratio cannot be represented as a finite positive number")
        peak = values[0]
        drawdown = 0.0
        for value in values:
            peak = max(peak, value)
            drawdown = min(drawdown, value / peak - 1)
        annualized = math.expm1(math.log(ratio) * 365.25 / elapsed) if elapsed >= 365 else None
        if annualized is not None and not math.isfinite(annualized):
            raise ValueError("Annualized return cannot be represented as a finite number")
        results.append({"product": name, "inputPoints": len(points),
                        "excludedNonCommonPoints": len(points) - len(days),
                        "totalReturn": ratio - 1, "annualizedReturn": annualized,
                        "sampledMaxDrawdown": drawdown,
                        "normalizedSeries": [{"date": day.isoformat(), "value": value / values[0]}
                                             for day, value in zip(days, values)]})
    return {"valueKind": value_kind, "approximate": value_kind == "reference-nav",
            "startDate": days[0].isoformat(), "endDate": days[-1].isoformat(),
            "commonPoints": len(days), "calendarDays": elapsed, "returnUnit": "decimal",
            "alignment": "intersection-of-observed-dates-no-fill",
            "drawdownBasis": "common-observation-sample-not-full-history",
            "annualizationBasis": "calendar-365.25-only-if-at-least-365-days",
            "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--value-kind", required=True, choices=["adjusted-nav", "reference-nav"])
    parser.add_argument("--output", help="Write JSON to this path, otherwise stdout")
    args = parser.parse_args()
    try:
        result = json.dumps(compare(args.csv, args.value_kind), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            if Path(args.output).resolve() == Path(args.csv).resolve():
                raise ValueError("Output must not overwrite input")
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            print(result, end="")
        return 0
    except (ValueError, OSError, OverflowError, KeyError, TypeError) as error:
        print(f"Cannot compare NAV: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
