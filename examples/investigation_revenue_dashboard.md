# Revenue Dashboard Change — Investigation Summary

**Published by:** Saint CLI Agent  
**Session type:** `saint solve` (Hypothesis Testing Mode)  
**DataHub Document URN:** `urn:li:document:shared-saint-revenue-dashboard-investigation`  
**Topics:** `saint-analysis`, `explore`  
**Related Assets:** `urn:li:dataset:(urn:li:dataPlatform:bigquery,acryl-datahub.SampleBigQueryDataset.SampleBigQueryDataset,PROD)`

---

## Goal & Desired Outcome

**Original Goal:** I want to understand why the revenue dashboard changed

**Target Outcome:** Identify the root cause of the revenue dashboard metric shift by tracing upstream data lineage, reviewing recent schema and ownership changes, and confirming whether data quality issues or pipeline delays are contributing factors.

---

## Evidence & Findings

Based on the DataHub context graph, the following picture emerged:

The **Revenue Dashboard** draws its primary metric from `SampleBigQueryDataset.revenue_attribution`, which in turn depends on `customer_lifetime_value` and `order_summary_daily` as upstream sources.

Two signals stood out:

1. **Schema change detected** — `order_summary_daily` had a field added (`promo_adjusted_revenue`) 11 days ago. The dashboard's revenue metric was not updated to reflect this adjustment, causing an apparent drop in the primary series.

2. **Pipeline delay in upstream** — `customer_lifetime_value` has a freshness assertion that was failing as of the last audit. The latest partition timestamp was 36 hours behind the expected daily cadence, compressing the lookback window used for the metric rollup.

The combination of the unadjusted field and the stale upstream window explains the dashboard's apparent regression without any change to the dashboard query itself.

---

## Primary Assets Reviewed

- **SampleBigQueryDataset** (dataset): `urn:li:dataset:(urn:li:dataPlatform:bigquery,acryl-datahub.SampleBigQueryDataset.SampleBigQueryDataset,PROD)`
- **Baz Chart** (chart): `urn:li:chart:(looker,baz)`
- **Revenue Dashboard** (dashboard): `urn:li:dashboard:(looker,dashboards.5)`
- **Datahub Sales** (datajob): `urn:li:dataJob:(urn:li:dataFlow:(airflow,prod_etl,PROD),datahub_sales)`

---

## Recommended Actions

1. Update `revenue_attribution` to include `promo_adjusted_revenue` from the new field
2. Investigate the pipeline delay in `customer_lifetime_value` — check Airflow task logs for the `customer_ltv_refresh` DAG
3. Add a DataHub freshness assertion on `order_summary_daily` to catch future schema drift earlier

---

*Generated and published by Saint CLI Agent.*
