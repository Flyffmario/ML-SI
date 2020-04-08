# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:24:54 2020

@author: Stagiaire
"""

import os

root_folder=".../"
import sys
if (root_folder not in sys.path):
    sys.path.append(root_folder)

import mlsi.msi

from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

from time import strftime

#%%

def __extractEntryCharacteristics(src,dim):
    
    '''
    Read an entry from an entries file. To use in a "for line in file" structure.
    
    Returns in a list the characteristics of an entry. Its length depends on the file 2D or 1D structure. (5 for the first, 3 for the latter)
    '''
    
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
    Writes an entry in an entries file.
    
    fichier is the file path.
    sample_name is the sample reference.
    specter_name is the specter reference.
    x,y are respectively the axes of the specter.
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
        
def __getDimensionnality(fichier):
    '''
    Returns the dimensionnality of an entries file.
    
    If the file is formatted to compute 2D-specters, it will return 2.
    Else, it will return 1.
    '''
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
    
def __browserDirectory():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    folder = askdirectory() # show an "Open" dialog box and return the path to the selected folder
    return folder

def __browserFile():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    print("[INFO] A folder explorer window has been created. Please look for the folder where all the entries you want to concatene are.")
    fichier = askopenfilename() # show an "Open" dialog box and return the path to the selected folder
    return fichier
    
def __lookForUnreferencedAndMissing(fichier):
    
    '''
    Lists the specters already processed in the file. Walk in the parent folder of the file to see if there are missing or unreferenced specters.
    
    Returns two lists : unreferenced and missing. Note that those lists list entries names and not entries paths.
    '''

    path=fichier.split('/')
    name_fichier=path[-1]
    master_folder='/'.join(path[:len(path)-1])
    
    dim=__getDimensionnality(fichier)
    
    with open(fichier,'r') as src:
        #Le fichier concaténé.
        
       
        #Une entrée est unique, set est plus efficace que list et évites les doublons.
        #Étant un ensemble, les opérateurs d'intersection sont plus rapides
       
        referenced_files=set()
        for line in src:
            referenced_files.add(line.split('\n')[0])
            
            if dim==1:
                for i in range(3): next(src)
            elif dim==2:
                for i in range(5): next(src)
                
        #Maintenant on doit voir ce qui manque ou a été rajouté.
                
        existing_files=set()
        existing_subdirectories=set()
        for directory in os.walk(master_folder):
            #Finalement, c'est le dossier le plus à la racine du fichier où on regarde qui nous intéresse
            name_of_folder_being_looked=directory[0].split(master_folder)[1][1:]
            #Prends tous les fichiers à la racine folder, leur retire folder
            components_of_path=name_of_folder_being_looked.split('/')
            
            if('1' in components_of_path or '1SLin' in components_of_path or 'pdata' in components_of_path):
                pass
            else:
                #Au mieux on est dans le fichier
                #Au pire, on est ou dans des fichiers au dessus de la racine, ou au niveau du dir du spectre
                
                if ('1' in directory[1]):
                    pass
                else:
                    #Il n'y a pas de subdir nommé '1', autrement dit nous ne sommes pas dans un dossier de spectre
                    #On ne peut être qu'à la racine où sont toutes les entrées ou plus haut.
                    
                    if len(name_of_folder_being_looked.split('/'))>=2:
                        category=name_of_folder_being_looked.split('/')[-2]
                        entry_name=name_of_folder_being_looked.split('/')[-1]
                        
                        existing_subdirectories.add(category)
                    else:
                        entry_name=name_of_folder_being_looked
                        
                    existing_files.add(entry_name)
        
        existing_files=existing_files-existing_subdirectories
        unreferenced_files=existing_files-referenced_files
        unreferenced_files.remove('')
        
        missing_files=referenced_files-existing_files
        
        if (len(missing_files)==0 and len(unreferenced_files)==0):
            print("[INFO] No missing or unreferenced files.")
        elif (len(missing_files)!=0):
            print("[WARN] Missing files present in "+name_fichier+".")
            print("[WARN] The names of the missing files are the following :")
            for i in missing_files:
                print(i)
        elif (len(unreferenced_files)!=0):
            print("[WARN] Unreferenced files present in "+master_folder+".")
            print("[WARN] The names of the unreferenced files are the following :")
            for i in unreferenced_files:
                print(i)
        
        return unreferenced_files,missing_files

#%%

#PUBLIC FUNCTIONS    

#%%



def browserNormalizeDatabase(add_info_type_1=[['191024','MYCO','E2']],add_info_type_2=[['191210','BACT','J3','E2']]):
    normalizeDatabase(__browserDirectory(),add_info_type_1=add_info_type_1,add_info_type_2=add_info_type_2)

def normalizeDatabase(folder,add_info_type_1=[['191024','MYCO','E2']],add_info_type_2=[['191210','BACT','J3','E2']]):
    
    '''
    Transforms every file name in the tree folder "folder" :
        
                J3 calibration 24102019_autres_20191024-1011017172_1214 (type 1) || BACT_191210_1011001152_1214 (type 2)
                                                          V
                                        BACT_J3_20191210_clone_1011001152_1214_E2
                                        
    Normalizing the database.
    
    
    folder is the directory path.
    
    add_info_type_1 has this format :
        [[date,machine,method],[date,machine,method],...]
        A type 1 entry corresponding to the date will be annotated with corresponding machine and method used
    add_info_type_2 has this format :
        [[date,machine,age,method],[date,machine,age,method],...]
        A type 2 entry corresponding to the date and machine used will be annotated with corresponding stem's age and method used
        
    Those infos are crucial to normalize the database, otherwise the normalization will not function well.

    '''

    for directory in os.walk(folder):
        
        #Finalement, c'est le dossier le plus à la racine du fichier où on regarde qui nous intéresse
        name_of_folder_being_looked=directory[0].split(folder)[1][1:]
        #Prends tous les fichiers à la racine folder, leur retire folder
        components_of_path=name_of_folder_being_looked.split('/')
        
        if('1' in components_of_path or '1SLin' in components_of_path or 'pdata' in components_of_path):
            pass
        else:
            
            #Au mieux on est dans le fichier
            #Au pire, on est ou dans des fichiers au dessus de la racine, ou au niveau du dir du spectre
            
            if ('1' in directory[1]):
                pass
            else:
                #Il n'y a pas de subdir nommé '1', autrement dit nous ne sommes pas dans un dossier de spectre
                #On ne peut être qu'à la racine où sont toutes les entrées ou plus haut.
                
                if len(name_of_folder_being_looked.split('/'))>=2:
                    category=name_of_folder_being_looked.split('/')[-2]
                    entry_name=name_of_folder_being_looked.split('/')[-1]
                else:
                    entry_name=name_of_folder_being_looked
                
                if(len(entry_name)!=0):
                    
                    debut_de_ligne=entry_name.split(' ')[0].split('_')[0]
                    
                    if (len(debut_de_ligne)==2):
                        
                        #model1
                        if (" calibration " in entry_name):
                            #Si ça passe pas, ça veut dire que c'est le mauvais nom de fichier
                            #J3 calibration 24102019_autres_20191024-1011017172_1214
                            
                            
                            name=entry_name
                            compacted_name='_'.join(name.split(' calibration '))
                            compacted_name='_'.join(compacted_name.split('-',1))
                            compacted_name=compacted_name.split('_')
                            del compacted_name[1]
                            compacted_name='_'.join(compacted_name)
                            contents=compacted_name.split('_')
                            
                            contents[1],contents[2]=contents[2],contents[1]
                            
                            for i in add_info_type_1:
                                if(contents[1][2:]==i[0]):
                                    #Identifiant : Date
                                    machine=i[1]
                                    methode=i[2]
                                    contents.insert(0,str(machine))
                                    contents.insert(len(contents),str(methode))
                            
                            final_name='_'.join(contents)

                            os.rename(directory[0],folder+'/'+final_name)
        
                    elif (len(debut_de_ligne)==4):
                        #model2
                        
                        contents=entry_name.split('_')
                        
                        if len(contents)==4:
                            
                            #<machine>_<calib>_<plaque>_<souche>
                            
                            found_case=False
                            for i in add_info_type_2:
                                if(contents[1]==i[0] and contents[0]==i[1]):
                                    #Identifiants : Date et Machine
                                    Jour=i[2]
                                    methode=i[3]
                                    found_case=True
                                    
                            if found_case==False:
                                #Occurrence non trouvée
                                Jour='JX'
                                methode='EX'
                            final_name='_'.join([contents[0],Jour,'20'+contents[1],category,contents[2],contents[3],methode])
                            os.rename(directory[0],folder+'/'+category+'/'+final_name)
    print("[INFO] Database at "+folder+" Normalized.")

#%%

def browserCreateconcatenatedEntries(func_used,lissage=6):
    createConcatenatedEntries(__browserDirectory(),func_used,liss=lissage)

def createConcatenatedEntries(folder,func_used,liss=6):
    
    '''
    Walks in the folder tree starting from "folder" path directory.
    Concatenate all entries found in a txt file having this structure :
        "Spectres_Concatenes_<parent folder name>_<date of update>_<time of update>_<mlsi.msi function used>.txt"
    
    Exemple on the folder tree Flavus :
        Flavus/
            Flavus/Flavus_Manip1
            Flavus/Flavus_Manip2
        Let's say we only want the entries in Flavus/Flavus_Manip1 with mlsi.msi.MSI2, we'll give to the parameter "folder" the path leading to :
            Flavus/Flavus_Manip1/
        The txt file containing all entries from Flavus/Flavus_Manip1 will be generated with the name "Spectres_Concatenes_Flavus_Manip1_<date>_<time>_MSI2.txt" dans :
            Flavus/Flavus_Manip1/
    
    func_used is a mlsi.msi function.
    '''

    
    filename=folder+"/Spectres_Concatenes_"+folder.split('/')[-1]+'_'+strftime("%Y%m%d")+"_"+strftime("%H%M%S")+'_'+func_used.__name__+".txt"
    
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
                    
                    spectre=func_used(directory[0],lissage=liss)
                    
                    if len(spectre)==2:
                        #Two elements, [[x],[y]]
                        spectre[0]=spectre[0][:len(spectre[1])]
                        __writeEntry(current_file,sample_name,specter_name,x=spectre[0],y=spectre[1])
                    elif len(spectre)==1:
                        #One element, [[x]]
                        __writeEntry(current_file,sample_name,specter_name,x=spectre[0])
                        
                else:
                    pass
            else:
                pass

#%%
    
def browserUpdateConcatenatedentries():
    updateConcatenatedEntries(__browserFile())

def updateConcatenatedEntries(fichier,liss=6):
    
    '''
    Updates the concatenated file with the latest entries in the database present in the parent folder of the file being opened.
    The newest unreferenced entries are normalized first, then they are added to the already existing file. The name of the file is then modified to match current date and time.
    
    Returns nothing.
    '''
    
    
    path=fichier.split('/')
    master_folder='/'.join(path[:len(path)-1])
    name_fichier=path[-1]
    name_of_func_used=name_fichier.split('_')[-1].split('.txt')[0]
    
    normalizeDatabase(master_folder)
    unreferenced,missing=__lookForUnreferencedAndMissing(fichier)

    if len(unreferenced)!=0:
        print("[INFO] Updating "+name_fichier+" with the unreferenced files found...")
    
        #L'idée est maintenant d'ajouter des données à la suite du fichier concaténé déjà existant
        with open(fichier,'a') as current_file:
            #'a' est important, on ne réecrit pas en entier le fichier !
            for root, dirs, files in os.walk(master_folder):
                if(dirs!=[]):
                    if(dirs[0]=='pdata'):
                        #BACT_J3_20191210_autres_1011001152_1269_E2/0_C6/1/1SLin,['pdata'],['acqu', 'acqus', 'fid', 'sptype']
                        data_on_path=root.split('/')
                        sample_name=data_on_path[-4]
                        if (sample_name in unreferenced):
                            
                            specter_name=data_on_path[-3]
                            
                            if (name_of_func_used=='MSI2'):
                                spectre=mlsi.msi.MSI2(root,lissage=liss)
                            elif (name_of_func_used=='MSI3'):
                                spectre=mlsi.msi.MSI3(root,lissage=liss)
                            elif (name_of_func_used=='MSI4'):
                                spectre=mlsi.msi.MSI4(root,lissage=liss)
                                
                            if len(spectre)==2:
                                #Two elements, [[x],[y]]
                                spectre[0]=spectre[0][:len(spectre[1])]
                                __writeEntry(current_file,sample_name,specter_name,x=spectre[0],y=spectre[1])
                            elif len(spectre)==1:
                                #One element, [[x]]
                                __writeEntry(current_file,sample_name,specter_name,x=spectre[0])
        
        components_of_name=name_fichier.split('_')
        components_of_name[-3]=strftime("%Y%m%d")
        components_of_name[-2]=strftime("%H%M%S")
        
        os.rename(fichier,master_folder+'/'+'_'.join(components_of_name))
        
        print("[INFO] Updated "+name_fichier+", renamed to ",'_'.join(components_of_name))

#%%

def browserUpdateDatabase(func_used):
    updateDatabase(__browserDirectory(),func_used)
  
def updateDatabase(folder,func_used,add_info_type_1=[['191024','MYCO','E2']],add_info_type_2=[['191210','BACT','J3','E2']],lissage=6):
    '''
    Updates the whole database to match the format we're looking for.
    It does multiple things, in that order :
        Normalize the Database.
        Look for the latest file that contains the concatenated entries and matches the MSI function used.
            If it exists, updates it.
                If there are unreferenced entries, adds those entries to the file, and updates its date and time of latest update.
                If there are missing entries, warn the user.
            If not, creates a file that contains all the concatenated entries.
    
    Returns nothing.
    
    folder is the path to the root of the database, where all the entries are organized and found.
    func_used is the mlsi.msi function used.
    
    add_info_type_1 has this format :
        [[date,machine,method],[date,machine,method],...]
        A type 1 entry corresponding to the date will be annotated with corresponding machine and method used
    add_info_type_2 has this format :
        [[date,machine,age,method],[date,machine,age,method],...]
        A type 2 entry corresponding to the date and machine used will be annotated with corresponding stem's age and method used
        
    lissage is the amount of smoothing used in the mlsi.msi function.
    '''
    normalizeDatabase(folder,add_info_type_1=add_info_type_1,add_info_type_2=add_info_type_2)

    #À modifier, le format de fichier n'est plus le même.'
    #par défaut, essaies d'updater le concatenated entry le plus récent
    
    #On veut juste l'arborescence directe des fichiers à la racine
    f = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        f.extend(filenames)
        break
    max_date=0
    max_time=0
    for i in filenames:
        if i.startswith("Spectres_Concatenes"):
            if (not i.endswith("compacted.txt")) and (not i.endswith("Sorted.txt") and i.endswith(func_used.__name__+".txt")):
                #On est sûr d'avoir des fichiers concaténés bruts sans aucun traitement préalable et avec la bonne fonction utilisée
                #Maintenant il peut y avoir plusieurs fichiers préalables, on veut le plus récent
                if (max_date==0 and max_time==0):
                    max_date,max_time=int(i.split('_')[-3]),int(i.split('_')[-2])
                else:
                    current_date,current_time=int(i.split('_')[-3]),int(i.split('_')[-2])
                    if (current_date>max_date):
                        max_date=current_date
                    if (current_time>max_time):
                        max_time=current_time
    fichier=folder+'/Spectres_Concatenes_'+folder.split('/')[-1]+'_'+str(max_date)+'_'+str(max_time)+'_'+func_used.__name__+".txt"
    
    try:
        updateConcatenatedEntries(fichier,liss=lissage)
    except:
        createConcatenatedEntries(folder,func_used,liss=lissage)

        

#%%
    
def browserSortBy():
    fichier=__browserFile()
    mode=int(input("Specify mode used (0:type / 1:age / 2:calibration / 3:plate / 4:name_stem / 5:machine / 6:method)"))
    sortBy(fichier,mode=mode)
           
def sortBy(fichier,mode=0):
    
    '''
    Automatically sorts an entries file by a characteristic defined by "mode".

    Returns nothing, but creates as much txt files as there are different unique characteristics at the parent folder of the read file.

    fichier is the path to the file.
    mode define the characteristic being sorted :
        - 0 is the qualification of the stem (clonal, unidentified...)
        - 1 is its age
        - 2 is its calibration date
        - 3 is its plate's id
        - 4 is its stem's id
        - 5 is the machine used
        - 6 is the method used
    '''
    
    dim=__getDimensionnality(fichier)
    
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
            feature=None
            
            if (mode==0):
                #Tri suivant Clone ou non
                sorting_var=cat
                feature="category"
            elif (mode==1):
                #Tri suivant J_culture
                sorting_var=J
                feature="age"
            elif (mode==2):
                #Tri suivant J_calibration
                sorting_var=calibration
                feature="calibration"
            elif (mode==3):
                #Tri suivant la plaque
                sorting_var=num_plaque
                feature="plate"
            elif (mode==4):
                #Tri suivant la nom_echantillon sur la plaque
                sorting_var=id_ech
                feature="stem"
            elif (mode==5):
                #Tri suivant la machine utilisée
                sorting_var=mach
                feature="machine"
            elif (mode==6):
                #Tri suivant la méthode utilisée
                sorting_var=mthde.split('\n')[0]
                feature="method"
            else:
                #Aucun tri existant correspondant
                raise("[ERROR] Invalid mode specified.")
            
            if (sorting_var in file_dictionnary):
                #catX existe déjà
                for i in characteristics:             
                    file_dictionnary[sorting_var].write(i)
            else:
                #catX n'existe pas encore
                file_dictionnary[sorting_var]=open(fichier.split('.txt')[0]+"_"+sorting_var+"_"+feature+"Sorted.txt",'w')
        for i in file_dictionnary.keys():
            file_dictionnary[i].close()



#%%

def browserCompactEntries():
    compactEntries(__browserFile())

def compactEntries(fichier):
    
    '''
    Take a entries file organized like this :
        nom de l'espèce
        référence du spectre
        taille de l'abscisse
        abscisse
        taille de l'ordonnée
        ordonnée
    Or like this :
        nom de l'espèce
        référence du spectre
        taille de l'abscisse
        abscisse
        
    and compacts it, with the mention "_compacted" added at the end, entries organized like this :
        abscisse,ordonnée
    or like this :
        abscisse
    The aim is to create a txt file easily exploitable by a learning algorithm.
    
    fichier is the path to the file.
    '''
    
    #On prépare le fichier qui sera utilisé pour l'apprentissage
    
    try:
        os.remove(fichier.split('.txt')[0]+"_compacted.txt")
    except:
        pass
    
    #Test de formattage du fichier, si c'est 1D ou 2D
    
    dim=__getDimensionnality(fichier)
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

def browserExtractCompactedEntries(limit=10):
    return extractCompactedEntries(__browserFile(),limit=limit)

def extractCompactedEntries(fichier,limit=10):
    
    '''
    Extracts a set number of entries from a txt file with the mention "_compacted" at the end.
    There are no randomisation : the X first entries will be extracted, X being equal to the parameter "limit".
    
    Returns a list of length equal to "limit", of specters (which are lists too).
    
    fichier is the path to the file.
    limit is an int, and defines the set number of entries imported. BEWARE that extracting a lot of entries can cost the computer in processing time.
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

#%%
        
def browserCompactAndExtractCompactedEntries(limit=10):
    data=compactAndExtractCompactedEntries(__browserFile(),limit=limit)
    return data

def compactAndExtractCompactedEntries(filename,limit=10):
    '''
    Compacts the file specified and extracts its content in a list. If a compacted version already exists, it ignores compaction and straight up extracts the contents of the compacted file in a list.
    
    Returns a list of length equal to "limit", of specters (which are lists too).
    
    filename is the file path to the uncompacted version.
    limit is an int, and defines the set number of entries imported. BEWARE that extracting a lot of entries can cost the computer in processing time.
    '''
    
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
        print(filename.split('.txt')[0]+'_compacted.txt')
        data=extractCompactedEntries(filename.split('.txt')[0]+'_compacted.txt',limit=10)
    except:
        print("[ERROR] Not a Valid path or Not a .txt file or Entries not found/not valid in the mentioned file.")
        data=None
    return data

#%%
            
def browserExtractFeatureRelatedData(feature,limit=10):
    return extractFeatureRelatedData(__browserDirectory(),feature,limit=limit)

def extractFeatureRelatedData(folder,feature,limit=10):
    '''
    Extracts all sorted compacted data in the folder root path, with specified feature in last Sorted field in its name.
    
    Returns X, y, and a dictionnary that link y to its original label.
    '''
    referenced_class=dict()
    classnumber=0
    
    data=[]
    verite=[]
    
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for i in filenames:
            if(i.endswith("compacted.txt") and i.startswith("Spectres_Concatenes")):
                #Le dernier Sorted compte
                #Attention, ça ne compte pas s'il y a plusieurs Sorted, il prends juste le dernier
                feature_extracted=i.split('_')[-2].split('Sorted')[0]
                if (feature_extracted==feature):
                    #Le fichier récupéré est un fichier trié comme on le souhaite
                    #On l'extrait
                    current_path=dirpath+'/'+i
                    current_data=extractCompactedEntries(current_path,limit=limit)
                    
                    feature_category=i.split('_')[-3]
                    referenced_class[classnumber]=feature_category
                    
                    for j in range(len(current_data)):
                        data.append(current_data[j])
                        verite.append(classnumber)
                    
                    classnumber+=1
        break
    
    return data,verite,referenced_class

#%%
    
def cropSpecterToMinimumLength(L,dim=2,offset=0):
    #[[],[],[],[]]

    minima_L=len(L[0])
    for i in range(1,len(L)):
        if minima_L>len(L[i]):
            minima_L=len(L[i])
    #la taille minimum est trouvée  
            
    new_L=[]
        
    for i in L:
        if dim==2:
            x=i[:(len(i)//2)]
            y=i[(len(i)//2):]
            new_x=x[:minima_L//2-offset//2]
            new_y=y[:minima_L//2-offset//2]
            new_L.append(new_x+new_y)
        elif dim==1:
            new_L.append(i[:minima_L-offset])
    return new_L
        
        
    