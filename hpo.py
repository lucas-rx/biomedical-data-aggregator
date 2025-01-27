from pyspark.sql.functions import col, explode


def load(spark):
    """
    Load the hpo.obo file into a Spark DataFrame.
    Returns a DataFrame with the following columns:
    id, name, description, synonyms, alt_ids
    """
    print("reading hpo.obo...")

    with open("data/hpo.obo", 'r') as f:
        data = f.read()

    entries = data.split('\n\n')

    results = []
    for entry in entries:
        if entry.startswith('[Term]'):
            lines = entry.split('\n')
            entry_dict = {}
            for line in lines:
                key_value = line.split(': ')
                if len(key_value) == 2:
                    key = key_value[0]
                    value = key_value[1]
                    if key not in entry_dict:
                        entry_dict[key] = []
                    entry_dict[key] += [value]

            id_value = entry_dict.get('id', '')[0]

            name = entry_dict.get('name', '')
            name = name[0].lower() if name else ''

            description = entry_dict.get('def', '')
            description = description[0].lower() if description else ''

            synonyms_dict = entry_dict.get('synonym', '')
            synonyms = ""
            for synonym in synonyms_dict:
                synonyms += synonym.lower() + " "

            alt_id_value = entry_dict.get('alt_id', '')
            alt_id_value = [alt_id for alt_id in alt_id_value]

            results += [(id_value, name, description, synonyms, alt_id_value)]

    print("creating hpo dataframe...")
    hpo_df = spark.createDataFrame(results, ['id', 'name', 'description', 'synonyms', 'alt_ids'])
    print("done")
    hpo_df.cache()
    return hpo_df


def search(term, hpo):
    """
    Return the list of diseases (ids HP) coming from the symptom term.
    Return a list of ids
    """
    term = term.lower()
    result = hpo.filter(
        col("name").rlike(term)
        | col("description").rlike(term)
        | col("synonyms").rlike(term))
    # assuming your dataframe is named 'df'
    merged_ids = result.selectExpr("id as merged_id").union(
        result.select(explode("alt_ids").alias("merged_id"))).distinct().collect()
    merged_ids_list = [row["merged_id"] for row in merged_ids]
    return merged_ids_list
