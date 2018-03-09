misc --- Miscellaneous scripts
==============================
This directory is organized into the following sub-directories. 

assembly
--------
* ``approve_assemblies.py`` - Approve all assemblies for selected entries.
* ``delete_contigs.py`` - Delete contigs(if present) from sequence experiments 
  of selected entries.
* ``disapprove_assemblies.py`` - Disapprove all assemblies for selected entries.  
* ``import_traces.py`` - Import ABI sequence trace files into a connected 
  database.

gui
---
* ``set_field.py`` - A simple PyQt based dialog application to set field value of 
  selected entries. (`Related blog post <https://vimal.io/pyqt-interfaces-in-bionumerics-6/>`__).
* ``setfielddlg.ui`` - Qt Designer user interface definition file (XML Format).

utils
-----
* ``bn6_epydoc.py`` - Generate epydoc documentation of Bionumerics 6
  Python modules.
* ``concat_characters.py`` - Concatenate sequences in a character set 
  experiment for a list of keys.
* ``create_exper.py`` - Create sequence experiments using experiment names from 
  AB1 files.
* ``dbf.py`` - Common database functions.
* ``delete_subsets.py`` - Delete all empty subsets.
* ``logging_example.py`` - Using the python logging module.
* ``unittest_example.py`` - Using the unittest module.

