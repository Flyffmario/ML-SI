# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 15:48:51 2020

@author: Stagiaire
"""

root_folder=".../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)
    
import mlsi.entryprocessing

import matplotlib.pyplot as plt

import sklearn

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

#%%

class Study:
    '''
    Study est une paillasse où seront expérimentés les différents algos de learning.
    
    data=[[descripteurs],[verité]]
    algo
    
    Dans sa structure, il prend :
        - Des données d'entrée : [[descripteurs],[classes]] qu'on peut modifier, ajouter, supprimer... bref on y a accès facilement
        - Un algo de learning : à voir comment on organise, mais idem, on définit ce qu'on veut et fait ce qu'on veut..
    
    Et en retour :
        - On peut entraîner l'algo prévu
        - On peut visualiser les résultats de l'algo, sa structure, ses propriétés, son fonctionnement
onstruc        - On peut configurer à volonté l'algo
        
        - On peut tester l'étude sur des données non triées
        - On peut vérifier son efficacité, ses propriétés et résultats
        
        - On peut exporter l'étude
        
    Seulement, c'est multiclasse (pré-définitions) ou multilabel (propriétés) ?
    MultiLabel semble être plus approprié : on doit pouvoir définir toutes les propriétés d'une souche
    Genre : J3, E3, clonal ou pas
    
    Multioutput-multiclass : on cherche à obtenir des props uniques parmis plusieurs ensembles.
    https://stackoverflow.com/questions/46770088/multioutput-classifier-learning-5-target-variables
    '''
    
    
    def __init__(self):
        #ctr
        
        #Essentiel
        self.data=None
        self.veritas=None
        self.dict_veritas=None
        
        self.algorithm=None
        
        self.X_train=None
        self.Y_train=None
        self.X_test=None
        self.Y_test=None
    
    def testAccuracy(self):
        scores = sklearn.model_selection.cross_val_score(self.algorithm, self.data, self.veritas, cv=5)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores.mean(), scores.std()*2
    
    def train(self,size_of_test=0.2):
        self.X_train, self.X_test, self.Y_train, self.Y_test = sklearn.model_selection.train_test_split(self.data, self.veritas, test_size=size_of_test, random_state=0)
        self.algorithm.fit(self.X_train,self.Y_train)
    
    def confusionMatrix(self):
        tn,fp,fn,tp=confusion_matrix(self.Y_test,self.algorithm.predict(self.X_test)).ravel()
        sensibilite=tp/(tp+fn)
        specificite=tn/(tn+fp)
        
        print("Vraies souches : {} ; Fausses souches : {} ; Faux Clones : {} ; Vrais Clones : {}".format(tn,fn,fp,tp))
        print("Sensibilité = {} ; Specificité = {}".format(sensibilite,specificite))
    
    def rocCurve(self):
        
        test_score=self.algorithm.predict_proba(self.X_test)
        
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(2):
            fpr[i], tpr[i], _ = roc_curve(self.Y_test,test_score[:,1])
            roc_auc[i] = auc(fpr[i], tpr[i])
        
        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(self.Y_test, test_score[:,1])
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
        
        plt.figure()
        lw = 2
        plt.plot(fpr[1], tpr[1], color='darkorange',
                 lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        plt.show()
        
        

#%%

