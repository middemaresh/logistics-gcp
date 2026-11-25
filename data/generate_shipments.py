#!/usr/bin/env python3
"""Generate reproducible synthetic shipment records as a CSV."""

import argparse
import csv
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CARRIERS = ["NorthStar", "RapidFreight", "BlueRoad", "ParcelPeak"]
CITIES = ["Seattle", "Portland", "San Francisco", "Los Angeles", "Denver", "Dallas", "Chicago", "Atlanta", "Miami", "New York"]
STATUSES = ["delivered", "in_transit", "delayed", "exception"]


def generate(output: Path, rows: int, seed: int) -> None:
    rng = random.Random(seed)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "shipment_id", "event_timestamp", "event_date", "status", "origin", "destination",
        "carrier", "weight_kg", "shipping_cost", "delivery_days", "on_time",
    ]
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for number in range(1, rows + 1):
            event_time = now - timedelta(minutes=rng.randint(0, 60 * 24 * 90))
            origin, destination = rng.sample(CITIES, 2)
            status = rng.choices(STATUSES, weights=[70, 18, 8, 4], k=1)[0]
            delivery_days = round(rng.uniform(0.5, 12), 2)
            on_time = status == "delivered" and delivery_days <= 5
            writer.writerow({
                "shipment_id": f"SHP-{number:08d}",
                "event_timestamp": event_time.isoformat().replace("+00:00", "Z"),
                "event_date": event_time.date().isoformat(),
                "status": status,
                "origin": origin,
                "destination": destination,
                "carrier": rng.choice(CARRIERS),
                "weight_kg": round(rng.uniform(0.2, 500), 2),
                "shipping_cost": round(rng.uniform(5, 250), 2),
                "delivery_days": delivery_days,
                "on_time": on_time,
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/shipments.csv"))
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.rows < 1:
        parser.error("--rows must be greater than zero")
    generate(args.output, args.rows, args.seed)
    print(f"Generated {args.rows} shipment rows at {args.output}")


if __name__ == "__main__":
    main()
