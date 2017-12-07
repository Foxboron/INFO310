from flask import Flask, render_template, request, redirect, url_for, flash
from collections import OrderedDict
from elasticsearch import Elasticsearch

import json

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200}])
app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.secret_key="LOLKEKSECURE"

def json_response(func):
    from functools import wraps

    @wraps(func)
    def wrapped(*args, **kwargs):
        response = func(*args, **kwargs)
        jsons = response
        if isinstance(response, list):
            jsons = []
            for result in response:
                jsons.append(OrderedDict(sorted(result.items(), key=lambda t: t[0])))
        dump = json.dumps(jsons, indent=2, sort_keys=False)
        return dump, 200, {'Content-Type': 'application/json; charset=utf-8'}
    return wrapped


@app.route("/version/<datasett>/<id>/<version>")
@json_response
def get_version(datasett, id, version):
    e = es.get(index="testversioningdag", doc_type=datasett+"versions", id="{id}_{version}".format(id=id, version=version))
    return [e["_source"]]

def get_diff(datasett, id, version, new_version):
    if version > new_version:
        return "Lolfeil"
    try:
        old = es.get(index="testversioningdag", doc_type=datasett+"versions", id="{id}_{version}".format(id=id, version=version))
        old = old["_source"]

        new = es.get(index="testversioningdag", doc_type=datasett+"versions", id="{id}_{version}".format(id=id, version=new_version))
        new = new["_source"]
    except Exception as e:
        return {}


    ret = {"old": old,
            "new": new,
            "diff": {}
            }
    for key in old.keys() & new.keys():
        if old[key] != new[key]:
            ret["diff"][key] = [old[key], new[key]]
    return ret


@app.route("/version/<datasett>/<id>/<version>/diff/<new_version>")
@json_response
def diff_versions(datasett, id, version, new_version):
    return get_diff(datasett, id, version, new_version)


def search(string):
    e = es.search(index="testversioningdag", doc_type="testdict", version=True, body={
            "query": {
                "multi_match": {
                        "query": string,
                        "fields": ["orgnr", "name", "Antall_ansatte", "Version"],
                        "fuzziness": "AUTO"
                    }
                }
            })
    return e

@app.route("/search/<string>")
@json_response
def search_results(string):
    e = search(string)
    return e["hits"]["hits"]


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search_es():
    e = search(request.form.get("search"))
    return render_template("tabell++.html", result=e["hits"]["hits"])

@app.route("/choose/<datasett>/<id>")
def choose_row(datasett, id):
    new = es.get(index="testversioningdag", doc_type=datasett, id="{id}".format(id=id))
    return render_template("org.html", result=new)

@app.route("/diff/<datasett>/<id>", methods=["POST", "GET"])
def diff_rows(datasett, id):
    versions = list(request.form)
    if len(versions) == 2:
        l = get_diff(datasett, id, versions[0], versions[1])
        return render_template("compare.html", results=l)
    return render_template("compare.html", results=[])

@app.route("/histogram", methods=["POST", "GET"])
def get_history():
    aggs = {
    "aggs" : {
        "date_over_time" : {
            "date_histogram" : {
                "field" : "date",
                "interval" : "1D",
                "format" : "yyyy-MM-dd",
                "keyed": True
            }
        }
    }
}
    res = es.search(index="testversioningdag", body=aggs)

    return json.dumps(res, indent=2, sort_keys=False), 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True)
