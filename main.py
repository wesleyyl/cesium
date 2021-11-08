#Flask
from flask import Flask, request, render_template
from flask import Response

#mongoMethods Dependencies
import pymongo
import tellurium
import dns

#Miscellaneous Packages
from zipfile import ZipFile
import sys
sys.path.insert(0, './oscillatorDB')
import oscillatorDB.mongoMethods as mm

#Creating Flask app and mongoMethods Startup
app = Flask(__name__)
mm.startup()

#Index Page
@app.route("/")
def index():
    num_nodes = request.args.get("num_nodes", "")
    num_reactions = request.args.get("num_reactions", "")
    oscillator = request.args.get("oscillator", "")
    mass_conserved = request.args.get("mass_conserved", "")

    if oscillator == "osc_yes":
      oscillator_status = True
    elif oscillator == "osc_no":
      oscillator_status = False

    if mass_conserved == "conserved_yes":
      conserved = True
    elif mass_conserved == "conserved_no":
      conserved = False

    query = { "num_nodes" : int(num_nodes), "num_reactions" : int(num_reactions), "oscillator" : oscillator_status, "mass_conserved" : conserved }
    model_IDS = mm.get_ids(query)

    for ID in model_IDS:
      antimony = mm.get_antimony({ "ID" : ID })
      filename = String(ID) + ".txt"
      saveToTextFile(filename, antimony)
      createZipFile("download.zip", filename)


    return render_template('index.html')


def saveToTextFile(filename, antimony_model):
  with open(filename, "w") as text_file:
    text_file.write(antimony_model)

def createZipFile(zipfilename, file):
  with ZipFile(zipfilename, "w") as zip_file:
    zip_file.write(file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
