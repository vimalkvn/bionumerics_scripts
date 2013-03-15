"""Functions for reading primer files"""
import os
import glob


def readPrimer(fname):
	"""Read primer sequence from the given primer file"""
	primer = fdata = ""
	with open(fname) as f:
		primer = os.path.basename(os.path.splitext(fname)[0])
		fdata = f.readline().strip()
	return primer, fdata


def getList(primer_path, extension="txt"):
	"""Return list of primer files in path (*.txt)"""
	flist = glob.glob(primer_path + "\*.{0}".format(extension))
	return flist


def getPrimers(primer_path, extension="txt"):
	"""Read primer files and return data as a dictionary of
	{primer name: primer data}

	"""
	primer_list = {}
	messages = []
	if not os.path.isdir(primer_path):
		messages.append("Primer path is not valid\n{0}\n".format(primer_path))
		return primer_list, messages

	files = getList(primer_path, extension)
	if not len(files):
		messages.append("No primer files found at \n{0}\n".format(primer_path))
		return primer_list, messages

	for item in files:
		primer_name, primer_seq = readPrimer(item)
		if primer_seq in primer_list.values():
			for key, value in primer_list.iteritems():
				if primer_seq == value:
					msg = ("Primer {0} is a duplicate of {1}"
						"<br><br>Please delete before "
						"proceeding".format(primer_name, key))
					messages.append(msg)
					break
			continue
		else:
			primer_list[primer_name] = primer_seq
	return primer_list, messages
