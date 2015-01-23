<!-- R Markdown Documentation, DO NOT EDIT THE PLAIN MARKDOWN VERSION OF THIS FILE -->

<!-- Licensed under the Apache License, Version 2.0 (the "License"); -->
<!-- you may not use this file except in compliance with the License. -->
<!-- You may obtain a copy of the License at -->

<!--     http://www.apache.org/licenses/LICENSE-2.0 -->

<!-- Unless required by applicable law or agreed to in writing, software -->
<!-- distributed under the License is distributed on an "AS IS" BASIS, -->
<!-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. -->
<!-- See the License for the specific language governing permissions and -->
<!-- limitations under the License. -->


Naive Variant Merge
========================================



Variant Level Fields before the merge:

```
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
```
<!-- html table generated in R 3.1.1 by xtable 1.7-4 package -->
<!-- Fri Jan 23 14:34:41 2015 -->
<table border=1>
<tr> <th> contig_name </th> <th> start_pos </th> <th> end_pos </th> <th> reference_bases </th> <th> alt </th> <th> END </th> <th> SVLEN </th> <th> SVTYPE </th>  </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458786 </td> <td> N </td> <td>  </td> <td align="right"> 120458785 </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458774 </td> <td> TAA </td> <td> TAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458777 </td> <td> TAAAAA </td> <td> TAAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
   </table>

Counts of bi-allelic and multi-allelic records and sample calls.

```
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
```

```r
result
```

```
##   num_variant_records num_biallelic_variant_records
## 1            43794109                      42746980
##   num_multiallelic_variant_records num_sample_calls
## 1                          1047129        956447432
##   num_biallelic_sample_calls num_multiallelic_sample_calls
## 1                  952088182                       4359250
```

```r
result$num_multiallelic_variant_records / result$num_variant_records
```

```
## [1] 0.02391027
```

```r
result$num_multiallelic_sample_calls / result$num_sample_calls
```

```
## [1] 0.004557752
```

Variant Level Fields *after* the merge

```
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

Running query:   RUNNING  2.1s
Running query:   RUNNING  2.7s
```
<!-- html table generated in R 3.1.1 by xtable 1.7-4 package -->
<!-- Fri Jan 23 14:34:48 2015 -->
<table border=1>
<tr> <th> contig_name </th> <th> start_pos </th> <th> end_pos </th> <th> reference_bases </th> <th> alternate_bases </th> <th> END </th> <th> SVLEN </th> <th> SVTYPE </th>  </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458786 </td> <td> N </td> <td>  </td> <td align="right"> 120458785 </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458774 </td> <td> TAA </td> <td> TAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458777 </td> <td> TAAAAA </td> <td> TAAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> </tr>
   </table>

Sample Level Fields before the merge:

```
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
```
<!-- html table generated in R 3.1.1 by xtable 1.7-4 package -->
<!-- Fri Jan 23 14:34:52 2015 -->
<table border=1>
<tr> <th> contig_name </th> <th> start_pos </th> <th> end_pos </th> <th> reference_bases </th> <th> alt </th> <th> END </th> <th> SVLEN </th> <th> SVTYPE </th> <th> callset_name </th> <th> genotype </th> <th> phaseset </th> <th> genotype_likelihood </th>  </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458786 </td> <td> N </td> <td>  </td> <td align="right"> 120458785 </td> <td align="right">  </td> <td>  </td> <td> huB1FD55 </td> <td> 0,0 </td> <td>  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4BE6F2 </td> <td> 1,-1 </td> <td>  </td> <td> -26,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3073E3 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -38,0,-103 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFAF983 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -75,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu52B7E5 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -66,0,-40 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFA70A3 </td> <td> 1,0 </td> <td>  </td> <td> -36,0,-28 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE9B698 </td> <td> 1,1 </td> <td>  </td> <td> -117,-17,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu599905 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -74,0,-108 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC5733C </td> <td> 1,-1 </td> <td>  </td> <td> -55,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu034DB1 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -71,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu661AD0 </td> <td> 1,0 </td> <td>  </td> <td> -46,0,-46 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu15FECA </td> <td> 1,-1 </td> <td>  </td> <td> -34,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3A8D13 </td> <td> 1,0 </td> <td>  </td> <td> -82,0,-37 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu241DEA </td> <td> 1,0 </td> <td>  </td> <td> -38,0,-25 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0A4518 </td> <td> 1,-1 </td> <td>  </td> <td> -63,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC434ED </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -106,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0D1FA1 </td> <td> 1,0 </td> <td>  </td> <td> -72,0,-105 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huBE0B25 </td> <td> 1,-1 </td> <td>  </td> <td> -21,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huED0F40 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -79,0,-169 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu67EBB3 </td> <td> 1,0 </td> <td>  </td> <td> -23,0,-23 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4BF398 </td> <td> 1,-1 </td> <td>  </td> <td> -60,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC3160A </td> <td> 0,1 </td> <td> 120458762 </td> <td> -102,0,-183 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu868880 </td> <td> 1,-1 </td> <td>  </td> <td> -47,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5B8771 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -30,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu470099 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -52,0,-348 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0CF2EE </td> <td> 1,0 </td> <td> 120458771 </td> <td> -45,0,-23 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huF2DA6F </td> <td> 1,1 </td> <td>  </td> <td> -95,-25,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu627574 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -61,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu68929D </td> <td> 1,0 </td> <td>  </td> <td> -37,0,-52 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFFAD87 </td> <td> 1,1 </td> <td>  </td> <td> -64,-11,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu132B5C </td> <td> 1,0 </td> <td>  </td> <td> -55,0,-55 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huA02824 </td> <td> 1,0 </td> <td>  </td> <td> -59,0,-59 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu553620 </td> <td> 1,1 </td> <td>  </td> <td> -87,-11,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEDEA65 </td> <td> 1,-1 </td> <td>  </td> <td> -31,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAFA81C </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -45,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huB4D223 </td> <td> 1,-1 </td> <td>  </td> <td> -49,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE2E371 </td> <td> 1,0 </td> <td>  </td> <td> -78,0,-54 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huDF04CC </td> <td> 1,-1 </td> <td>  </td> <td> -25,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD10E53 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -24,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAEC1B0 </td> <td> 1,-1 </td> <td>  </td> <td> -31,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu775356 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -67,0,-184 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu297562 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -20,0,-112 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAA245C </td> <td> 1,0 </td> <td>  </td> <td> -22,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5FB1B9 </td> <td> 1,0 </td> <td>  </td> <td> -22,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu620F18 </td> <td> 1,-1 </td> <td>  </td> <td> -63,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE58004 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -35,0,-35 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huCD380F </td> <td> 1,-1 </td> <td>  </td> <td> -56,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu27FD1F </td> <td> 1,0 </td> <td> 120458771 </td> <td> -70,0,-32 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu72C17A </td> <td> 1,0 </td> <td> 120458771 </td> <td> -39,0,-94 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3CAB43 </td> <td> 1,1 </td> <td>  </td> <td> -74,-14,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu92FD55 </td> <td> 1,-1 </td> <td>  </td> <td> -100,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu90B053 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -50,0,-175 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD09534 </td> <td> 1,1 </td> <td>  </td> <td> -75,-10,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3F864B </td> <td> 1,-1 </td> <td>  </td> <td> -108,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu939B7C </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -125,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4FE0D1 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -41,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC92BC9 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -23,0,-71 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu011C57 </td> <td> 1,0 </td> <td>  </td> <td> -36,0,-36 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3C0611 </td> <td> 1,1 </td> <td>  </td> <td> -124,-32,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu33E2D9 </td> <td> 1,0 </td> <td>  </td> <td> -30,0,-30 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu04F220 </td> <td> 1,-1 </td> <td>  </td> <td> -64,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEC6EEC </td> <td> 1,0 </td> <td> 120458771 </td> <td> -43,0,-59 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5CD2C6 </td> <td> 1,1 </td> <td>  </td> <td> -61,-13,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huF5AD12 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -34,0,-134 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4B0812 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -21,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu42D651 </td> <td> 1,0 </td> <td>  </td> <td> -37,0,-24 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu44DCFF </td> <td> 1,0 </td> <td>  </td> <td> -20,0,-20 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu57A769 </td> <td> 1,-1 </td> <td>  </td> <td> -37,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu71E59D </td> <td> 1,2 </td> <td>  </td> <td> -71,-71,-71,-71,0,-71 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huCA14D2 </td> <td> 1,2 </td> <td>  </td> <td> -70,-70,-70,-70,0,-70 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5FCE15 </td> <td> 1,2 </td> <td>  </td> <td> -68,-68,-68,-68,0,-68 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu8073B9 </td> <td> 1,2 </td> <td>  </td> <td> -196,-155,-155,-196,0,-196 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEBD467 </td> <td> 1,2 </td> <td>  </td> <td> -100,-100,-100,-78,0,-78 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu032C04 </td> <td> 1,2 </td> <td>  </td> <td> -82,-82,-82,-82,0,-82 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA,T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD103CC </td> <td> 1,2 </td> <td>  </td> <td> -50,-50,-50,-50,0,-50 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458774 </td> <td> TAA </td> <td> TAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu016B28 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -71,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458777 </td> <td> TAAAAA </td> <td> TAAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu63EB0A </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -28,0,0 </td> </tr>
   </table>

Sample Level Fields *after* the merge:

```
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

Running query:   RUNNING  2.8s
Running query:   RUNNING  3.4s
```
<!-- html table generated in R 3.1.1 by xtable 1.7-4 package -->
<!-- Fri Jan 23 14:34:58 2015 -->
<table border=1>
<tr> <th> contig_name </th> <th> start_pos </th> <th> end_pos </th> <th> reference_bases </th> <th> alternate_bases </th> <th> END </th> <th> SVLEN </th> <th> SVTYPE </th> <th> callset_name </th> <th> genotype </th> <th> phaseset </th> <th> genotype_likelihood </th>  </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458786 </td> <td> N </td> <td>  </td> <td align="right"> 120458785 </td> <td align="right">  </td> <td>  </td> <td> huB1FD55 </td> <td> 0,0 </td> <td>  </td> <td>  </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEDEA65 </td> <td> 1,-1 </td> <td>  </td> <td> -31,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0A4518 </td> <td> 1,-1 </td> <td>  </td> <td> -63,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAFA81C </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -45,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huB4D223 </td> <td> 1,-1 </td> <td>  </td> <td> -49,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE2E371 </td> <td> 1,0 </td> <td>  </td> <td> -78,0,-54 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huDF04CC </td> <td> 1,-1 </td> <td>  </td> <td> -25,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD10E53 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -24,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3073E3 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -38,0,-103 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4BE6F2 </td> <td> 1,-1 </td> <td>  </td> <td> -26,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFAF983 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -75,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu52B7E5 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -66,0,-40 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFA70A3 </td> <td> 1,0 </td> <td>  </td> <td> -36,0,-28 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE9B698 </td> <td> 1,1 </td> <td>  </td> <td> -117,-17,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu599905 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -74,0,-108 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC5733C </td> <td> 1,-1 </td> <td>  </td> <td> -55,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu034DB1 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -71,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu661AD0 </td> <td> 1,0 </td> <td>  </td> <td> -46,0,-46 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu15FECA </td> <td> 1,-1 </td> <td>  </td> <td> -34,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3A8D13 </td> <td> 1,0 </td> <td>  </td> <td> -82,0,-37 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu241DEA </td> <td> 1,0 </td> <td>  </td> <td> -38,0,-25 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5B8771 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -30,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu71E59D </td> <td> 2,1 </td> <td>  </td> <td> -71,-71,-71,-71,0,-71 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huCA14D2 </td> <td> 2,1 </td> <td>  </td> <td> -70,-70,-70,-70,0,-70 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5FCE15 </td> <td> 2,1 </td> <td>  </td> <td> -68,-68,-68,-68,0,-68 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu8073B9 </td> <td> 2,1 </td> <td>  </td> <td> -196,-196,-196,-155,0,-155 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEBD467 </td> <td> 2,1 </td> <td>  </td> <td> -100,-78,-78,-100,0,-100 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu032C04 </td> <td> 2,1 </td> <td>  </td> <td> -82,-82,-82,-82,0,-82 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD103CC </td> <td> 2,1 </td> <td>  </td> <td> -50,-50,-50,-50,0,-50 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC3160A </td> <td> 0,1 </td> <td> 120458762 </td> <td> -102,0,-183 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu868880 </td> <td> 1,-1 </td> <td>  </td> <td> -47,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu553620 </td> <td> 1,1 </td> <td>  </td> <td> -87,-11,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu470099 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -52,0,-348 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0CF2EE </td> <td> 1,0 </td> <td> 120458771 </td> <td> -45,0,-23 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huF2DA6F </td> <td> 1,1 </td> <td>  </td> <td> -95,-25,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu627574 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -61,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu68929D </td> <td> 1,0 </td> <td>  </td> <td> -37,0,-52 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huFFAD87 </td> <td> 1,1 </td> <td>  </td> <td> -64,-11,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4BF398 </td> <td> 1,-1 </td> <td>  </td> <td> -60,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huA02824 </td> <td> 1,0 </td> <td>  </td> <td> -59,0,-59 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu0D1FA1 </td> <td> 1,0 </td> <td>  </td> <td> -72,0,-105 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu775356 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -67,0,-184 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu297562 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -20,0,-112 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAA245C </td> <td> 1,0 </td> <td>  </td> <td> -22,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5FB1B9 </td> <td> 1,0 </td> <td>  </td> <td> -22,0,-22 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu620F18 </td> <td> 1,-1 </td> <td>  </td> <td> -63,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huE58004 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -35,0,-35 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huCD380F </td> <td> 1,-1 </td> <td>  </td> <td> -56,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu27FD1F </td> <td> 1,0 </td> <td> 120458771 </td> <td> -70,0,-32 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu72C17A </td> <td> 1,0 </td> <td> 120458771 </td> <td> -39,0,-94 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3CAB43 </td> <td> 1,1 </td> <td>  </td> <td> -74,-14,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu92FD55 </td> <td> 1,-1 </td> <td>  </td> <td> -100,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu90B053 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -50,0,-175 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huF5AD12 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -34,0,-134 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD09534 </td> <td> 1,1 </td> <td>  </td> <td> -75,-10,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3F864B </td> <td> 1,-1 </td> <td>  </td> <td> -108,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4FE0D1 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -41,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC434ED </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -106,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu939B7C </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -125,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huBE0B25 </td> <td> 1,-1 </td> <td>  </td> <td> -21,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huED0F40 </td> <td> 0,1 </td> <td> 120458762 </td> <td> -79,0,-169 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu67EBB3 </td> <td> 1,0 </td> <td>  </td> <td> -23,0,-23 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5CD2C6 </td> <td> 1,1 </td> <td>  </td> <td> -61,-13,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu132B5C </td> <td> 1,0 </td> <td>  </td> <td> -55,0,-55 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huAEC1B0 </td> <td> 1,-1 </td> <td>  </td> <td> -31,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEC6EEC </td> <td> 1,0 </td> <td> 120458771 </td> <td> -43,0,-59 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu04F220 </td> <td> 1,-1 </td> <td>  </td> <td> -64,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu33E2D9 </td> <td> 1,0 </td> <td>  </td> <td> -30,0,-30 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu3C0611 </td> <td> 1,1 </td> <td>  </td> <td> -124,-32,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu011C57 </td> <td> 1,0 </td> <td>  </td> <td> -36,0,-36 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> T </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huC92BC9 </td> <td> 1,0 </td> <td> 120458771 </td> <td> -23,0,-71 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu4B0812 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -21,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu42D651 </td> <td> 1,0 </td> <td>  </td> <td> -37,0,-24 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458772 </td> <td> T </td> <td> TA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu44DCFF </td> <td> 1,0 </td> <td>  </td> <td> -20,0,-20 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu5FCE15 </td> <td> 1,2 </td> <td>  </td> <td> -68,-68,-68,-68,0,-68 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu8073B9 </td> <td> 1,2 </td> <td>  </td> <td> -196,-155,-155,-196,0,-196 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huEBD467 </td> <td> 1,2 </td> <td>  </td> <td> -100,-100,-100,-78,0,-78 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu032C04 </td> <td> 1,2 </td> <td>  </td> <td> -82,-82,-82,-82,0,-82 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huD103CC </td> <td> 1,2 </td> <td>  </td> <td> -50,-50,-50,-50,0,-50 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu57A769 </td> <td> 1,-1 </td> <td>  </td> <td> -37,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> huCA14D2 </td> <td> 1,2 </td> <td>  </td> <td> -70,-70,-70,-70,0,-70 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458773 </td> <td> TA </td> <td> TAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu71E59D </td> <td> 1,2 </td> <td>  </td> <td> -71,-71,-71,-71,0,-71 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458774 </td> <td> TAA </td> <td> TAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu016B28 </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -71,0,0 </td> </tr>
  <tr> <td> 6 </td> <td align="right"> 120458771 </td> <td align="right"> 120458777 </td> <td> TAAAAA </td> <td> TAAAA </td> <td align="right">  </td> <td align="right">  </td> <td>  </td> <td> hu63EB0A </td> <td> 1,-1 </td> <td> 120458771 </td> <td> -28,0,0 </td> </tr>
   </table>
