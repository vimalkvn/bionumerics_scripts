'''Generate epydoc documentation of Bionumerics6 Python modules

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
'''

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