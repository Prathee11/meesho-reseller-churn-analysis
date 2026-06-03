SELECT 
    city_tier,
    COUNT(*) AS total_resellers,
    SUM(CONVERT(INT, churn_label)) AS churned,
    CAST(ROUND(SUM(CONVERT(INT, churn_label)) * 100.0 / COUNT(*), 1) AS DECIMAL(5,1)) AS churn_rate_pct
FROM resellers_table
GROUP BY city_tier
ORDER BY city_tier;