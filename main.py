#Flask
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask import Response

#mongoMethods Dependencies
import pymongo
import tellurium
import dns
import oscillatorDB.mongoMethods as mm

#Miscellaneous Packages
from zipfile import ZipFile
import os

#Initializing Flask app and mongoMethods Startup
app = Flask(__name__, static_folder = 'download')
mm.startup()
app.config["FILENAME"] = "download.zip"


#Index Page
@app.route("/")
def index():
    num_nodes = request.args.get("num_nodes", "")
    num_reactions = request.args.get("num_reactions", "")
    oscillator = request.args.get("oscillator", "")
    mass_conserved = request.args.get("mass_conserved", "")

    try:
      num_nodes = int(num_nodes)
      num_reactions = int(num_reactions)
    except ValueError:
      pass

    if oscillator == "osc_yes":
      oscillator_status = True
    elif oscillator == "osc_no":
      oscillator_status = False
    else:
      oscillator_status = -1; #default value when website first loaded

    if mass_conserved == "conserved_yes":
      conserved = True
    elif mass_conserved == "conserved_no":
      conserved = False
    elif mass_conserved == "conserved_NA":
      conserved = -1
    else:
      conserved = -1; #default value when website first loaded

    result = oscillatorDB(num_nodes, num_reactions, oscillator_status, conserved)

    if result[0] == "Done":
      return render_template('download.html', value=result[1])
      #return redirect('/download/' + app.config["FILENAME"])
    elif result == "No entries found":
      return render_template('index.html', value=result[0])
    else:
      return render_template('index.html', value="")
    #return render_template('index.html')

#FIND A WAY TO DELETE THE FILE AFTER DOWNLOADING IT!!


"""
@app.route("/download/<path:filename>", methods = ['GET'])
def download_zipfile(filename):
  return render_template('download.html', value=filename)
"""

  # if '/' in filename or '\\' in filename:
    # abort(404)
  #return send_from_directory(app.static_folder, filename, as_attachment=True)


@app.route("/download/<filename>")
def download_file(filename):
  #filepath = os.path.join(app.static_folder, app.config["FILENAME"])
  #filepath = app.static_folder
  try:
    return send_from_directory(app.static_folder, filename, as_attachment=True)
    #return send_file(file_path, as_attachment=True, attachment_filename="")
  except FileNotFoundError:
    abort(404)

"""
Replace with single endpoint

@app.route("/download/<path:filename>", methods = ['GET'])
def download_zipfile(filename):
  file_path = app.static_folder + filename
  try:
    return send_from_directory(file_path, filename, as_attachment=True)
    #return send_file(file_path, as_attachment=True, attachment_filename="")
  except FileNotFound:
    abort(404)


#Line 32:
  return redirect('/download/' + app.config["FILENAME"])

"""


# @app.route("/delete-files/<filename>")
# def remove_zipfile(filename):
#   try:
#     os.remove(os.path.join(app.static_folder, app.config["FILENAME"]))
#   except Exception as error:
#     pass





#Function to process parameters and create download.zip
def oscillatorDB(num_nodes, num_reactions, oscillator, mass_conserved):

  filepath = os.path.join(app.static_folder, app.config["FILENAME"])
  if os.path.exists(filepath):
    os.remove(filepath)

  def createToZipFile(zipfilename, filename, antimony_model): #simplify by removing zipfilename parameter
    #filepath = os.path.join(app.static_folder, zipfilename)
    with ZipFile(filepath, "a") as zip_file:
      zip_file.writestr(filename, antimony_model)

  

  try:
    if mass_conserved == -1:
      query = { "num_nodes" : num_nodes, "num_reactions" : num_reactions, "oscillator" : oscillator }
    else:
      query = { "num_nodes" : num_nodes, "num_reactions" : num_reactions, "oscillator" : oscillator, "mass_conserved" : mass_conserved }
    #query = { "num_nodes" : num_nodes, "num_reactions" : num_reactions, "oscillator" : oscillator, "mass_conserved" : mass_conserved }
    model_IDS = mm.get_ids(query)



    # createZipFile("download.zip")
    if model_IDS:
      for ID in model_IDS:
        ant = mm.get_antimony({ "ID" : ID })
        filename = str(ID) + ".txt"
        createToZipFile(app.config["FILENAME"], filename, ant) #can simplify by removing first parameter
      return ["Done", app.config["FILENAME"]]
    else:
      return ["No entries found"]

  except ValueError:
    return ["Invalid Input"]

#Flask Development Server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
