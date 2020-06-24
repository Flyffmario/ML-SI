# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 13:54:57 2020

@author: Stagiaire
"""

import numpy as np
import dateutil
from sklearn.model_selection import train_test_split

import tensorflow as tf
import ast
import pandas as pd

from sklearn.preprocessing import normalize

from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

from sklearn.utils.class_weight import compute_sample_weight

from sklearn.metrics import roc_curve, auc

from scipy import sparse
from scipy.sparse.linalg import spsolve

size = 10000

# def from_np_array(array_string):
#     array_string = ''.join(array_string.replace('[ ', '[').split())
#     #print(array_string)
#     return np.array(ast.literal_eval(array_string))[:size]


# def preparationss_spectre(spectre_lu):
#     bq = False
#     #####################################
#     #Lissage sur une fenêtre de taille 9#
#     #####################################
#     liss = 9
#     a = len(spectre_lu)
#     i = 0
#     N = 9
    
#     spectre_liss = np.convolve(spectre_lu, np.ones((N,))/N, mode='valid')

    
#     ###############
#     #Calcul montée#
#     ###############

#     spectre = []
#     i = 0
#     montee = 0
#     for i in range(len(spectre_liss)- 1):
#         if spectre_liss[i+1] >= spectre_liss[i]:#compare d'abord la valeur lissée puis le i
#             montee = montee + spectre_liss[i+1] - spectre_liss[i]#Si ça monte, on cumule sur toute la montée
#         else:
#             montee = 0
#         #on ajoute un triplet (montée, masse, intensité), montée ne peut pas petre négatif
#         spectre.append([montee, i,spectre_lu[i]])     
#     pic_list = np.zeros(a)
#     i = 0
#     ################
#     #Selection pics#
#     ################
    
#     for i in range(len(spectre) - 1):
#         if spectre[i][0] > spectre[i+1][0] and spectre[i][0]>200:#Si on a une pente plus forte avant qu'après et pente > 20
#             pic_list[i] = spectre[i][0]#Alors c'est un pic
#     sortes = np.sort(pic_list)
#     threshold = sortes[-100] ################################ CHANGER ICI POUR NOMBRE DE PICS ##########################""
#     pic_list = np.where(pic_list < threshold, 0, pic_list)
#     #print(pic_list.reshape(-1,10000).shape)
#     pic_list = normalize(pic_list.reshape(-1,size),norm='l1', axis = 1).reshape(size)
#     #print(pic_list.shape)
#     return pic_list*100

# def baseline_als(y, lam = 10000, p = 0.01, niter=10):
#     L = len(y)
#     D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
#     w = np.ones(L)
#     for i in range(niter):
#         W = sparse.spdiags(w, 0, L, L)
#         Z = W + lam * D.dot(D.transpose())
#         z = spsolve(Z, w*y)
#         w = p * (y > z) + (1-p) * (y < z)
#     return y-z

# def func(spectre):
#     return preparationss_spectre(from_np_array(spectre))
#     #return baseline_als(from_np_array(spectre))
# df = pd.read_csv("flavus.csv", converters={'data': func})
# df_2 = pd.read_csv("flavus_3.csv", converters={'data': func})

# def df_train_test(test_list, plaque, df, test = False): #test = False sert uniquement à supprimer les doublons de clone Flavus
#     df_filtered = df
#     train_indices = np.ones(len(df_filtered), dtype=bool)
#     test_indices = np.zeros(len(df_filtered), dtype=bool)

#     #Ici il s'agit de placer les éléments de la liste dans les listes train ou test
#     #qui sont disjointes
#     for souche in test_list:
#         train_indices = train_indices & (df_filtered['souche'] != souche)
#         test_indices = test_indices | (df_filtered['souche'] == souche)
#     if plaque != None:
#         df_train = df_filtered[train_indices & (df_filtered['plaque'] != plaque)]
#         if test and 'doublon' in df_2.keys():
#             df_test = df_filtered[test_indices & (df_filtered['plaque'] == plaque) & (df_filtered['doublon'] == 0)] 
#         else:
#             df_test = df_filtered[test_indices & (df_filtered['plaque'] == plaque)]
#     else:
#         df_train = df_filtered[train_indices]
#         df_test = df_filtered[test_indices] 

#     #print("taille df_train : ",len(df_train), "         taille df_len : ",len(df_test))
#     #print(df_filtered['souche'].unique(), test_list)

#     return df_train,df_test


# def training_arrays(df_train, df_test, select_column, select_value):
#     """Etant donné df_train et df_test, renvoie les données d'entrainements 
#     X_test et X_train
#     Les labels sont aussi selectionné pour savoir ce que l'on veut séparer, 
#     en fonction d'une colone et d'une valeur associée"""
#     X_train = np.stack(df_train['data'])
#     y_train = np.where(np.array(df_train[select_column] == select_value),0,1)
#     y_train = tf.keras.utils.to_categorical(y_train, num_classes=2)
#     if len(df_test) != 0:
#         X_test = np.stack(df_test['data'])
#         y_test = np.where(np.array(df_test[select_column] == select_value),0,1)
#         y_test = tf.keras.utils.to_categorical(y_test, num_classes=2)
#     else:
#         X_test = np.array([]).reshape(0,10000,1)
#         y_test = np.array([]).reshape(0,2)

    
    

#     #y_train = np.where(np.array(df_train['isolat'] == 'R3'),2,y_train)
#     #y_test = np.where(np.array(df_test['isolat'] == 'R3'),2,y_test)

    
    

#     return X_train, X_test, y_train, y_test





# def single_class_accuracy(y_true, y_pred, INTERESTING_CLASS_ID):
#     class_id_true = tf.argmax(y_true, axis=-1)
#     class_id_preds = tf.argmax(y_pred, axis=-1)
#     # Replace class_id_preds with class_id_true for recall here
#     accuracy_mask = tf.cast(tf.equal(class_id_preds, INTERESTING_CLASS_ID), 'int32')
#     class_acc_tensor = tf.cast(tf.equal(class_id_true, class_id_preds), 'int32') * accuracy_mask
#     class_acc = tf.keras.backend.sum(class_acc_tensor) / tf.maximum(tf.keras.backend.sum(accuracy_mask), 1)
#     return class_acc

#%%

dropout = 0.3
def model_simple():
    model = tf.keras.models.Sequential([
        tf.keras.layers.GaussianNoise(500),
        tf.keras.layers.Conv1D(8, 3, input_shape = (10000,1)),
        tf.keras.layers.AveragePooling1D(),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.Dropout(dropout),
        tf.keras.layers.Conv1D(8, 3),
        tf.keras.layers.AveragePooling1D(),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.Dropout(dropout),
        
        tf.keras.layers.Conv1D(8, 3),
        tf.keras.layers.AveragePooling1D(),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.Dropout(dropout),
        
        tf.keras.layers.Flatten(),
        #tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dropout(dropout),
        #tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')
        #tf.keras.layers.Dense(1, activation='linear')
    ])
    return model
def model_complex():
    model = tf.keras.models.Sequential([
        #tf.keras.layers.GaussianNoise(500),
        tf.keras.layers.Conv1D(8, 50, input_shape = (10000,1)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.MaxPooling1D(),
        tf.keras.layers.Dropout(dropout),
        tf.keras.layers.Conv1D(16, 25),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.MaxPooling1D(),
        tf.keras.layers.Dropout(dropout),
        tf.keras.layers.Conv1D(32, 10),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.MaxPooling1D(),
        tf.keras.layers.Dropout(dropout),
        tf.keras.layers.Conv1D(64, 10),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.MaxPooling1D(),
        tf.keras.layers.Dropout(dropout),
        #tf.keras.layers.Conv1D(16, 10),
        #tf.keras.layers.AveragePooling1D(),
        #tf.keras.layers.BatchNormalization(),
        #tf.keras.layers.ReLU(),
        #tf.keras.layers.Dropout(dropout),
        #tf.keras.layers.Conv1D(16, 10),
        #tf.keras.layers.AveragePooling1D(),
        #tf.keras.layers.BatchNormalization(),
        #tf.keras.layers.ReLU(),
        #tf.keras.layers.Dropout(0.2),
        
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(140, activation='relu'),
        #tf.keras.layers.Dropout(dropout),
        #tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(130, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')
        #tf.keras.layers.Dense(1, activation='linear')
    ])
    return model

def precision_model(test_list, plaque,df):
    
    #Mesure du fitting du modèle complexe
    
    #Split des données
    df_train, df_test = df_train_test(test_list,plaque,df)
    X_train, X_test, y_train, y_test = training_arrays(df_train, df_test, 'clone', 'CL')
    
    #==== A COPIER ====
    #Préparation à l'entraînement du modèle complexe
    mc = tf.keras.callbacks.ModelCheckpoint('best_model_flavus.h5', monitor='val_accuracy', mode='max', verbose=0, save_best_only=True)
    model = model_complex()
    model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False),
                loss='categorical_crossentropy',
                metrics=['accuracy'])
    
    #Entraînement
    if X_test.shape[0] != 0:
        model.fit(X_train.reshape((-1,10000,1)), y_train, epochs=50,verbose = 1,validation_data=(X_test.reshape((-1,10000,1)), y_test), callbacks=[mc], class_weight={0:5,1:1},batch_size = 16)
        model.load_weights('best_model_flavus.h5')
    else:
        #print("coucou")
        model.fit(X_train.reshape((-1,10000,1)), y_train, epochs=50,verbose = 0, callbacks=[], class_weight={0:1,1:1})
    
    return model
    #==== FIN A COPIER ====

#%%
def model_list_predict(X_test, model_list):
    k = []
    for model in model_list:
        k.append(np.argmax(model.predict(X_test.reshape(-1,size,1)), axis = 1))
    return np.where(np.sum(np.array(k), axis = 0)>(len(model_list)/2),1,0)


def evaluate_list(model_list,y_test,X_test,y_train = None, X_train = None):
    #print(X_test.shape)
    y_pred = model_list_predict(X_test,model_list)
    cc = tf.math.confusion_matrix(np.argmax(y_test, axis = 1), y_pred)
    print(cc.numpy())
    if y_train != None:
        print("""Score sur test : """,accuracy_score(np.argmax(y_test,axis = 1), y_pred),
          """\nScore sur train : """,accuracy_score(np.argmax(y_train,axis = 1), y_pred))
    else:
        print("""Score sur test : """,accuracy_score(np.argmax(y_test,axis = 1), y_pred))
        
def errors(model_list, X_test, y_test):
    y_pred = model_list_predict(X_test, model_list)#model.predict_classes(X_test.reshape((-1,10000,1)))

    ind = []
    y_test_c = np.argmax(y_test, axis = 1)
    for i, classe in enumerate(y_pred):
        if classe != y_test_c[i]:
            ind.append(i)
    for i in ind:
        df_err = df_test.iloc[i]
        if 'âge' in df_err.keys():
            print("souche : ",df_err['souche'],"   âge : ",df_err['âge'],"   passage : ",df_err['passage'],"   plaque",df_err['plaque'])
        else:
            print("souche : ",df_err['souche'],"   maldi : ", df_err['maldi'],"    date : ", df_err['date'],"    clone : ", df_err['clone'])


#%%

def evaluate(model,y_test,X_test,y_train = None, X_train = None):
    #print(X_test.shape)
    y_pred = model.predict_classes(X_test.reshape(-1,size,1))
    cc = tf.math.confusion_matrix(np.argmax(y_test, axis = 1), y_pred)
    print(cc.numpy())
    if y_train != None:
        print("""Score sur test : """,accuracy_score(np.argmax(y_test,axis = 1), y_pred),
          """\nScore sur train : """,accuracy_score(np.argmax(y_train,axis = 1), y_pred))
    else:
        print("""Score sur test : """,accuracy_score(np.argmax(y_test,axis = 1), y_pred))
        

def error(model, X_test, y_test):
    y_pred = model.predict(X_test)#model.predict_classes(X_test.reshape((-1,10000,1)))

    ind = []
    y_test_c = np.argmax(y_test, axis = 1)
    for i, classe in enumerate(y_pred):
        if classe != y_test_c[i]:
            ind.append(i)
    for i in ind:
        df_err = df_test.iloc[i]
        if 'âge' in df_err.keys():
            print("souche : ",df_err['souche'],"   âge : ",df_err['âge'],"   passage : ",df_err['passage'],"   plaque",df_err['plaque'])
        else:
            print("souche : ",df_err['souche'],"   maldi : ", df_err['maldi'],"    date : ", df_err['date'],"    clone : ", df_err['clone'])