WITH return_buckets AS (
    SELECT
        reseller_id,
        churn_label,
        monthly_gmv,
        return_rate,
        -- Split all resellers into 5 equal buckets by return rate
        -- Bucket 1 = lowest return rate, Bucket 5 = highest
        NTILE(5) OVER (ORDER BY return_rate) AS return_rate_bucket
    FROM resellers_table
),

bucket_summary AS (
    SELECT
        return_rate_bucket,
        ROUND(MIN(return_rate) * 100, 1) AS min_return_pct,
        ROUND(MAX(return_rate) * 100, 1) AS max_return_pct,
        COUNT(*) AS total_resellers,
        SUM(CONVERT(INT, churn_label)) AS churned,
        CAST(ROUND(SUM(CONVERT(INT, churn_label)) * 100.0 
             / COUNT(*), 1) AS DECIMAL(5,1)) AS churn_rate_pct,
        ROUND(AVG(monthly_gmv), 0) AS avg_gmv
    FROM return_buckets
    GROUP BY return_rate_bucket
)

-- RANK() orders buckets by churn rate to show the tipping point clearly
SELECT
    return_rate_bucket,
    CONCAT(CAST(min_return_pct AS VARCHAR), '% - ', 
           CAST(max_return_pct AS VARCHAR), '%') AS return_rate_range,
    total_resellers,
    churned,
    churn_rate_pct,
    avg_gmv,
    RANK() OVER (ORDER BY churn_rate_pct DESC) AS risk_rank
FROM bucket_summary
ORDER BY return_rate_bucket;