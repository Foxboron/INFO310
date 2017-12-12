import csv
import json
from elasticsearch import Elasticsearch

#Remove BOM mark
csvfile = open("C:/Users/Dag Vegard/Documents/enhetsregisteret.csv", mode='r', encoding='utf-8-sig').read()
open("C:/Users/Dag Vegard/Documents/enhetsregisteret.csv", mode='w', encoding='utf-8').write(csvfile)

csvfile = open("C:/Users/Dag Vegard/Documents/enhetsregisteret.csv", "r")

reader = csv.DictReader(csvfile, delimiter=';', quotechar="\"")

i = 0
es = Elasticsearch([{'host': 'velox.vulpes.pw', 'port': 9200, 'timeout': 30}])


# for row in reader:
#     #print(row)
#     print(row["orgnr"])
#     res = es.index(index='testenhetdag', doc_type='enhet', id=row['orgnr'], body=row)
#
#     print(res['created'])
#     i += 1
#
#     if i > 100:
#         break


# res = es.get(index="testenhetdag", doc_type='enhet', id=996901343)
# print(res)

res = es.search(index="testenhetdag", body={
            "query": {
                "match_all": {}
                # "bool": {
                #     "filter": {
                #         "term": {
                #          "organisasjonsform": "ENK"
                #          }}
                # }
            }
        })
for hit in res['hits']['hits']:
    print(hit["_source"])
    # print("%(orgnr)s %(navn)s %(organisasjonsform) s" % hit["_source"])