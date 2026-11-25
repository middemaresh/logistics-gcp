-- BigQuery multi-statement script. Fails the query if data quality assertions fail.
ASSERT (
  SELECT COUNT(*) = COUNT(DISTINCT shipment_id)
  FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
) AS 'Duplicate shipment IDs found';

ASSERT (
  SELECT COUNTIF(weight_kg <= 0 OR shipping_cost < 0 OR delivery_days < 0) = 0
  FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
) AS 'Invalid shipment metrics found';

ASSERT (
  SELECT COUNTIF(origin = destination OR shipment_id IS NULL) = 0
  FROM `YOUR_GCP_PROJECT_ID.logistics_analytics.shipment_events_clean`
) AS 'Invalid route or missing shipment ID found';
