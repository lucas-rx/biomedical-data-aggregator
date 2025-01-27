import sqlite3

DATABASE = "./data/hpo_annotations.sqlite"


def search_db(hp_id=""):
    """
    Return the disease names corresponding to the hp_id symptom.
    Return None if not found.
    """
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    res = cur.execute("SELECT disease_label FROM phenotype_annotation WHERE sign_id = ?", (hp_id,)).fetchone()

    cur.close()
    conn.close()

    return res[0] if res else None


def search_obo(symptoms_ids=[]):
    """
    Return the disease names corresponding to the list of symptoms.
    Return None if not found.
    """
    results = []
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    for elt in symptoms_ids:
        results.append(cur.execute("SELECT disease_label FROM phenotype_annotation WHERE sign_id = ?", (elt,)).fetchall())
    cur.close()
    conn.close()
    return [item[0] for sublist in results for item in sublist]
