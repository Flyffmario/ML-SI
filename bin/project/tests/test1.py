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

#mlsi.entryprocessing.normalizeDatabaseModel1()
mlsi.entryprocessing.concatenateEntries(func_used=mlsi.msi.MSI4,liss=6)
#mlsi.entryprocessing.browserSortBy()
