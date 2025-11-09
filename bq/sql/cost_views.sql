-- CoolBits.ai Cost Views - BigQuery
-- ==================================

-- Daily cost rollup by service and environment
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_daily` AS
SELECT
  DATE(usage_start_time) AS day,
  labels.env AS env,
  labels.service AS service,
  labels.owner AS owner,
  labels.cost_center AS cost_center,
  SUM(cost) AS cost_eur,
  COUNT(*) AS usage_records,
  AVG(cost) AS avg_cost_per_record
FROM `coolbits.billing_export.gcp_billing_export_v1_*`
WHERE labels.env IS NOT NULL
  AND labels.service IS NOT NULL
GROUP BY 1, 2, 3, 4, 5
ORDER BY day DESC, cost_eur DESC;

-- Weekly cost summary
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_weekly` AS
SELECT
  DATE_TRUNC(DATE(usage_start_time), WEEK) AS week_start,
  labels.env AS env,
  labels.service AS service,
  labels.owner AS owner,
  labels.cost_center AS cost_center,
  SUM(cost) AS cost_eur,
  COUNT(*) AS usage_records,
  AVG(cost) AS avg_cost_per_record
FROM `coolbits.billing_export.gcp_billing_export_v1_*`
WHERE labels.env IS NOT NULL
  AND labels.service IS NOT NULL
GROUP BY 1, 2, 3, 4, 5
ORDER BY week_start DESC, cost_eur DESC;

-- Monthly cost summary
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_monthly` AS
SELECT
  DATE_TRUNC(DATE(usage_start_time), MONTH) AS month_start,
  labels.env AS env,
  labels.service AS service,
  labels.owner AS owner,
  labels.cost_center AS cost_center,
  SUM(cost) AS cost_eur,
  COUNT(*) AS usage_records,
  AVG(cost) AS avg_cost_per_record
FROM `coolbits.billing_export.gcp_billing_export_v1_*`
WHERE labels.env IS NOT NULL
  AND labels.service IS NOT NULL
GROUP BY 1, 2, 3, 4, 5
ORDER BY month_start DESC, cost_eur DESC;

-- Cost by resource type
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_by_resource` AS
SELECT
  DATE(usage_start_time) AS day,
  labels.env AS env,
  labels.service AS service,
  service.description AS resource_type,
  SUM(cost) AS cost_eur,
  COUNT(*) AS usage_records
FROM `coolbits.billing_export.gcp_billing_export_v1_*`
WHERE labels.env IS NOT NULL
  AND labels.service IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY day DESC, cost_eur DESC;

-- Cost trend analysis (7-day moving average)
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_trend` AS
SELECT
  day,
  env,
  service,
  owner,
  cost_center,
  cost_eur,
  AVG(cost_eur) OVER (
    PARTITION BY env, service, owner, cost_center 
    ORDER BY day 
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS cost_7day_avg,
  cost_eur - LAG(cost_eur, 1) OVER (
    PARTITION BY env, service, owner, cost_center 
    ORDER BY day
  ) AS cost_daily_change
FROM `coolbits.billing.v_cost_daily`
ORDER BY day DESC, cost_eur DESC;

-- Budget vs actual cost
CREATE OR REPLACE VIEW `coolbits.billing.v_budget_vs_actual` AS
WITH monthly_budget AS (
  SELECT 
    DATE_TRUNC(CURRENT_DATE(), MONTH) AS month_start,
    1000.0 AS budget_eur  -- Monthly budget in EUR
),
monthly_actual AS (
  SELECT
    DATE_TRUNC(DATE(usage_start_time), MONTH) AS month_start,
    SUM(cost) AS actual_cost_eur
  FROM `coolbits.billing_export.gcp_billing_export_v1_*`
  WHERE labels.env IS NOT NULL
  GROUP BY 1
)
SELECT
  b.month_start,
  b.budget_eur,
  COALESCE(a.actual_cost_eur, 0) AS actual_cost_eur,
  b.budget_eur - COALESCE(a.actual_cost_eur, 0) AS remaining_budget_eur,
  COALESCE(a.actual_cost_eur, 0) / b.budget_eur AS budget_utilization_pct
FROM monthly_budget b
LEFT JOIN monthly_actual a ON b.month_start = a.month_start;

-- Cost alerts summary
CREATE OR REPLACE VIEW `coolbits.billing.v_cost_alerts` AS
SELECT
  day,
  env,
  service,
  owner,
  cost_center,
  cost_eur,
  CASE 
    WHEN cost_eur > 100 THEN 'HIGH_COST'
    WHEN cost_eur > 50 THEN 'MEDIUM_COST'
    ELSE 'LOW_COST'
  END AS cost_level,
  CASE 
    WHEN cost_eur > 100 THEN 'Alert: High daily cost detected'
    WHEN cost_eur > 50 THEN 'Warning: Medium daily cost detected'
    ELSE 'Normal: Low daily cost'
  END AS alert_message
FROM `coolbits.billing.v_cost_daily`
WHERE day >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
ORDER BY day DESC, cost_eur DESC;
