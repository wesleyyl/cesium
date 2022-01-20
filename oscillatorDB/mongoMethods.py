import os
from pymongo import MongoClient
import warnings
from random import randrange
import tellurium as te

###Fixes the pymongo.errors.ServerSelectionTimeoutError => references installed certificate authority bundle
import certifi
ca = certifi.where()

warnings.filterwarnings("ignore", category=DeprecationWarning)

###Initialization of variables
astr = ""
client = ""
database_names = ""
db = ""
collection = ""
cur = ""

###Startup function so we don't autmoatically call upon the db
# user: data
# pwd:  VuRWQ
def startup():
    global astr
    global client
    global database_names
    global db
    global collection
    global cur
    astr = "mongodb+srv://data:VuRWQ@networks.wqx1t.mongodb.net"
    #client = MongoClient(astr)
    #MY CHANGES!!!!
    client = MongoClient(astr, tlsCAFile=ca) ###fixes the pymongo.errors.ServerSelectionTimeoutError
    database_names = client.list_database_names()
    db = client['networks']
    db = client.networks
    collection = db['networks']
    cur = collection.find({})


def print_entries(cursor=cur, n=None):
    '''
    Prints entries in the database
    :param n: optional, print out the first n entries. By default n is none and all entries are printed.
    :return: print out of every entry dictionary
    '''
    print(f"There are {cursor.count()} entries in the database")
    if not n:
        for doc in cursor:
            print(doc)
    else:
        count = 1
        for doc in cursor:
            print(doc)
            if count < n:
                count += 1
            else:
                break


def get_connection():
    '''
    Connect to the mongoDB
    :return: a MongoClient object connected to the database
    '''
    return MongoClient("mongodb+srv://data:VuRWQ@networks.wqx1t.mongodb.net")


def get_collection_size(onlyOscillators=True):
    if onlyOscillators:
        results = collection.find({'oscillator': True})
        return results.count()
    else:
        return collection.count()


def get_random_oscillator(n=1):
    count = get_collection_size()
    return collection.find()[randrange(count)]

def load_lines(path):
    '''
    Load an antimony model from a local machine split into lines
    :param path: path to the .ant file
    :return: Returns the antimony test as a list of strings. Omits the first line if it is a comment.
    '''
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    lines = ant.split('\n')
    # First line is comment for fitness, ignore
    if lines[0].startswith('#'):
        lines = lines[1:]
    return lines


def load_antimony(path):
    '''
    Load an antimony model from a local machine split into lines
    :param path: path to the .ant file
    :return: a single antimony string for the model. Includes all lines including comments.
    '''
    # THIS WILL INCLUDE THE FIRST COMMENTED LINE!
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    return ant


def get_nReactions(ant):
    '''
    Count how many reactions are in the model
    :param ant: antimony strings split by line, usually loaded with load_lines
    :return: integer, number of reactions
    '''
    # Takes a list of strings for each line in ant file
    nReactions = 0
    for line in ant:
        if '->' in line and not line.startswith('#'):
            if line.startswith('k'):
                break
            nReactions += 1
    return nReactions


def get_nNodes(ant):
    nNodes = 0
    # Skip the first line if it is a comment
    if ant[0].startswith('#'):
        ant = ant[1:]
    for line in ant:
        if line.startswith('var') or line.startswith('ext'):
            nNodes += 1
        else:
            break
    return nNodes


def query_database(query):
    '''
    Retrieve all entries that match the query
    :param query: A dictionary of the desired model traits
    :return: A cursor object containing the dictionaries for all matching models
    '''
    cur = collection.find(query)
    print(f'Found {cur.count()} matching entries.')
    return collection.find(query)


def get_ids(query):
    '''
    Get the IDs of models that match the query
    :param query: A dictionary of model traits to look for
    :return: A list of IDs (str) for the matching models
    '''
    doc = collection.find(query)
    result = []
    for x in doc:
        result.append(x['ID'])
    if len(result) == 0:
        print('No entries found.')
        return None
    return result

def update_model(query, update):
    newValue = {"$set" : update}
    collection.update_one(query, newValue)


def get_model_by_id(id):
    # If the id is provided as an integer, convert to string
    if isinstance(id, int):
        id = str(id)
    result = collection.find_one({'ID': id})
    if not result:
        print(f'Model {id} not found.')
    else:
        return result


def get_antimony(query):
    '''
    Get the antimony string(s) of models that match the query
    :param query: A dictionary of model traits to look for
    :return: If there is only a single matching model, returns the string for that model.
             Otherwise, returns a list of model strings.
    '''
    doc = collection.find(query)
    result = []
    for x in doc:
        result.append(x['model'])
    if len(result) == 0:
        print('No entries found.')
    elif len(result) == 1:
        return result[0]
    else:
        return result


def yes_or_no(question):
    '''
    Prompt the user to answer a yes or no question
    :param question: The question to be asked (str)
    :return: True if yes, False if no (boolean)
    '''
    answered = False
    while not answered:
        reply = str(input(question + ' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        elif reply[0] == 'n':
            return False
        else:
            print('Please answer y or n.')


def add_many(path, oscillator, massConserved, num_nodes=None):
    '''
    Add several antimony models to the database from a local folder containing .ant files.
    :param path: Path to the folder where the antimony models are located.
    :param oscillator: Oscillation status. True for oscillator, False for non oscillator (booleans), or 'damped' (str)
    :return: None
    '''
    if not os.path.exists(path):
        raise ValueError("Invalid path")
    modelList = []
    os.chdir(path)
    for filename in os.listdir(path):
        if not filename.endswith('.ant') or os.path.isdir(filename):
            continue
        ant_lines = load_lines(filename)
        nReactions = get_nReactions(ant_lines)
        if not num_nodes:
            nNodes = get_nNodes(ant_lines)
        else:
            nNodes = num_nodes
        ant = load_antimony(filename)

        if filename.startswith('FAIL_Model_'):
            ID = filename[11:-4]
        elif filename.startswith('Model_'):
            ID = filename[6:-4]
        elif filename.endswith('.ant'):
            ID = filename[:-4]
        else:
            ID = filename
        if not (oscillator == True or oscillator == False or oscillator == 'damped'):
            raise ValueError("Oscillator argument must be True, False, or 'damped'")
        modelDict = {'ID': ID,
                     'num_nodes': nNodes,
                     'num_reactions': nReactions,
                     'model': ant,
                     'oscillator': oscillator,
                     'mass_conserved' : massConserved}
        modelList.append(modelDict)
    collection.insert_many(modelList)
    print(f"Successfully added {len(modelList)} models to database")


def add_ant_extension(path):
    os.chdir(path)
    count = 0
    for filename in os.listdir(path):
        os.rename(filename, filename[:-4])
        count += 1
    print(f'Successfully added .ant extension to {count} files')


def delete_by_query(query, yesNo=True):
    '''
    Delete models that match the query from the database
    :param query: A dictionary with the target traits of models to be deleted.
    :return: None
    '''
    if query == {}:
        print('Deleting the entire database is not allowed.')
        return None
    if yesNo:
        proceed = yes_or_no(f"Are you sure you want to delete all models that math the query {str(query)}?")
        if proceed:
            collection.delete_many(query)
            print(f"Successfully deleted models matching the query {str(query)}")
    else:
        collection.delete_many(query)



def delete_by_path(path):
    '''
    Delete models from the database that match models in a local folder.
    This is useful if models from a local folder were incorrectly or inadvertently added to the database.
    :param path: Path to local folder where the .ant files are located.
    :return: None
    '''
    if not os.path.exists(path):
        raise ValueError('Invalid path.')
    os.chdir(path)
    count = 0
    for filename in os.listdir(path):
        if filename.endswith('.ant'):
            if filename.startswith('FAIL_Model_'):
                ID = filename[11:-4]
            elif filename.startswith('Model_'):
                ID = filename[6:-4]
            else:
                ID = filename[-4]
            collection.delete_one({'ID': ID})
            count += 1
    print(f"Successfully deleted {count} models from the database.")


def get_sbml(query, sbml_path):
    id_list = get_ids(query)
    if not os.path.exists(sbml_path) or not os.path.isdir(sbml_path):
        os.mkdir(sbml_path)
    total = len(id_list)
    count = 0
    for id in id_list:
        try:
            ant = get_antimony({"ID": id})
            r = te.loada(ant)
            r.exportToSBML(f"{os.path.join(sbml_path, id)}.sbml")
            count += 1
        except:
            continue
    print(f"Exported {count} of {total} models to {sbml_path}")

def findMisProcessed(antimony):
    lines = antimony.splitlines()
    speciesList = []
    for line in lines:
        if line.startswith('var') or line.startswith('ext'):
            if line not in speciesList:
                speciesList.append(line)
            else:
                return True, antimony
    return False, None


def deleteBadModels(query, writeOut=False, destinationPath=None):
    results = mm.query_database(query)
    processed = 0
    count = 0
    if destinationPath:
        os.chdir(destinationPath)
    for model in results:
        isMisProcessed, antimony = findMisProcessed(model['model'])
        if isMisProcessed:
            count += 1
            mm.delete_by_query({'ID': model['ID']}, yesNo=False)
        processed += 1
        if writeOut:
            with open(model['ID']+'.ant', "w") as f:
                f.write(model['model'])
                f.close()
    print(f'Deleted {count} of {processed} models :(')



get_connection()
