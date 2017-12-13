import csv
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 60}])

res = es.delete_by_query(index="info310", body={
            "query": {
                "match_all": {}
            }
        })
print(res)