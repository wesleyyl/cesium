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
app = Flask(__name__, static_folder = 'static')
mm.startup()
app.config["DOWNLOAD_FOLDER"] = 'download'
app.config["FILENAME"] = "download.zip"


#Index Page
@app.route("/")
def index():
    num_nodes = request.args.get("num_nodes", "")
    num_reactions = request.args.get("num_reactions", "")
    oscillator = request.args.get("oscillator", "")
    autocatalysis = request.args.get("autocatalysis", "")
    degradation = request.args.get("degradation", "")

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

    result = oscillatorDB(num_nodes, num_reactions, oscillator_status)

    if result[0] == "Done":
      return render_template('download.html', value=result[1])
      #return redirect('/download/' + app.config["FILENAME"])
    elif result == "No entries found":
      return render_template('index.html', value=result[0])
    else:
      return render_template('index.html', value="")


@app.route("/download/<filename>")
def download_file(filename):
  #filepath = os.path.join(app.static_folder, app.config["FILENAME"])
  #filepath = app.static_folder

  filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["FILENAME"])
  
  # @app.after_request
  # def delete_file(response):
  #   try:
  #     os.remove(filepath)
  #   except Exception as error:
  #     app.logger.error("Error removing downloaded file handle", error)
  #   return response

  try:
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename, as_attachment=True)
  except FileNotFoundError:
    abort(404)



#Function to process parameters and create download.zip
def oscillatorDB(num_nodes, num_reactions, oscillator):

  filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["FILENAME"])
  if os.path.exists(filepath):
    os.remove(filepath)

  def createToZipFile(zipfilename, filename, antimony_model): #simplify by removing zipfilename parameter
    with ZipFile(filepath, "a") as zip_file:
      zip_file.writestr(filename, antimony_model)


  try:
    query = { "num_nodes" : num_nodes, "num_reactions" : num_reactions, "oscillator" : oscillator }
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
