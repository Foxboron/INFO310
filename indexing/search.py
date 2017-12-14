from elasticsearch import Elasticsearch


# This module provides simple search output for testing and is not essential to the rest of the system

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

res = es.search(index="info310", doc_type="brreg_versions", size=2000, body={
            "query": {
                "match_all": {}

            }
        })
print(res)

# finn versjonar over 1, for debugging slett
# res = es.search(index="info310", doc_type="brreg", size=50, body={
#    "version" : True
#         })
# print(res)

c = 0
for hit in res['hits']['hits']:
    # if c == 500:
    #     break
    # c += 1
    print(hit["_source"])
    print(hit["_id"])
    # print("version : " + str(hit["_version"]))
    print("%(orgnr)s" % hit["_source"])

