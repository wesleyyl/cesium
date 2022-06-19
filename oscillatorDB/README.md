# oscillatorDB

## Table of Contents
- [oscillatorDB](#oscillatordb)
  * [Recent Updates (2022-05-27)](#recent-updates--2022-05-27-)
    + [The "modelType" field](#the--modeltype--field)
      - [Example - modelType Field:](#example---modeltype-field-)
    + [New add_model method](#new-add-model-method)
  * [Set Up](#set-up)
  * [Database Schema](#database-schema)
  * [Queries](#queries)
    + [Simple Queries](#simple-queries)
    + [General Queries - most likely this is what you want](#general-queries---most-likely-this-is-what-you-want)
      - [Get IDs](#get-ids)
      - [Get antimony strings](#get-antimony-strings)
      - [Get SBML files](#get-sbml-files)
    + [Custom Queries](#custom-queries)
  * [Adding to Database](#adding-to-database)
    + [Adding a Single Model](#adding-a-single-model)
    + [Adding en Masse (USE CAUTION)](#adding-en-masse--use-caution-)
        * [Example - Adding Models en Masse:](#exampel---adding-models-en-masse-)



## Recent Updates (2022-05-27)
* All unused or redundant fields have been removed. 
* The field "oscillator" has been removed. To find oscillators, use "modelType": "oscillator"
* There is now a predifined list of possible modelTypes: "oscillator" or "random" (see below)
* There is a new method to add a single model called ```add_model(antString, modelType)``` (see below)
    

### The "modelType" field
There is now a defined set of possible model types for the field modelType. Currently these are "oscillator" and "random".

#### Example - modelType Field: 
<b>Get a list of the current model types:</b>

Input:
```
import mongoMethods as mm
mm.get_model_types()
```
Output:
```
['oscillator', 'random']
```
<b>Add a new model type:</b>

```
mm.add_model_type('bistable')
```


### New add_model method
* ```add_model(antString, modelType)```
* Arguments: antString - The antimony string for the model to be added
                 modelType - (string) model type from list of current model types
* Optional args: 
   * ID: (str) model's ID, populated automatically if left blank
   * num_nodes: (int) the number of species, populated automatically if left blank
   * num_reactions: (int) the number of reactions, populated automatically if left blank
   * addReactionProbabilites: int list, the probability of adding each reaction type:
       uni-uni, uni-bi, bi-uni, bi-bi
   * initialProbabilites: int list, the initial probability of adding each reaction type when generating a
       random network: uni-uni, uni-bi, bi-uni, bi-bi
   * autocatalysisPresent: boolean, True if there is an autocatalytic reaction
   * degradationPresent: boolean, True if there is a degradation reaction

The antimony string must be formatted as follows:
```
antimony_string = '''
var S0                        # Species must be declared first using 'var' or 'ext' (getting the correct num_nodes count depends on this!)
var S1
var S2
S1 -> S1+S0; k0*S1      
S2 + S0 -> S0; k1*S2*S0
S2 -> S2+S1; k2*S2
S0 -> S1; k3*S0
S1 -> S2; k4*S1
S2 -> S2+S2; k5*S2
k0 = 2.58                     # Rate constants must start with "k"
k1 = 25.10                    # The number of rate constants must equal the number of reactions
k2 = 5.69
k3 = 12.40
k4 = 28.62
k5 = 63.57
S0 = 1.0
S1 = 5.0
S2 = 9.0'''
```
Adding the new model:
```
mm.add_model(antimony_string, "oscillator", num_nodes=3, num_reactions=6, autocatalysis=True)
```
If left blank, the fields ID, num_nodes, and num_reactions will automatically be populated. Any other optional arguments that are left blank will be None.

It's helpful to put all known info into the optional arguments and leave as few blanks as possible, but in the future I will restructure stuff so you can analyze the reactions from here.

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
<b> Note to self: </b> DO NOT INSTALL bson into this environment. 


## Database Schema
Also available via ```print_schema()```

The data base stores:
* ID: model's ID number (str)
* num_nodes: number of species (int)
* num_reactions: number of reactions (int)
* model: antimony string for the model
* modelType: eg. "oscillator" or "random" (str)
* combinedReactions: identical reactions that were fused in post-processing (list of strings)
* deletedReactions: reactions that were not needed for oscillation and removed (list of strings)
* reactionCounts: Tally for different reaction types: Uni-Uni, Uni-Bi, Bi-Uni, Bi-Bi, Degradation, Autocatalysis, Total (dict)
* Autocatalysis Present: True if an autocatalytic reaction is present (boolean)
* Degradation Present: True if a degradation reaction is present (boolean)
* addReactionProbabilities: The probability of adding each reaction type <b>during evolution</b>: uni-uni, uni-bi, bi-uni, bi-bi (eg. [0.25, 0.25, 0.25,0.25]) (list of floats)
* initialProbabilities: The probability of adding each reaction type <b>during the initial random generation</b>, uni-uni, uni-bi, bi-uni, bi-bi (eg. [0.25, 0.25, 0.25,0.25]) (list of floats)



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

## Adding to Database 
### Adding a Single Model
(copied from recent updates)
* ```add_model(antString, modelType)```
* Arguments: antString - The antimony string for the model to be added
             modelType - (string) model type from list of current model types
* Optional args: 
 * ID: (str) model's ID, populated automatically if left blank
 * num_nodes: (int) the number of species, populated automatically if left blank
 * num_reactions: (int) the number of reactions, populated automatically if left blank
 * addReactionProbabilites: int list, the probability of adding each reaction type:
     uni-uni, uni-bi, bi-uni, bi-bi
 * initialProbabilites: int list, the initial probability of adding each reaction type when generating a
     random network: uni-uni, uni-bi, bi-uni, bi-bi
 * autocatalysisPresent: boolean, True if there is an autocatalytic reaction
 * degradationPresent: boolean, True if there is a degradation reaction

The antimony string must be formatted as follows:
```
antimony_string = '''
var S0                        # Species must be declared first using 'var' or 'ext' (getting the correct num_nodes count depends on this!)
var S1
var S2
S1 -> S1+S0; k0*S1      
S2 + S0 -> S0; k1*S2*S0
S2 -> S2+S1; k2*S2
S0 -> S1; k3*S0
S1 -> S2; k4*S1
S2 -> S2+S2; k5*S2
k0 = 2.58                     # Rate constants must start with "k"
k1 = 25.10                    # The number of rate constants must equal the number of reactions
k2 = 5.69
k3 = 12.40
k4 = 28.62
k5 = 63.57
S0 = 1.0
S1 = 5.0
S2 = 9.0'''
```
Adding the new model:
```
mm.add_model(antimony_string, "oscillator", num_nodes=3, num_reactions=6, autocatalysis=True)
```
If left blank, the fields ID, num_nodes, and num_reactions will automatically be populated. Any other optional arguments that are left blank will be None.
