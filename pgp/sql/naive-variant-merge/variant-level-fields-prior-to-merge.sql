# Display variant-level fields.
SELECT
  contig_name,
  start_pos,
  end_pos,
  reference_bases,
  GROUP_CONCAT(alternate_bases) WITHIN RECORD AS alt,
  END,
  SVLEN,
  SVTYPE
FROM
  [google.com:biggene:pgp.gvcf_variants]
WHERE
  contig_name = '6'
  AND start_pos = 120458771
ORDER BY
  alt
