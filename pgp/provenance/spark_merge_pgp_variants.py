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
"""

import json
import sys

from pyspark import SparkContext

import merge_pgp_variants

def emit_non_simple_variants(input_lines):
  non_simple_records = input_lines.map(json.loads).filter(lambda r: not merge_pgp_variants.IsSimpleVariant(r)).map(merge_pgp_variants.CleanRecord).map(json.dumps)

  non_simple_records.saveAsTextFile(sys.argv[2] + "_non-simple")

def emit_merged_simple_variants(input_lines):
  records = input_lines.map(json.loads).filter(merge_pgp_variants.IsSimpleVariant).map(merge_pgp_variants.CleanRecord)

  pairs = records.map(merge_pgp_variants.MapRecord)
  merged_records = pairs.reduceByKey(merge_pgp_variants.FoldByKeyVariant)
  output_lines = merged_records.map(lambda r: json.dumps(r[1]))

  output_lines.saveAsTextFile(sys.argv[2] + "_simple")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print >> sys.stderr, "Usage: spark_merge_pgp_variants <input file glob> <output filepath>"
    exit(-1)

  # Initialize the spark context.
  sc = SparkContext(appName="PGPVariantMerge")

  input_lines = sc.textFile(sys.argv[1], 1)

  emit_merged_simple_variants(input_lines)
  emit_non_simple_variants(input_lines)

  sc.stop()
