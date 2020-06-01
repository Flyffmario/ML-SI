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

import matplotlib.pyplot as plt

#%%
#EntryProcessing Part

#%%

#ATTENTION ! Choisissez la racine de fichier où toutes les entrées sont !
#La fonction va normaliser la base, et la concaténer en un fichier "Spectres_Concatenes_<parent folder>_<date d'édition>_<horaire d'édition>_<mlsi.MSI>.txt"

working_directory=mlsi.entryprocessing.browserDirectory()
used_function=mlsi.msi.MSI4

#Fin des paramètres de base

mlsi.entryprocessing.updateDatabase(working_directory,used_function)

entree=str(input("Do you want to sortBy ? y/[n]"))
if entree=="y":
    chosen_mode=int(input("Specify mode used (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))
    
    latestFile=mlsi.entryprocessing.findLatestConcatenatedFile(working_directory, used_function)
    mlsi.entryprocessing.sortBy(latestFile,mode=chosen_mode)
    mlsi.entryprocessing.compactFeatureRelatedData(working_directory,chosen_mode,limit=100)
else:
    chosen_mode=int(input("Choose feature related data to extract (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))

data,verite,dict_label=mlsi.entryprocessing.extractFeatureRelatedData(working_directory,chosen_mode)
data=mlsi.entryprocessing.castToFloat32(data)
new_data=mlsi.entryprocessing.cropSpecterToMinimumLength(data)

# plt.plot(new_data[0])
# plt.xlabel('position')
# plt.ylabel('hauteur')

#%%
#Learning Part

#%%

'''

https://machinelearningmastery.com/one-vs-rest-and-one-vs-one-for-multi-class-classification/

Inherently multiclass :

    sklearn.naive_bayes.BernoulliNB

    sklearn.tree.DecisionTreeClassifier

    sklearn.tree.ExtraTreeClassifier

    sklearn.ensemble.ExtraTreesClassifier

    sklearn.naive_bayes.GaussianNB

    - sklearn.neighbors.KNeighborsClassifier

    sklearn.semi_supervised.LabelPropagation

    sklearn.semi_supervised.LabelSpreading

    sklearn.discriminant_analysis.LinearDiscriminantAnalysis

    sklearn.svm.LinearSVC (setting multi_class=”crammer_singer”)

    - sklearn.neural_network.MLPClassifier

    sklearn.neighbors.NearestCentroid

    sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis

    sklearn.neighbors.RadiusNeighborsClassifier

    sklearn.ensemble.RandomForestClassifier

    sklearn.linear_model.RidgeClassifier

    sklearn.linear_model.RidgeClassifierCV
    
Multiclass as One-Vs-One:

    sklearn.svm.NuSVC

    sklearn.svm.SVC.

    sklearn.gaussian_process.GaussianProcessClassifier (setting multi_class = “one_vs_one”)

Multiclass as One-Vs-The-Rest:

    sklearn.ensemble.GradientBoostingClassifier

    sklearn.gaussian_process.GaussianProcessClassifier (setting multi_class = “one_vs_rest”)

    - sklearn.svm.LinearSVC (setting multi_class=”ovr”)

    sklearn.linear_model.SGDClassifier

    sklearn.linear_model.Perceptron

    sklearn.linear_model.PassiveAggressiveClassifier

'''

listOfAlgorithms=[sklearn.svm.LinearSVC(multi_class="crammer_singer"),
                  sklearn.linear_model.LogisticRegression(random_state=0,multi_class="multinomial"),
                  sklearn.neural_network.MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1),
                  ]

print("Creating List of Studies...")
listOfStudies=[]
for algo in listOfAlgorithms:
    new_study=mlsi.learning.Study(new_data,verite,dict_label,algo)
    listOfStudies.append(new_study)
    
print("Training List of Studies...")
for study in listOfStudies:
    study.train()

print("Electing best accuracy...")
bestStudy=mlsi.learning.electBestAccuracy(listOfStudies)
print(bestStudy)



















