from functools import reduce

from pyspark.sql.functions import col

import subprocess
import time


def load(spark):
    # Parse STITCH file : only extract the lines with an ATC code
    # subprocess.run(["awk", "-f", "./stitch_parser.awk", "./data/chemical.sources.v5.0.tsv"])
    print("Loading STITCH database...")
    stitch = spark.read.option("delimiter", "\t").csv("data/parsed_stitch.tsv", header=True)
    stitch_rows = stitch.collect()
    dict_list = [row.asDict() for row in stitch_rows]
    for dict in dict_list:
        dict.pop("Database")
    stitch = spark.createDataFrame(dict_list)
    # stitch.select("CIDm").show()
    # stitch.show()
    stitch.cache()
    return stitch


def search(stitch_id_list, stitch_df):
    """
        Return a list of ATC codes corresponding to the STITCH IDs given in parameter.
    """

    print(f"Number of STITCH IDs : {len(stitch_id_list)}")

    pattern = "|".join(stitch_id[4:] for stitch_id in stitch_id_list)

    searched_atc = stitch_df.filter(
        col("CIDm").rlike(pattern)
        | col("CIDs").rlike(pattern)
    ).select("ATCCode").collect()

    atc_codes = [code.ATCCode for code in searched_atc]

    return atc_codes
