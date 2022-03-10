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
# import base64


#Initializing Flask app and mongoMethods Startup
app = Flask(__name__, static_folder = 'static')
mm.startup()


#Config Values
app.config["DOWNLOAD_FOLDER"] = 'download'
app.config["ZIPF_NAME"] = "download.zip"


#Index Page
@app.route("/")
def index():
    return render_template('index.html')

#Download Transition Page
# 
# This route will take form data and convert parameters into a query dictionary.
# 
@app.route("/download", methods = ['GET', 'POST'])
def download():
  if request.method == 'GET':
      error = "No query data submitted. Please submit query data through the form page."
      return render_template('error.html', error_msg=error) #ADD A PAGE THAT REDIRECTS BACK TO THE HOME PAGE (html page)

      #return "No data submitted. Please submit query data through the form."
      

  elif request.method == 'POST':
    form_data = request.form #this is a dictionary w/ keys & values

    num_nodes = int(form_data.get("num_nodes"))
    num_reactions = int(form_data.get("num_reactions"))
    oscillator = form_data.get("oscillator")
    autocatalysis = form_data.get("autocat")
    degradation = form_data.get("degrade")

    # try:
    #   num_nodes = int(num_nodes)
    #   num_reactions = int(num_reactions)
    # except ValueError:
    #   pass


    #CONVERTS HTML FORM VALUES TO BOOLEAN
    if oscillator == "osc_yes":
      oscillator_status = True
    elif oscillator == "osc_no":
      oscillator_status = False
    else:
      oscillator_status = False

    #IF AUTOCATALYSIS LEFT EMPTY IT DEFAULTS TO NO!
    if autocatalysis == "Y/N":
      autocatalysis = False

    #IF DEGRADATION LEFT EMPTY IT DEFAULTS TO NO!
    if degradation == "Y/N":
      degradation = False

    queryParam = {
      'nodes' : num_nodes,
      'reac' : num_reactions,
      'osc' : oscillator_status,
      'autocat' : autocatalysis,
      'degrade' : degradation
    }

    # cesiumZip = cesiumQuery(queryParam)

    # encoded_zipF = base64.b64encode(cesiumZip.getvalue())


    #DEBUG CODE: TO LOAD PAGE WITH QUERY VALUES UNDERNEATH
    if cesiumQueryExists(queryParam):
      return render_template('download.html', query=json.dumps(queryParam))
    elif not cesiumQueryExists(queryParam):
      error = "No models found. Please try a different query."
      return render_template('error.html', error_msg=error)
    elif status == -1:
      error = "Invalid inputs. Please try again."
      return render_template('error.html', error_msg=error)

    #DEBUG CODE: TO CHECK THAT VALUES ARE ACTUALLY GOING THROUGH
    # return form_data
    #DEBUG CODE: TO CHECK THAT SPECIFIC VALUE IS CORRECT
    # return str(num_nodes)


#Download File Page
@app.route("/download/<query>")
def download_file(query):
  # filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["ZIPF_NAME"])
  filename = app.config["ZIPF_NAME"]
  
  # return query

  cesiumZip = cesiumQuery(json.loads(query))

  return send_file(cesiumZip, attachment_filename=filename, as_attachment=True)

  # try:

    #Method 1
    # with open(filepath, 'rb') as zipFile:
    #   data = zipFile.readlines()
    # os.remove(filepath)
    # 
    # return Response(data, headers={
    #   'Content-Type': 'application/zip',
    #   'Content-Disposition': 'attachment; filename=%s;' % app.config["ZIPF_NAME"]
    #   })


    #Method 2
    # response = make_response(file.read())
    # response.headers.set('Content-Type', 'zip')
    # response.headers.set('Content-Disposition', 'attachment', filename='%s.zip' % app.config["ZIPF_NAME"])

    # return response



    #Method 3
    # return Response(file, mimetype='application/zip', headers={'Content-Disposition': 'attachment;filename={}'.format(filename)})


    #Method 4
    # return send_file(cesiumZip, attachment_filename=app.config["ZIPF_NAME"], as_attachment=True)
  # except FileNotFoundError:
  #   abort(404)


#About Page
@app.route("/about")
def about():
  return render_template('about.html')


#FAQ Page
@app.route("/faq")
def faq():
  return render_template('faq.html')


def cesiumQueryExists(query):
  query = { "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"] }
  model_IDS = mm.get_ids(query)

  if model_IDS:
    return True
  else:
    return False

def cesiumQuery(query):

  # filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["ZIPF_NAME"])

  query = { "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"] }
  model_IDS = mm.get_ids(query)
  
  if model_IDS:
    memZipFile = BytesIO()
    with ZipFile(memZipFile, "w") as zipF:
      for ID in model_IDS:
        antStr = mm.get_antimony({ "ID" : ID })
        txtFilename = str(ID) + ".txt"
        zipF.writestr(txtFilename, antStr)
    memZipFile.seek(0)

    return memZipFile

        
  else:
    return None


# def createTextFile(antStr, txtFileName):
#   txtFile = io.BytesIO()
#   with open(txtFileName, "wb") as txtF:
#     txtF.write(antStr)



# def addToZip(memZip, txtFileName, antStr): #simplify by removing zipfilename parameter
#     with zipfile.ZipFile(zip, "w", zipfile.ZIP_DEFLATED) as zipF:
#       zipF.writestr(txtFileName, antStr)








#Function to process parameters and create download.zip
# 
# return -1: invalid inputs (fix later with form validation features)
# return 0: no models found using that query
# return 1: query successful
# 
# def oscillatorDB(num_nodes, num_reactions, oscillator):

#   filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["FILENAME"])
#   if os.path.exists(filepath):
#     os.remove(filepath)

#   def createToZipFile(zipfilename, filename, antimony_model): #simplify by removing zipfilename parameter
#     with ZipFile(filepath, "a") as zip_file:
#       zip_file.writestr(filename, antimony_model)


#   try:
#     query = { "num_nodes" : num_nodes, "num_reactions" : num_reactions, "oscillator" : oscillator }
#     model_IDS = mm.get_ids(query)

#     # createZipFile("download.zip")
#     if model_IDS:
#       for ID in model_IDS:
#         ant = mm.get_antimony({ "ID" : ID })
#         filename = str(ID) + ".txt"
#         createToZipFile(app.config["FILENAME"], filename, ant) #can simplify by removing first parameter
#       return 1
#     else:
#       return 0

#   except ValueError:
#     return -1



#Flask Development Server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
