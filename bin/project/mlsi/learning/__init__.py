# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 15:48:51 2020

@author: Stagiaire
"""

root_folder=".../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

#import matplotlib.pyplot as plt

import sklearn
#import neat

#from sklearn.linear_model import LogisticRegression
#from sklearn.metrics import confusion_matrix
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
    
    
    def __init__(self,data,veritas,dict_veritas,algorithm):
        #ctr
        
        #Essentiel
        self.data=data
        self.veritas=veritas
        self.dict_veritas=dict_veritas
        
        self.algorithm=algorithm
        
        self.X_train, self.X_test, self.Y_train, self.Y_test = sklearn.model_selection.train_test_split(self.data, self.veritas, test_size=0.2, random_state=0)
    
    def showDataCharacteristics(self):
        matrix_len=len(self.data[0])
        unbalanced_matrix=False
        for entry in self.data:
            if len(entry)!=matrix_len:
                unbalanced_matrix=True
        if unbalanced_matrix==True:
            print("[WARN] Matrice irrégulière. Veuillez vérifier la taille de chaque entrée.")
            for entry in self.data:
                print(len(entry))
        else:
            print("[INFO] Matrice régulière. Rien à signaler. Taille = {}x{}".format(len(self.data),matrix_len))
            
    def testAccuracy(self):
        scores = sklearn.model_selection.cross_val_score(self.algorithm, self.data, self.veritas, cv=5)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        return scores.mean(), scores.std()*2
    
    def train(self):
        self.algorithm.fit(self.X_train,self.Y_train)
        
    def mergeClasses(self,merged_id,being_merged_id):
        #merged_id --> being_merged_id
        #On merge 3 vers 2 : merged_id=3, being_merged_id=2
    
        new_veritas=self.veritas
        for i in new_veritas:
            if i==merged_id:
                i=being_merged_id
                
        new_dict=self.dict_veritas
        del new_dict[merged_id]
        
        self.veritas=new_veritas
        self.dict_veritas=new_dict
    
    # def confusionMatrix(self):
    #     tn,fp,fn,tp=confusion_matrix(self.Y_test,self.algorithm.predict(self.X_test)).ravel()
    #     sensibilite=tp/(tp+fn)
    #     specificite=tn/(tn+fp)
        
    #     print("Vraies souches : {} ; Fausses souches : {} ; Faux Clones : {} ; Vrais Clones : {}".format(tn,fn,fp,tp))
    #     print("Sensibilité = {} ; Specificité = {}".format(sensibilite,specificite))
    
    # def rocCurve(self):
        
    #     test_score=self.algorithm.predict_proba(self.X_test)
        
    #     fpr = dict()
    #     tpr = dict()
    #     roc_auc = dict()
    #     for i in range(2):
    #         fpr[i], tpr[i], _ = roc_curve(self.Y_test,test_score[:,1])
    #         roc_auc[i] = auc(fpr[i], tpr[i])
        
    #     # Compute micro-average ROC curve and ROC area
    #     fpr["micro"], tpr["micro"], _ = roc_curve(self.Y_test, test_score[:,1])
    #     roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
        
    #     plt.figure()
    #     lw = 2
    #     plt.plot(fpr[1], tpr[1], color='darkorange',
    #              lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
    #     plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    #     plt.xlim([0.0, 1.0])
    #     plt.ylim([0.0, 1.05])
    #     plt.xlabel('False Positive Rate')
    #     plt.ylabel('True Positive Rate')
    #     plt.title('Receiver operating characteristic example')
    #     plt.legend(loc="lower right")
    #     plt.show()

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

def electBestAccuracy(listOfStudies):
    
    # #Extracting scores from data training
    # ML_score_dict=dict()
    # for i in listOfStudies:
    #     score=i.testAccuracy()
    #     ML_score_dict[i]=score
        
    # #Looking for maximum accuracy
    # maxAcc=0
    # bestStudy=None
    # for study in ML_score_dict.keys():
    #     score_got=ML_score_dict[study]
    #     if score_got[0]>maxAcc:
    #         maxAcc=score_got[0]
    #         bestStudy=study
    
    podium=[]
    
    for i in range(len(listOfStudies)):
        podium.append([listOfStudies[i],listOfStudies[i].testAccuracy(),i])
        
    podium = sorted(podium, key=lambda podium:podium[1][0])#tri par intensite
    podium.reverse()
    podium_bests=podium[:10] #10 meilleurs
    podium_worst=podium[-10:] #10 pires
            
    return podium_bests,podium_worst

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

