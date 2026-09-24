-- Hours in which the SE branch feed carries more than one snapshot timestamp.
-- One row per hour: how many snapshots, their times, and the branch-row count of each
-- (a count well below the others = a partial solve). ERCOTSTATIONINJECTION keeps every
-- snapshot as its own TIMESTAMP row; consumers should take the latest snapshot per hour.
-- Full scan of ISOERCOTSEBRANCH (clustered by device): ~20 s on an X-Small.

WITH snap AS (
    SELECT "TIMESTAMP", COUNT(*) AS BRANCH_ROWS
    FROM AW.DBO.ISOERCOTSEBRANCH
    WHERE "TIMESTAMP" >= '2022-01-01'          -- adjust range as needed
    GROUP BY "TIMESTAMP"
)
SELECT DATE_TRUNC('HOUR', "TIMESTAMP")                                        AS HOUR_START,
       COUNT(*)                                                               AS SNAPSHOTS,
       LISTAGG(TO_CHAR("TIMESTAMP", 'HH24:MI:SS'), ' , ')
           WITHIN GROUP (ORDER BY "TIMESTAMP")                                AS SNAPSHOT_TIMES,
       LISTAGG(BRANCH_ROWS, ' , ') WITHIN GROUP (ORDER BY "TIMESTAMP")        AS BRANCH_ROWS_PER_SNAPSHOT,
       DAYNAME(DATE_TRUNC('HOUR', "TIMESTAMP"))                               AS DOW
FROM snap
GROUP BY 1
HAVING COUNT(*) > 1
ORDER BY 1;
