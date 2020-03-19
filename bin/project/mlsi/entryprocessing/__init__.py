# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:24:54 2020

@author: Stagiaire
"""

import os

from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

#%%

def __extractEntryCharacteristics(src,dim):
    
    if (dim==2):
        id_spectre=next(src) #id_spectre
        len_x=next(src) #len X
        x_string=next(src) #X
        len_y=next(src) #len Y
        y_string=next(src) #Y
        return [id_spectre,len_x,x_string,len_y,y_string]
    elif (dim==1):
        id_spectre=next(src) #id_spectre
        len_x=next(src) #len X
        x_string=next(src) #X
        return [id_spectre,len_x,x_string]

def __writeEntry(fichier,sample_name,specter_name,x,y=None):
    
    '''
    Ecrit une entrée dans le fichier mentionné.
    Utilisé principalement pour générer une base de données sous forme .txt.
    
    fichier est le chemin vers le fichier texte où écrire.
    sample_name est la référence de l'échantillon.
    specter_name est la référence du spectre.
    x,y sont respectivement l'abscisse et l'ordonnée du spectre à écrire.
    '''
    
    if y!=None:
        #Spectre en deux dimensions
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
    else:
        #Spectre en une dimension
        fichier.write(sample_name+'\n')
        fichier.write(specter_name+'\n')
        fichier.write("Len X = "+str(len(x))+'\n')
        for i in range(len(x)-1):
            fichier.write(str(x[i])+',')
        fichier.write(str(x[len(x)-1]))
        fichier.write('\n')
        
def getDimensionnality(fichier):
    src=open(fichier,'r')
    next(src)
    next(src)
    next(src)
    next(src)
    comp=next(src)
    dim=0
    if(len(comp.split('_'))>1):
        #Fichier 1D, on est à l'entrée suivante
        dim=1
    else:
        #Fichier 2D, on est pas encore à l'entrée suivante
        dim=2
    src.close()
    return dim

#%%

def concatenateEntries(func_used,liss=1):
    
    '''
    Parcours une arborescence de fichiers et concatène les spectres trouvés en un fichier.
    Génère un .txt avec toutes les entrées trouvées dans les dossiers enfants.
    Utilisé pour extraire les entrées d'une arborescence de base de données.
    
    Exemple sur l'arborescence Flavus :
        Flavus
            Flavus_Manip1
            Flavus_Manip2
        Supposons que l'on ne souhaite que les données de Flavus_Manip1, on fera pointer l'endroit où tous les spectres sont sur :
            Flavus/Flavus_Manip1/
        Le .txt contenant tous les spectres sera généré avec le nom "Spectres_Concatenes_Flavus_Manip1.txt" dans le dossier Flavus/Flavus_Manip1/
    
    func_used est une fonction qui détermine le type de traitement utilisé pour extraire les spectres de la base.
    liss est une variable correspondant à la quantité de lissage utilisée avec MSI2.
    '''
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    folder = askdirectory() # show an "Open" dialog box and return the path to the selected folder
    
    filename=folder+"/Spectres_Concatenes_"+folder.split('/')[-1]+".txt"
    
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
                    
                    data_on_path=directory[0].split('/')
                    sample_name=data_on_path[-4]
                    specter_name=data_on_path[-3]
                    
                    #on peut spliter sur les _ et prendre l'index 1, vérifier l'orthographe et écrire accordément
                    #[jour_calibration,cat,date_et_numero,souche]=sample_name.split('_')
                    #ou
                    #[type_de_machine,date,numero,souche]=sample_name.split('_')
                    
                    spectre=func_used(directory[0],lissage=liss)
                    
                    if len(spectre)==2:    
                        spectre[0]=spectre[0][:len(spectre[1])]
                        __writeEntry(current_file,sample_name,specter_name,x=spectre[0],y=spectre[1])
                    elif len(spectre)==1:
                        __writeEntry(current_file,sample_name,specter_name,x=spectre[0])
                        
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
    
def browserSortBy():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    fichier = askopenfilename() # show an "Open" dialog box and return the path to the selected folder
    mode=int(input("Specify mode used (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))
    __sortBy(fichier,mode)
           
def __sortBy(fichier,mode=0):
    
    '''
    Trie automatiquement un fichier contenant des entrées suivant ce qui est demandé d'être trié.
    
    Crée autant de fichiers qu'il y a d'occurrences différentes trouvées. Les fichiers auront dans le nom une mention supplémentaire nommant le type de tri effectué.
    
    fichier est le chemin vers le fichier à trier.
    mode définit la méthode de tri utilisée :
        - 0 trie suivant si la qualification de la culture
        - 1 trie suivant l'âge de la culture.
        - 2 trie suivant le jour où la calibration a été réalisée.
        - 3 trie suivant l'identifiant de la plaque
        - 4 trie suivant l'identifiant de la souche
        - 5 trie suivant la machine utilisée
        - 6 trie suivant la méthode utilisée
    '''
    
    dim=getDimensionnality(fichier)
    
    with open(fichier,'r') as src:
        file_dictionnary=dict()
        for line in src:
            name=line #nom de l'échantillon
            [mach,J,calibration,cat,num_plaque,id_ech,mthde]=line.split('_')
            
            #Dans la nouvelle base de données, un nom d'entrée sera organisée ainsi :
            #BACT_J3_191210_clone_1011001152_1214_E2
            #<machine>_<age_de_culture>_<date_de_calibration>_<plaque>_<id_de_l_echantillon>_<methode_d_extraction>
            #[mach,age,calib,num_plaque,id_ech,mthde]=line.split('_')
            
            characteristics=[name]+__extractEntryCharacteristics(src,dim)
            sorting_var=None
            
            if (mode==0):
                #Tri suivant Clone ou non
                sorting_var=cat
            elif (mode==1):
                #Tri suivant J_culture
                sorting_var=J
            elif (mode==2):
                #Tri suivant J_calibration
                sorting_var=calibration
            elif (mode==3):
                #Tri suivant la plaque
                sorting_var=num_plaque
            elif (mode==4):
                #Tri suivant la nom_echantillon sur la plaque
                sorting_var=id_ech
            elif (mode==5):
                #Tri suivant la machine utilisée
                sorting_var=mach
            elif (mode==6):
                #Tri suivant la méthode utilisée
                sorting_var=mthde.split('\n')[0]
            else:
                #Aucun tri existant correspondant
                raise("[ERROR] Invalid mode specified.")
            
            if (sorting_var in file_dictionnary):
                #catX existe déjà
                for i in characteristics:             
                    file_dictionnary[sorting_var].write(i)
            else:
                #catX n'existe pas encore
                file_dictionnary[sorting_var]=open(fichier.split('.txt')[0]+"_"+sorting_var+"_Sorted.txt",'w')
        for i in file_dictionnary.keys():
            file_dictionnary[i].close()

#%%

def normalizeDatabaseModel1():
    
    '''
    Transformes un nom de fichier en un autre :
        
            J3 calibration 24102019_autres_20191024-1011017172_1214
                              V
            BACT_J3_191210_clone_1011001152_1214_E2
            
    Normalisant ainsi la base de données.
    '''
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    folder = askdirectory() # show an "Open" dialog box and return the path to the selected folder
    for directory in os.walk(folder):
        
        #Finalement, c'est le dossier le plus à la racine du fichier où on regarde qui nous intéresse
        name_of_folder_being_looked=directory[0].split(folder)[1][1:]
        
        if(len(name_of_folder_being_looked.split('/'))==1 and len(name_of_folder_being_looked)!=0):
            #Fichier Racine seulement !
        
            name=name_of_folder_being_looked
            compacted_name=name.split(' calibration ')[0]+'_'+name.split(' calibration ')[1].split('_',1)[1]
            compacted_name='MYCO_'+compacted_name.replace('-','_')+'_E2'
            final_name=compacted_name.split('_')
            final_name[2],final_name[3]=final_name[3],final_name[2]
            
            final_name='_'.join(final_name)
            
            #print(name_of_folder_being_looked)
            os.rename(directory[0],folder+'/'+final_name)
    print("[INFO] Each entry in the specified folder has been correctly renamed.")
                
def normalizeDatabaseModel2():
    '''
    Transformes un nom de fichier en un autre :
                BACT_191210_1011001152_1214
                              V
            BACT_J3_191210_clone_1011001152_1214_E2
    Normalisant ainsi la base de données.
    '''
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    folder = askdirectory() # show an "Open" dialog box and return the path to the selected folder
    print(folder)
    
    category=folder.split('/')[-1]
    
    for directory in os.walk(folder):
        
        #Finalement, c'est le dossier le plus à la racine du fichier où on regarde qui nous intéresse
        name_of_folder_being_looked=directory[0].split(folder)[1][1:]
        #print(name_of_folder_being_looked)
        
        if(len(name_of_folder_being_looked.split('/'))==1 and len(name_of_folder_being_looked)!=0):
            contents=name_of_folder_being_looked.split('_')
            if(contents[1]=='191210'):
                Jour='J3'
                methode='E2'
            final_name='_'.join([contents[0],Jour,contents[1],category,contents[2],contents[3],methode])
            os.rename(directory[0],folder+'/'+final_name)
        
    print("[INFO] Each entry in the specified folder has been correctly renamed.")

#%%

def __compactEntries(fichier):
    
    '''
    Prends une base de données organisée dans un .txt ainsi :
        nom de l'espèce
        référence du spectre
        taille de l'abscisse
        abscisse
        taille de l'ordonnée
        ordonnée
    Ou ainsi :
        nom de l'espèce
        référence du spectre
        taille de l'abscisse
        abscisse
        
    Et crée un fichier .txt avec le même nom, la mention "_compacted" rajoutée au nom, avec des entrées organisées ainsi :
        abscisse,ordonnée
    Ou ainsi :
        abscisse
    Le but est de créer un fichier aisément exploitable par un algorithme de learning.
    Compacter deux axes sur un seul n'affecte pas la performance ni ne biaise l'analyse.
    
    fichier est le chemin vers le fichier.
    '''
    
    #On prépare le fichier qui sera utilisé pour l'apprentissage
    
    try:
        os.remove(fichier.split('.txt')[0]+"_compacted.txt")
    except:
        pass
    
    #Test de formattage du fichier, si c'est 1D ou 2D
    
    dim=getDimensionnality(fichier)
    print(dim)
    
    #Extraction
    with open(fichier,'r') as src, open(fichier.split('.txt')[0]+"_compacted.txt",'w') as trgt:
        #on doit passer les trois premières lignes
        for line in src:
            #nom de l'échantillon en entier
            
            if(dim==2):
                next(src) #identification du spectre
                next(src) #len X
                x_string=src.readline() #X
                next(src) #len Y
                y_string=src.readline() #Y
                
                z_string=x_string.split('\n')[0]+','+y_string
            elif(dim==1):
                next(src) #identification du spectre
                next(src) #len X
                x_string=src.readline() #X
                z_string=x_string
            
            trgt.write(z_string)

def __extractCompactedEntries(fichier,limit=10):
    
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
             __compactEntries(filename)
             print("[INFO] Process done !")
             
        #Si la version compactée n'existait pas, elle existe maintenant.
        print("[INFO] Extracting "+filename.split('/')[-1].split('.txt')[0]+"_compacted.txt"+"...")
        data=__extractCompactedEntries(filename.split('.txt')[0]+'_compacted.txt',limit=20)
        return data
    except:
        print("[ERROR] Not a Valid path or Not a .txt file or Entries not found/not valid in the mentioned file.")

    
#%%
    
