# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 15:48:51 2020

@author: Stagiaire
"""

import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

def learn(donnees_autres,donnees_clones,proportion_entrainement=80):
    #RegressionLogistique !
    #Ratio 80/20 Entraînement/Test

    ratio_entrainement=int((proportion_entrainement/100)*len(donnees_autres))
    
    #On doit définir deux choses :
    #- Une liste qui contient tous les paramètres à analyser (donc le contenu des txt)
    #- Une liste qui qualifie si un échantillon correspondant à la liste précédente est un clone ou un autre
    #   - on définira 0 comme autres et 1 comme clone


    #Extraire d'abord les données
    autres_entrainement=donnees_autres[:ratio_entrainement]
    clones_entrainement=donnees_clones[:ratio_entrainement]
    entrainement=autres_entrainement+clones_entrainement
    verite_entrainement=[0]*len(autres_entrainement)+[1]*len(clones_entrainement)
    
    autres_test=donnees_autres[ratio_entrainement:]
    clones_test=donnees_clones[ratio_entrainement:]
    test=autres_test+clones_test
    verite_test=[0]*len(autres_test)+[1]*len(clones_test)
    

    clf = LogisticRegression(random_state=0,max_iter=1000).fit(entrainement, verite_entrainement)
    #print(clf.predict(test))
    #print()
    test_score=clf.predict_proba(test)
    print(test_score[:,1])
    tn,fp,fn,tp=confusion_matrix(verite_test,clf.predict(test)).ravel()
    sensibilite=tp/(tp+fn)
    specificite=tn/(tn+fp)
    
    '''
    plt.figure()
    df_cm = [[tp,fn],[fp,tn]]
    # plt.figure(figsize=(10,7))
    legende={'Info Réelle':('Clone','Normal'),'Info calculée':('Clone','Normal')}
    sn.set(font_scale=1.4) # for label size
    sn.heatmap(df_cm, annot=True, annot_kws={"size": 16},index='Info Réelle',columns='Info') # font size
    plt.show()
    '''
    
    #COURBE ROC
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(2):
        fpr[i], tpr[i], _ = roc_curve(verite_test,test_score[:,1])
        roc_auc[i] = auc(fpr[i], tpr[i])
    
    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(verite_test, test_score[:,1])
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
    
    print("Vraies souches : {} ; Fausses souches : {} ; Faux Clones : {} ; Vrais Clones : {}".format(tn,fn,fp,tp))
    print("Sensibilité = {} ; Specificité = {}".format(sensibilite,specificite))