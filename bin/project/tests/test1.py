# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:48:01 2020

@author: Stagiaire
"""

'''
test1.py
'''

#from tkinter import Tk
#from tkinter.filedialog import askopenfilename, askdirectory

root_folder="../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.entryprocessing
import mlsi.msi
import mlsi.learning

#mlsi.entryprocessing.browserNormalizeDatabase()
#mlsi.entryprocessing.browserCreateconcatenatedEntries(mlsi.msi.MSI2)
#mlsi.entryprocessing.browserUpdateConcatenatedentries()

#mlsi.entryprocessing.browserSortBy()

autres=mlsi.entryprocessing.browserExtractCompactedEntries()
clones=mlsi.entryprocessing.browserExtractCompactedEntries()

autres_adapted=mlsi.entryprocessing.updateSpecterLength(autres)
clones_adapted=mlsi.entryprocessing.updateSpecterLength(clones)

mlsi.learning.learn(autres_adapted,clones_adapted)