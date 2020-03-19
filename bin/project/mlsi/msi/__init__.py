#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:13:42 2020

@author: desiree
"""

import numpy as np
from math import sqrt
import os

def __getvar(parameters, name):#paremeters est le fichier acqu = zip.read('/'.join(spot) + '/acqu')
    """Utilisée dans la fonction __build_raw_spectrum() pour récupérer les valeurs ML1, ML2, ML3, ..."""
    parse_var = parameters.find(b'$'+name+b'= ')#pourquoi ce b? ce ne sont pas des bytes c'ets du texte pourtant ça marche en spyder il n'y a pas de b et ça marche. Find retourne l'index du '$' contenu dans $ML2 par exemple
    return parameters[parse_var + len(name) + 3:parse_var + 50].split(b' ')[0]#lit la ligne depuis $ + ML2 + 3 (2 pour "= " et 1 pour le début à 0) jusqu'à $+50 lettres et conserve tout ce qui est avant " " mais je ne vois aucun " " et sous spyder c'est pareil avec ou sans split

def __tof2mass(tof, ML1, ML2, ML3):
    """Fonction qui calcule les valeurs necessaires à la lecture des fid de Bruker"""
    A = ML3
    B = np.sqrt(1E12/ML1)
    C = ML2 - tof
    if (A == 0): return ((C * C)/(B * B))
    else: return (((-B + np.sqrt((B * B) - (4 * A * C))) / (2 * A))**2)

def __build_raw_spectrum(folder):
    
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
            raw_mz_scale = __tof2mass(DELAY + np.arange(TD) * DW, ML1, ML2, ML3)
            raw_mz_scale2= raw_mz_scale.tolist()
            #Intensité de chaque pic
            raw_intensite = np.zeros((len(files), TD), dtype = np.int32)
            raw_intensite = np.fromfile(folder  +'/fid', dtype = np.int32)
            raw_intensite2=raw_intensite.tolist() 
            
            data = [raw_mz_scale2,raw_intensite2]
            spectrelu.append(data)
            #Format : [ [ raw_mz_scale2,raw_intensite2 ] ]

        return spectrelu, folder #, DATE
    
    # """Fonction qui crée les spectres bruts de Bruker / parameters est le fichier acqu = zip.read('/'.join(spot) + '/acqu') """
    # if parameters == '' or np.fromstring(fid, dtype = np.int32).size==0  or np.fromstring(fid, dtype = np.int32)[0]=='':
    #     return [0],[0], ''#None, None, None#[0],[0], ''

    # ML1 = float(__getvar(parameters, b'ML1'))
    # ML2 = float(__getvar(parameters, b'ML2'))
    # ML3 = float(__getvar(parameters, b'ML3'))
    # DELAY = int(__getvar(parameters, b'DELAY'))
    # DW = float(__getvar(parameters, b'DW'))
    # TD = int(__getvar(parameters, b'TD'))
    # DATE = dateutil.parser.parse(__getvar(parameters, b'AQ_DATE')[1:-1]) #[1:-1] pour supprimer les <>
    # raw_mz_scale = __tof2mass(DELAY + np.arange(TD) * DW, ML1, ML2, ML3).tolist()
    # raw_intensite = np.fromstring(fid, dtype = np.int32).tolist()
    # #print("mz0",raw_mz_scale[0])
    # # for i in range(len(raw_mz_scale)):
    # #     if raw_mz_scale[i]>1998 and raw_mz_scale[i]<2002:
    # #         print(i, raw_mz_scale[i],raw_intensite [i])
    # return raw_mz_scale, raw_intensite, DATE

#%%
        
def MSI2(folder,lissage=1):
    
    '''
    Applique la méthode MSI2, qui normalise le spectre en entrée suivant une correction de la ligne de base.
    
    La ligne de base est définie comme un bruit de basse fréquence, se traduisant comme un relief très peu pentu sur une grande partie du spectre.
    
    folder est le chemin vers la racine des fichiers à extraire. La fin du chemin se termine avec "1SLin" normalement.
    lissage définit le niveau de lissage appliqué par l'algorithme.
    '''
    
    #La majeure partie de cette fonction a été récupérée à partir d'une autre fonction.
    
    spectre=__build_raw_spectrum(folder)
    
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

def __define_peaks(liste_masse, liste_intensite,liss = 6):
    if liste_masse == []or liste_intensite == []:#None:
        return [0,0,0]#None [0,0,0]pour quadruplets
    spectre_liss = np.convolve(liste_intensite, np.ones(liss)/liss,"valid")
    list_pairs_mz_montee = []
    montee = 0
    for i in range(len(spectre_liss)- 1):
        if spectre_liss[i+1] > spectre_liss[i]:
            montee = montee + spectre_liss[i+1] - spectre_liss[i]# delta d'intensités entre X voisins tant que augmente
        else:
            montee = 0#se remet à zéro si descend
        list_pairs_mz_montee.append([liste_masse[i+2],montee])
    return(list_pairs_mz_montee)
    
def __linearize_spectrum(list_pairs_mz_montee,debut=2000, min_montee =20):
    len1=len(list_pairs_mz_montee)
    linearized=[]
    for j in range (0,len1-1):
        if list_pairs_mz_montee[j][0] < debut: # 490000à peu près m/z à 2400 et 450000 à 2000
            pass#linear+=[[0,0]]
        else:
            if list_pairs_mz_montee[j+1][1] < list_pairs_mz_montee[j][1] and list_pairs_mz_montee[j][1]>min_montee:#montee s'arrete ie j+1 plus petit que j et montee >20
                linearized.append([int(10000*sqrt(list_pairs_mz_montee[j][0])),sqrt(list_pairs_mz_montee[j][1])])  # linearisation des mz #idem pour les montees
            else:#
                if j==len1-1 and list_pairs_mz_montee[j+1][1]>20:# si le dernier point est en montee et si cette montee est forte
                    linearized.append([int(10000*sqrt(list_pairs_mz_montee[j+1][0])),sqrt(list_pairs_mz_montee[j+1][1])])
                else:
                    pass#linear+=[[0,0]]
        #     else:
        #         linear[j-1][0]=0
        #         linear[j-1][1]=0
        # else:
    return linearized

def __select_point_pairs(liste_mz_montee_linearisee, max_diff=10000, taille_produit=1):#liste de tuples ou de listes de 2 elements mz montees
    # max_diff = 10000
    # taille_produit = 1
    if liste_mz_montee_linearisee == [[0,0]] or liste_mz_montee_linearisee== None:
        #print("couples vides")
        return None #[0,0,0]
    #else:
    triplets = []
    len2 = len(liste_mz_montee_linearisee)
    #print("length", length)
    for i in range(len2):#1 pour le nom
        for j in range(i+1,len2):#1 parceque on commece à i+1
            #print("monteedanslignage",liste[i][1] * liste[j][1])
            produit = liste_mz_montee_linearisee[i][1] * liste_mz_montee_linearisee[j][1]#produit des montées
            difference = liste_mz_montee_linearisee[j][0] - liste_mz_montee_linearisee[i][0]#distance entre pics
            if difference > max_diff and produit > taille_produit:
                pointA = liste_mz_montee_linearisee[i][0] #emplacement du premier pic
                triplets+=[[difference, produit, pointA]]#essayer avec 200 au lieu de 100
                 #couples.append([(difference*0.9997)-100, (difference*1.0003)+100, produit, pointA ])#essayer avec 200 au lieu de 100
    triplets = sorted(triplets, key=lambda triplets: triplets[1], reverse = True)[:200] # tri des 200 plus grands produits d'intensité enfin de montées
    #print("couples",couples)
    triplets=sorted(triplets, key=lambda triplets: triplets[0])# remise en ordre de distance (pour scorage)
    #.split("_")[0]+"_"+liste[0].split("_")[1]+"_"+liste[0].split("_")[2]+"_"+liste[0].split("_")[3])
    spectre_ligne=[]
    for elt in triplets:
        spectre_ligne+=[elt[0]]
        spectre_ligne+=[elt[2]]
    #print("spectre_ligne", spectre_ligne)
    #print("lignage", spectre_ligne)
    return spectre_ligne

def __preparation_spectre(liste_masse, liste_intensite):
    if liste_masse == None :
        return None
    spectre=__select_point_pairs(__linearize_spectrum(__define_peaks(liste_masse, liste_intensite,liss = 6),debut=2000,min_montee=20), max_diff=10000, taille_produit=1)
    # print("prepare", spectre[:2])
    return spectre

#%%

def MSI3(folder,lissage=6):

    results=__build_raw_spectrum(folder)
    
    contenu=results[0][0]
    folder=results[1]
    liste_masses=contenu[0]
    liste_intensites=contenu[1]
    
    spectre=__preparation_spectre(liste_masses,liste_intensites)
    
    return [spectre]
    

#%%

