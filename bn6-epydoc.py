import bns
import sys

sys.path.append(r'C:\Python26\Lib')
sys.path.append(r'C:\Python26\Lib\site-packages')

sys.__dict__['argv'] = ['--html', '--dotpath', 
r'C:\Program Files\Graphviz2.26.3\bin\dot.exe', '--graph', 'all', 
'--graph-font','times','-o', r'G:\Documents\build\html\bn6python', 
'bns.CallBnsFunction', 'bns.Characters', 'bns.Comparison', 
'bns.ComparisonExtensions', 'bns.ConnectedDb','bns.Database','bns.DST', 
'bns.Fingerprints','bns.Gel2D', 'bns.Graphics','bns.Identification', 
'bns.Matrices','bns.Sequences', 'bns.TrendData','bns.Util','bns.Windows']

logfile = open(r'C:\tmp\bn6-epydoc.log', 'w')
sys.stdout = logfile
sys.stderr = logfile
from epydoc.cli import cli
cli()
logfile.close()