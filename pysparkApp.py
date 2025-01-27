from pyspark.sql import SparkSession
from pyspark.sql.functions import col

import drugbankIndexer as dbdata
import omimparser as op
import meddraSearcher as md
import stitch as st
import keg_parser as atc
import time
import hpo
import hpo_annotation
import collections

spark = SparkSession.builder \
    .appName("DrugBank XML Parser") \
    .config("spark.jars.packages", "com.databricks:spark-xml_2.12:0.16.0") \
    .getOrCreate()

drugbank = None
omim_onto, omim = None, None
meddra, meddra_ind, meddra_se = None, None, None
stitch = None
atc_data = None
hpo_df = None


def load_drugbank():
    global drugbank
    drugbank = dbdata.load(spark)

def load_omim():
    global omim_onto, omim
    omim_onto, omim = op.load(spark)

def load_meddra():
    global meddra, meddra_ind, meddra_se
    meddra, meddra_ind, meddra_se = md.load(spark)

def load_stitch():
    global stitch
    stitch = st.load(spark)

def load_atc():
    global atc_data
    atc_data = atc.load(spark)

def load_hpo():
    global hpo_df
    hpo_df = hpo.load(spark)


def load():
    """
    Load all the data in PySpark dataframes
    """
    global drugbank, omim_onto, omim, meddra, meddra_ind, meddra_se, stitch, atc_data, hpo_df
    drugbank = dbdata.load(spark)
    omim_onto, omim = op.load(spark)
    meddra, meddra_ind, meddra_se = md.load(spark)
    stitch = st.load(spark)
    atc_data = atc.load(spark)
    hpo_df = hpo.load(spark)


"""
print("DrugBank :")
drugbank.show()
start = time.time()
print(dbdata.search("nausea",drugbank))
duree = start-time.time()
print(duree)
print("OMIM (txt) :")
omim.show()
print("OMIM_ONTO (csv) :")
omim_onto.show()
print("meddra :")
meddra.show()
print("meddra_all_indications :")
meddra_ind.show()
print("meddra_all_se:")
meddra_se.show()
print("STITCH :")
stitch.show()
print("ATC :")
atc_data.show()
print("HPO :")
hpo_df.show()
"""


##POUR RECHERCHER DANS DRUGBANK
# test_recherche = dbdata.search('cancer',drugBankData,sideeffect=True, symptome=True)
# test_recherche.show()
##POUR RECHERCHER DANS OMIM
# print(op.search("cancer", omim))
##POUR RECHERCHER DANS Meddra
# print(md.search_meddra_ind(md.search_meddra("nausea", meddra), meddra_ind))
# print(md.search_meddra_se(md.search_meddra("nausea", meddra), meddra_se))
##POUR RECHERCHER DANS HPO
# hpo_list = hpo.search("death", hpo_df)
# hpo_maladies_list = hpo_annotation.search_obo(hpo_list)
# print(hpo_maladies_list)


def search_alt(term, timestamp=True):
    """
    Take a symptom `term`, return 3 lists :
    `list_one` : list of disease with this symptom ;
    `list_two` : list of meds causing this side effect ;
    `list_three` : list of meds healing the symptom.\n
    Optional : `timestamps`: a dict with timestamps
    """
    if timestamp:
        timestamps = {}
    list_one = []
    list_two = []
    list_three = []

    # DRUGBANK SEARCH
    if timestamp:
        start_drugbank = time.time()
    for med in dbdata.search(term, drugbank, sideeffect=True, symptom=False):
        list_two.append((med, "DrugBank"))
    for med in dbdata.search(term, drugbank, sideeffect=False, symptom=True):
        list_three.append((med, "DrugBank"))
    if timestamp:
        timestamps["drugbank"] = time.time() - start_drugbank
        print(f"DrugBank : {timestamps['drugbank']}")

    # OMIM SEARCH
    if timestamp:
        start_omim = time.time()
    diseaseAndSyn = op.search_onto(op.search(term, omim), omim_onto)
    for disease in diseaseAndSyn:
        list_one.append((disease, "OMIM"))
    if timestamp:
        timestamps["omim"] = time.time() - start_omim
        print(f"OMIM : {timestamps['omim']}")

    # MEDDRA SEARCH
    if timestamp:
        start_meddra = time.time()
    tmp = md.search_meddra(term, meddra)
    stitch_ind = md.search_meddra_ind(tmp, meddra_ind)
    stitch_se = md.search_meddra_se(tmp, meddra_se)
    if timestamp:
        timestamps["meddra"] = time.time() - start_meddra
        print(f"MedDRA : {timestamps['meddra']}")

    # STITCH SEARCH
    # fonctionseatchdestitchandATC(stitch_ind) dans list_three
    if timestamp:
        start_stitch_ind = time.time()
    atc_codes_ind = st.search(stitch_ind, stitch)
    medicines_ind = atc.search(atc_codes_ind, atc_data)
    for med in medicines_ind:
        list_three.append((med, "STITCH"))

    if timestamp:
        timestamps["stitch_ind"] = time.time() - start_stitch_ind
        print(f"STITCH - Indications : {timestamps['stitch_ind']}")

    # fonctionseatchdestitchandATC(stitch_se) dans list_two
    if timestamp:
        start_stitch_se = time.time()
    atc_codes_se = st.search(stitch_se, stitch)
    medicines_se = atc.search(atc_codes_se, atc_data)
    for med in medicines_se:
        list_two.append((med, "STITCH"))
    if timestamp:
        timestamps["stitch_se"] = time.time() - start_stitch_se
        print(f"STITCH - Side effects : {timestamps['stitch_se']}")

    # OBO search
    if timestamp:
        start_OBO = time.time()
    diseaseAndSynOBO = op.search_onto(hpo_annotation.search_obo(hpo.search(term, hpo_df)), omim_onto)
    for disease in diseaseAndSynOBO:
        list_one.append((disease, "HPO"))
    if timestamp:
        timestamps["OBO"] = time.time() - start_OBO
        print(f"HPO OBO : {timestamps['OBO']}")

    # if timestamp:
    # return list_one,list_two,list_three,timestamps

    return list_one,list_two,list_three


def search(term):
    """
    Main function of the program : return
    the diseases and the medicines (indications + side effects)
    from a list of symptoms
    """
    term = term.replace("*", ".*")
    if " OU " not in term and " ET " not in term:
        list_one,list_two,list_three = search_alt(term)
        list_one = collections.Counter(list_one)
        list_one = dict(sorted(list_one.items(), key=lambda item: item[1], reverse=True))
        list_two = collections.Counter(list_two)
        list_two = dict(sorted(list_two.items(), key=lambda item: item[1], reverse=True))
        list_three = collections.Counter(list_three)
        list_three = dict(sorted(list_three.items(), key=lambda item: item[1], reverse=True))
        return list_one,list_two,list_three
    terms = term.split(" OU ")
    finale = [term.split(" ET ") for term in terms]
    lists_one = []
    lists_two = []
    lists_three = []
    for term in finale:
        if len(term) > 1:
            print("\n", term, "\n")
            list_one, list_two, list_three = intersect_terms(term)
        else:
            list_one, list_two, list_three = search_alt(term[0])
        lists_three.append(list_three)
        lists_two.append(list_two)
        lists_one.append(list_one)
    lists_one = [item for sublist in lists_one for item in sublist]
    lists_two = [item for sublist in lists_two for item in sublist]
    lists_three = [item for sublist in lists_three for item in sublist]
    lists_one = collections.Counter(lists_one)
    lists_one = dict(sorted(lists_one.items(), key=lambda item: item[1], reverse=True))
    lists_two = collections.Counter(lists_two)
    lists_two = dict(sorted(lists_two.items(), key=lambda item: item[1], reverse=True))
    lists_three = collections.Counter(lists_three)
    lists_three = dict(sorted(lists_three.items(), key=lambda item: item[1], reverse=True))
    return lists_one, lists_two, lists_three


def intersect(list_of_lists):
    """
    Return the intersection of many lists, keeping duplicates
    """
    from collections import Counter

    # Trouver les occurrences de chaque élément dans chaque liste
    counters = [Counter(lst) for lst in list_of_lists]

    # Trouver les occurrences minimales de chaque élément dans toutes les listes
    min_occurrences = counters[0].copy()
    for counter in counters[1:]:
        for key, value in counter.items():
            if key in min_occurrences:
                min_occurrences[key] = min(min_occurrences[key], value)
            else:
                min_occurrences.pop(key, None)

    # Reconstruire la liste d'intersection avec les doublons
    intersection = []
    for key, value in min_occurrences.items():
        intersection.extend([key] * value)

    return intersection


def union(list_of_lists):
    """
    Return the union of many lists
    """
    # Convertir les listes internes en ensembles
    sets = [set(lst) for lst in list_of_lists]

    # Trouver l'union de tous les ensembles
    union = set.union(*sets)

    return list(union)


def intersect_terms(terms):
    """
    Useful for ET operator : intersect many lists of :
    - diseases
    - indications
    - side effects
    """
    lists_one = []
    lists_two = []
    lists_three = []
    for term in terms:
        list_one, list_two, list_three = search_alt(term)
        lists_one.append(list_one)
        lists_two.append(list_two)
        lists_three.append(list_three)
    lists_one = intersect(lists_one)
    lists_two = intersect(lists_two)
    lists_three = intersect(lists_three)
    return lists_one, lists_two, lists_three


def union_terms(terms):
    """
    Useful for OU operator : intersect many lists of :
    - diseases
    - indications
    - side effects
    """
    lists_one = []
    lists_two = []
    lists_three = []
    for term in terms:
        list_one, list_two, list_three = search_alt(term)
        lists_one.append(list_one)
        lists_two.append(list_two)
        lists_three.append(list_three)
    lists_one = union(lists_one)
    lists_two = union(lists_two)
    lists_three = union(lists_three)
    return lists_one, lists_two, lists_three


"""load()
debut = time.time()
#print(search("bl*ding"))
#print(search("nausea OU nausea ET headache"))
#print(search("nausea"))
#print("duree : ", time.time() - debut)
print(search("headache OU nausea OU skin rash"))
print("duree : ", time.time() - debut)"""
