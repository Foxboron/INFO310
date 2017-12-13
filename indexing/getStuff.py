from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 60}])


allCount = es.count(index="info310", body={
            "query": {
                "match_all": {}

            }
        })

print('Count of entire index: ' + str(allCount))

mainCount = es.count(index="info310", doc_type='brreg', body={
            "query": {
                "match_all": {}

            }
        })

print('Count of main doc type: ' + str(mainCount))

versionCount = es.count(index="info310", doc_type='brreg', body={
            "query": {
                "match_all": {}

            }
        })

print('Count of versioning doc type: ' + str(versionCount))

res = es.search(index="info310", doc_type="brreg_versions", size=50, body={
            "query": {
                "match_all": {}

            }
        })
print(res)


c = 0
for hit in res['hits']['hits']:
    if c == 20:
        break
    c += 1
    print(hit["_source"])
    print(hit["_id"])
    print("%(orgnr)s" % hit["_source"])

