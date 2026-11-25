-- Replace YOUR_GCP_PROJECT_ID with your project ID before running.

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
PARTITION BY event_date
CLUSTER BY carrier, status AS
SELECT
  shipment_id,
  event_timestamp,
  event_date,
  LOWER(TRIM(status)) AS status,
  TRIM(origin) AS origin,
  TRIM(destination) AS destination,
  TRIM(carrier) AS carrier,
  weight_kg,
  shipping_cost,
  delivery_days,
  on_time
FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events`
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY shipment_id
  ORDER BY event_timestamp DESC
) = 1;

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.logistics_analytics.carrier_performance` AS
SELECT
  carrier,
  COUNT(*) AS shipment_count,
  COUNTIF(status = 'delivered') AS delivered_shipments,
  SAFE_DIVIDE(COUNTIF(on_time), COUNTIF(status = 'delivered')) AS on_time_delivery_rate,
  ROUND(AVG(IF(status = 'delivered', delivery_days, NULL)), 2) AS avg_delivery_days,
  ROUND(SUM(shipping_cost), 2) AS total_shipping_cost
FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
GROUP BY carrier;

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.logistics_analytics.route_performance` AS
SELECT
  origin,
  destination,
  COUNT(*) AS shipment_count,
  ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
  SAFE_DIVIDE(COUNTIF(on_time), COUNTIF(status = 'delivered')) AS on_time_delivery_rate,
  ROUND(AVG(shipping_cost), 2) AS avg_shipping_cost
FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
GROUP BY origin, destination;
