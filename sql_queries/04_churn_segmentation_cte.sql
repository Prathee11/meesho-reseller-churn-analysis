-- CTE 1: Label each reseller by return rate risk
WITH base_segments AS (
    SELECT
        reseller_id,
        city_tier,
        primary_category,
        monthly_gmv,
        churn_label,
        CASE 
            WHEN return_rate > 0.22 THEN 'High Return Risk'
            ELSE 'Normal'
        END AS return_risk_segment
    FROM resellers_table
),

-- CTE 2: Summarise churn by segment

churn_summary AS (
    SELECT
        city_tier,
        primary_category,
        return_risk_segment,
        COUNT(*) AS total_resellers,
        SUM(CONVERT(INT, churn_label)) AS churned,
        CAST(ROUND(SUM(CONVERT(INT, churn_label)) * 100.0 
             / COUNT(*), 1) AS DECIMAL(5,1)) AS churn_rate_pct,
        ROUND(AVG(monthly_gmv), 0) AS avg_gmv
    FROM base_segments
    GROUP BY city_tier, primary_category, return_risk_segment
)

-- Final SELECT: top 5 highest churn rate segments
SELECT TOP 5
    city_tier,
    primary_category,
    return_risk_segment,
    total_resellers,
    churned,
    churn_rate_pct,
    avg_gmv
FROM churn_summary
ORDER BY churn_rate_pct DESC;