#Flask Packages
from flask import Flask, request, render_template, url_for, send_from_directory
from flask import Response
#from flask import redirect

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


#Config Values
app.config["DOWNLOAD_FOLDER"] = 'download'
app.config["FILENAME"] = "download.zip"


#Index Page
@app.route("/")
def index():
    
    return render_template('index.html')


    # num_nodes = request.args.get("num_nodes", "")
    # num_reactions = request.args.get("num_reactions", "")
    # oscillator = request.args.get("oscillator", "")
    # autocatalysis = request.args.get("autocatalysis", "")
    # degradation = request.args.get("degradation", "")

    # try:
    #   num_nodes = int(num_nodes)
    #   num_reactions = int(num_reactions)
    # except ValueError:
    #   pass

    # # num_nodes = 3
    # # num_reactions = 5
    # # WHY ARE THESE 2 VALUES NOT BEING PASSED/RETURNED?!

    # if oscillator == "osc_yes":
    #   oscillator_status = True
    # elif oscillator == "osc_no":
    #   oscillator_status = False
    # else:
    #   oscillator_status = -1; #default value when website first loaded

    # result = oscillatorDB(num_nodes, num_reactions, oscillator_status)

    # if result[0] == "Done":
    #   return render_template('download.html', value=result[1])
    #   #return redirect('/download/' + app.config["FILENAME"])
    # elif result == "No entries found":
    #   return render_template('index.html', value=result[0])
    # else:
    #   return render_template('index.html', value="")

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

    #IF AUTOCATALYSIS LEFT EMPTY IT DEFAULTS TO NO!
    if autocatalysis == "Y/N":
      autocatalysis = False

    #IF DEGRADATION LEFT EMPTY IT DEFAULTS TO NO!
    if degradation == "Y/N":
      degradation = False

    
    status = oscillatorDB(num_nodes, num_reactions, oscillator_status)

    queryParam = {
      'nodes' : num_nodes,
      'reac' : num_reactions,
      'osc' : oscillator_status,
      'autocat' : autocatalysis,
      'degrade' : degradation
    }

    # return render_template('download.html', filename=app.config["FILENAME"])

    #DEBUG CODE: TO LOAD PAGE WITH QUERY VALUES UNDERNEATH
    if status == 1:
      return render_template('download.html', filename=app.config["FILENAME"], query=queryParam)
    elif status == 0:
      error = "No models found. Please try something different."
      return render_template('error.html', error_msg=error)
    elif status == -1:
      error = "Invalid inputs. Please try again."
      return render_template('error.html', error_msg=error)

    #DEBUG CODE: TO CHECK THAT VALUES ARE ACTUALLY GOING THROUGH
    # return form_data
    #DEBUG CODE: TO CHECK THAT SPECIFIC VALUE IS CORRECT
    # return str(num_nodes)

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
# 
# return -1: invalid inputs (fix later with form validation features)
# return 0: no models found using that query
# return 1: query successful
# 
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
      return 1
    else:
      return 0

  except ValueError:
    return -1




@app.route("/about")
def about():
  return render_template('about.html')

@app.route("/faq")
def faq():
  return render_template('faq.html')

#Flask Development Server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
