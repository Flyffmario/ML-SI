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
print(data[0][len(data[0])//2:])

plt.plot(data[0][len(data[0])//2:])
plt.xlabel("index")
plt.ylabel("intensité")
plt.show()

#%%
#Learning Part

#%%

'''

https://machinelearningmastery.com/one-vs-rest-and-one-vs-one-for-multi-class-classification/

'''

listOfAlgorithms=[]

#Création d'une banque d'algos à faire apprendre
for i in range(1,11):
    for j in range (1,2):
        #Note: The default solver ‘adam’ works pretty well on relatively large datasets
        #(with thousands of training samples or more) in terms of both training time and
        #validation score. For small datasets, however, ‘lbfgs’ can converge faster and perform better.
        listOfAlgorithms.append(MLPClassifier(solver='adam', alpha=1e-5,hidden_layer_sizes=(i, j), random_state=1,max_iter=10000))

print("Creating List of Studies...")
listOfStudies=[]
for algo in listOfAlgorithms:
    new_study=mlsi.learning.Study(algo)
    listOfStudies.append(new_study)

print("Electing best accuracy...")
podium=mlsi.learning.electBestAccuracy(listOfStudies,new_data,verite, X_train, X_test, y_train, y_test)

for current_study,score,position in podium[0]:
    i=position//5
    j=position%5+1
    print(current_study,",",score,",",i,",",j)
    
for current_study,score,position in podium[1]:
    i=position//5
    j=position%5+1
    print(current_study,",",score,",",i,",",j)
    
#Entrainement du meilleur algo

best_study=podium[0][0][0]
best_study.train(X_train,y_train)
print(best_study.algorithm.predict(X_test))
print(y_test)

best_study.confusionMatrix(X_test,y_test,dict_label)

#Regression logistique