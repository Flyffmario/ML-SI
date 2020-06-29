# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 15:48:51 2020

@author: Stagiaire
"""

root_folder=".../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import matplotlib.pyplot as plt

import numpy as np
import tensorflow as tf

import sklearn
print(sklearn.__version__)
import sklearn.metrics
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import accuracy_score

#import neat
#from sklearn.linear_model import LogisticRegression
#from sklearn.metrics import roc_curve, auc

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
    
    '''
    Stocker à nouveau les données à chaque fois est une mauvaise idée
    La RAM crash sinon..
    '''
    
    def __init__(self,algorithm):
        #ctr
        self.algorithm=algorithm
        
    def showDataCharacteristics(self,data):
        matrix_len=len(data[0])
        unbalanced_matrix=False
        for entry in data:
            if len(entry)!=matrix_len:
                unbalanced_matrix=True
        if unbalanced_matrix==True:
            print("[WARN] Matrice irrégulière. Veuillez vérifier la taille de chaque entrée.")
            for entry in data:
                print(len(entry))
        else:
            print("[INFO] Matrice régulière. Rien à signaler. Taille = {}x{}".format(len(self.data),matrix_len))
            
    def testAccuracy(self,data,veritas):
        scores = sklearn.model_selection.cross_val_score(self.algorithm, data, veritas, cv=5)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores.mean(), scores.std()*2
    
    def train(self,X_train,Y_train):
        
        self.algorithm.fit(X_train,Y_train)
        
    def confusionMatrix(self,X_test,Y_test,dict_veritas):
        class_names=dict_veritas.values()
        titles_options=[("Confusion Matrix, Nb. of cases",None),("Confusion Matrix, Normalized",'true')]
        
        for title,normalize in titles_options:
            disp=plot_confusion_matrix(
                self.algorithm,X_test,Y_test,
                display_labels=class_names,
                cmap=plt.cm.Blues,
                normalize=normalize
                )
            disp.ax_.set_title(title)            
            print(title)
            
        plt.show()
        
        return disp.confusion_matrix

#NEAT est plutôt du learning par renforcement
# class NEATClassifier:
#     # 2-input XOR inputs and expected outputs.
    
    
#     def __init__(self):
#         self.xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
#         self.xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]
    
    
#     def eval_genomes(self,genomes, config):
#         for genome_id, genome in genomes:
#             genome.fitness = 4.0
#             net = neat.nn.FeedForwardNetwork.create(genome, config)
#             for xi, xo in zip(self.xor_inputs, self.xor_outputs):
#                 output = net.activate(xi)
#                 genome.fitness -= (output[0] - xo[0]) ** 2
    
    
#     def run(self,config_file):
#         # Load configuration.
#         config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
#                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
#                              config_file)
    
#         # Create the population, which is the top-level object for a NEAT run.
#         p = neat.Population(config)
    
#         # Add a stdout reporter to show progress in the terminal.
#         p.add_reporter(neat.StdOutReporter(True))
#         stats = neat.StatisticsReporter()
#         p.add_reporter(stats)
#         p.add_reporter(neat.Checkpointer(5))
    
#         # Run for up to 300 generations.
#         winner = p.run(self.eval_genomes, 300)
    
#         # Display the winning genome.
#         print('\nBest genome:\n{!s}'.format(winner))
    
#         # Show output of the most fit genome against training data.
#         print('\nOutput:')
#         winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
#         for xi, xo in zip(self.xor_inputs, self.xor_outputs):
#             output = winner_net.activate(xi)
#             print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))
    
#         p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
#         p.run(self.eval_genomes, 10)

#%%

def electBestAccuracy(listOfStudies,data,veritas,X_train,X_test,y_train,y_test):
    
    podium=[]
    
    for i in range(len(listOfStudies)):
        
        if isinstance(listOfStudies[i],tf.keras.models.Sequential):
            #do things specific to tf.keras
            evaluate(listOfStudies[i],y_test,X_test,y_train=y_train,X_train=X_train)
        else:
            podium.append([listOfStudies[i],listOfStudies[i].testAccuracy(data,veritas),i])
        
    podium = sorted(podium, key=lambda podium:podium[1][0])#tri par intensite
    podium.reverse()
    podium_bests=podium[:10] #10 meilleurs
    podium_worst=podium[-10:] #10 pires
            
    return podium_bests,podium_worst

def model_list_predict(X_test, model_list):
    size=10000
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
        
#def errors(model_list, X_test, y_test):
#    y_pred = model_list_predict(X_test, model_list)#model.predict_classes(X_test.reshape((-1,10000,1)))
#
#    ind = []
#    y_test_c = np.argmax(y_test, axis = 1)
#    for i, classe in enumerate(y_pred):
#        if classe != y_test_c[i]:
#            ind.append(i)
#    for i in ind:
#        df_err = df_test.iloc[i]
#        if 'âge' in df_err.keys():
#            print("souche : ",df_err['souche'],"   âge : ",df_err['âge'],"   passage : ",df_err['passage'],"   plaque",df_err['plaque'])
#        else:
#            print("souche : ",df_err['souche'],"   maldi : ", df_err['maldi'],"    date : ", df_err['date'],"    clone : ", df_err['clone'])

def evaluate(model,y_test,X_test,y_train = None, X_train = None):
    size=10000
    #print(X_test.shape)
    y_pred = model.predict_classes(X_test.reshape(-1,size,1))
    cc = tf.math.confusion_matrix(np.argmax(y_test, axis = 1), y_pred)
    print(cc.numpy())
    return accuracy_score(np.argmax(y_test,axis = 1), y_pred)
        

#def error(model, X_test, y_test):
#    y_pred = model.predict(X_test)#model.predict_classes(X_test.reshape((-1,10000,1)))
#
#    ind = []
#    y_test_c = np.argmax(y_test, axis = 1)
#    for i, classe in enumerate(y_pred):
#        if classe != y_test_c[i]:
#            ind.append(i)
#    for i in ind:
#        df_err = df_test.iloc[i]
#        if 'âge' in df_err.keys():
#            print("souche : ",df_err['souche'],"   âge : ",df_err['âge'],"   passage : ",df_err['passage'],"   plaque",df_err['plaque'])
#        else:
#            print("souche : ",df_err['souche'],"   maldi : ", df_err['maldi'],"    date : ", df_err['date'],"    clone : ", df_err['clone'])

#%%

def MSI4CropNTriplets(data,n):
    new_data=[]
    for i in data:
        new_data.append(i[:(3*n)])
    return new_data

def mergeClasses(veritas,dict_veritas,merged_id,being_merged_id):
    #merged_id --> being_merged_id
    #On merge 3 vers 2 : merged_id=3, being_merged_id=2

    new_veritas=veritas
    for i in range(len(new_veritas)):
        if new_veritas[i]==merged_id:
            new_veritas[i]=being_merged_id
            
    new_dict=dict_veritas
    del new_dict[merged_id]
    
    #Il faut minimiser le nombre de classes décrites
    #Il peut y avoir des trous genre 0,2,3,4,5..
    #On doit trouver ces trous, et les combler.
    
    return new_veritas,new_dict
    
#%%

#Code Aurélien

def model_simple():
    dropout = 0.3
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
def model_complex(size):
    dropout = 0.3
    model = tf.keras.models.Sequential([
        #tf.keras.layers.GaussianNoise(500),
        tf.keras.layers.Conv1D(8, 50, input_shape = (None,size)),
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
        tf.keras.layers.Dense(2, activation='softmax',input_shape = (None,size))
        #tf.keras.layers.Dense(1, activation='linear')
    ])
    return model

def precision_model(base_model,X_train,X_test,y_train,y_test):
    
    size=len(X_train)
    length=len(X_train[0])
    
    #Mesure du fitting du modèle complexe
    
    #Préparation à l'entraînement du modèle complexe
    model=base_model
    mc = tf.keras.callbacks.ModelCheckpoint('best_model_flavus.h5', monitor='val_accuracy', mode='max', verbose=0, save_best_only=True)
    model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False),
                loss='categorical_crossentropy',
                metrics=['accuracy'])
    
    np_X_train=np.array(X_train)
    np_y_train=np.array(y_train)
    np_X_test=np.array(X_test)
    np_y_test=np.array(y_test)
    
    #Entraînement
    if X_test.shape[0] != 0:
        model.fit(np_X_train.reshape(-1,size,1), np_y_train, epochs=50,verbose = 1,validation_data=(np_X_test.reshape(-1,size,1), np_y_test), callbacks=[mc], class_weight={0:5,1:1},batch_size=length)
        model.load_weights('best_model_flavus.h5')
    else:
        #print("coucou")
        model.fit(np_X_train.reshape(-1,size,1), np_y_train, epochs=50,verbose = 0, callbacks=[], class_weight={0:1,1:1})
    
    return model     

#%%

