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

import sklearn

#D'abord choisissez l'arborescence de fichiers que vous souhaitez traiter
#ATTENTION ! Choisissez la racine de fichier où toutes les entrées sont !
#La fonction va normaliser la base, et la concaténer en un fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
mlsi.entryprocessing.browserUpdateDatabase(mlsi.msi.MSI2)

#Choisissez le fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
#mlsi.entryprocessing.browserSortBy()
#Choisissez le mode 0

#On compacte les deux fichiers créés
#Penser à faire une fonction qui compacte tous les fichiers Sorted
#mlsi.entryprocessing.browserCompactEntries()
#mlsi.entryprocessing.browserCompactEntries()

data,verite,dict_label=mlsi.entryprocessing.browserExtractFeatureRelatedData('category')
new_data=mlsi.entryprocessing.cropSpecterToMinimumLength(data)

#Étudions la capacité de la nouvelle classe
study=mlsi.learning.Study()

study.data=new_data
study.veritas=verite
study.dict_veritas=dict_label

study.algorithm=sklearn.svm.LinearSVC(random_state=0, tol=1e-5)

study.testAccuracy()
study.train()
study.confusionMatrix()
#study.rocCurve()




















