import os
import mongoMethods as mm

'''
Please don't use any of these without talking to Lilly
'''

def update_model(query, update):
    newValue = {"$set" : update}
    mm.collection.update_one(query, newValue)


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
        nReactions = mm.get_nReactions(ant_lines)
        if not num_nodes:
            nNodes = mm.get_nNodes(ant_lines)
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
    mm.collection.insert_many(modelList)
    print(f"Successfully added {len(modelList)} models to database")


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
    results =mm. query_database(query)
    processed = 0
    count = 0
    if destinationPath:
        os.chdir(destinationPath)
    for model in results:
        isMisProcessed, antimony = findMisProcessed(model['model'])
        if isMisProcessed:
            count += 1
            delete_by_query({'ID': model['ID']}, yesNo=False)
        processed += 1
        if writeOut:
            with open(model['ID']+'.ant', "w") as f:
                f.write(model['model'])
                f.close()
    print(f'Deleted {count} of {processed} models :(')


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
            mm.collection.delete_one({'ID': ID})
            count += 1
    print(f"Successfully deleted {count} models from the database.")


def add_ant_extension(path):
    os.chdir(path)
    count = 0
    for filename in os.listdir(path):
        os.rename(filename, filename[:-4])
        count += 1
    print(f'Successfully added .ant extension to {count} files')


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


def delete_by_query(query, yesNo=True):
    '''
    USE WITH CAUTION
    Delete models that match the query from the database
    :param query: A dictionary with the target traits of models to be deleted.
    :return: None
    '''
    if query == {}:
        print('Deleting the entire database is not allowed.')
        return None
    if yesNo:
        proceed = mm.yes_or_no(f"Are you sure you want to delete all models that math the query {str(query)}?")
        if proceed:
            mm.collection.delete_many(query)
            print(f"Successfully deleted models matching the query {str(query)}")
    else:
        mm.collection.delete_many(query)
