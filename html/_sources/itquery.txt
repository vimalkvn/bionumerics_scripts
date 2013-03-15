itquery --- An interface to query ItemTracker from BioNumerics
==============================================================
Version: ``2.0.8``


About
-----
itquery is a graphical interface to display location information of strains, 
frozen stock's and DNA's stored in a LIMS system (ItemTracker) within a strain 
database maintained in BioNumerics. An "ItemTracker ID" links data related to a 
strain in both databases. 

Features
--------

* Display location information of Strains, Frozen stock's or DNA's in the freezer.
* Display and set/unset the selection status of Strains, Frozen stock's or DNA's in the LIMS database. 
* Display additional information related to an item in both databases (Saved 
  between sessions).
* Get all items marked as selected in the LIMS database.
* Cherry picking view displays status of sequencing (Finished, Repeat, Picked). 
  Filter by user or sequencing status. 
* Export sequence trace information or DNA information related to a strain as 
  a CSV file. 

Citation
--------
itquery is discussed in

`Transforming Microbial Genotyping: A Robotic Pipeline for Genotyping Bacterial Strains <http://www.plosone.org/article/info:doi/10.1371/journal.pone.0048022>`_

O’Farrell B, Haase JK, Velayudhan V, Murphy RA, Achtman M (2012). 
PLoS ONE 7(10): e48022. doi:10.1371/journal.pone.0048022

Requirements
------------
* `BioNumerics <http://applied-maths.com>`_
  
* `ItemTracker <http://www.itemtracker.com>`_
  
* Python 2.6 (tested with 2.6.6)
  
  Download - http://python.org/

* PyQt4 32-bit for Python 2.6 (tested with 4.9.1)
  
  Download - http://www.riverbankcomputing.co.uk/software/pyqt/download

* Database connectivity requires the pyodbc module (not required for demo)
  
  Download - http://code.google.com/p/pyodbc/

Demo
----
Run file :file:`itquery_demo.py`

The main program is ``itquery.py`` would require modification to handle a
specific data structure. A sample of all data structures used for the demo is 
contained in :file:`data.json`. 

Screenshots
-----------

Main Window
...........

.. image:: /images/itquery_mainwindow.png
   :width: 90%

Get all selected view
.....................

.. image:: /images/itquery_getallselected.png
   :width: 90%

Cherry picking view
...................

.. image:: /images/itquery_cherrypicking.png
   :width: 90%
