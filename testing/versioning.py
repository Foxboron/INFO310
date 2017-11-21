import csv
from elasticsearch import Elasticsearch

csvfile = open('C://users/Dag Vegard/')
csvfile = open("../testdata/test3.csv", "r")

reader = csv.DictReader(csvfile, delimiter=';', quotechar="\"")

rows = list(reader)

# TODO: problemene kjem frå av csv.DictReader() ikkje gir ordna liste, dvs. tilfeldig rekkefoolge, enten finn alternativ
# TODO: med sortert dict, eller proov med random testdata
# TODO: Problem pga iterator over DictReader... list() fikser problemet men tar for mykje minne på einhetsregisteret



es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])

# res = es.search(index="testversioningdag", body={
#             'version': 'true',
#             "query": {
#                'match_all': {}
#             }
#         })

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
i = 0
for rad in rows:
    i += 1
    if i > 999:
        break
    # Exception handling for errors related to elastic search not finding the row uploaded to the index
    try:
        res = es.get(index="testversioningdag", doc_type="testdict", id=rad['orgnr'])

    except Exception as e:
        print('Organization not found (probably): ' + e)
        versionDocList.append(rad)
        versionList[rad['orgnr']] = (str(rad['orgnr']) + '_' + 1)
        print('New org was appended to versionList')
    else:
        print(repr(res['_source']))
        print(repr(rad))
        print('equal? ' + str(res['_source'] == rad))
        if res['found']:
            if res['_source'] != rad:
                print(str(rad['orgnr']) + "have changed")
                versionDocList.append(rad)
                print('version : ' + res['_version'])
                versionList[rad['orgnr']] = (str(rad['orgnr']) + '_' + res['_version'] + 1)
            else:
                print(str(rad['orgnr']) + ' no change')
        else:
            print(str(rad['orgnr']) + ' not found - strange because this should cause an ES exception')

print(len(versionDocList))
print('versionList length: ' + str(len(versionList)))
print(versionList)

print('Checking length of reader after update comparison: ')
totalrows = 0
for row in rows:
    totalrows += 1
print(totalrows)

# Indexing the new document
print('Checkmark for main indexing')
idx = 0
for raad in rows:
    idx += 1
    if idx > 999:
        break
    res = es.index(index="testversioningdag", doc_type="testdict", id=raad['orgnr'], body=raad)
    print("hovedindeks: " + res['result'])

# Indexing altered rows into the versioning document type, in order to store all versions of rows
print('Checkmark for versioning indexing')
for row in versionDocList:
    print(row)
    res = es.index(index='testversioningdag', doc_type='testdict_versions', id=versionList[row['orgnr']], body=row)
    print(res['_version'])
    print(res['_id'])


