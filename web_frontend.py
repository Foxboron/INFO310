import requests
import json

from collections import OrderedDict

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, redirect, url_for, flash

# Hostname and port for the ElasticSearch instance
HOSTNAME=""
PORT=""


es = Elasticsearch([{'host': HOSTNAME, 'port': PORT}])
app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
app.secret_key=""

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
    e = es.get(index="info310", doc_type=datasett+"_versions", id="{id}_{version}".format(id=id, version=version))
    return [e["_source"]]

def get_diff(datasett, id, version, new_version):
    if version > new_version:
        return {}
    try:
        old = es.get(index="info310", doc_type=datasett+"_versions", id="{id}_{version}".format(id=id, version=version))
        old = old["_source"]

        new = es.get(index="info310", doc_type=datasett+"_versions", id="{id}_{version}".format(id=id, version=new_version))
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
    r = requests.get("http://hotell.difi.no/api/json/brreg/enhetsregisteret/fields")
    fields = [i["shortName"] for i in r.json()]
    e = es.search(index="info310", doc_type="brreg", version=True, body={
        "query": {
            "multi_match": {
                "query": string,
                "fields": fields, 
                "fuzziness": "AUTO"
                }
            }
        })
    return e

@app.route("/search/<string>")
@json_response
def search_results(string):
    e = search(string)
    return e


def get_indexes():
    res = es.search(index="info310", body={
        "aggs": {
            "typesAgg": {
                "terms": {
                    "field": "_type",
                    "size": 200
                    }
                }
            },
        "size": 0
        })
    return [i["key"] for i in res["aggregations"]["typesAgg"]["buckets"] if "_versions" not in i["key"]]

def get_histogram(data=None):
    indexes = [data]
    if not data:
        indexes = get_indexes()
    aggs = {
            "query": {
                "terms": {
                    "_type": indexes
                    },
                },
            "aggs" : {
                "date_over_time" : {
                    "date_histogram" : {
                        "field" : "timestamp",
                        "interval" : "1D",
                        "format" : "yyyy-MM-dd",
                        "keyed": True
                        }
                    }
                }
            }
    res = es.search(index="info310", size=0, body=aggs) 
    bucket = res["aggregations"]["date_over_time"]["buckets"]
    data = [[],[]]
    for v in bucket.values():
        data[0].append(v["key_as_string"])
        data[1].append(v["doc_count"])
    return data

@app.route("/histogram", defaults={'data': None}, methods=["POST", "GET"])
@app.route("/histogram/<data>", methods=["POST", "GET"])
def get_history(data):
    data = get_histogram(data=data)
    return json.dumps(data, indent=2, sort_keys=False), 200, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/")
def index():
    data = get_histogram()
    res = get_indexes()
    return render_template("index.html", datasets=res, graph=data)

@app.route("/search", methods=["POST", "GET"])
def search_es():
    e = search(request.form.get("search"))
    return render_template("tabell++.html", result=e["hits"]["hits"])

@app.route("/choose/<datasett>/<id>")
def choose_row(datasett, id):
    new = es.get(index="info310", doc_type=datasett, id="{id}".format(id=id))
    return render_template("org.html", result=new)

@app.route("/diff/<datasett>/<id>", methods=["POST", "GET"])
def diff_rows(datasett, id):
    data = get_histogram(data=datasett)
    versions = list(request.form)
    if len(versions) == 2:
        l = get_diff(datasett, id, versions[0], versions[1])
        return render_template("compare.html", results=l, graph=data)
    return render_template("compare.html", results=[], graph=data)

@app.route("/items", methods=["POST", "GET"])
def get_items():
    res = es.search(index="info310", body={
        "aggs": {
            "typesAgg": {
                "terms": {
                    "field": "_type",
                    "size": 200
                    }
                }
            },
        "size": 0})
    return json.dumps(res, indent=2, sort_keys=False), 200, {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True)
