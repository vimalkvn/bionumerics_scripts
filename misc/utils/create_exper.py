"""Create sequence experiments using experiment names from AB1 files

file name format: Well_Strain_Experiment_Anything.ab1 

Change TESTING to False to create the actual experiments
"""
TESTING = False

import bns
import os
import glob
MessageBox = bns.Util.Program.MessageBox

#directory containing AB1 files
source_dir = r'C:\Users\vimal\Workspace\bionumerics_new\data\ANAP000463_2011-07-20\*.ab1'
flist = glob.glob(source_dir)
exper_present = []
exper_absent = []

#get list of experiments
db_exper = [item.Name for item in bns.Database.Db.ExperimentTypes]
for item in flist:
	fname = os.path.basename(item)
	exper = fname.split('_')[2]
	if exper in db_exper:
		exper_present.append(exper)
	else:
		exper_absent.append(exper)

exper_absent = set(exper_absent)
if not len(exper_absent):
	MessageBox('Information', 'No experiments to add', 'information')
	__bnscontext__.Stop()

exper_present = set(exper_present)
msg = 'Will create the following experiments\n\n%s\n\n' % ', '.join(exper_absent)
if len(exper_present):
	msg += 'These experiments exist in database\n\n%s\n\n' % ', '.join(exper_present)

if TESTING:
	msg += 'Please change TESTING=False to create these experiments\n' 

MessageBox('Information', msg, 'information')

if not TESTING:
	for exper in exper_absent:
		#create a Sequence type experiment
		bns.Database.Db.ExperimentTypes.Create(exper, 'SEQ')
		__bnscontext__.SetBusy('Created %s' % exper)
			
__bnscontext__.SetBusy('Finished')

