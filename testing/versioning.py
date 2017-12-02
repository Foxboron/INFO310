import csv
from elasticsearch import Elasticsearch


csvfile = open("../testdata/test2.csv", "r")
reader = csv.DictReader(csvfile, delimiter=';', quotechar="\"")

rows = list(reader)

# TODO: problemene kjem frå av csv.DictReader() ikkje gir ordna liste, dvs. tilfeldig rekkefoolge, enten finn alternativ
# TODO: med sortert dict, eller proov med random testdata
# TODO: Problem pga iterator over DictReader... list() fikser problemet men tar for mykje minne på einhetsregisteret
# TODO: Split into different files, at least a logger class?...

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])

versionDocList = []
versionList = {}

# Comparing the new document being indexed against the already indexed document,
# to detect rows that have been altered
print('Checking length of reader before update comparison: ')
totalrows = 0
for row in rows:
    totalrows += 1
print(totalrows)
print('Checkmark for update comparison')
def compareInputAgainstOldData(input, versionDocList, versionList, index, doctype):
    for row in input:
        # Exception handling for errors related to elastic search not finding the row uploaded to the index
        try:
            res = es.get(index=index, doc_type=doctype, id=row['orgnr'])

        except Exception as e:
            print('Organization not found (probably): ' + str(e))
            versionDocList.append(row)
            versionList[row['orgnr']] = (str(row['orgnr']) + '_' + str(1))
            print('New org was appended to versionList')
        else:
            print(repr(res['_source']))
            print(repr(row))
            print('equal? ' + str(res['_source'] == row))
            if res['found']:
                if res['_source'] != row:
                    print(str(row['orgnr']) + "have changed")
                    versionDocList.append(row)
                    print('version : ' + str(res['_version']))
                    versionList[row['orgnr']] = (str(row['orgnr']) + '_' + str(res['_version'] + 1))
                else:
                    print(str(row['orgnr']) + ' no change')
            else:
                print(str(row['orgnr']) + ' not found - strange because this should cause an ES exception')


compareInputAgainstOldData(rows, versionDocList, versionList, 'testversioningdag', 'testdict')

print('versionDocList length: ' + str(len(versionDocList)))
print('versionList length: ' + str(len(versionList)))
print(versionList)

print('Checking length of reader after update comparison: ')
totalrows = 0
for rad in rows:
    totalrows += 1
print(totalrows)

# Indexing the new document
def indexIntoMainIndex(input, index, doctype):
    print('Checkmark for main indexing')
    for row in input:
        res = es.index(index=index, doc_type=doctype, id=row['orgnr'], body=row)
        print("Main Index updated?: " + res['result'])


indexIntoMainIndex(rows, 'testversioningdag', 'testdict')

# Indexing altered rows into the versioning document type, in order to store all versions of rows
def indexIntoVersioningIndex(input, versionList, index, doctype):
    print('Checkmark for versioning indexing')
    for row in input:
        print(row)
        res = es.index(index=index, doc_type=doctype, id=versionList[row['orgnr']], body=row)
        print(res['_version'])
        print(res['_id'])


indexIntoVersioningIndex(versionDocList, versionList,'testversioningdag', 'testdictversions')






