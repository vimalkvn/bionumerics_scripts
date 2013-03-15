"""BioNumerics functions for iterate_crispr"""
import bns  # IGNORE:F0401 @UnresolvedImport
DB = bns.Database.Db


def getChecklist(experiments):
	"""Get a list of entries and experiments to check

	If there are selected entries, use them else return all items
	in the database

	"""
	selected = DB.Selection
	entries = []
	if len(selected):
		entries = list(selected)
	else:
		entries = DB.Entries

	result = {}
	for entry in entries:
		key = entry.Key
		for exper in experiments:
			if bns.Database.Experiment(key, exper).ExperID:
				try:
					result[key].append(exper)
				except KeyError:
					result[key] = [exper]
	return result


def deleteContigs(asmb):
	"""Remove sequences from a contig if they belong to a contig.

	If all sequences are removed, the contig is removed automatically.

	"""
	if not len(asmb.Contigs):
		return
	for j in range(len(asmb.Sequences)):
		seq = bns.Sequences.AsmSequence(asmb, j)
		if seq.GetContig():
			seq.ContigRemove()
	asmb.Save()
	return
