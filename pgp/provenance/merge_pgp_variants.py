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

Note that these methods are very specific to the PGP gVCF data
and take into account the meanings of the various INFO key/value pairs
as defined in the VCF header.  Some INFO key/values are discarded,
since they are no longer useful in a merged context.  Others are
re-written as part of the merge.

To use this library:

(0) Export BigQuery table [google.com:biggene:pgp.gvcf_variants] as
    json to a Google Cloud Storage bucket.

(1) Spin up a spark cluster on Google Compute Engine.  See
    https://groups.google.com/forum/#!topic/gcp-hadoop-announce/EfQms8tK5cE

(2) Ship this script to the spark master
    gcutil push hadoop-m merge_pgp_variants.py /home/$USER

(3) ssh to the spark master and run the job
    ./bdutil shell
    pyspark --py-files merge_pgp_variants.py

This library could also be used in the context of a Hadoop Streaming job.
"""

import json
import unittest


def CleanRecord(fields):
  """Remove VCF info key/value pairs that are not useful in this context."""
  # INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
  fields.pop("NS", None)
  # INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in called genotypes">
  fields.pop("AN", None)
  # INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in genotypes, for each ALT allele">
  fields.pop("AC", None)

  return fields


def IsSimpleVariant(fields):
  """Determine whether or not the record fields constitute a variant."""
  if "alternate_bases" in fields and fields["alternate_bases"]:
    # It is a variant, not a reference-matching block.  Now, is it "simple"?
    if "SVTYPE" not in fields and "<CGA_CNVWIN>" != fields["alternate_bases"][0]:
      return True
  return False


def MapRecord(fields):
  """Emit a key/value pair for the record.
  """
  if IsSimpleVariant(fields):
    # Note: the key does not include alternate_bases because that's
    # what we want to group in the reduce step.  The key also does not
    # include 'end' because in this dataset its only set for
    # structural variants and reference-matching blocks, both of which
    # we emit directly as-is from this step.
    key = "%s:%s:%s" % (fields["contig_name"],
                        fields["start_pos"],
                        fields["reference_bases"])
  else:
    # Note: this is equivalent to the Variant Store import key and
    # therefore should be unique
    alt = ""
    end = ""
    if "alternate_bases" in fields and fields["alternate_bases"]:
      alt = ",".join(fields["alternate_bases"])
    if "END" in fields:
      end = fields["END"]
    elif "end" in fields:
      end = fields["end"]
    key = "%s:%s:%s:%s:%s" % (fields["contig_name"],
                              fields["start_pos"],
                              fields["reference_bases"],
                              alt,
                              end)

  return (key, fields)


def FoldByKeyVariant(a, b):
  """Naively merge two 'simple' variant records with the same key."""
  # Handle zero value
  if not a: return b
  if not b: return a

  if not (IsSimpleVariant(a) and IsSimpleVariant(b)):
    raise Exception("Attempting to merge non-simple variants: "
                    + str(a) + str(b))

  # TODO(deflaux): this isn't actually commutative and associative
  # yet.  We need to sort alternate_bases alphabetically and re-write
  # the genotype numbers for both the src and dest as needed for it to
  # be so.

  # Choose the direction in which to merge (but either way would be fine)
  if len(a["alternate_bases"]) < len(b["alternate_bases"]):
    src = a
    dest = b
  else:
    src = b
    dest = a

  # Populate our alt number mapping
  genotype_map = [0]
  for alt in src["alternate_bases"]:
    if alt not in dest["alternate_bases"]:
      dest["alternate_bases"].append(alt)
    genotype_map.append(dest["alternate_bases"].index(alt) + 1)

  # Re-write the genotype numbers
  for call in src["call"]:
    for idx in range(0, len(call["genotype"])):
      if 0 < call["genotype"][idx]:
        call["genotype"][idx] = genotype_map[call["genotype"][idx]]

  # TODO(deflaux): also re-write alt specific INFO fields such as
  # CGA_XR or discard them.

  # TODO(deflaux): check that any variant level values we are throwing
  # out match those that remain

  # Now merge the calls
  dest["call"].extend(src["call"])

  return dest


class VariantMergeTest(unittest.TestCase):
  def testIsSimpleVariant(self):
    self.assertTrue(IsSimpleVariant(json.loads(self.var_both_ins_del)))
    self.assertFalse(IsSimpleVariant(json.loads(self.var_sv)))
    self.assertFalse(IsSimpleVariant(json.loads(self.ref_block)))
    self.assertFalse(IsSimpleVariant(json.loads(self.no_call)))

  def testMapRecord(self):
    expected_key = "6:120458771:TA"
    for var in [self.var_both_ins_del, self.var_ins, self.var_del]:
      (key, value) = MapRecord(json.loads(var))
      self.assertEqual(expected_key, key)
      self.assertDictEqual(CleanRecord(json.loads(var)), value)

    (key, value) = MapRecord(json.loads(self.var_ins_encoded_differently))
    self.assertEqual("6:120458771:T", key)
    self.assertDictEqual(CleanRecord(json.loads(
        self.var_ins_encoded_differently)), value)

    (key, value) = MapRecord(json.loads(self.var_del_encoded_differently))
    self.assertEqual("6:120458771:TAAAAA", key)
    self.assertDictEqual(CleanRecord(json.loads(
        self.var_del_encoded_differently)), value)

    (key, value) = MapRecord(json.loads(self.var_sv))
    self.assertEqual("11:132083603:G:GN[11:132084035[:", key)
    self.assertDictEqual(CleanRecord(json.loads(self.var_sv)), value)

    (key, value) = MapRecord(json.loads(self.ref_block))
    self.assertEqual("2:77608523:N::77608540", key)
    self.assertDictEqual(CleanRecord(json.loads(self.ref_block)), value)

  def testFoldByKeyVariant(self):
    merged_var = None
    for var in [self.var_both_ins_del, self.var_ins, self.var_del]:
      if merged_var is None:
        merged_var = json.loads(var)
      else:
        merged_var = FoldByKeyVariant(json.loads(var), merged_var)

    self.assertDictEqual(json.loads(self.var_merged), merged_var)

  def setUp(self):
    self.var_both_ins_del = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":[
    "TAA",
    "T"
  ],
  "AC":[
    "1",
    "1"
  ],
  "AN":"2",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":[
    "dbsnp.130|rs71806210",
    "dbsnp.129|rs61212177"
  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "callset_name":"huD103CC",
      "genotype":[
        1,
        2
      ],
      "genotype_likelihood":[
        -50,
        -50,
        -50,
        -50,
        0,
        -50
      ],
      "AD":[
        "9",
        "6"
      ],
      "CGA_RDP":"3",
      "DP":"24",
      "EHQ":[
        "49",
        "49"
      ],
      "FILTER":true,
      "FT":"PASS",
      "GQ":"50",
      "HQ":[
        "50",
        "50"
      ],
      "QUAL":0
    }
  ]
}
"""

    self.var_del = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":[
    "T"
  ],
  "AC":[
    "1"
  ],
  "AN":"2",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":[
    "dbsnp.129|rs61212177"
  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"7122130836277736291-0",
      "callset_name":"hu939B7C",
      "genotype":[
        1,
        -1
      ],
      "phaseset":"120458771",
      "genotype_likelihood":[
        -125,
        0,
        0
      ],
      "AD":[
        "15",
        "."
      ],
      "CGA_RDP":"4",
      "DP":"19",
      "EHQ":[
        "114",
        "."
      ],
      "FILTER":true,
      "FT":"PASS",
      "HQ":[
        "125",
        "."
      ],
      "QUAL":0
    },
    {
      "callset_id":"7122130836277736291-1",
      "callset_name":"hu553620",
      "genotype":[
        1,
        1
      ],
      "genotype_likelihood":[
        -87,
        -11,
        0
      ],
      "AD":[
        "8",
        "8"
      ],
      "CGA_RDP":"2",
      "DP":"10",
      "EHQ":[
        "87",
        "11"
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "GQ":"11",
      "HQ":[
        "87",
        "11"
      ],
      "QUAL":0
    },
    {
      "callset_id":"7122130836277736291-7",
      "callset_name":"hu68929D",
      "genotype":[
        1,
        0
      ],
      "genotype_likelihood":[
        -37,
        0,
        -52
      ],
      "AD":[
        "8",
        "10"
      ],
      "CGA_RDP":"10",
      "DP":"18",
      "EHQ":[
        "57",
        "52"
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "GQ":"37",
      "HQ":[
        "37",
        "52"
      ],
      "QUAL":0
    }
  ]
}
"""

    self.var_ins = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":[
    "TAA"
  ],
  "AC":[
    "1"
  ],
  "AN":"1",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":[
    "dbsnp.130|rs71806210"
  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"7122130836277736291-97",
      "callset_name":"hu57A769",
      "genotype":[
        1,
        -1
      ],
      "genotype_likelihood":[
        -37,
        0,
        0
      ],
      "AD":[
        "2",
        "."
      ],
      "CGA_RDP":"4",
      "DP":"12",
      "EHQ":[
        "37",
        "."
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "HQ":[
        "37",
        "."
      ],
      "QUAL":0
    }
  ]
}
"""

    self.var_ins_encoded_differently = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458772",
  "reference_bases":"T",
  "alternate_bases":[
    "TA"
  ],
  "AC":[
    "1"
  ],
  "AN":"2",
  "CGA_FI":[

  ],
  "CGA_MEDEL":[

  ],
  "CGA_MIRB":[

  ],
  "CGA_PFAM":[

  ],
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":[
    "dbsnp.130|rs71806210"
  ],
  "CIPOS":[

  ],
  "MEINFO":[

  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"7122130836277736291-104",
      "callset_name":"hu4B0812",
      "genotype":[
        1,
        -1
      ],
      "phaseset":"120458771",
      "genotype_likelihood":[
        -21,
        0,
        0
      ],
      "AD":[
        "2",
        "."
      ],
      "CGA_RDP":"3",
      "DP":"6",
      "EHQ":[
        "20",
        "."
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "HQ":[
        "21",
        "."
      ],
      "QUAL":0
    },
    {
      "callset_id":"7122130836277736291-107",
      "callset_name":"hu44DCFF",
      "genotype":[
        1,
        0
      ],
      "genotype_likelihood":[
        -20,
        0,
        -20
      ],
      "AD":[
        "3",
        "9"
      ],
      "CGA_RDP":"9",
      "DP":"12",
      "EHQ":[
        "17",
        "17"
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "GQ":"20",
      "HQ":[
        "20",
        "20"
      ],
      "QUAL":0
    },
    {
      "callset_id":"7122130836277736291-125",
      "callset_name":"hu42D651",
      "genotype":[
        1,
        0
      ],
      "genotype_likelihood":[
        -37,
        0,
        -24
      ],
      "AD":[
        "3",
        "3"
      ],
      "CGA_RDP":"3",
      "DP":"6",
      "EHQ":[
        "37",
        "24"
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "GQ":"24",
      "HQ":[
        "37",
        "24"
      ],
      "QUAL":0
    }
  ]
}
"""

    self.var_del_encoded_differently = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458777",
  "reference_bases":"TAAAAA",
  "alternate_bases":[
    "TAAAA"
  ],
  "AC":[
    "1"
  ],
  "AN":"1",
  "CGA_FI":[

  ],
  "CGA_MEDEL":[

  ],
  "CGA_MIRB":[

  ],
  "CGA_PFAM":[

  ],
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":[
    "dbsnp.129|rs61212177"
  ],
  "CIPOS":[

  ],
  "MEINFO":[

  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"7122130836277736291-106",
      "callset_name":"hu63EB0A",
      "genotype":[
        1,
        -1
      ],
      "phaseset":"120458771",
      "genotype_likelihood":[
        -28,
        0,
        0
      ],
      "AD":[
        "3",
        "."
      ],
      "CGA_RDP":"1",
      "DP":"5",
      "EHQ":[
        "27",
        "."
      ],
      "FILTER":true,
      "FT":"VQLOW",
      "HQ":[
        "28",
        "."
      ],
      "QUAL":0
    }
  ]
}
"""

    self.var_merged = """
{
  "AC":[
    "1",
    "1"
  ],
  "NS":"1",
  "reference_bases":"TA",
  "alternate_bases":[
    "TAA",
    "T"
  ],
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "AN":"2",
  "CGA_XR":[
    "dbsnp.130|rs71806210",
    "dbsnp.129|rs61212177"
  ],
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "CGA_RDP":"3",
      "FT":"PASS",
      "AD":[
        "9",
        "6"
      ],
      "GQ":"50",
      "EHQ":[
        "49",
        "49"
      ],
      "HQ":[
        "50",
        "50"
      ],
      "FILTER":true,
      "QUAL":0,
      "callset_name":"huD103CC",
      "genotype_likelihood":[
        -50,
        -50,
        -50,
        -50,
        0,
        -50
      ],
      "DP":"24",
      "genotype":[
        1,
        2
      ]
    },
    {
      "callset_id":"7122130836277736291-97",
      "CGA_RDP":"4",
      "FT":"VQLOW",
      "AD":[
        "2",
        "."
      ],
      "EHQ":[
        "37",
        "."
      ],
      "HQ":[
        "37",
        "."
      ],
      "FILTER":true,
      "QUAL":0,
      "callset_name":"hu57A769",
      "genotype_likelihood":[
        -37,
        0,
        0
      ],
      "DP":"12",
      "genotype":[
        1,
        -1
      ]
    },
    {
      "callset_id":"7122130836277736291-0",
      "CGA_RDP":"4",
      "FT":"PASS",
      "AD":[
        "15",
        "."
      ],
      "phaseset":"120458771",
      "EHQ":[
        "114",
        "."
      ],
      "HQ":[
        "125",
        "."
      ],
      "FILTER":true,
      "QUAL":0,
      "callset_name":"hu939B7C",
      "genotype_likelihood":[
        -125,
        0,
        0
      ],
      "DP":"19",
      "genotype":[
        2,
        -1
      ]
    },
    {
      "callset_id":"7122130836277736291-1",
      "CGA_RDP":"2",
      "FT":"VQLOW",
      "AD":[
        "8",
        "8"
      ],
      "GQ":"11",
      "EHQ":[
        "87",
        "11"
      ],
      "HQ":[
        "87",
        "11"
      ],
      "FILTER":true,
      "QUAL":0,
      "callset_name":"hu553620",
      "genotype_likelihood":[
        -87,
        -11,
        0
      ],
      "DP":"10",
      "genotype":[
        2,
        2
      ]
    },
    {
      "callset_id":"7122130836277736291-7",
      "CGA_RDP":"10",
      "FT":"VQLOW",
      "AD":[
        "8",
        "10"
      ],
      "GQ":"37",
      "EHQ":[
        "57",
        "52"
      ],
      "HQ":[
        "37",
        "52"
      ],
      "FILTER":true,
      "QUAL":0,
      "callset_name":"hu68929D",
      "genotype_likelihood":[
        -37,
        0,
        -52
      ],
      "DP":"18",
      "genotype":[
        2,
        0
      ]
    }
  ],
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773"
}
"""

    self.var_sv = """
{
  "contig_name":"11",
  "start_pos":"132083603",
  "end_pos":"132083604",
  "reference_bases":"G",
  "alternate_bases":[
    "GN[11:132084035["
  ],
  "AC":[

  ],
  "CGA_BF":0.59999999999999998,
  "CGA_BNDG":"NM_001048209|+&NM_001144058|+&NM_001144059|+&NM_016522|+",
  "CGA_BNDGO":"NM_001048209|+&NM_001144058|+&NM_001144059|+&NM_016522|+",
  "CGA_FI":[

  ],
  "CGA_MEDEL":[
    "AluYa5",
    "11",
    "132083622",
    "132083926"
  ],
  "CGA_MIRB":[

  ],
  "CGA_PFAM":[

  ],
  "CGA_RPT":[

  ],
  "CGA_XR":[

  ],
  "CIPOS":[

  ],
  "MATEID":"GS000015177-ASM_4128_R",
  "MEINFO":[

  ],
  "NS":"1",
  "SVTYPE":"BND",
  "call":[
    {
      "callset_id":"11785686915021445549-148",
      "callset_name":"huF80F84",
      "genotype":[
        1
      ],
      "genotype_likelihood":[

      ],
      "AD":[

      ],
      "CGA_BNDDEF":"GN[132084035[",
      "CGA_BNDMPC":"46",
      "CGA_BNDP":"IMPRECISE",
      "CGA_BNDPOS":"132083603",
      "EHQ":[

      ],
      "FILTER":true,
      "FT":"TSNR",
      "HQ":[

      ],
      "QUAL":0
    }
  ]
}
"""

    self.ref_block = """
{
  "contig_name":"2",
  "start_pos":"77608523",
  "end_pos":"77608541",
  "reference_bases":"N",
  "alternate_bases":[

  ],
  "AC":[

  ],
  "AN":"0",
  "CGA_FI":[

  ],
  "CGA_MEDEL":[

  ],
  "CGA_MIRB":[

  ],
  "CGA_PFAM":[

  ],
  "CGA_RPT":[

  ],
  "CGA_XR":[

  ],
  "CIPOS":[

  ],
  "END":"77608540",
  "MEINFO":[

  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"11785686915021445549-93",
      "callset_name":"hu259AC7",
      "genotype":[
        0,
        0
      ],
      "genotype_likelihood":[

      ],
      "AD":[

      ],
      "EHQ":[

      ],
      "FILTER":true,
      "HQ":[

      ],
      "QUAL":0
    }
  ]
}
"""

    self.no_call = """
{
  "contig_name":"7",
  "start_pos":"47378001",
  "end_pos":"47378002",
  "reference_bases":"T",
  "alternate_bases":[
    "<CGA_CNVWIN>"
  ],
  "AC":[

  ],
  "CGA_FI":[

  ],
  "CGA_MEDEL":[

  ],
  "CGA_MIRB":[

  ],
  "CGA_PFAM":[

  ],
  "CGA_RPT":[

  ],
  "CGA_WINEND":"47380000",
  "CGA_XR":[

  ],
  "CIPOS":[

  ],
  "MEINFO":[

  ],
  "NS":"1",
  "call":[
    {
      "callset_id":"11785686915021445549-0",
      "callset_name":"hu775356",
      "genotype":[
        -1
      ],
      "genotype_likelihood":[

      ],
      "AD":[

      ],
      "CGA_CL":1.002,
      "CGA_CP":"2",
      "CGA_CT":"=",
      "CGA_GP":"0.84",
      "CGA_LS":"496",
      "CGA_NP":"1.30",
      "CGA_PS":"45",
      "CGA_TS":"45",
      "EHQ":[

      ],
      "FILTER":true,
      "HQ":[

      ],
      "QUAL":0
    }
  ]
}
"""

if __name__ == "__main__":
  unittest.main()
