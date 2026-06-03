SELECT
  SUM(CASE WHEN churn_label = 1 THEN monthly_gmv ELSE 0 END) AS gmv_lost,
  SUM(monthly_gmv) AS total_gmv,
  ROUND(SUM(CASE WHEN churn_label = 1 THEN monthly_gmv ELSE 0 END) * 100.0 / SUM(monthly_gmv), 1) AS pct_gmv_at_risk
FROM resellers_table;S