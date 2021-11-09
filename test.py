#mongoMethods Dependencies
import pymongo
import tellurium
import dns
import oscillatorDB.mongoMethods as mm

#Miscellaneous Packages
from zipfile import ZipFile
import os
# import sys
# sys.path.insert(0, './oscillatorDB')


mm.startup()

# def saveToTextFile(filename, antimony_model):
#   with open(filename, "w") as text_file:
#     text_file.write(antimony_model)

# def createZipFile(zipfilename):
#   ZipFile(zipfilename, "w")

# def addToZipFile(zipfilename, file):
#   with ZipFile(zipfilename, "a") as zip_file:
#     zip_file.write(file)
#   os.remove(file)

def createToZipFile(zipfilename, filename, antimony_model):
  subdir = "download"
  filepath = os.path.join(subdir, zipfilename)

  with ZipFile(filepath, "a") as zip_file:
    zip_file.writestr(filename, antimony_model)


num_nodes = 2
num_reactions = 3
oscillator = "osc_yes"
mass_conserved = "conserved_no"

if oscillator == "osc_yes":
  oscillator_status = True
elif oscillator == "osc_no":
  oscillator_status = False

if mass_conserved == "conserved_yes":
  conserved = True
elif mass_conserved == "conserved_no":
  conserved = False


query = { "num_nodes" : int(num_nodes), "num_reactions" : int(num_reactions), "oscillator" : oscillator_status, "mass_conserved" : conserved }
#query = { "num_nodes" : 3, "num_reactions" : 5, "oscillator" : True } #set mass_conserved to false, otherwise no entries found and model_IDS becomes a NoneType
#for some reaon removing mass_conserved parameter from query increases the number of IDS from 1 to 5
model_IDS = mm.get_ids(query)

#createZipFile("download.zip")

if model_IDS:
  for ID in model_IDS:
    ant = mm.get_antimony({ "ID" : ID })
    filename = str(ID) + ".txt"
    createToZipFile("download.zip", filename, ant)
    # saveToTextFile(filename, ant)
    # addToZipFile("download.zip", filename)
else:
  print("No entries found.")


