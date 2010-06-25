'''Concatenate sequences in a character set experiment for 
a list of keys. 

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

Requires: experiment name
Requires: dbf module

Optional
Keys to be excluded can be added to the EXCLUDE list

Output
Characters(genes) are concatenated in alphabetical order.

Output will be in the file exp_concat.txt in the 
database path in FASTA format, where exp is the experiment name.

'''

import os
import sys

moduledir = r"E:\users\vimal\Python\Bionumerics" #for dbf
if moduledir not in sys.path:
	sys.path.append(moduledir)

import bns
import dbf


if __name__ == "__main__":
	
	exper = "MLST" #specify experiment name here
	outfile = open(os.path.join(dbf.get_dbpath(), exper + "_concat.txt"), "w")
	keys = dbf.get_all_keys()
	characters = dbf.get_characters(exper)
	
	#list of excluded keys
	EXCLUDE = ["S.typhi", "86155469690", "39518146360", "61197002200", "DBS100", 
	"temp", "RefUserSeqTemporary"]	
	
	for excl in EXCLUDE:
		if excl in keys:
			keys.remove(excl)
	
	for key in keys:
		#remove entries with RefSeq in their key
		if len(key) and key.startswith("RefSeq") is False: 
			concat = ""
			
			for character in sorted(characters):
				seq = bns.Sequences.SequenceData(key, character)
				seqstr = seq.LoadSequence()
				concat += seqstr
	
			outfile.write(">%s\n%s\n" % (key, concat))
	
	outfile.close()