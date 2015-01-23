# Count the number of samples in the phenotypic data
SELECT
  COUNT(sample) AS all_samples,
  SUM(IF(In_Phase1_Integrated_Variant_Set = TRUE, 1, 0)) AS samples_in_variants_table
FROM
  [genomics-public-data:1000_genomes.sample_info]
