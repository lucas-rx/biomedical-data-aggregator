from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, when

def load(spark):
    """
    Load drugbank.xml into a PySpark data frame
    """
    print("parsing with spark-xml...")

    data = spark.read \
        .format("xml") \
        .options(rowTag="drug") \
        .load("data/drugbank.xml", schema="toxicity STRING, indication STRING, name STRING, `drugbank-id` STRING")

    data = data \
        .withColumnRenamed("toxicity", "side_effect") \
        .withColumnRenamed("indication", "symptome") \
        .withColumnRenamed("drugbank-id", "id")
    data.cache()
    print("done")
    return data

def search(term, dataXML, sideeffect=True, symptom=True):
    """
    Search a symptom `term`in the drugbank PySpark data frame
    `side_effect` : true if we want to search a side effect
    `symptom` : true if we want to search a symptom
    """
    term = term.lower()
    
    conditions = []

    if sideeffect:
        conditions.append((col("side_effect").isNotNull()) & (lower(col("side_effect")).rlike(term)))
    if symptom:
        conditions.append((col("symptome").isNotNull()) & (lower(col("symptome")).rlike(term)))
    
    if not conditions:
        return None
    
    result = dataXML.filter(when(conditions[0], True))
    for condition in conditions[1:]:
        result = result.filter(when(condition, True))
    return [elt.name for elt in result.collect()]
