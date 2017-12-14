import requests
import time
import shutil
import os
import errno
from threading import Thread
from indexing import versioning, BOMremover

# This module is intended to run 24/7 and monitors the Difi API for updated datasets
# when a dataset is found to have been updated since we last indexed it, we re-index it

# todo FIX lastIndexed til noko skikkelig... må lagra til fil muligens?

while True:
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

                # We use timestamp to differentiate between different versions of the same dataset
                currentUnixTimestamp = time.time()
                currentUnixTimestamp = int(currentUnixTimestamp)
                print(currentUnixTimestamp)

                # folder path for saving datasets currently set to working directory,
                # but not included in the delivery archive
                folderPath = os.path.expanduser("~\\difi_differ\\brreg")

                # If the directory doesn't exist we create it
                try:
                    os.makedirs(folderPath)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

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
                # worker.setDaemon(True)
                worker.start()

        print("Checking the other datasets continues")
        # TODO need some join/close stuff here?

    # finally sleep 1 hour
    time.sleep(3600)
