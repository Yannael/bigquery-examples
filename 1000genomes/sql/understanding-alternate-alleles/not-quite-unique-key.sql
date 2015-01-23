# This query demonstrates that some additional field is needed to
# comprise a unique key for the rows in the table.
SELECT
  reference_name,
  start,
  reference_bases,
  alt,
  vt,
  COUNT(1) AS cnt
FROM (
  SELECT
    reference_name,
    start,
    reference_bases,
    GROUP_CONCAT(alternate_bases) WITHIN RECORD AS alt,
    vt,
  FROM
    [genomics-public-data:1000_genomes.variants])
  GROUP EACH BY
  reference_name,
  start,
  reference_bases,
  alt,
  vt
HAVING
  cnt > 1
ORDER BY
  reference_name
