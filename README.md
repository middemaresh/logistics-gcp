# GCP Logistics Analytics Platform

A portfolio-ready batch data engineering project for logistics operations. It generates shipment data, lands it in Google Cloud Storage, loads it into a partitioned BigQuery table, and builds analytics marts for carrier and route performance.

## Architecture

```text
Synthetic shipment generator
        ↓ CSV
Google Cloud Storage (raw landing)
        ↓ BigQuery load job
BigQuery: logistics_analytics.shipment_events
        ↓ SQL transformations
Cleaned shipments + carrier and route performance marts
```

This starter intentionally uses managed GCP services and keeps orchestration simple. It is suitable for extending with Cloud Composer, scheduled queries, Pub/Sub streaming, or Looker dashboards.

## Repository layout

- `data/generate_shipments.py` — creates deterministic synthetic shipment CSV data.
- `src/load_to_bigquery.py` — uploads the CSV to GCS and loads it to a partitioned BigQuery table.
- `sql/` — deduplication, analytics marts, and data-quality assertions.
- `terraform/` — provisions the GCS landing bucket and BigQuery dataset.

## Prerequisites

- A Google Cloud project with billing enabled.
- `gcloud`, Terraform, and Python 3.10+ installed.
- APIs enabled: Cloud Storage and BigQuery. The Terraform Google provider will report if an API must be enabled.
- An identity with permissions to create the Terraform resources and write objects/load data in the bucket and dataset.

Authenticate locally:

```bash
gcloud auth application-default login
```

## 1. Provision the GCP resources

```bash
cd terraform
terraform init
terraform apply \
  -var="project_id=YOUR_GCP_PROJECT_ID" \
  -var="bucket_name=YOUR_GLOBALLY_UNIQUE_BUCKET_NAME"
cd ..
```

The dataset is created as `logistics_analytics`. Keep the bucket name globally unique. Terraform state may contain infrastructure metadata; do not commit local state or credentials.

## 2. Generate and load sample data

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python data/generate_shipments.py --output data/shipments.csv --rows 5000
python src/load_to_bigquery.py \
  --project YOUR_GCP_PROJECT_ID \
  --bucket YOUR_GLOBALLY_UNIQUE_BUCKET_NAME \
  --input data/shipments.csv
```

The loader writes `shipments/shipments.csv` to GCS and replaces the BigQuery table `logistics_analytics.shipment_events`. The table is partitioned by `event_date` and clustered by `carrier` and `status`.

## 3. Build the analytics tables

Replace `YOUR_GCP_PROJECT_ID` in the SQL files, then run them in BigQuery in order:

1. `sql/01_transform_and_marts.sql`
2. `sql/02_data_quality_checks.sql`

The first script creates `shipment_events_clean`, `carrier_performance`, and `route_performance`. The second script uses BigQuery `ASSERT` statements and fails if duplicates or invalid shipment metrics are detected.

Example questions to answer from the marts:

- Which carriers have the highest on-time delivery rate?
- Which origin/destination routes have the longest average delivery time?
- How do shipment volume and shipping cost vary by carrier?

## Data model

Each generated row represents a shipment record with a unique `shipment_id`, event timestamp/date, origin and destination, carrier, status, weight, shipping cost, estimated delivery duration, and on-time indicator. The generator is deterministic by default (`--seed 42`) so that runs are reproducible.

## Production extensions

- Add a Cloud Run Job or Composer DAG to orchestrate generation, ingestion, and SQL execution.
- Add Pub/Sub and Dataflow for event-by-event tracking updates.
- Add schema evolution handling, dead-letter records, and incremental `MERGE` processing.
- Add CI checks for Python formatting/tests and Terraform validation.
- Connect the marts to Looker Studio for an operations dashboard.

## Cleanup

When finished, run `terraform destroy` from `terraform/` with the same variables. Confirm that you no longer need the bucket data before deleting infrastructure.
