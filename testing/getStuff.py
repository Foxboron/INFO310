from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 60}])


allCount = es.count(index="testversioningdag", body={
            "query": {
                "match_all": {}

            }
        })

print('Count of entire index: ' + str(allCount))

mainCount = es.count(index="testversioningdag", doc_type='testdict', body={
            "query": {
                "match_all": {}

            }
        })

print('Count of main doc type: ' + str(mainCount))

versionCount = es.count(index="testversioningdag", doc_type='testdictversions', body={
            "query": {
                "match_all": {}

            }
        })

print('Count of versioning doc type: ' + str(versionCount))

res = es.search(index="testversioningdag", doc_type="testdictversions", size=50, body={
            "query": {
                "match_all": {}

            }
        })
print(res)
for hit in res['hits']['hits']:
    print(hit["_source"])
    print(hit["_id"])
    print("%(orgnr)s %(Name) s" % hit["_source"])