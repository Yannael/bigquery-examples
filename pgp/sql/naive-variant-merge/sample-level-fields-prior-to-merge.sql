# Display sample-level fields.
SELECT
  contig_name,
  start_pos,
  end_pos,
  reference_bases,
  GROUP_CONCAT(alternate_bases) WITHIN RECORD AS alt,
  END,
  SVLEN,
  SVTYPE,
  call.callset_name AS callset_name,
  GROUP_CONCAT(STRING(call.genotype)) WITHIN call AS genotype,
  call.phaseset AS phaseset,
  GROUP_CONCAT(STRING(call.genotype_likelihood)) WITHIN call AS genotype_likelihood,
FROM
  [google.com:biggene:pgp.gvcf_variants]
WHERE
  contig_name = '6'
  AND start_pos = 120458771
ORDER BY
  alt
