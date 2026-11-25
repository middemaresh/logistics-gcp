#!/usr/bin/env python3
"""Upload a shipment CSV to GCS and load it into a partitioned BigQuery table."""

import argparse
from pathlib import Path

from google.cloud import bigquery, storage

SCHEMA = [
    bigquery.SchemaField("shipment_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("event_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("origin", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("destination", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("carrier", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("weight_kg", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("shipping_cost", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("delivery_days", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("on_time", "BOOL", mode="REQUIRED"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Google Cloud project ID")
    parser.add_argument("--bucket", required=True, help="Existing GCS landing bucket")
    parser.add_argument("--input", type=Path, required=True, help="Local shipment CSV")
    parser.add_argument("--dataset", default="logistics_analytics")
    parser.add_argument("--table", default="shipment_events")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")

    object_name = "shipments/shipments.csv"
    storage_client = storage.Client(project=args.project)
    storage_client.bucket(args.bucket).blob(object_name).upload_from_filename(str(args.input))

    table_id = f"{args.project}.{args.dataset}.{args.table}"
    config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(field="event_date"),
        clustering_fields=["carrier", "status"],
    )
    job = bigquery.Client(project=args.project).load_table_from_uri(
        f"gs://{args.bucket}/{object_name}", table_id, job_config=config
    )
    job.result()
    table = bigquery.Client(project=args.project).get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}")


if __name__ == "__main__":
    main()
