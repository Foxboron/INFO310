import requests
import time
import shutil
import os
import errno
from threading import Thread
from indexing import versioning, bom_remover

# This module is intended to run 24/7 and monitors the Difi API for updated datasets
# when a dataset is found to have been updated since we last indexed it, we re-index it

# creating a dict over when the datasets (for now enhetsregisteret) we're working with were last indexed
difi_last_indexed = {}

# temp assignment for testing purposes
# for practical usage the timestamps for when datasets were last indexed should be stored somewhere
# in case the live monitor is cancelled for whatever reason
difi_last_indexed["brreg"] = 0

while True:
    r = requests.get("http://hotell.difi.no/api/json")
    r = r.json()

    # Iterating through the difi api to check if datasets have been updated after we indexed them last
    for entry in r:
        # for the purposes of this project we only care about brreg
        if entry["shortName"] == "brreg":
            if entry["updated"] > difi_last_indexed["brreg"]:
                download = requests.get("http://hotell.difi.no/download/brreg/enhetsregisteret", stream=True)
                print("Downloading dataset")

                # We use timestamp to differentiate between different versions of the same dataset
                current_unix_timestamp = time.time()
                current_unix_timestamp = int(current_unix_timestamp)

                # folder path for saving datasets currently set to a new folder in
                # the user's home directory (regardless of OS)
                folder_path = os.path.expanduser("~\\difi_differ\\brreg")

                # If the directory doesn't exist we create it
                try:
                    os.makedirs(folder_path)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

                full_path = folder_path + "\\brreg_" + str(current_unix_timestamp) + ".csv"

                print("Copying download to file..")
                with open(full_path, "wb") as file:
                    shutil.copyfileobj(download.raw, file)
                print("Done copying to file")
                print("The dataset can be found at: " + full_path)

                # The datasets come with a BOM which we remove
                bom_remover.remove_bom_from_csv(full_path)
                print("BOM removed")

                # Assign the task of indexing the updated dataset to a new thread
                # so that checking the other datasets in the API can continue without waiting
                worker = Thread(target=versioning.index_datasett, args=("info310", "brreg", full_path,
                                                                        lambda x: x['orgnr']))
                worker.start()

                difi_last_indexed["brreg"] = time.time()

        print("Checking the other datasets continues")
        # TODO need some join/close stuff here?

    # finally sleep 1 hour before checking datasets again
    time.sleep(3600)
