import csv
from elasticsearch import Elasticsearch
from queue import *
from threading import Thread
import datetime
import time


es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])

# Methods for inserting a row into the two doctypes, with a timestamp
def insert_to_main(row, id, index, doctype):
    row["timestamp"] = datetime.datetime.now()
    es.index(index=index, doc_type=doctype, id=id, body=row)


def insert_new_version(row, id, version, index, doctype):
    row["timestamp"] = datetime.datetime.now()
    id = "{}_{}".format(str(id), str(version))
    es.index(index=index, doc_type=doctype, id=id, body=row)


def indexing(row, index, doctype, key):
    # Exception handling for errors related to elastic search not finding the row uploaded to the index
    try:
        res = es.get(index=index, doc_type=doctype, id=key(row))
    except Exception as e:
        # print('Organization not found (probably): ' + str(e))

        print("Handling orgnr: " + str(key(row)))
        insert_to_main(row, key(row), index, doctype)
        insert_new_version(row, key(row), 1, index, doctype + "_versions")
        # print('New org was appended to versionList')
    else:
        # print(repr(res['_source']))
        # print(repr(row))
        # print('equal? ' + str(res['_source'] == row))
        if res['found']:
            # Removing unique timestamps to check equality with already indexed documents
            del res["_source"]["timestamp"]
            if res["_source"] != row:
                print(str(key(row)) + "have changed")
                print('version : ' + str(res['_version']))
                insert_to_main(row, key(row), index, doctype)
                insert_new_version(row, key(row), res['_version'] + 1, index, doctype + "_versions")
            else:
                print(str(row['orgnr']) + ' no change')
        # else:
        # print(str(row['orgnr']) + ' not found - strange because this should cause an ES exception')



# Defines the behavior of threads
def index_loop(input, index, doctype, key):
    while True:
        row = input.get()
        if row == None:
            input.task_done()
            break
        indexing(row, index, doctype, key)
        input.task_done()
    print("thead exited")


# Sets up multithreading and opens a csvfile for indexing
def index_datasett(index, doctype, file, key):
    numOfThreadds = 10
    q = Queue(maxsize=0)

    for i in range(numOfThreadds):
        worker = Thread(target=index_loop, args=(q, index, doctype, key))
        worker.setDaemon(True)
        worker.start()

    csvfile = open(file, "r", encoding="utf-8")
    rows = csv.DictReader(csvfile, delimiter=';', quotechar="\"")

    # Currently we limit the upload to 1000 rows, for testing speed
    i = 0
    for r in rows:
        if i == 1000:
            break
        i += 1
        q.put(r)
    for i in range(numOfThreadds):
        q.put(None)
    q.join()


if __name__ == "__main__":
    tt = time.time()

    es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])

    # keymap = {'brreg': lambda x: x['orgnr']}

    index_datasett("info310", "brreg", "C:/Users/DagVegard/Documents/info310/brreg/enhetsregisteretnovember.csv",
                   lambda x: x['orgnr'])

    print("Took : " + str((time.time() - tt)))

# TODO:
# mulige bugs med versjonnummer? ser ut til å bli inkrementert med 2 i stedet for 1, og når det eigentlig ikkje er
# ny version. Er definitivt ein bug med versjonnummer, sannsynligvis har de med at fleire trådar jobber med samme org?
