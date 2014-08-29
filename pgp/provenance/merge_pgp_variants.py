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

import copy
import json
import unittest

def FlattenFieldAssociatedWithAlt(fields, field_name, alt_num):
  """Change array values to scalar values.

  Change this array to instead be a scalar whose value is the one
  associated with the alternate allele we are flattening.
  """
  if field_name in fields and fields[field_name]:
    fields[field_name] = fields[field_name][alt_num - 1]
  else:
    # The field is empty, just nuke it.
    fields.pop(field_name, None)

    
def SimplifyRecord(fields, alt_num=None):
  """Modify our record to be in a form easier to work with in BigQuery.

  Specifically drop some fields and flatten any associated with alternate_bases.  
  """
  if "alternate_bases" in fields and fields["alternate_bases"]:
    if len(fields["alternate_bases"]) > 1 and alt_num is None:
      raise Exception("Attempting to flatten a record with multiple alternate " +
                      "alleles with no specific alternate to use specified.")
    if alt_num is None:
      # There is only one alternate, use its index.
      alt_num = 1

  # Remove VCF info key/value pairs that are not useful in this context.
  # INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
  fields.pop("NS", None)
  # INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in called genotypes">
  fields.pop("AN", None)
  # INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in genotypes, for each ALT allele">
  fields.pop("AC", None)

  # Flatten the alternate_bases field and the associated INFO fields of
  # type Number=A indicating the field has one value per alternate
  # allele.
  FlattenFieldAssociatedWithAlt(fields, "alternate_bases", alt_num)
  ##INFO=<ID=CGA_XR,Number=A,Type=String,Description="Per-ALT external database reference (dbSNP, COSMIC, etc)">
  FlattenFieldAssociatedWithAlt(fields, "CGA_XR", alt_num)
  ##INFO=<ID=AF,Number=A,Type=String,Description="Allele frequency, or &-separated frequencies for complex variants (in latter, '?' designates unknown parts)">
  FlattenFieldAssociatedWithAlt(fields, "AF", alt_num)
  ##INFO=<ID=CGA_FI,Number=A,Type=String,Description="Functional impact annotation">
  FlattenFieldAssociatedWithAlt(fields, "CGA_FI", alt_num)
  ##INFO=<ID=CGA_BNDG,Number=A,Type=String,Description="Transcript name and strand of genes containing breakend">
  FlattenFieldAssociatedWithAlt(fields, "CGA_BNDG", alt_num)
  ##INFO=<ID=CGA_BNDGO,Number=A,Type=String,Description="Transcript name and strand of genes containing mate breakend">
  FlattenFieldAssociatedWithAlt(fields, "CGA_BNDGO", alt_num)

  # Re-write the genotypes and genotype likelihoods.
  for call in fields["call"]:
    for idx in range(0, len(call["genotype"])):
      if 0 < call["genotype"][idx]:
        if alt_num == call["genotype"][idx]:
          # genotypes corresponding to _this_ alternate are now all '1'
          call["genotype"][idx] = 1
        else:
          # genotypes corresponding to _any_other_ alternate are now '2'
          call["genotype"][idx] = 2
    if 2 == alt_num:
      # We have a 1/2 record we are re-writing. From the spec "for
      # triallelic sites the ordering is: AA,AB,BB,AC,BC,CC" so the
      # new ordering should be: AA, AC, CC, AB, BC, BB.
      gl = [
        call["genotype_likelihood"][0],
        call["genotype_likelihood"][3],
        call["genotype_likelihood"][5],
        call["genotype_likelihood"][1],
        call["genotype_likelihood"][4],
        call["genotype_likelihood"][2],
        ]
      call["genotype_likelihood"] = gl
    elif 2 < alt_num:
      # We don't actually have any of these in the PGP data, but adding
      # a check here to be on the safe side.
      raise Exception("Attempting to expand genotype for a record that " +
                      "is more than trialleic.")

  return fields


def HasAlternate(fields):
  if "alternate_bases" in fields and fields["alternate_bases"]:
    return True
  return False


def MapRecord(fields):
  """Emit one or more key/value pairs for the record.

  Here we are using the same key as the Variant Store import _expect_
  that we use one value from alternate_bases and emit multiple records
  if alternate_bases has more than one value.
  """
  alts = [""]
  if "alternate_bases" in fields and fields["alternate_bases"]:
    alts = fields["alternate_bases"]

  end = ""
  if "END" in fields:
    end = fields["END"]
  elif "end" in fields:
    end = fields["end"]

  pairs = []
  for idx in range(0, len(alts)):  
    key = "%s:%s:%s:%s:%s" % (fields["contig_name"],
                              fields["start_pos"],
                              fields["reference_bases"],
                              alts[idx],
                              end)
    if 1 == len(alts):
      pairs.append( (key, SimplifyRecord(fields)) )
    else:
      pairs.append( (key, SimplifyRecord(copy.deepcopy(fields), alt_num=idx+1)) )
    
  return pairs


def FoldByKeyVariant(a, b):
  """Naively merge the calls within two variant records with the same key."""
  # Handle zero value
  if not a: return b
  if not b: return a

  # TODO: to make this commutative and associative for any data we
  # might see, fail if any INFO values differ between the two records
  # we are merging.  But be pragmatic for now, variant store import
  # can also silently drops values that differ in info fields of
  # merged record.

  # Note: The ordering of calls within the record is not
  # meaningful, not bothering to sort them here for the value of that
  # field to be commutative and associative from this function.
  
  a["call"].extend(b["call"])

  return a


class VariantMergeTest(unittest.TestCase):
  def testHasAlternate(self):
    self.assertTrue(HasAlternate(json.loads(self.var_both_ins_del)))
    self.assertTrue(HasAlternate(json.loads(self.var_sv)))
    self.assertTrue(HasAlternate(json.loads(self.no_call)))
    self.assertFalse(HasAlternate(json.loads(self.ref_block)))

  def testSimplifyRecord(self):
    self.assertDictEqual(json.loads(self.var_ins_simplified), 
                         SimplifyRecord(json.loads(self.var_ins)))
    
    self.assertDictEqual(json.loads(self.var_del_simplified), 
                         SimplifyRecord(json.loads(self.var_del)))

    # This is the 1/2 genotype record
    self.assertRaises(Exception, SimplifyRecord, json.loads(self.var_both_ins_del))
    self.assertDictEqual(json.loads(self.var_both_ins_simplified), 
                         SimplifyRecord(json.loads(self.var_both_ins_del),
                                        alt_num=1))
    self.assertDictEqual(json.loads(self.var_both_del_simplified), 
                         SimplifyRecord(json.loads(self.var_both_ins_del),
                                        alt_num=2))

  def testMapRecord(self):
    pairs = MapRecord(json.loads(self.var_ins_encoded_differently))
    self.assertEqual(1, len(pairs))
    self.assertEqual("6:120458771:T:TA:", pairs[0][0])

    pairs = MapRecord(json.loads(self.var_del_encoded_differently))
    self.assertEqual(1, len(pairs))
    self.assertEqual("6:120458771:TAAAAA:TAAAA:", pairs[0][0])

    pairs = MapRecord(json.loads(self.var_sv))
    self.assertEqual(1, len(pairs))
    self.assertEqual("11:132083603:G:GN[11:132084035[:", pairs[0][0])

    pairs = MapRecord(json.loads(self.ref_block))
    self.assertEqual(1, len(pairs))
    self.assertEqual("2:77608523:N::77608540", pairs[0][0])

  def testMapAndMergeRecords(self):
    pairs = MapRecord(json.loads(self.var_ins))
    self.assertEqual(1, len(pairs))
    self.assertEqual("6:120458771:TA:TAA:", pairs[0][0])
    self.assertDictEqual(json.loads(self.var_ins_simplified), 
                         pairs[0][1])
    var_ins = pairs[0][1]
    
    pairs = MapRecord(json.loads(self.var_del))
    self.assertEqual(1, len(pairs))
    self.assertEqual("6:120458771:TA:T:", pairs[0][0])
    self.assertDictEqual(json.loads(self.var_del_simplified), 
                         pairs[0][1])
    var_del = pairs[0][1]

    # This is the 1/2 genotype record
    pairs = MapRecord(json.loads(self.var_both_ins_del))
    self.assertEqual(2, len(pairs))
    self.assertEqual("6:120458771:TA:TAA:", pairs[0][0])
    self.assertDictEqual(json.loads(self.var_both_ins_simplified), 
                         pairs[0][1])
    het_alt_var_ins = pairs[0][1]

    self.assertEqual("6:120458771:TA:T:", pairs[1][0])
    self.assertDictEqual(json.loads(self.var_both_del_simplified), 
                         pairs[1][1])
    het_alt_var_del = pairs[1][1]

    # Note: deep copy these since we're using them in two separate
    # tests and FoldByKeyVariant modified the dictionaries in place.
    self.assertDictEqual(json.loads(self.var_ins_merged),
                         FoldByKeyVariant(copy.deepcopy(het_alt_var_ins),
                                          copy.deepcopy(var_ins)))
    self.assertDictEqual(json.loads(self.var_del_merged),
                         FoldByKeyVariant(copy.deepcopy(het_alt_var_del), 
                                          copy.deepcopy(var_del)))

    # Check this other direction.  In practice its not worth sorting
    # them because the order of calls has no meaning.
    self.assertDictEqual(self.sort_calls(json.loads(self.var_ins_merged)),
                         self.sort_calls(FoldByKeyVariant(var_ins, het_alt_var_ins)))
    self.assertDictEqual(self.sort_calls(json.loads(self.var_del_merged)),
                         self.sort_calls(FoldByKeyVariant(var_del, het_alt_var_del)))

  def sort_calls(self, record):
    record["call"] = sorted(record["call"], key=lambda k: k["callset_id"]) 
    return record


  def setUp(self):
    self.maxDiff = None

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
        0,
        1,
        2,
        3,
        4,
        5
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

    self.var_both_ins_simplified = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"TAA",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.130|rs71806210",
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "callset_name":"huD103CC",
      "genotype":[
        1,
        2
      ],
      "genotype_likelihood":[
        0,
        1,
        2,
        3,
        4,
        5
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

    self.var_both_del_simplified = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"T",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.129|rs61212177",
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "callset_name":"huD103CC",
      "genotype":[
        2,
        1
      ],
      "genotype_likelihood":[
        0,
        3,
        5,
        1,
        4,
        2
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

    self.var_del_simplified = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"T",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.129|rs61212177",
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

    self.var_ins_simplified = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"TAA",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.130|rs71806210",
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

    self.var_ins_merged = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"TAA",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.130|rs71806210",
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "callset_name":"huD103CC",
      "genotype":[
        1,
        2
      ],
      "genotype_likelihood":[
        0,
        1,
        2,
        3,
        4,
        5
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
    },
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

    self.var_del_merged = """
{
  "contig_name":"6",
  "start_pos":"120458771",
  "end_pos":"120458773",
  "reference_bases":"TA",
  "alternate_bases":"T",
  "CGA_RPT":[
    "A-rich|Low_complexity|20.4"
  ],
  "CGA_XR":"dbsnp.129|rs61212177",
  "call":[
    {
      "callset_id":"7122130836277736291-2",
      "callset_name":"huD103CC",
      "genotype":[
        2,
        1
      ],
      "genotype_likelihood":[
        0,
        3,
        5,
        1,
        4,
        2
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
    },
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

if __name__ == "__main__":
  unittest.main()
