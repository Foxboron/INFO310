import csv
from elasticsearch import Elasticsearch
from queue import *
from threading import Thread
import datetime
import time
import requests

tt = time.time()



es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])




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
        insert_to_main(row, key(row), index, doctype)
        insert_new_version(row, key(row), 1, index, doctype+"_versions")
        # print('New org was appended to versionList')
    else:
        # print(repr(res['_source']))
        # print(repr(row))
        # print('equal? ' + str(res['_source'] == row))
        if res['found']:
            if res['_source'] != row:
                print(str(key(row)) + "have changed")
                print('version : ' + str(res['_version']))
                insert_to_main(row, key(row), index, doctype)
                insert_new_version(row, key(row), res['_version']+1, index, doctype+"_versions")
            # else:
                # print(str(row['orgnr']) + ' no change')
        # else:
            # print(str(row['orgnr']) + ' not found - strange because this should cause an ES exception')


# Indexing the new document
def indexIntoMainIndex(input, index, doctype, key):
    print('Checkmark for main indexing')
    while True:
        row = input.get()
        if row == None:
            input.task_done()
            break
        indexing(row, index, doctype, key)
        # Version index: testdict_version
        # print("Main Index updated?: Probably")
        input.task_done()
    print("thead exited")


def index_datasett(index, doctype, file, key):
    numOfThreadds = 10
    q = Queue(maxsize=0)

    for i in range(numOfThreadds):
        worker = Thread(target=indexIntoMainIndex, args=(q, index, doctype, key))
        worker.setDaemon(True)
        worker.start()

    csvfile = open(file, "r", encoding="utf-8")
    rows = csv.DictReader(csvfile, delimiter=';', quotechar="\"")
    i = 0
    for r in rows:
        if i == 10000:
            break
        i += 1
        q.put(r)
    for i in range(numOfThreadds):
        q.put(None)
    q.join()


# keymap = {'brreg': lambda x: x['orgnr']}

#index_datasett("info310", "brreg", "C:/Users/DagVegard/Documents/enhetsregistereteistundsiden.csv", lambda x: x['orgnr'])

print("Took : " + str((time.time()-tt)))
# todo: lek med apiet til Morten, sjekk siste oppdaterte tidspunkt og indekser om det er brreg og er seinare enn indeksering