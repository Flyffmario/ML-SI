# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 13:54:57 2020

@author: Stagiaire
"""

root_folder="../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.entryprocessing
import mlsi.msi
import mlsi.learning

import os

import sklearn
from sklearn.neural_network import MLPClassifier
import sklearn.preprocessing

print(sklearn.__version__)

import matplotlib.pyplot as plt

#%%

#La fonction va normaliser la base, et la concaténer en un fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"
working_directory=mlsi.entryprocessing.browserDirectory()
used_function=mlsi.msi.MSI2
#Fin des paramètres de base

#DEBUT PIPELINE

working_directory=os.path.normpath(working_directory) #Normalisation Windows/Linux
mlsi.entryprocessing.updateDatabase(working_directory,used_function) #Update, Normalisation et Importation

entree=str(input("Do you want to sortBy ? y/[n]"))
if entree=="y":
    chosen_mode=int(input("Specify mode used (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))
    
    latestFile=mlsi.entryprocessing.findLatestConcatenatedFile(working_directory, used_function)
    mlsi.entryprocessing.sortBy(latestFile,mode=chosen_mode)
    mlsi.entryprocessing.compactFeatureRelatedData(working_directory,chosen_mode)
else:
    chosen_mode=int(input("Choose feature related data to extract (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))

data,verite,dict_label=mlsi.entryprocessing.extractFeatureRelatedData(working_directory,chosen_mode,limit=10) #Extraction des données
print(dict_label)
entree=str(input("Do you want to merge a class ? y/[n]"))
if entree=="y":
  loop_condition="y"
  while loop_condition!="n":
    chosen_class=int(input("Please enter the class being merged : "))
    chosen_class_2=int(input("Please enter the class being merged into : "))
    verite,dict_label=mlsi.learning.mergeClasses(verite, dict_label, chosen_class, chosen_class_2)
    print(dict_label)
    loop_condition=str(input("Do you want to do another class ? [y]/n"))
else:
  pass

#Traitement des données extraites
data=mlsi.entryprocessing.castToFloat32(data)
new_data=mlsi.entryprocessing.cropSpecterToMinimumLength(data)
#new_data=mlsi.learning.MSI4CropNTriplets(new_data, 200)
print("Scaling Data...")
min_max_scaler=sklearn.preprocessing.MinMaxScaler()
new_data=min_max_scaler.fit_transform(new_data)

X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(new_data, verite, test_size=0.2, random_state=42)

#FIN PIPELINE

#%%

base_model=mlsi.learning.model_complex(X_train[0].shape[0])

best_model=mlsi.learning.precision_model(base_model,X_train,X_test,y_train,y_test)

score=mlsi.learning.evaluate(best_model,y_test,X_test,y_train=y_train, X_train=X_train)
print(score)