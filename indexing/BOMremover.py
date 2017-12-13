

# Enhetsregisteret comes with a BOM mark which prevents Python processing by default, this class removes it
def removeBOMFromCSV(csvFile):
    csvfile = open(csvFile, mode='r', encoding='utf-8-sig').read()
    open(csvFile, mode='w', encoding='utf-8').write(csvfile)
