import requests
import time
import shutil
from threading import Thread
from indexing import versioning, BOMremover

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

                # Remove BOM
                BOMremover.removeBOMFromCSV(fullPath)
                print("BOM removed")

                # Assign the task of indexing the updated dataset to a new thread
                # so that checking the other datasets in the API can continue without waiting
                worker = Thread(target=versioning.index_datasett, args=("info310", "brreg", fullPath,
                               lambda x: x['orgnr']))
                #worker.setDaemon(True)
                worker.start()

    print("Checking the other datasets continues")
                # TODO need some join/close stuff here?


# finally sleep 1 hour
#time.sleep(3600)





