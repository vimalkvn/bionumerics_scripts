"""Common database functions"""

import bns


def get_dbpath():
	"""Returns database path"""
	
	db = bns.Database.Db
	dbpath = db.Info.Path
	
	return dbpath


def get_all_keys():
	"""Returns a list of database entry keys"""
	
	keys = []
	db = bns.Database.Db
	
	for i in range(len(db.Entries)):
		key = db.Entries[i].Key
		
		if len(key) and key not in keys:
			keys.append(key)
			
	return keys
	

def get_characters(exper):
	"""Returns list of characters in a character set 
	experiment
	
	"""	
	characters = []
	exp_types = bns.Database.Db.ExperimentTypes	

	for item in exp_types:
		if item.Name == exper and item.Class == 'CHR':
			charset = bns.Characters.CharSetType(exper)	
			
			for i in range(charset.GetCount()):
				characters.append(charset.GetChar(i))
	
	return characters