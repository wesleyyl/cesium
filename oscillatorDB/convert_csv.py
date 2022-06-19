import json
import csv
with open("/home/hellsbells/projects/oscillator_backup/networks.json") as json_file:
    data = json.load(json_file)


model = data[3358]

csv_file = open("/home/hellsbells/projects/oscillator_backup/networks.csv", "w")

csv_writer = csv.writer(csv_file)
header = model.keys()
csv_writer.writerow(header)

rownum = set()
for i in range(len(data)):
    model = data[i]

    row = []

    for key in header:
        try:
            entry = model[key]
        except:
            entry = None
        row.append(entry)

    rownum.add(len(row))
    csv_writer.writerow(row)

csv_file.close()

json_file.close()

print(rownum)


'''
The problem is that somehow the deleted reactions column is getting separated by the ; and shifts data over 
one column. But not all the time'''