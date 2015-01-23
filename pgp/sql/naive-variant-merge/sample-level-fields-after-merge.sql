# Display sample-level fields.
SELECT
  contig_name,
  start_pos,
  end_pos,
  reference_bases,
  alternate_bases,
  END,
  SVLEN,
  SVTYPE,
  call.callset_name AS callset_name,
  GROUP_CONCAT(STRING(call.genotype)) WITHIN call AS genotype,
  call.phaseset AS phaseset,
  GROUP_CONCAT(STRING(call.genotype_likelihood)) WITHIN call AS genotype_likelihood,
FROM
  [google.com:biggene:test.pgp_gvcf_variants_biallelic]
WHERE
  contig_name = '6'
  AND start_pos = 120458771
ORDER BY
  alternate_bases
