from elasticsearch import Elasticsearch

# This module simply deletes the indexed data for testing and is not essential to the rest of the system

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 60}])

res = es.delete_by_query(index="info310", body={
            "query": {
                "match_all": {}
            }
        })
print(res)
