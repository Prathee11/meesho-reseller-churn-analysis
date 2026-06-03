SELECT 
    COUNT(*) AS total_high_value_dormant,
    ROUND(SUM(monthly_gmv), 0) AS total_monthly_gmv,
    ROUND(SUM(monthly_gmv) * 12, 0) AS annual_gmv_opportunity
FROM resellers_table
WHERE churn_label = 1
AND monthly_gmv > (SELECT AVG(monthly_gmv) FROM resellers_table);