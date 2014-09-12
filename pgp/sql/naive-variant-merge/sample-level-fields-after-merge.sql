# Display sample-level fields.
SELECT
  contig_name,
  start_pos,
  end_pos,
  reference_bases,
  alternate_bases,
  CGA_BF,
  CGA_BNDG,
  CGA_BNDGO,
  CGA_FI,
  GROUP_CONCAT(CGA_MEDEL) WITHIN RECORD AS medel,
  GROUP_CONCAT(CGA_MIRB) WITHIN RECORD AS mirb,
  GROUP_CONCAT(CGA_PFAM) WITHIN RECORD AS pfam,
  GROUP_CONCAT(CGA_RPT) WITHIN RECORD AS rpt,
  CGA_SDO,
  CGA_WINEND,
  CGA_XR,
  GROUP_CONCAT(STRING(CIPOS)) WITHIN RECORD AS cipos,
  END,
  IMPRECISE,
  MATEID,
  GROUP_CONCAT(MEINFO) WITHIN RECORD AS meinfo,
  SVLEN,
  SVTYPE,
  call.callset_name AS callset_name,
  GROUP_CONCAT(STRING(call.genotype)) WITHIN RECORD AS genotype,
  call.phaseset AS phaseset,
  GROUP_CONCAT(STRING(call.genotype_likelihood)) WITHIN RECORD AS genotype_likelihood,
FROM
  FLATTEN([google.com:biggene:test.pgp_gvcf_variants_biallelic], call)
WHERE
  contig_name = '6'
  AND start_pos = 120458771
ORDER BY
  alternate_bases
