import mongoMethods as mm
from pymongo import MongoClient

astr = "mongodb+srv://data:VuRWQ@networks.wqx1t.mongodb.net"
client = MongoClient(astr)
database_names = client.list_database_names()
print(database_names)
org = client.networks
og = org['networks']
db = client.models
collection = db['models']
cur = collection.find({})






for i, model in enumerate(cur):
    if i % 100 == 0:
        print(f"working on model {i}...")
    ID = model["ID"]
    oldModel = og.find({"ID": ID})
    newVal = {}
    try:
        newVal['autocatalysisPresent'] = oldModel['Autocatalysis Present']
    except:
        newVal['autocatalysisPresent'] = None
    try:
        newVal['degradationPresent'] = oldModel['Degradation Present']
    except:
        newVal['degradationPresent'] = None
    try:
        newVal['initialProbabilities'] = oldModel['initialProbabilities']
    except:
        newVal['initialProbabilities'] = None
    try:
        newVal['addReactionProbabilities'] = oldModel['addReactionProbabilities']
    except:
        newVal['addReactionProbabilities'] = None

    # try:
    #     newVal["combinedReactions"] = oldModel["combinedReactions"]
    # except:
    #     newVal["combinedReactions"] = None
    #
    # try:
    #     newVal['deletedReactions'] = oldModel['deletedReactions']
    # except:
    #     newVal['deletedReactions'] = None
    #
    # try:
    #     newVal['reactionCounts'] = oldModel['reactionCounts']
    # except:
    #     newVal['reactionCounts'] = None

    collection.update_one({"ID": ID}, {"$set": newVal})




# for i, model in enumerate(currentDB):
#     if i%100 == 0:
#         print(i)
#     entry = {
#         "ID": model["ID"],
#         "modelType": model["modelType"],
#         "name": None,
#         "isPublished": False,
#         "author": None,
#         "journal": None,
#         "isEvolved": True,
#         "antimonyModel": model['model'],
#         "numBoundary": None,
#         "numFloat": None,
#         "numSpecies": model['num_nodes'],
#         "numReactions": model['num_reactions'],
#         "addReactionProbabilities": [0.25, 0.25, 0.25, 0.25],
#         "initialReactionProbabilities": [0.1, 0.4, 0.4, 0.1],
#     }
#     try:
#         entry["combinedReactions"] = model["combinedReactions"]
#     except:
#         entry["combinedReactions"] = None
#
#     try:
#         entry['deletedReactions'] = model['deletedReactions']
#     except:
#         entry['deletedReactions'] = None
#
#     try:
#         entry['reactionCounts'] = model['reactionCounts']
#     except:
#         entry['reactionCounts'] = None
#
#     if entry['numSpecies'] < min_species:
#         min_species = entry['numSpecies']
#     if entry['numReactions'] < min_reactions:
#         min_reactions = entry['numReactions']
#     if entry['numSpecies'] > max_species:
#         max_species = entry['numSpecies']
#     if entry['numReactions'] > max_reactions:
#         max_reactions = entry['numReactions']
#
#     models.append(entry)

# networkDB = client['meta_data']
# collection = db['meta_data']
#
# entry = {'totalModels': 18189,
#          'totalOscillators': 2065,
#          'totalRandom': 16124,
#          'modelTypes': ["oscillator", "random"]}
#
# collection.insert_one(entry)
# for entry in models:
#     collection.insert_one(entry)
#
#
# r = collection.find({})

### Un-nest the antimony dictionary