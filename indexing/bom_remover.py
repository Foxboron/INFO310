

# Enhetsregisteret comes with a BOM mark which prevents Python processing by default, this class removes it
# TODO csvfile og csvFile ka skjer og kvifor kraesjer det når eg gir dei samme namn? gjoor det i det heile tatt noko?
def remove_bom_from_csv(csvFile):
    csvfile = open(csvFile, mode='r', encoding='utf-8-sig').read()
    open(csvFile, mode='w', encoding='utf-8').write(csvfile)
