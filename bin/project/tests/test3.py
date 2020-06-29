# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 16:13:55 2020

@author: Stagiaire
"""


#from tkinter import Tk
#from tkinter.filedialog import askopenfilename, askdirectory

root_folder="../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.entryprocessing
import mlsi.msi
import mlsi.learning

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sklearn
from sklearn.neural_network import MLPClassifier
import sklearn.preprocessing

print(sklearn.__version__)

import matplotlib.pyplot as plt

#%%
#EntryProcessing Part

#%%

#ATTENTION ! Choisissez la racine de fichier où toutes les entrées sont !
#La fonction va normaliser la base, et la concaténer en un fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
working_directory=mlsi.entryprocessing.browserDirectory()
used_function=mlsi.msi.MSI2
#Fin des paramètres de base

#DEBUT PIPELINE

working_directory=os.path.normpath(working_directory) #Normalisation Windows/Linux
mlsi.entryprocessing.updateDatabase(working_directory,used_function) #Update, Normalisation et Importation

latest_file=mlsi.entryprocessing.findLatestConcatenatedFile(working_directory, used_function)
df=mlsi.entryprocessing.extractConcatenatedEntriesAndConvertToPandas(latest_file,limit=1000)

print(df)
