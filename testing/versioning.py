import csv
from elasticsearch import Elasticsearch
from queue import *
from threading import Thread
import time

tt = time.time()


es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])




def insert_to_main(row, id, index, doctype):
    res = es.index(index=index, doc_type=doctype, id=id, body=row)

def insert_new_version(row, id, version, index, doctype):
    id = "{}_{}".format(str(id), str(version))
    print(id)
    res = es.index(index=index, doc_type=doctype, id=id, body=row)


def indexing(row, index, doctype):
    # Exception handling for errors related to elastic search not finding the row uploaded to the index
    try:
        res = es.get(index=index, doc_type=doctype, id=row['orgnr'])
    except Exception as e:
        print('Organization not found (probably): ' + str(e))
        insert_to_main(row, row["orgnr"], "testversioningdag", "testdict")
        insert_new_version(row, row["orgnr"], 1, "testversioningdag", "testdictversions")
        print('New org was appended to versionList')
    else:
        print(repr(res['_source']))
        print(repr(row))
        print('equal? ' + str(res['_source'] == row))
        if res['found']:
            if res['_source'] != row:
                print(str(row['orgnr']) + "have changed")
                print('version : ' + str(res['_version']))
                insert_to_main(row, row["orgnr"], "testversioningdag" "testdict")
                insert_new_version(row, row["orgnr"], res['_version']+1, "testversioningdag", "testdictversions")
            else:
                print(str(row['orgnr']) + ' no change')
        else:
            print(str(row['orgnr']) + ' not found - strange because this should cause an ES exception')


# Indexing the new document
def indexIntoMainIndex(input, index, doctype):
    print('Checkmark for main indexing')
    while True:
        row = input.get()
        if row == None:
            input.task_done()
            break
        indexing(row, "testversioningdag", "testdict")
        # Version index: testdict_version
        print("Main Index updated?: Probably")
        input.task_done()
    print("thead exited")


# Setting up multithreading via queues
numOfThreadds = 10
q = Queue(maxsize=0)

# maa eg skriva om all koden slik at det faktisk er ein queue av rows??
for i in range(numOfThreadds):
    worker = Thread(target=indexIntoMainIndex, args=(q, "testversioningdag", "testdict"))
    worker.setDaemon(True)
    worker.start()

csvfile = open("C:/Users/DagVegard/Documents/enhetsregisteretkanskje17_10_17.csv", "r", encoding="utf-8")
reader = csv.DictReader(csvfile, delimiter=';', quotechar="\"")

# rows = list(reader)
rows = reader

i = 0
for r in rows:
    if i == 1000:
        break
    i += 1
    # indexing(r, "testversioningdag", "testdict")
    q.put(r)



# Finally add a sentinel value to prevent blocking TODO revider this comment lol
for i in range(numOfThreadds):
    q.put(None)
print("Done converting dictreader to queue")

print("Putting rows into queue worked probably")
print("Queue size: " + str(q.qsize()))
# Historiske problem... :
#  problemene kjem frå av csv.DictReader() ikkje gir ordna liste, dvs. tilfeldig rekkefoolge, enten finn alternativ
#  med sortert dict, eller proov med random testdata
#  Problem pga iterator over DictReader... list() fikser problemet men tar for mykje minne på einhetsregisteret
#  Split into different files, at least a logger class?...
#
q.join()
print("Multithreading finished?")




# compareInputAgainstOldData(rows, versionDocList, versionList, 'testversioningdag', 'testdict')
# indexIntoMainIndex(rows, 'testversioningdag', 'testdict')
# indexIntoVersioningIndex(versionDocList, versionList,'testversioningdag', 'testdictversions')

print(time.time()-tt)

