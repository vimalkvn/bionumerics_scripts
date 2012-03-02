"""Import ABI sequence trace files into Bionumerics. 

Configuration
source_dir: must be defined
directory containg the sequence traces in ABI format. Other formats 
like SCF would work but not tested. 

File names should be of the form KEY_EXPER. The entry with KEY must be
present in the database. If absent, the files are saved under the
directory called problems under source_dir. 

Imported files will be saved under a directory called 'imported' under
source_dir.

"""
import os.path
import shutil
import glob
import bns

#directory containing abi, ab1 files. must be defined
source_dir = r'C:\Users\vimal\tmp\import_traces'

trace_files = os.path.join(source_dir, '*.ab*')
imported_dir = os.path.join(source_dir, 'imported')
problems_dir = os.path.join(source_dir, 'problems')

#create directories if absent
for dname in (imported_dir, problems_dir):
    if not os.path.exists(dname):
        os.mkdir(dname)
    
#make a list of all KEY's in the database
db_keys = [item.Key for item in bns.Database.Db.Entries]

#make a list of all experiments in the database
db_exper = [item.Name for item in bns.Database.Db.ExperimentTypes]

#get list of abi, ab1 files under source_dir
flist = glob.glob(trace_files)

#sequence object to check and create sequence type experiment if missing
seq = bns.Sequences.Sequence()

#assembly object to import the sequence trace into assembly
asm = bns.Sequences.Assembly()

for item in flist:
    fname = os.path.basename(item)
    items = fname.split('_')
    key, exper = items[0], items[1]
    
    if(key in db_keys) and (exper in db_exper):
        if not seq.Load(key, exper):
            seq.Create(exper, "", key)
        
        asm.OpenWindow(key, exper)
        asm.ImportSeq(item, "ABI")
        
        #if assembly is required uncomment line below
        #asm.AlignAll()
        asm.Save()
        asm.Close()
        new_name =  os.path.join(imported_dir, fname)
    else:
        new_name = os.path.join(problems_dir, fname)
    
    shutil.move(item, new_name)

