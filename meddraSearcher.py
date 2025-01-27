from pyspark.sql import Row
from pyspark.sql.functions import col
from pyspark.sql.functions import lower

def load(spark):
    """
    Load meddra.tsv, meddra_all_indications.tsv and meddra_all_se.tsv in a PySpark data frame
    """
    meddra = spark.read.csv("data/meddra.tsv",sep="\t",header = True)
    meddra = meddra.select("umls_concept_id","side_effect")
    meddra = meddra.withColumnRenamed("umls_concept_id","CUI") \
        .withColumnRenamed("side_effect","symptom")
    
    meddra.cache()
    
    meddra_all_ind = spark.read.csv("data/meddra_all_indications.tsv",sep="\t",header = True)
    meddra_all_ind = meddra_all_ind.select("umls_concept_id_label","umls_concept_id_meddra_team","stitch_flat_id")
    meddra_all_ind = meddra_all_ind.withColumnRenamed("umls_concept_id_label","CUI1") \
        .withColumnRenamed("umls_concept_id_meddra_team","CUI2") \
        .withColumnRenamed("stitch_flat_id","stitchID")
    
    meddra_all_ind.cache()
    
    meddra_all_se = spark.read.csv("data/meddra_all_se.tsv",sep="\t",header = True)
    meddra_all_se = meddra_all_se.select("umls_concept_id_label","umls_concept_id_meddra_team","stitch_flat_id","stitch_stereo_id")
    meddra_all_se = meddra_all_se.withColumnRenamed("umls_concept_id_label","CUI1") \
        .withColumnRenamed("umls_concept_id_meddra_team","CUI2") \
        .withColumnRenamed("stitch_flat_id","stitchID1") \
        .withColumnRenamed("stitch_stereo_id","stitchID2")
    
    meddra_all_se.cache()
    
    return meddra,meddra_all_ind,meddra_all_se

def search_meddra(term,meddra):
    """
    Take a symptom `term`and return the corresponding list of CUI
    """
    term = term.lower()
    result = meddra.filter(
        (lower(col("symptom")).rlike(term))
    )
    return [elt.CUI for elt in result.collect()]

def search_meddra_ind(CUI,meddra_ind):
    """
    Take a list of CUI `CUI`, return a list of STITCH ID for the STITCH database
    """
    stitch_id = []
    for idt in CUI:
        result = meddra_ind.filter(
            (col("CUI1") == idt) | (col("CUI2") == idt)
        )
        stitch_id.extend(st_id.stitchID for st_id in result.collect())
    return stitch_id

def search_meddra_se(CUI,meddra_se):
    """
    Take a list of CUI `CUI`, return a list of STITCH ID for the STITCH database
    """
    stitch_id = []
    for idt in CUI:
        result = meddra_se.filter(
            (col("CUI1") == idt) | (col("CUI2") == idt)
        )
        for st_id in result.collect():
            stitch_id.extend((st_id.stitchID1, st_id.stitchID2))
    return stitch_id