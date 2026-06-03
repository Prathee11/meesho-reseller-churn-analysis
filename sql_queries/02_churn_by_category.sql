SELECT 
    primary_category,
    COUNT(*) AS total_resellers,
    SUM(CONVERT(INT, churn_label)) AS churned,
    CAST(ROUND(SUM(CONVERT(INT, churn_label)) * 100.0 / COUNT(*), 1) AS DECIMAL(5,1)) AS churn_rate_pct,
    ROUND(AVG(monthly_gmv), 0) AS avg_gmv
FROM resellers_table
GROUP BY primary_category
ORDER BY churn_rate_pct DESC;