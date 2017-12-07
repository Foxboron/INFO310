# Enhetsregisteret comes with a BOM mark which prevents Python processing by default, this class removes it
csvfile = open("C:/Users/DagVegard/Documents/enhetsregisteret.csv", mode='r', encoding='utf-8-sig').read()
open("C:/Users/DagVegard/Documents/enhetsregisteret.csv", mode='w', encoding='utf-8').write(csvfile)
