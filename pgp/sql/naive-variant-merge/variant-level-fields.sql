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
  reference_bases != 'N'
LIMIT
  1000
