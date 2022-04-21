# oscillatorDB

## Set Up
Clone this repository:
```git clone https://github.com/really-lilly/oscillatorDB.git```

This module requires:
* PyMongo
* dnsPython
* tellurium

These can be installed via pip or conda. Alternatively, environment.yml is a conda environment containing all the necessary packages. To use it:
```
conda env create -f environment.yml
conda activate oscillatorDB
 ```
<b> Note to self: </b> DO NOT INSTALL bson into this environment. It will break everything and you'll waste an entire day trying to fix it and then just end up re-cloning the repo. Trust me, I know. Don't think it will be a good idea to back up the database and google how to do it. Don't implent the accepted answer on StackOverflow. Don't mess with the environment. Do not do what I have done.

You think that doesn't sound that bad? Well you also have to delete the environment and then rebuild it. And then reset your python interpreter to the new environment. Just don't do that. 


## Database Description

The data base stores:
* ID: model's ID number (str)
* num_nodes: number of species (int)
* num_reactions: number of reactions (int)
* model: antimony string for the model
* oscillator: If the model oscillates or not (boolean). True if does, False if it does not. 
    * Models are filtered so none go to infinity
* mass_conserved: True if there are no reactions that violate mass conservation (eg. A + B -> A). False otherwise


## Queries

### Simple Queries
Queries are specified by a dictionary containing the traits of interest. There are two query helper methods in the module to get a list of IDs or the antimony strings of models that match the query. 

### General Queries - most likely this is what you want
```import mongoMethods as mm

query = {"num_nodes": 3, "oscillator": True, "Autocatalysis Present": True}
result = mm.query_database(query)
```
The variable "result" is a cursor (essentially a list) containing the matching entries as dictionaries. You can iterate through the cursor as you would a list:
```
for model in result:
    print(model["num_reactions"])
```
To view the antimony string for a model in the cursor:
```
print(result[0]["model"]
```

#### Get IDs
```
import mongoMethods as mm

# Get IDs of oscillators with 3 nodes
query = { "num_nodes" : 3, "oscillator" : True)}
model_IDS = mm.get_ids(query)
```
#### Get antimony strings
```
import mongoMethods as mm

# Get antimony string for model 12345
query = { "ID" : "1234" }
ant = mm.get_antimony(query)
```
#### Get SBML files
```
import mongoMethods as mm

# Get SBML files for all oscillating 3-node models:
query = {"num_nodes" : 3, "oscillator" True}
path = "~/path/to/SBML_directory"  # Directory to store SBML files (will be created if it doesn't exist already)
mm.get_sbml(query, path)
```

### Custom Queries
More general queries can be made with the function ```query_database()``` which accepts a query dictionary and returns a cursor object containing the dictionaries for all matching entries. The cursor object can be accessed and interated over as if it were a list of dictionaries.

```
import mongoMethods as mm

# Get a list of all models with 3 nodes
query = { 'num_nodes' : 3 }
models = mm.query_database(query)

# Get the ID of the first model
ID = models[0]['ID']

# Print the number of reactions in each model
for model in models:
    print(model['num_reactions'])
```

The collection can also be directly queried after directly connecting to the database collection
```
import mongoMethods as mm

# Connect to the database collection
collection = mm.collection

# Get oscillators with 3 nodes and 5 reactions
query = { "num_nodes" : 3, "num_reactions" : 5, "oscillator" : True }
entries = collection.find(query)

# Get the IDs of models that match the query
for entry in entries:
    print(entry['ID'])
```

## Adding to Database

New models can be added en masse provided that all antimony files are stored in a single folder. You will also need to provide the oscillation status (True, False). The number of nodes/species will automatically be counted provided that the antimony file starts with listing the species as shown below. 
'''
var S0
var S1
#etc
'''
This will also work if the first line is a comment. If your antimony file does not have this information, the number of nodes can be manually provided with the option argument "num_nodes"

**NOTE: There is currently no safeguard to prevent adding duplicate models to the database. Running the same add_many command twice will duplicate the models previously added.**

##### EXAMPLE: 
Add oscillating networks from the folder ant_folder
```
import mongoMethods as mm


path = "/home/user/ant_folder"

# True indicates oscillating model
mm.add_many(path, True, num_nodes=3)   #add_many(path, oscillator, massConserved, num_nodes=None)
```

It may be necessary to delete models from the database if they've been erroneously added. **Be catious**, deleting models is permanent and effects the entire database.

##### EXAMPLE:
Let's say that in the previous example, we added antimony models to the database from the folder ant_folders, but they were erroneously added as oscillators when they are not. We can delete all the models that are stored in the local folder from the database and then re-add them with the correct oscillation status.
```
import mongoMethods as mm

connection = mm.get_connection()
path = "C:\\Users\\user\\ant_folder"

# Remove the models
mm.delete_by_path(path)

# Re-add the models with the correct oscillator status
mm.add_many(path, False)
```
Models can also be deleted by query. This is useful if you want to delete a specific model. For example, the model 12345 can be deleted by
```mm.delete_by_query({ 'ID' : '12345' })```
Please be careful when deleting by query. If your query is not specific enough, you may end up permanently deleting other models from the database as well.

## What's in the database
Last updated 2021-07-15

* 10 node oscillators
* 10 node controls (non-oscillators)
* 3 node oscillators
* 3 node controls

