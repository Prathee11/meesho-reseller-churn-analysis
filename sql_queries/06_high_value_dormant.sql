WITH category_benchmarks AS (
    -- Step 1: Calculate average GMV per category
    -- This becomes our benchmark to identify "high value" resellers
    SELECT
        primary_category,
        ROUND(AVG(monthly_gmv), 0) AS category_avg_gmv
    FROM resellers_table
    GROUP BY primary_category
),

reseller_vs_benchmark AS (
    -- Step 2: Compare each reseller to their category average
    -- LAG() here peeks at the previous row's category_avg_gmv
    -- to show the gap between this reseller and the one above
    SELECT
        r.reseller_id,
        r.primary_category,
        r.city_tier,
        r.monthly_gmv,
        r.churn_label,
        r.days_since_last_order,
        r.tenure_days,
        c.category_avg_gmv,
        ROUND(r.monthly_gmv - c.category_avg_gmv, 0) AS gmv_vs_avg,
        LAG(r.monthly_gmv) OVER (
            PARTITION BY r.primary_category 
            ORDER BY r.monthly_gmv DESC
        ) AS prev_reseller_gmv
    FROM resellers_table r
    JOIN category_benchmarks c 
        ON r.primary_category = c.primary_category
),

high_value_dormant AS (
    -- Step 3: Filter only churned resellers above category average
    SELECT
        reseller_id,
        primary_category,
        city_tier,
        monthly_gmv,
        category_avg_gmv,
        gmv_vs_avg,
        days_since_last_order,
        tenure_days,
        -- Rank by GMV within each category
        -- Top ranked = highest recovery potential
        RANK() OVER (
            PARTITION BY primary_category 
            ORDER BY monthly_gmv DESC
        ) AS recovery_rank
    FROM reseller_vs_benchmark
    WHERE churn_label = 1
      AND monthly_gmv > category_avg_gmv
)

-- Final: Top 10 highest priority win-back targets
SELECT TOP 10
    reseller_id,
    primary_category,
    city_tier,
    ROUND(monthly_gmv, 0) AS monthly_gmv,
    ROUND(category_avg_gmv, 0) AS category_avg_gmv,
    gmv_vs_avg AS gmv_above_average,
    days_since_last_order,
    recovery_rank
FROM high_value_dormant
ORDER BY monthly_gmv DESC;