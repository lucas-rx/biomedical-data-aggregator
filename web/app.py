import time

import flask
from flask import render_template, Flask, request, redirect, url_for

import pysparkApp
app = Flask(__name__)

loading = True

@app.route('/')
def index():
    global loading
    is_loaded = loading
    loading = False
    return render_template('home.jinja2', results={"disease": {}, "side_effect": {}, "drug": {}}, load=is_loaded)

@app.route('/load_drugbank')
def load_drugbank():
    time_start = time.time()
    pysparkApp.load_drugbank()
    time_end = time.time()
    print("Time load drugbank : ", time_end-time_start)
    return {}

@app.route('/load_omim')
def load_omim():
    time_start = time.time()
    pysparkApp.load_omim()
    time_end = time.time()
    print("Time load omim : ", time_end-time_start)
    return {}

@app.route('/load_meddra')
def load_meddra():
    time_start = time.time()
    pysparkApp.load_meddra()
    time_end = time.time()
    print("Time load meddra : ", time_end-time_start)
    return {}

@app.route('/load_stitch')
def load_stitch():
    time_start = time.time()
    pysparkApp.load_stitch()
    time_end = time.time()
    print("Time load stitch : ", time_end-time_start)
    return {}

@app.route('/load_atc')
def load_atc():
    time_start = time.time()
    pysparkApp.load_atc()
    time_end = time.time()
    print("Time load atc : ", time_end-time_start)
    return {}

@app.route('/load_hpo')
def load_hpo():
    time_start = time.time()
    pysparkApp.load_hpo()
    time_end = time.time()
    print("Time load hpo : ", time_end-time_start)
    return {}



@app.route('/search/', methods=['GET', 'POST'])
def search():
    if loading:
        return redirect('/')
    symptoms = None
    if request.method == 'POST':
        symptoms = flask.request.form['symptoms']
    if symptoms is None:
        return redirect('/')
    start = time.time()
    search_res = pysparkApp.search(symptoms)
    time_search = time.time() - start
    print("Time : ", time_search)
    results = {"disease": search_res[0], "side_effect": search_res[1], "drug": search_res[2]}
    print(results)
    result = {}
    for key, values in results.items():
        result[key] = {}
        for term, count in values.items():
            name = term[0]
            if name not in result[key]:
                result[key][name] = []
            result[key][name].append((term[1], count))
    for key in result:
        for name, occurrences in result[key].items():
            result[key][name] = sorted(occurrences, key=lambda x: x[1], reverse=True)
        result[key] = dict(sorted(result[key].items(), key=lambda x: sum([occurrence[1] for occurrence in x[1]]), reverse=True))
    return render_template('home.jinja2', results=result, symptoms=symptoms, nb_disease=len(result["disease"]), nb_side_effect=len(result["side_effect"]), nb_drug=len(result["drug"]))


if __name__ == '__main__':
    app.run(debug=True)
