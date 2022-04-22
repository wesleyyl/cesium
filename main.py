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
# app.config["DOWNLOAD_FOLDER"] = 'download'
app.config["ZIPF_NAME"] = "cesium-download" #default value to be changed


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

  elif request.method == 'POST':
    
    #Retrieve Form Data
    form_data = request.form #this is a dictionary w/ keys & values

    model_type = form_data.get("mtype")
    num_nodes = int(form_data.get("num_nodes"))
    num_reactions = int(form_data.get("num_reactions"))
    oscillator = form_data.get("oscillator")
    autocatalysis = form_data.get("autocat")
    degradation = form_data.get("degrade")
    telsimulatable = "isSimulatable" in form_data


    # if form_data.get("isSimulatable"):
    #   telsimulatable = True
    # else:
    #   telsimulatable = False
    # telsimulatable = form_data.get("isSimulatable")
    # telsimulatable = True


    #CONVERTS HTML FORM VALUES TO BOOLEAN
    if oscillator == "osc_yes":
      oscillator_status = True
    elif oscillator == "osc_no":
      oscillator_status = False
    else:
      # oscillator = "osc_no"
      oscillator_status = False

    #IF AUTOCATALYSIS LEFT EMPTY IT DEFAULTS TO NO!
    if autocatalysis == "autocat_yes":
      autocatalysis_status = True
    elif autocatalysis == "autocat_no":
      autocatalysis_status = False
    else:
      # autocatalysis = "autocat_no"
      autocatalysis_status = False

    #IF DEGRADATION LEFT EMPTY IT DEFAULTS TO NO!
    if degradation == "degrade_yes":
      degradation_status = True
    elif degradation == "degrade_no":
      degradation_status = False
    else:
      # degradation = "degrade_no"
      degradation_status = False

    queryParam = {
      'type' : model_type,
      'nodes' : num_nodes,
      'reac' : num_reactions,
      'osc' : oscillator_status,
      'autocat' : autocatalysis_status,
      'degrade' : degradation_status,
      'simulatable' : telsimulatable
    }

    # app.config["ZIPF_NAME"] = ".".join([str(num_nodes), str(num_reactions), oscillator, autocatalysis, degradation])


    # cesiumZip = cesiumQuery(queryParam)

    # encoded_zipF = base64.b64encode(cesiumZip.getvalue())


    #DEBUG CODE: TO LOAD PAGE WITH QUERY VALUES UNDERNEATH
    if cesiumQueryExists(queryParam):
      return render_template('download.html', query=queryParam, queryJSON=json.dumps(queryParam))
    elif not cesiumQueryExists(queryParam):
      error = "No models found. Please try a different query."
      return render_template('error.html', error_msg=error)
    elif status == -1:
      error = "Invalid inputs. Please try again."
      return render_template('error.html', error_msg=error)

    #DEBUG CODE: TO CHECK THAT VALUES ARE ACTUALLY GOING THROUGH
    # return form_data


#Download File Page
@app.route("/download/<query>")
def download_file(query):
  # filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["ZIPF_NAME"])
  # filename = "{}.zip".format(app.config["ZIPF_NAME"])

  query = json.loads(query)
  

  cesiumZip = cesiumQuery(query)


  # for param in queryDict.values():
  #   queryList.append(str(param))

  # filename = ".".join(queryList)



  return send_file(cesiumZip, attachment_filename="{}.zip".format(app.config["ZIPF_NAME"]), as_attachment=True)



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
  dbquery = { "modelType" : query["type"], "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"] }
  # dbquery = { "modelType" : query["type"], "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"], "Autcatalysis Present": query["autocat"] }
  model_IDS = mm.get_ids(dbquery)

  if model_IDS:
    return True
  else:
    return False

def cesiumQuery(query):

  # filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], app.config["ZIPF_NAME"])

  dbquery = { "modelType" : query["type"], "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"] }
  # dbquery = { "modelType" : query["type"], "num_nodes" : query["nodes"], "num_reactions" : query["reac"], "oscillator" : query["osc"], "Autcatalysis Present": query["autocat"] }
  model_IDS = mm.get_ids(dbquery)
  
  if model_IDS:
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



#Flask Development Server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
