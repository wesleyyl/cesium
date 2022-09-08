#Flask Packages
from flask import Flask, request, render_template, url_for, send_file, Response
#from flask import redirect, make_response, send_from_directory

#mongoMethods Dependencies
import pymongo
import tellurium
import dns
import oscillatorDB.mongoMethods as mm

#Miscellaneous Packages
from zipfile import ZipFile
from io import BytesIO
import os
import json #to convert string to dictionary
import random #for filename
# import base64


#Initializing Flask app and mongoMethods Startup
app = Flask(__name__, static_folder = 'static')
# mm.startup()



#Index Page
@app.route("/")
def index():
    types = mm.get_model_types()
    return render_template('index.html', types=types)

#Download Transition Page
# 
# This route will take form data and convert parameters into a query dictionary.
# 
@app.route("/download", methods = ['GET', 'POST'])
def download():
  if request.method == 'GET':
      error = "No query submitted. Please submit a query from the home page."
      return render_template('error.html', error_msg=error)

  elif request.method == 'POST':
    
    #Retrieve Form Data
    form_data = request.form #this is a dictionary w/ keys & values

    modelType = form_data.get("mtype")
    numSpecies = form_data.get("numSpecies")
    numReactions = form_data.get("numReactions")
    autocatalysis = form_data.get("autocat")
    degradation = form_data.get("degrade")
    telSimulatable = "isSimulatable" in form_data

    if numSpecies != "": #numSpecies is not None
      numSpecies = int(numSpecies)
    else:
      numSpecies = None

    if numReactions != "": #why doesn't it default to None if no values found?!
      numReactions = int(numReactions)
    else:
      numReactions = None


    #IF AUTOCATALYSIS LEFT EMPTY IT DEFAULTS TO NONE
    if autocatalysis == "autocat_yes":
      autocatalysis = True
    elif autocatalysis == "autocat_no":
      autocatalysis = False
    else:
      autocatalysis = None

    #IF DEGRADATION LEFT EMPTY IT DEFAULTS TO NONE
    if degradation == "degrade_yes":
      degradation = True
    elif degradation == "degrade_no":
      degradation = False
    else:
      degradation = None

    queryParam = {
      'type' : modelType,
      'species' : numSpecies,
      'reac' : numReactions,
      'autocat' : autocatalysis,
      'degrade' : degradation,
      'simulatable' : telSimulatable
    }


    #DEBUG CODE: TO LOAD PAGE WITH QUERY VALUES UNDERNEATH
    if cesiumQueryExists(queryParam) > 0:
      return render_template('download.html', query=queryParam, queryJSON=json.dumps(queryParam), numModels=cesiumQueryExists(queryParam))
    elif cesiumQueryExists(queryParam) == 0:
      error = "No models found. Please try a different query."
      return render_template('error.html', error_msg=error)
    else:
      error = "Invalid inputs. Please try again."
      return render_template('error.html', error_msg=error)

    #DEBUG CODE: TO CHECK THAT VALUES ARE ACTUALLY GOING THROUGH
    # return form_data


#Download File Page
@app.route("/download/<query>")
def download_file(query):
  query = json.loads(query)

  numModels = cesiumQueryExists(query)

  if numModels == 1:
    filename = singleID(query)

  else:
    randInt = random.randint(1000000, 9999999)
    filename = "{}.zip".format("cesium-models-" + str(numModels) + "-" + str(randInt))

  cesiumZip = cesiumQuery(query)

  return send_file(cesiumZip, download_name=filename, as_attachment=True)

  # return send_file(cesiumZip, attachment_filename=filename, as_attachment=True)


#About Page
@app.route("/about")
def about():
  return render_template('about.html')


# #FAQ Page
# @app.route("/faq")
# def faq():
#   return render_template('faq.html')


#Returns number of models in query if it exists. Otherwise it returns 0.
def cesiumQueryExists(query):

  dbquery = { "modelType" : query["type"], "numSpecies" : query["species"], "numReactions" : query["reac"], "Autcatalysis Present": query["autocat"], "Autodegradation Present": query["degrade"] }

  for key in list(dbquery.keys()):
    if dbquery[key] is None:
      del dbquery[key]

  model_IDS = mm.get_ids(dbquery)

  if model_IDS:
    return len(model_IDS)
  else:
    return 0

def cesiumQuery(query):

  dbquery = { "modelType" : query["type"], "numSpecies" : query["species"], "numReactions" : query["reac"], "Autcatalysis Present": query["autocat"], "Autodegradation Present": query["degrade"] }

  for key in list(dbquery.keys()):
    if dbquery[key] is None:
      del dbquery[key]
  model_IDS = mm.get_ids(dbquery)
  

  # Generate Single Text File
  if len(model_IDS) == 1:
    antStr = mm.get_antimony({ "ID" : model_IDS[0] })
    # filename = str(model_IDS[0]) + ".txt"

    if query["simulatable"]:
      telStr = "import tellurium as te\n\nr = te.loada('''\n" + antStr + "\n''')\n\nm = r.simulate(0, 2, 400)\nr.plot()"
      memTxtFile = BytesIO(bytes(telStr, encoding='utf-8'))
    else:
      memTxtFile = BytesIO(bytes(antStr, encoding='utf-8'))

    memTxtFile.seek(0)
    return memTxtFile

  # Generate Zip File with all Text Files
  elif model_IDS:
    memZipFile = BytesIO()
    with ZipFile(memZipFile, "w") as zipF:
      for ID in model_IDS:
        antStr = mm.get_antimony({ "ID" : ID })
        txtFilename = str(ID) + ".txt"
        if query["simulatable"]:
          telStr = "import tellurium as te\n\nr = te.loada('''\n" + antStr + "\n''')\n\nm = r.simulate(0, 2, 400)\nr.plot()"
          zipF.writestr(txtFilename, telStr)
        else:
          zipF.writestr(txtFilename, antStr)

    memZipFile.seek(0)
    return memZipFile

  else:
    return None


# Returns ID for queries with only one model
def singleID(query):
  dbquery = { "modelType" : query["type"], "numSpecies" : query["species"], "numReactions" : query["reac"], "Autcatalysis Present": query["autocat"], "Autodegradation Present": query["degrade"] }
  model_IDS = mm.get_ids(dbquery)
  filename = str(model_IDS[0]) + ".txt"
  return filename



#Flask Development Server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
