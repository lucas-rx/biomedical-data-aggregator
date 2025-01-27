import sqlite3
import pandas as pd
import typing

DATABASE = "./data/meddra_database.db"

def drop_database() -> None:
    print("Initialize database...")
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS meddra;
        DROP TABLE IF EXISTS meddra_all_indications;
        DROP TABLE IF EXISTS meddra_all_se;
        DROP TABLE IF EXISTS meddra_freq;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Done !")

def load_meddra_database() -> None:
    print("Loading MedDRA data in the database...")
    df_meddra = pd.read_csv("./data/meddra.tsv", delimiter='\t')
    df_meddra_all_indications = pd.read_csv("./data/meddra_all_indications.tsv", delimiter='\t')
    df_meddra_all_se = pd.read_csv("./data/meddra_all_se.tsv", delimiter='\t')
    df_meddra_freq = pd.read_csv("./data/meddra_freq.tsv", delimiter='\t')

    conn = sqlite3.connect(DATABASE)

    df_meddra.to_sql("meddra", conn, if_exists = "replace")
    df_meddra_all_indications.to_sql("meddra_all_indications", conn, if_exists = "replace")
    df_meddra_all_se.to_sql("meddra_all_se", conn, if_exists = "replace")
    df_meddra_freq.to_sql("meddra_freq", conn, if_exists = "replace")

    conn.close()
    print("Done !")

def load(spark):
    meddra_all_indications = spark.read.tsv("data/meddra.tsv", header=True)
    meddra_all_indications = meddra_all_indications.select("stitch_flat_id", "umls_concept_id_label", "umls_concept_id_meddra_team", "concept_name", "meddra_concept_name")

    meddra_all_se = spark.read.tsv("data/meddra.tsv", header=True)
    meddra_all_se = meddra_all_se.select("stitch_flat_id", "stitch_stereo_id", "umls_concept_id_label", "umls_concept_id_meddra_team", "side_effect")

    return meddra_all_indications, meddra_all_se

def search_in_meddra_database(term, meddra_all_indications, meddra_all_se, symptom=True, side_effect=True) -> None:
    term = term.lower()
    """
    Return a list of indications of the symptom 'term',
    and a list of side effects of 
    """



if __name__ == "__main__":
    #drop_database()
    #load_meddra_database()
    search_in_meddra_database("muscle", True, False)

