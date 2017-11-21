#Remove BOM mark
csvfile = open("C:/Users/Dag Vegard/Documents/enhetsregisteret17_11_17.csv", mode='r', encoding='utf-8-sig').read()
open("C:/Users/Dag Vegard/Documents/enhetsregisteret17_11_17.csv", mode='w', encoding='utf-8').write(csvfile)
