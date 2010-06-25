'''General database functions

Copyright (C) 2010  Vimalkumar Velayudhan <vimal@ucc.ie>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

'''

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