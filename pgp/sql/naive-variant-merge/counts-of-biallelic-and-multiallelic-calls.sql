# Count multi-allelic record and calls within our dataset.
SELECT
  COUNT(1) AS num_variant_records,
  SUM(num_alts = 1) AS num_biallelic_variant_records,
  SUM(num_alts > 1) AS num_multiallelic_variant_records,
  SUM(num_samples) AS num_sample_calls,
  SUM(IF(num_alts = 1,
      INTEGER(num_samples),
      0)) AS num_biallelic_sample_calls,
  SUM(IF(num_alts > 1,
      INTEGER(num_samples),
      0)) AS num_multiallelic_sample_calls,
FROM (
  SELECT
    COUNT(alternate_bases) WITHIN RECORD AS num_alts,
    COUNT(call.callset_name) WITHIN RECORD AS num_samples,
  FROM
    [google.com:biggene:pgp.gvcf_variants]
  HAVING
    num_alts > 0)
