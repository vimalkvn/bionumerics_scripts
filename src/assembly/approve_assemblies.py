"""Approve all assemblies for selected entries"""
#TODO: move common functions

import bns

entries = list(bns.Database.Db.Selection)
if not len(entries):
	bns.Util.Program.MessageBox('Information', 'No entries selected', 'exclamation')
	__bnscontext__.Stop()
	
def get_sequence_objectid(key, exper):
	CDB = bns.ConnectedDb
	ot = CDB.ObjectType('SEQUENCES')
	seqflds = {'KEY': key, 'EXPERIMENT': exper}
	return CDB.ObjectID(ot, seqflds)
	
def update_contig_status(key, exper, status):
	CDB = bns.ConnectedDb
	seqobject = get_sequence_objectid(key, exper)
	ot = seqobject.GetType()
	lx = seqobject.GetExpression()
	action = CDB.ObjAction('Set contig status')
	objaction = CDB.ObjectSpecifAction(action, seqobject)
	objaction.UpdateSingleField(ot, 'CONTIGSTATUS', lx, status)
	objaction.Close()
	action.Close()
	return True
	
def get_contig_status(key, exper):
	db = bns.ConnectedDb
	keycol = db.DbColumn('KEY').Equal(key)
	genecol = db.DbColumn('EXPERIMENT').Equal(exper)
	lx = keycol & genecol
	records = db.DbRecordSet('SEQUENCES', ['CONTIGSTATUS'])
	result = records.Select(lx)
	result = list(result)
	return result[0]['CONTIGSTATUS']
	
def is_approved(key, exper):
	status = get_contig_status(key, exper)
	if status == 'OK':
		return True
	else:
		return False
	
if __name__ == '__main__':	
	experiments = [item.Name for item in bns.Database.Db.ExperimentTypes]
	experlist = []
	for item in experiments:
		if not (item.startswith('merged') or item.endswith('TRANSL')):
			if bns.Database.ExperimentType(item).Class == 'SEQ':
				experlist.append(item)
	
	updated = False
	for entry in entries:
		profile = {}
		key = entry.Key	
		for exper in experlist:
			if bns.Database.Experiment(key, exper).ExperID:
				if not is_approved(key, exper):
					updated = update_contig_status(key, exper, 'OK')
					
	if updated:
		response = bns.Util.Program.MessageBox('Restart', 
		'Please restart Bionumerics to reload the database.\n'\
		'Do you want to restart now?\n\nWARNING: this will close all '\
		'opened windows without saving, with possible loss of data.', 
		'question+yesno+defbutton2')
		
		if response == 1:
			bns.Database.bnsIntern.db.Restart('')
