import requests
import time
import shutil
from indexing import versioning

# while True:
r = requests.get("http://hotell.difi.no/api/json")
r = r.json()

# creating a dict over when the datasets we're working with were last indexed
# in our case, we only have enhetsregisteret
difiLastIndexed = {}
# temp assignment for testing purposes
difiLastIndexed["brreg"] = 0

# Iterating through the difi api to check if datasets have been updated after we indexed them last
for entry in r:
    # for the purposes of this project we only care about brreg
    if entry["shortName"] == "brreg":
            if entry["updated"] > difiLastIndexed["brreg"]:
                download = requests.get("http://hotell.difi.no/download/brreg/enhetsregisteret", stream=True)

                currentUnixTimestamp = time.time()
                currentUnixTimestamp = int(currentUnixTimestamp)
                print(currentUnixTimestamp)

                # folder path currently set to local computer
                folderPath = "C:\\Users\\DagVegard\\Documents\\info310\\brreg"
                fullPath = folderPath + "\\brreg_" + str(currentUnixTimestamp) + ".csv"

                with open(fullPath, "wb") as file:
                    shutil.copyfileobj(download.raw, file)
                print("done copying to file")

                versioning.index_datasett("info310", "brreg", fullPath,
                               lambda x: x['orgnr'])











