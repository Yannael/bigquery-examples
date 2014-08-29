# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Perform a naive merge of variants in the PGP gVCF dataset.

Note that this PySpark script is very specific to the PGP gVCF data
and takes into account the meanings of the various INFO key/value pairs
as defined in the VCF header.  Some INFO key/values are discarded,
since they are no longer useful in a merged context.  Others are
re-written as part of the merge.

To use this script:

(0) Export BigQuery table [google.com:biggene:pgp.gvcf_variants] as
    json to a Google Cloud Storage bucket.

(1) Spin up a spark cluster on Google Compute Engine.  See
    https://groups.google.com/forum/#!topic/gcp-hadoop-announce/EfQms8tK5cE

(2) Ship this script and the library to the spark master
    gcutil push hadoop-m spark_merge_pgp_variants.py merge_pgp_variants.py /home/$USER

(3) ssh to the spark master and run the job
    ./bdutil shell
    spark-submit spark_merge_pgp_variants.py --py-files merge_pgp_variants.py gs://bigquery/export/path gs://output/path

(4) Import the modified json back into BigQuery using the revised schema below.
"""

import json
import sys

from pyspark import SparkContext

import merge_pgp_variants

def emit_empty_alternate_records(input_lines):
  records = input_lines.map(json.loads).filter(lambda r: not merge_pgp_variants.HasAlternate(r)).map(merge_pgp_variants.SimplifyRecord).map(json.dumps)

  records.saveAsTextFile(sys.argv[2] + "_null_alternate_bases")

def emit_merged_variants(input_lines):
  records = input_lines.map(json.loads).filter(merge_pgp_variants.HasAlternate)

  pairs = records.flatMap(merge_pgp_variants.MapRecord)
  merged_records = pairs.reduceByKey(merge_pgp_variants.FoldByKeyVariant)
  output_lines = merged_records.map(lambda r: json.dumps(r[1]))

  output_lines.saveAsTextFile(sys.argv[2] + "_variants")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print >> sys.stderr, "Usage: spark_merge_pgp_variants <input file glob> <output filepath>"
    exit(-1)

  # Initialize the spark context.
  sc = SparkContext(appName="PGPVariantMerge")

  input_lines = sc.textFile(sys.argv[1], 1)

  emit_merged_variants(input_lines)

  # This will emit reference-matching block records and any DELs where
  # alternate_bases is null.
  emit_empty_alternate_records(input_lines)

  sc.stop()


"""
Revised BigQuery schema to use when loading the resulting data from this spark job:

[
  {
    "name":"contig_name",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"An identifier from the reference genome or an angle-bracketed ID String pointing to a contig in the assembly file"
  },
  {
    "name":"start_pos",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"The reference position, with the 1st base having position 1."
  },
  {
    "name":"end_pos",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"For precise variants, end_pos is start_pos + length of REF allele - 1."
  },
  {
    "name":"reference_bases",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"Each base must be one of A,C,G,T,N (case insensitive). Multiple bases are permitted. The value in the POS field refers to the position of the first base in the String."
  },
  {
    "name":"alternate_bases",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"List of alternate non-reference alleles called on at least one of the samples. (\"at least one\" not true for this dataset)"
  },
  {
    "name":"CGA_BF",
    "type":"FLOAT",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_BF,Number=1,Type=Float,Description=\"Frequency in baseline\"&gt;"
  },
  {
    "name":"CGA_BNDG",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_BNDG,Number=A,Type=String,Description=\"Transcript name and strand of genes containing breakend\"&gt;"
  },
  {
    "name":"CGA_BNDGO",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_BNDGO,Number=A,Type=String,Description=\"Transcript name and strand of genes containing mate breakend\"&gt;"
  },
  {
    "name":"CGA_FI",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_FI,Number=A,Type=String,Description=\"Functional impact annotation\"&gt;"
  },
  {
    "name":"CGA_MEDEL",
    "type":"STRING",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=CGA_MEDEL,Number=4,Type=String,Description=\"Consistent with deletion of mobile element; type,chromosome,start,end\"&gt;"
  },
  {
    "name":"CGA_MIRB",
    "type":"STRING",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=CGA_MIRB,Number=.,Type=String,Description=\"miRBaseId\"&gt;"
  },
  {
    "name":"CGA_PFAM",
    "type":"STRING",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=CGA_PFAM,Number=.,Type=String,Description=\"PFAM Domain\"&gt;"
  },
  {
    "name":"CGA_RPT",
    "type":"STRING",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=CGA_RPT,Number=.,Type=String,Description=\"repeatMasker overlap information\"&gt;"
  },
  {
    "name":"CGA_SDO",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_SDO,Number=1,Type=Integer,Description=\"Number of distinct segmental duplications that overlap this locus\"&gt;"
  },
  {
    "name":"CGA_WINEND",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_WINEND,Number=1,Type=Integer,Description=\"End of coverage window\"&gt;"
  },
  {
    "name":"CGA_XR",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=CGA_XR,Number=A,Type=String,Description=\"Per-ALT external database reference (dbSNP, COSMIC, etc)\"&gt;"
  },
  {
    "name":"CIPOS",
    "type":"INTEGER",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=CIPOS,Number=2,Type=Integer,Description=\"Confidence interval around POS for imprecise variants\"&gt;"
  },
  {
    "name":"END",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=END,Number=1,Type=Integer,Description=\"End position of the variant described in this record\"&gt;"
  },
  {
    "name":"IMPRECISE",
    "type":"BOOLEAN",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=IMPRECISE,Number=0,Type=Flag,Description=\"Imprecise structural variation\"&gt;"
  },
  {
    "name":"MATEID",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=MATEID,Number=1,Type=String,Description=\"ID of mate breakend\"&gt;"
  },
  {
    "name":"MEINFO",
    "type":"STRING",
    "mode":"REPEATED",
    "description":"INFO=&lt;ID=MEINFO,Number=4,Type=String,Description=\"Mobile element info of the form NAME,START,END,POLARITY\"&gt;"
  },
  {
    "name":"SVLEN",
    "type":"INTEGER",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=SVLEN,Number=.,Type=Integer,Description=\"Difference in length between REF and ALT alleles\"&gt;"
  },
  {
    "name":"SVTYPE",
    "type":"STRING",
    "mode":"NULLABLE",
    "description":"INFO=&lt;ID=SVTYPE,Number=1,Type=String,Description=\"Type of structural variant\"&gt;"
  },
  {
    "name":"call",
    "type":"RECORD",
    "mode":"REPEATED",
    "fields":[
      {
        "name":"callset_id",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"The id of the callset from which this data was exported from the Variants API."
      },
      {
        "name":"callset_name",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"Sample identifier."
      },
      {
        "name":"genotype",
        "type":"INTEGER",
        "mode":"REPEATED",
        "description":"List of genotypes."
      },
      {
        "name":"phaseset",
        "type":"STRING",
        "mode":"NULLABLE"
      },
      {
        "name":"genotype_likelihood",
        "type":"FLOAT",
        "mode":"REPEATED",
        "description":"List of genotype likelihoods."
      },
      {
        "name":"AD",
        "type":"STRING",
        "mode":"REPEATED",
        "description":"FORMAT=&lt;ID=AD,Number=2,Type=Integer,Description=\"Allelic depths (number of reads in each observed allele)\"&gt;"
      },
      {
        "name":"CGA_BNDDEF",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_BNDDEF,Number=1,Type=String,Description=\"Breakend definition\"&gt;"
      },
      {
        "name":"CGA_BNDMPC",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_BNDMPC,Number=1,Type=Integer,Description=\"Mate pair count supporting breakend\"&gt;"
      },
      {
        "name":"CGA_BNDP",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_BNDP,Number=1,Type=String,Description=\"Precision of breakend\"&gt;"
      },
      {
        "name":"CGA_BNDPOS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_BNDPOS,Number=1,Type=Integer,Description=\"Breakend position\"&gt;"
      },
      {
        "name":"CGA_CL",
        "type":"FLOAT",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_CL,Number=1,Type=Float,Description=\"Nondiploid-model called level\"&gt;"
      },
      {
        "name":"CGA_CP",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_CP,Number=1,Type=Integer,Description=\"Diploid-model called ploidy\"&gt;"
      },
      {
        "name":"CGA_CT",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_CT,Number=1,Type=String,Description=\"Diploid-model CNV type\"&gt;"
      },
      {
        "name":"CGA_ETS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_ETS,Number=1,Type=Float,Description=\"MEI ElementTypeScore: confidence that insertion is of type indicated by CGA_ET/ElementType\"&gt;"
      },
      {
        "name":"CGA_GP",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_GP,Number=1,Type=Float,Description=\"Depth of coverage for 2k window GC normalized to mean\"&gt;"
      },
      {
        "name":"CGA_IDC",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_IDC,Number=1,Type=Float,Description=\"MEI InsertionDnbCount: count of paired ends supporting insertion\"&gt;"
      },
      {
        "name":"CGA_IDCL",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_IDCL,Number=1,Type=Float,Description=\"MEI InsertionLeftDnbCount: count of paired ends supporting insertion on 5' end of insertion point\"&gt;"
      },
      {
        "name":"CGA_IDCR",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_IDCR,Number=1,Type=Float,Description=\"MEI InsertionRightDnbCount: count of paired ends supporting insertion on 3' end of insertion point\"&gt;"
      },
      {
        "name":"CGA_IS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_IS,Number=1,Type=Float,Description=\"MEI InsertionScore: confidence in occurrence of an insertion\"&gt;"
      },
      {
        "name":"CGA_KES",
        "type":"FLOAT",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_KES,Number=1,Type=Float,Description=\"MEI KnownEventSensitivityForInsertionScore: fraction of known MEI insertion polymorphisms called for this sample with CGA_IS at least as high as for the current call\"&gt;"
      },
      {
        "name":"CGA_LS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_LS,Number=1,Type=Integer,Description=\"Nondiploid-model called level score\"&gt;"
      },
      {
        "name":"CGA_NBET",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_NBET,Number=1,Type=String,Description=\"MEI NextBestElementType: (sub)type of second-most-likely inserted mobile element\"&gt;"
      },
      {
        "name":"CGA_NP",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_NP,Number=1,Type=Float,Description=\"Coverage for 2k window, GC-corrected and normalized relative to copy-number-corrected multi-sample baseline\"&gt;"
      },
      {
        "name":"CGA_PS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_PS,Number=1,Type=Integer,Description=\"Diploid-model called ploidy score\"&gt;"
      },
      {
        "name":"CGA_RDC",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_RDC,Number=1,Type=Integer,Description=\"MEI ReferenceDnbCount: count of paired ends supporting reference allele\"&gt;"
      },
      {
        "name":"CGA_RDP",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_RDP,Number=1,Type=Integer,Description=\"Number of reads observed supporting the reference allele\"&gt;"
      },
      {
        "name":"CGA_TS",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=CGA_TS,Number=1,Type=Integer,Description=\"Diploid-model CNV type score\"&gt;"
      },
      {
        "name":"DP",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=DP,Number=1,Type=Integer,Description=\"Total Read Depth\"&gt;"
      },
      {
        "name":"EHQ",
        "type":"STRING",
        "mode":"REPEATED",
        "description":"FORMAT=&lt;ID=EHQ,Number=2,Type=Integer,Description=\"Haplotype Quality, Equal Allele Fraction Assumption\"&gt;"
      },
      {
        "name":"FILTER",
        "type":"BOOLEAN",
        "mode":"NULLABLE",
        "description":"PASS if this position has passed all filters, i.e. a call is made at this position. Otherwise, if the site has not passed all filters, a list of codes for filters that fail."
      },
      {
        "name":"FT",
        "type":"STRING",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=FT,Number=1,Type=String,Description=\"Genotype filters\"&gt;"
      },
      {
        "name":"GQ",
        "type":"INTEGER",
        "mode":"NULLABLE",
        "description":"FORMAT=&lt;ID=GQ,Number=1,Type=Integer,Description=\"Genotype Quality\"&gt;"
      },
      {
        "name":"HQ",
        "type":"STRING",
        "mode":"REPEATED",
        "description":"FORMAT=&lt;ID=HQ,Number=2,Type=Integer,Description=\"Haplotype Quality\"&gt;"
      },
      {
        "name":"QUAL",
        "type":"FLOAT",
        "mode":"NULLABLE",
        "description":"phred-scaled quality score for the assertion made in ALT."
      }
    ],
    "description":"Per-sample measurements."
  }
]


"""
  
