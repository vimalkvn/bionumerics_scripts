"""Delete all empty subsets"""
import bns
MessageBox = bns.Util.Program.MessageBox

#get a list of subsets
subsets = bns.Database.Db.Subsets

for subset in subsets:
	#delete all empty subsets
	if not len(subset):
		__bnscontext__.SetBusy('Deleting subset %s' % subset)
		subsets.Delete(subset)
		
__bnscontext__.SetBusy('Finished')
