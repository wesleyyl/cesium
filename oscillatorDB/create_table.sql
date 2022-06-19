CREATE TABLE models (
	_id varchar,
	ID varchar PRIMARY KEY,
	num_nodes int,
	initialProbabilities varchar,
	addReactionProbabilities varchar,
	model varchar,
	combinedReactions varchar,
	deletedReactions varchar,
	num_reactions int,
	Autocatalysis_Present varchar,
	Degradation_Present varchar,
	reactionCounts varchar,
	modelType varchar);
	
PRAGMA foreign_keys=ON;

.mode csv

.import /home/hellsbells/projects/oscillator_backup/networks.csv models
