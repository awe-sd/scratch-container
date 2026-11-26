-- Hours whose best available SE snapshot is a partial publish (no full solve in the nearest-hour bucket).
-- Rollout-night stubs (a few rows, followed by a full solve in the same bucket) are NOT listed here;
-- see se_multiple_snapshot_hours.sql for those. Threshold: best snapshot < 50% of the median snapshot size.
-- Full scan of ISOERCOTSEBRANCH (clustered by device): ~20 s on an X-Small.

WITH snap AS (
    SELECT "TIMESTAMP", COUNT(*) AS BRANCH_ROWS
    FROM AW.DBO.ISOERCOTSEBRANCH
    WHERE "TIMESTAMP" >= '2022-01-01'          -- adjust range as needed
    GROUP BY "TIMESTAMP"
),
best AS (
    SELECT DATE_TRUNC('HOUR', DATEADD(MINUTE, 30, "TIMESTAMP")) AS HOUR_BUCKET,
           "TIMESTAMP", BRANCH_ROWS,
           MEDIAN(BRANCH_ROWS) OVER () AS MEDIAN_ROWS
    FROM snap
    QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC('HOUR', DATEADD(MINUTE, 30, "TIMESTAMP"))
                               ORDER BY BRANCH_ROWS DESC, "TIMESTAMP" DESC) = 1
)
SELECT HOUR_BUCKET, "TIMESTAMP" AS SNAPSHOT, BRANCH_ROWS, MEDIAN_ROWS::INT AS MEDIAN_ROWS,
       ROUND(100 * BRANCH_ROWS / MEDIAN_ROWS, 1) AS PCT_OF_MEDIAN
FROM best
WHERE BRANCH_ROWS < 0.5 * MEDIAN_ROWS
ORDER BY HOUR_BUCKET;
