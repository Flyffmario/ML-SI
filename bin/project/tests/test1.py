# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:48:01 2020

@author: Stagiaire
"""

import sys

#import os
#from pathlib import Path
#root_folder=Path(os.getcwd()).parent

root_folder="../"
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.entryprocessing
#import mlsi.learning

try:
    file=open("Spectres_autres_Concatenes_Flavus1_compacted.txt",'r')
    file.close()
    file2=open("Spectres_clones_Concatenes_Flavus1_compacted.txt",'r')
    file2.close()
    print("[INFO] Compacted files already existing. Bypassing...")
except:
    print("[INFO] Compacted files not existing. Creating...")
    mlsi.entryprocessing.compactEntries("Spectres_autres_Concatenes_Flavus1.txt")
    mlsi.entryprocessing.compactEntries("Spectres_clones_Concatenes_Flavus1.txt")
    print("[INFO] Done !")
    
autres=mlsi.entryprocessing.extractCompactedEntries("Spectres_autres_Concatenes_Flavus1_compacted.txt")
clones=mlsi.entryprocessing.extractCompactedEntries("Spectres_clones_Concatenes_Flavus1_compacted.txt")

#mlsi.learning.learn(autres,clones)