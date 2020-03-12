# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:24:54 2020

@author: Stagiaire
"""

import os
import numpy as np

from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

#%%


'''
les fonctions importées ici sont purement à but de test pour comprendre le fonctionnement
'''

def tof2mass(tof, ML1, ML2, ML3):
    A = ML3
    B = np.sqrt(1E12/ML1)
    C = ML2 - tof
    if (A == 0): return ((C * C)/(B * B))
    else: return (((-B + np.sqrt((B * B) - (4 * A * C))) / (2 * A))**2)

def lire_spectre_Bruker(folder):
    #folder=list_dir_to1SLin('C:\\Users\\...\\MonDossierDeSpectres_a_Analyser') 
    #folder=list_dir_to1SLin('my_path_panel')
    
    #Lit une entrée
    
    files=os.listdir(folder)
    spectrelu=[]
    if 'acqu' not in files or 'fid' not in files:
#        DATE=''
        data=[[0]*2000,[0]*2000]
        spectrelu.append(data)
    else:
        parameters = open(folder  + "/acqu").read()
        if parameters =='' or np.fromfile(folder  +'/fid', dtype = np.int32).size==0:
#        DATE=''
            data=[[0]*2000,[0]*2000]
            spectrelu.append(data)
        else:
            parse_var = parameters.find('$ML1= ')
            ML1 = float(parameters[parse_var + 6:parse_var + 20].split(' ')[0])
            parse_var = parameters.find('$ML2= ')
            ML2 = float(parameters[parse_var + 6:parse_var + 20].split(' ')[0])
            parse_var = parameters.find('$ML3= ')
            ML3 = float(parameters[parse_var + 6:parse_var + 20].split(' ')[0])
            parse_var = parameters.find('$DELAY= ')
            DELAY = int(parameters[parse_var + 8:parse_var + 22].split(' ')[0])
            parse_var = parameters.find('$DW= ')
            DW = float(parameters[parse_var + 5:parse_var + 19].split(' ')[0])
            parse_var = parameters.find('$TD= ')
            TD = int(parameters[parse_var + 5:parse_var + 19].split(' ')[0])
            parse_var = parameters.find('$AQ_DATE= ')
            #        DATE = parameters[parse_var + 11:parse_var + 21].split(' ')[0]
            #Traduction TOF à Mass
            raw_mz_scale = tof2mass(DELAY + np.arange(TD) * DW, ML1, ML2, ML3)
            raw_mz_scale2= raw_mz_scale.tolist()
            #Intensité de chaque pic
            raw_intensite = np.zeros((len(files), TD), dtype = np.int32)
            raw_intensite = np.fromfile(folder  +'/fid', dtype = np.int32)
            raw_intensite2=raw_intensite.tolist() 
            
            data = [raw_mz_scale2,raw_intensite2]
            spectrelu.append(data)
            #Format : [ [ raw_mz_scale2,raw_intensite2 ] ]

        return spectrelu, folder #, DATE

# In[15]:

def MSI2(folder,lissage=1):
    
    '''
    Applique la méthode MSI2, qui normalise le spectre en entrée suivant une correction de la ligne de base.
    
    La ligne de base est définie comme un bruit de basse fréquence, se traduisant comme un relief très peu pentu sur une grande partie du spectre.
    
    folder est le chemin vers la racine des fichiers à extraire. La fin du chemin se termine avec "1SLin" normalement.
    lissage définit le niveau de lissage appliqué par l'algorithme.
    '''
    
    #La majeure partie de cette fonction a été récupérée à partir d'une autre fonction.
    
    spectre=lire_spectre_Bruker(folder)
    
    #Importation des Données
    contenu=spectre[0][0]
    folder=spectre[1]
    liste_masses=contenu[0]
    liste_intensites=contenu[1]
    
    intens1=[]
    intens2=[]
    
    #étape de lissage
    i = 0
    while  i < (len(liste_intensites) - lissage+1):
        j = 0
        somme = 0
        while j < lissage:
            somme = somme + liste_intensites[i + j]
            j += 1
        #print("i =", i, "somme =", somme)
        intens1.append(somme)
        intens2.append(somme)
        #print("i =", i, "intens2[i] =", intens2[i])
        i += 1
    #print(intens1)
    #print(intens2)
        
    #travail sur la ligne de base
    i = 0
    j = 0
    b = 100 #je pense qu'il ne peut pas être différent de c mais c'est à creuser
    c = 100 #taille du dy dans dx/dy
    d = 0
    mini = []
    minimum = 0
    while d < ((len(intens1)/c) - 1):
        minimum = intens1[c * d]
        i = c * d
        #1.1.0
        while i <(c * d) + b:
            intens1[i] = minimum
            if intens1[i + 1] > intens1[i] and i <(c * d) + b - 1 :
                minimum = intens1[i]
            elif intens1[i + 1] > intens1[i] and i ==(c * d) + b - 1 :
                minimum = intens1[i]
                k = c * d
                while k <(c * d) + b:
                    mini.append(minimum)
                    k += 1
            elif intens1[i + 1] <= intens1[i] and i < (c * d) + b - 1 :
                minimum = intens1[i + 1]
            elif intens1[i + 1] <= intens1[i] and i == (c * d) + b - 1 :
                minimum = intens1[i + 1]
                k = c * d
                while k <(c * d) + b:
                    mini.append(minimum)
                    k += 1
            i += 1
        d += 1

    ligne_base = []
    i = 0
    while i < (len(mini) - 150):
        n = 0
        while n < 100:
            ligne_base.append( ((mini[i + 50]*(100 - n)) + (mini[i + 150] * n))/100 )
            n += 1
        i += 100

    int_corrigee = []
    i = 0
    while i < len(mini) - 150:
        int_corrigee.append( intens2[i] - ligne_base[i] )
        """if int_corrigee[i] >= 500:
            print("***", "i =", i, "int_corrigee[i] =", int_corrigee[i])"""
        i += 1

    #print(int_corrigee)
    
    #Exportation
    return [liste_masses,int_corrigee]

#%%

def writeEntry(fichier,sample_name,specter_name,x,y):
    
    '''
    Ecrit une entrée dans le fichier mentionné.
    Utilisé principalement pour générer une base de données sous forme .txt.
    
    fichier est le chemin vers le fichier texte où écrire.
    sample_name est la référence de l'échantillon.
    specter_name est la référence du spectre.
    x,y sont respectivement l'abscisse et l'ordonnée du spectre à écrire.
    '''
    
    fichier.write(sample_name+'\n')
    fichier.write(specter_name+'\n')
    fichier.write("Len X = "+str(len(x))+'\n')
    for i in range(len(x)-1):
        fichier.write(str(x[i])+',')
    fichier.write(str(x[len(x)-1]))
    fichier.write('\n')
    fichier.write("Len Y = "+str(len(y))+'\n')
    for i in range(len(y)-1):
        fichier.write(str(y[i])+',')
    fichier.write(str(y[len(y)-1]))
    fichier.write('\n')

def concatenateEntries(func_used=MSI2,liss=1):
    
    '''
    Parcours une arborescence de fichiers et concatène les spectres trouvés en un fichier.
    Génère un .txt avec toutes les entrées trouvées dans les dossiers enfants.
    Utilisé pour extraire les entrées d'une arborescence de base de données.
    
    Exemple sur l'arborescence Flavus :
        Flavus
            Flavus_Manip1
            Flavus_Manip2
        Supposons que l'on ne souhaite que les données de Flavus_Manip1, on fera pointer l'endroit où tous les spectres sont sur :
            Flavus/Flavus_Manip1
        Le .txt contenant tous les spectres sera généré avec le nom "Spectres_Concatenes_Flavus_Manip1.txt" dans le dossier Flavus/
    
    func_used est une fonction qui détermine le type de traitement utilisé pour extraire les spectres de la base.
    liss est une variable correspondant à la quantité de lissage utilisée avec MSI2.
    '''
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    folder = askdirectory() # show an "Open" dialog box and return the path to the selected folder
    
    filename=folder+"Spectres_Concatenes_"+folder.split('/')[-1]+".txt"
    
    try:
        os.remove(filename)
    except:
        pass

    with open(filename, "w") as current_file:
        
        #développer deux fichiers : l'un avec les clones, l'un avec les autres
        #à partir de là, on pourra entraîner des algos assez facilement
        
        #l'algo prends ~10min pour trier la BDD Flavus1
        
        for directory in os.walk(folder):
            #walk est très rapide par rapport aux autres méthodes, mais liste trop de choses
            #https://stackoverflow.com/questions/800197/how-to-get-all-of-the-immediate-subdirectories-in-python
            
            #On peut trier les données ainsi : si il existe un subdirectory 'pdata' alors on est au bon endroit pour extraire les spectres
            #exemple : ('Flavus/Flavus_Manip1/J3 calibration 25102019_autres_20191025-1011017172_BDX-NC-4/0_G10/1/1SLin', ['pdata'], ['sptype', 'fid', 'acqu', 'acqus'])
            
            if(directory[1]!=[]):
                if(directory[1][0]=='pdata'):
                    #Parfait on est au bon endroit
                    #print(directory[0])
                    
                    #[(other_master,other_master...),direct_master,sample_name,specter_name,one,oneSLine]
                    #Sélectionner à partir de la fin
                    #[-1] renvoie oneSLine, [-2] renvoie one, ainsi de suite...
                    
                    data_on_path=directory[0].split('\\')
                    sample_name=data_on_path[-4]
                    specter_name=data_on_path[-3]
                    
                    #un nom d'entrée s'organise ainsi
                    #J3 calibration 24102019_autres_20191024-1011017172_1214
                    #J5 calibration 26102019_clones masques_20191026-1011017215_I7
                    #ou ainsi
                    #BACT_191210_1011001152_1214
                    
                    #on peut spliter sur les _ et prendre l'index 1, vérifier l'orthographe et écrire accordément
                    #[jour_calibration,cat,date_et_numero,souche]=sample_name.split('_')
                    #ou
                    #[type_de_machine,date,numero,souche]=sample_name.split('_')
                    
                    [x,y]=func_used(directory[0],lissage=liss)
                    x=x[:len(y)]
                    
                    writeEntry(current_file,sample_name,specter_name,x,y)
                else:
                    pass
            else:
                pass

#Comme ça prend 10 min, j'ai envie de faire autre chose au milieu
#Pour m'avertir quand ça finit quand je suis avec le casque avec la musique à fond
#duration = 2  # seconds
#freq = 440  # Hz
#os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

#%%

def compactEntries(fichier):
    
    '''
    Prends une base de données organisée dans un .txt ainsi :
        nom de l'espèce
        référence du spectre
        taille de l'abscisse
        abscisse
        taille de l'ordonnée
        ordonnée
    Et crée un fichier .txt avec le même nom, la mention "_compacted" rajoutée au nom, avec des entrées organisées ainsi :
        abscisse,ordonnée
    Le but est de créer un fichier aisément exploitable par un algorithme de learning.
    Compacter deux axes sur un seul n'affecte pas la performance ni ne biaise l'analyse.
    
    fichier est le chemin vers le fichier.
    '''
    
    #On prépare le fichier qui sera utilisé pour l'apprentissage
    
    try:
        os.remove(fichier.split('.txt')[0]+"_compacted.txt")
    except:
        pass
    with open(fichier,'r') as src, open(fichier.split('.txt')[0]+"_compacted.txt",'w') as trgt:
        #on doit passer les trois premières lignes
        for line in src:
            #nom de l'échantillon en entier
            next(src) #identification du spectre
            next(src) #len X
            x_string=src.readline() #X
            next(src) #len Y
            y_string=src.readline() #Y
            
            z_string=x_string.split('\n')[0]+','+y_string
            
            trgt.write(z_string)

#compactEntries("Spectres_autres_Concatenes_Flavus1.txt")
#compactEntries("Spectres_clones_Concatenes_Flavus1.txt")

#D'abord tout extraire
def extractCompactedEntries(fichier,limit=10):
    
    '''
    Fonction qui extrait d'un txt avec la mention _compacted un certain nombre d'entrées.
    Il n'y a pas de randomisation, la fonction prendra les X premières entrées (ici X=limit).
    
    Renvoie une liste de taille égale à la variable limit, qui contient les listes des spectres compactés extraits de taille correspondant à ce qui a été extrait.
    
    fichier est le chemin vers le fichier.
    limit est un int, et définit le nombre d'entrées que l'on veut importer. 10 par défaut. Attention de ne pas préciser une taille trop grande pour des ordinateurs lents.
    '''
    
    with open(fichier,'r') as src:
        L=[]
        i=0
        for line in src:
            if(i>=limit):
                #Faut mettre une limite sinon c'est la merde, ça prend trop de temps à calculer...
                break
            donnee_brute=line.split('\n')
            #https://stackoverflow.com/questions/1574678/efficient-way-to-convert-strings-from-split-function-to-ints-in-python
            #map est légèrement plus rapide et moins consommateur de CPU
            donnee_organisee=list(map(float,donnee_brute[0].split(',')))
            L.append(donnee_organisee)
            i+=1
        return L
    
def importCompactExtractEntries():
    '''
    Import an entry database in the form of a txt, create a compacted version if it isn't existing in the root folder of the imported file, and extracts its contents.
    
    No parameters needed, a file explorer will open in order to let the user choose the file to import.
    '''
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A file explorer window has been created. Please look for the file you want to import, compact and extract.")
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    try:
        try:
            temp_file=open(filename.split('.txt')[0]+'_compacted.txt','r')
            temp_file.close()
            print("[INFO] Processed version of given file already existing in the current path. Skipping...")
        except:
             print("[INFO] Processing "+filename.split('/')[-1]+"...")
             compactEntries(filename)
             print("[INFO] Process done !")
             
        #Si la version compactée n'existait pas, elle existe maintenant.
        print("[INFO] Extracting "+filename.split('/')[-1].split('.txt')[0]+"_compacted.txt"+"...")
        data=extractCompactedEntries(filename.split('.txt')[0]+'_compacted.txt',limit=20)
        return data
    except:
        print("[ERROR] Not a Valid path or Not a .txt file or Entries not found/not valid in the mentioned file.")

    
#%%
    
