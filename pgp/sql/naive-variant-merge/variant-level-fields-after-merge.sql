# Display variant-level fields.
SELECT
  contig_name,
  start_pos,
  end_pos,
  reference_bases,
  alternate_bases,
  END,
  SVLEN,
  SVTYPE
FROM
  [google.com:biggene:test.pgp_gvcf_variants_biallelic]
WHERE
  contig_name = '6'
  AND start_pos = 120458771
ORDER BY
  alternate_bases
