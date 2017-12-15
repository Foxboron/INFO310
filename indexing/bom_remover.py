

# Enhetsregisteret comes with a BOM mark which prevents Python processing by default, this module removes it
# No longer seems necessary but included in case examiners run into encoding problems
def remove_bom_from_csv(csvFile):
    csvfile = open(csvFile, mode='r', encoding='utf-8-sig').read()
    open(csvFile, mode='w', encoding='utf-8').write(csvfile)
