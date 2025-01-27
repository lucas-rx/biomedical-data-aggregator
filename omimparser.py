import pandas as pd
import re
from pyspark.sql import Row
from pyspark.sql.functions import col
from pyspark.sql.functions import lower



def parserTI(ti):
    """Take a row corresponding to TI in omim parse it to have the disease name and the abbreviation"""
    liste = ti.split("//")
    result = []
    for s in liste:
        s = re.sub(r'^[#%\d]+\s*', '', s)
        s = re.sub(r';;', '', s)
        parts = s.split(';', 1)
        tuples = tuple(part.strip() for part in parts)
        result.append(tuples)
    return result


def parserSynonyms(s):
    """Take a string of terms separated by | return a list of all individuals term"""
    liste = s.split('|')
    liste = [elt for elt in liste if len(elt) > 0]
    return liste


def load(spark):
    """
    Parse the text file omim.txt, then load this parsed file and omim_onto.csv in a PySpark data frame
    """
    print("dataframe omim_onto...")
    omim_onto = spark.read.csv("data/omim_onto.csv", header=True)
    omim_onto = omim_onto.select("CUI", "Preferred Label", "Synonyms")
    omim_onto = omim_onto \
        .withColumnRenamed("CUI", "id") \
        .withColumnRenamed("Preferred Label", "name") \
        .withColumnRenamed("Synonyms", "synonyms")
    omim_onto.cache()

    print("reading omim.txt...")
    with open('data/omim.txt', 'r') as file:
        lines = file.readlines()

    data = []
    columns = ['NO', 'TI', 'CS']

    print("parsing...")
    record_data = {'NO': None, 'TI': None, 'CS': None}
    first = True
    for line in lines:
        if line.startswith('*FIELD*'):
            column_name = line.strip().split(' ')[-1]
        elif line.startswith('*RECORD*'):
            if data:
                if first:
                    first = False
                else:
                    data.append(record_data.copy())
                record_data = {'NO': None, 'TI': None, 'CS': None}
            else:
                record_data = {'NO': None, 'TI': None, 'CS': None}
                data.append(record_data)
                first = True
        elif column_name in columns:
            field_data = line.strip()
            if record_data[column_name] is None:
                record_data[column_name] = field_data
            else:
                record_data[column_name] = record_data[column_name] + '//' + field_data
    data.append(record_data)

    # Convert list of dictionaries to PySpark DataFrame
    omim = spark.createDataFrame(data)
    print("done")
    omim = omim \
        .withColumnRenamed("TI", "name") \
        .withColumnRenamed("CS", "symptome") \
        .withColumnRenamed("NO", "id")
    omim.cache()
    return omim_onto, omim


def search(term, omim):
    """
    Take a symptom `term` and return a filter of spark corresponding to row with the symptoms
    """
    term = term.lower()
    result = omim.filter((lower(col("symptome")).contains(term)))
    return [elt.name for elt in result.collect() if len(elt.name) > 0]


def search_onto(result, omim_onto):
    """Take a list of name of disease return a list containing the disease and their synonym and abbreviation if
    existing"""
    names = [name for elt in result for name in parserTI(elt) if len(name) > 0]
    search = omim_onto.filter(col("name").isin([name[0] for name in names])).select("name", "synonyms").collect()
    res = []
    for row in search:
        res.append(row.name)
        if row.synonyms:
            res.extend(parserSynonyms(row.synonyms))
    abbreviations = [name[1] for name in names if len(name) > 1 and len(name[1]) > 0]
    res.extend(abbreviations)

    return res
