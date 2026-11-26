-- Hours in which the SE branch feed carries more than one snapshot.
-- Snapshots are stamped :57/:58 and represent the state at the top of the NEXT hour, so bucket by
-- nearest hour, not by floor. With that, every multi-snapshot hour (179 over 2022-01..2026-07) is a
-- production-model rollout night: a small first snapshot (<=33 branch rows, 98% of them devices whose
-- DATEACTIVEEND is that day, i.e. lines leaving the model) followed by the full snapshot on the new model.
-- Not a data problem; consumers should take the latest snapshot per hour bucket.
-- Full scan of ISOERCOTSEBRANCH (clustered by device): ~20 s on an X-Small.

WITH snap AS (
    SELECT "TIMESTAMP", COUNT(*) AS BRANCH_ROWS
    FROM AW.DBO.ISOERCOTSEBRANCH
    WHERE "TIMESTAMP" >= '2022-01-01'          -- adjust range as needed
    GROUP BY "TIMESTAMP"
)
SELECT DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, "TIMESTAMP"))                 AS HOUR_BUCKET,
       COUNT(*)                                                               AS SNAPSHOTS,
       LISTAGG(TO_CHAR("TIMESTAMP", 'HH24:MI:SS'), ' , ')
           WITHIN GROUP (ORDER BY "TIMESTAMP")                                AS SNAPSHOT_TIMES,
       LISTAGG(BRANCH_ROWS, ' , ') WITHIN GROUP (ORDER BY "TIMESTAMP")        AS BRANCH_ROWS_PER_SNAPSHOT,
       DAYNAME(MIN("TIMESTAMP"))                                              AS DOW
FROM snap
GROUP BY 1
HAVING COUNT(*) > 1
ORDER BY 1;
