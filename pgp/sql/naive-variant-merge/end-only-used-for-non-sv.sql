# 'end' is not set when the record is not a reference-matching block or a
# structural variant.
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
  svtype IS NULL
  AND END IS NOT NULL
  AND reference_bases != 'N'
LIMIT
  100
