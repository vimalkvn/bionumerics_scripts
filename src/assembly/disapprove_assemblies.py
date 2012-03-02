"""Disapprove all assemblies for selected entries"""

import bns

def get_sequence_objectid(entry_key, entry_exper):
	CDB = bns.ConnectedDb
	ot = CDB.ObjectType('SEQUENCES')
	seqflds = {'KEY': entry_key, 'EXPERIMENT': entry_exper}
	return CDB.ObjectID(ot, seqflds)
	
def update_contig_status(entry_key, entry_exper, status):
	"""updates the CONTIGSTATUS in table SEQUENCES using status"""
	CDB = bns.ConnectedDb
	seqobject = get_sequence_objectid(entry_key, entry_exper)
	ot = seqobject.GetType()
	lx = seqobject.GetExpression()
	action = CDB.ObjAction('Set contig status')
	objaction = CDB.ObjectSpecifAction(action, seqobject)
	objaction.UpdateSingleField(ot, 'CONTIGSTATUS', lx, status)
	objaction.Close()
	action.Close()
	return True
	
def get_contig_status(entry_key, entry_exper):
	db = bns.ConnectedDb
	keycol = db.DbColumn('KEY').Equal(entry_key)
	genecol = db.DbColumn('EXPERIMENT').Equal(entry_exper)
	lx = keycol & genecol
	records = db.DbRecordSet('SEQUENCES', ['CONTIGSTATUS'])
	result = records.Select(lx)
	result = list(result)
	return result[0]['CONTIGSTATUS']
	
def is_approved(entry_key, entry_exper):
	status = get_contig_status(entry_key, entry_exper)
	if status == 'OK':
		return True
	else:
		return False

if __name__ == '__main__':
	#get the list of selected entries
	entries = list(bns.Database.Db.Selection)
	if not len(entries):
		bns.Util.Program.MessageBox('Information', 
								'No entries selected', 'exclamation')
		__bnscontext__.Stop()
	
	#get list of all experiments in database
	experiments = [ex.Name for ex in bns.Database.Db.ExperimentTypes]
	experlist = []
	for item in experiments:
		#we don't want the 'merged' experiment or protein sequences
		if not (item.startswith('merged') or item.endswith('TRANSL')):
			#only look for sequence type experiments [SEQ]
			if bns.Database.ExperimentType(item).Class == 'SEQ':
				experlist.append(item)
	
	updated = False #restart when updated
	for entry in entries:
		profile = {}
		key = entry.Key	
		for exper in experlist:
			if bns.Database.Experiment(key, exper).ExperID:
				if is_approved(key, exper):
					#set it disapproved using . for status
					updated = update_contig_status(key, exper, '.')
					
	if updated:
		response = bns.Util.Program.MessageBox('Restart', 
		'Please restart Bionumerics to reload the database.\n'\
		'Do you want to restart now?\n\nWARNING: this will close all '\
		'opened windows without saving, with possible loss of data.', 
		'question+yesno+defbutton2')
		
		if response == 1:
			bns.Database.bnsIntern.db.Restart('')
		
