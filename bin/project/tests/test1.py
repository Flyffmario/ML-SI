# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:48:01 2020

@author: Stagiaire
"""
from tkinter import Tk
from tkinter.filedialog import askopenfilename

root_folder="../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.entryprocessing

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
print("[INFO] A file explorer window has been created. Please look for the file you want to import, compact and extract.")
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
try:
   
    try:
        temp_file=open(filename.split('.txt')[0]+'_compacted.txt','r')
        temp_file.close()
        print("[INFO] Processed version of given file already existing in the current path. Skipping...")
    except:
         print("[INFO] Processing "+filename.split('/')[-1]+"...")
         mlsi.entryprocessing.compactEntries(filename)
         print("[INFO] Process done !")
         
    #Si la version compactée n'existait pas, elle existe maintenant.
    print("[INFO] Extracting "+filename.split('/')[-1].split('.txt')[0]+"_compacted.txt"+"...")
    data=mlsi.entryprocessing.extractCompactedEntries(filename.split('.txt')[0]+'_compacted.txt',limit=20)
    print("[INFO] Extraction done ! Look at the root file of the imported file.")
except:
    print("[ERROR] Not a Valid path or Not a .txt file or Entries not found/not valid in the mentioned file.")

#mlsi.learning.learn(autres,clones)