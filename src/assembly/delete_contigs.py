"""Delete contigs(if present) from sequence experiments of selected entries. 
Traces are not removed from the assembly.
Experiment names that start with 'merged' and end with 'TRANSL' are ignored.
Changes made to traces are not reverted. It is not clear how to do this.

"""
import bns
MessageBox = bns.Util.Program.MessageBox
Stop = __bnscontext__.Stop

#get list of selected entries
selected = bns.Database.Db.Selection
if not len(selected):
    MessageBox('Information', 'No entries selected', 'information')
    Stop()

#create list of experiments
experiments = []
for item in bns.Database.Db.ExperimentTypes:
    exper = item.Name
    if (item.Class == 'SEQ' and not(exper.startswith('merged') or 
                                exper.endswith('TRANSL'))):
        experiments.append(exper)

#iterate over selection. remove contigs if present
asm = bns.Sequences.Assembly()
for entry in selected:
    key = entry.Key
    
    for exper in experiments:
        if asm.IsPresent(key, exper):
            asm.Load(key, exper)
            num_contigs = len(asm.Contigs)

            if num_contigs:
                asm.OpenWindow(key, exper)
                #remove all sequences from contig which also removes the contig
                
                for i in range(num_contigs):
                    for j in range(len(asm.Sequences)):
                        asmseq = bns.Sequences.AsmSequence(asm, j)
                        if asmseq.GetContig():
                            asmseq.ContigRemove()
                            
                #remove 'Approved' status of experiment
                asm.ProjectStatus = 0
                asm.Save()
            asm.Close()
    
MessageBox('Finished', 'Finished deleting assemblies', 'information')
