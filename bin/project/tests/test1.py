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

#D'abord choisissez l'arborescence de fichiers que vous souhaitez traiter
#ATTENTION ! Choisissez la racine de fichier où toutes les entrées sont !
#La fonction va normaliser la base, et la concaténer en un fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
mlsi.entryprocessing.browserUpdateDatabase(mlsi.msi.MSI2)

#Choisissez le fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
mlsi.entryprocessing.browserSortBy()
#Choisissez le mode 0

#Choisissez le fichier trié par catégorie "autres" ("Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>_autres_Sorted.txt")
autres=mlsi.entryprocessing.browserExtractCompactedEntries()
#Choisissez le fichier trié par catégorie "clones" ou "clones masques" ("Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>_clones masques_Sorted.txt")
clones=mlsi.entryprocessing.browserExtractCompactedEntries()

#Partie de Learning et Résultats
autres_adapted=mlsi.entryprocessing.updateSpecterLength(autres)
clones_adapted=mlsi.entryprocessing.updateSpecterLength(clones)
mlsi.learning.learn(autres_adapted,clones_adapted)