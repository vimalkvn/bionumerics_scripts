"""Bionumerics functions for itquery"""
import bns
DB = bns.Database

def createIdMap():
	"""Map of ItemTracker ID:Bionumerics KEY for all entries."""
	field = "ItemTracker ID"

	itemNames = {}
	for entry in DB.Db.Entries:
		key = entry.Key
		itemId = DB.EntryField(key, field).Content

		if itemId and len(itemId):
			try:
				itemId = int(itemId)
			except (ValueError, TypeError):
				continue
			itemNames[itemId] = key
	return itemNames

def getFieldNames():
	"""Returns the field/column names of the current Bionumerics database."""
	fieldNames = [item.Name for item in DB.Db.Fields]
	return fieldNames

def getItemIds(idField, entries):
	"""Returns ItemTracker ID's of selected entries."""
	getIds = {}
	errorIds = {}

	if not len(entries):
		return getIds, errorIds

	for entry in entries:
		key = entry.Key
		try:
			itemId = DB.EntryField(key, idField).Content
			itemId = itemId.strip()
		except RuntimeError:
			# bugfix: don't display if ItemTracker ID contains spaces
			itemId = None

		if not itemId:
			continue
		try:
			itemId = int(itemId) # remove invalid ids
		except (ValueError, TypeError):
			errorIds[key] = "Invalid {0}: {1}".format(idField, itemId)

		if isinstance(itemId, int):
			if not getIds.get(itemId):
				getIds[itemId] = key
			else:
				dupKey = getIds.pop(itemId)
				errorIds[key] = ("Duplicate ItemTracker ID {0}.Other key: {1}."
								" Not processed".format(itemId, dupKey))
	return getIds, errorIds

def getSelectedFields(key, fields):
	"""Get all field values for a given KEY."""
	contents = {}
	for field in fields:
		values = DB.EntryField(key, field).Content
		contents[field] = values

	return contents

def selectEntries(keys):
	"""Select entries with given keys."""
	DB.Db.Selection.Clear()

	for key in keys:
		DB.Db.Entries[key].Selection = 1
