import dateutil
import numpy as np
import matplotlib.pyplot as plt
from math import fabs, sqrt
from operator import itemgetter
from statistics import median
from django.conf import settings
#from pymzML.pymzml.run import Reader
from io import BytesIO
from . import models
import time
#from itertools import imap
#import pymzml
def getvar(parameters, name):#paremeters est le fichier acqu = zip.read('/'.join(spot) + '/acqu')
    """Utilisée dans la fonction build_raw_spectrum() pour récupérer les valeurs ML1, ML2, ML3, ..."""
    parse_var = parameters.find(b'$'+name+b'= ')#pourquoi ce b? ce ne sont pas des bytes c'ets du texte pourtant ça marche en spyder il n'y a pas de b et ça marche. Find retourne l'index du '$' contenu dans $ML2 par exemple
    return parameters[parse_var + len(name) + 3:parse_var + 50].split(b' ')[0]#lit la ligne depuis $ + ML2 + 3 (2 pour "= " et 1 pour le début à 0) jusqu'à $+50 lettres et conserve tout ce qui est avant " " mais je ne vois aucun " " et sous spyder c'est pareil avec ou sans split

def tof2mass(tof, ML1, ML2, ML3):
    """Fonction qui calcule les valeurs necessaires à la lecture des fid de Bruker"""
    A = ML3
    B = np.sqrt(1E12/ML1)
    C = ML2 - tof
    if (A == 0): return ((C * C)/(B * B))
    else: return (((-B + np.sqrt((B * B) - (4 * A * C))) / (2 * A))**2)

def build_raw_spectrum(spot, parameters, fid):
    """Fonction qui crée les spectres bruts de Bruker / parameters est le fichier acqu = zip.read('/'.join(spot) + '/acqu') """
    if parameters == '' or np.fromstring(fid, dtype = np.int32).size==0  or np.fromstring(fid, dtype = np.int32)[0]=='':
        return [0],[0], ''#None, None, None#[0],[0], ''

    ML1 = float(getvar(parameters, b'ML1'))
    ML2 = float(getvar(parameters, b'ML2'))
    ML3 = float(getvar(parameters, b'ML3'))
    DELAY = int(getvar(parameters, b'DELAY'))
    DW = float(getvar(parameters, b'DW'))
    TD = int(getvar(parameters, b'TD'))
    DATE = dateutil.parser.parse(getvar(parameters, b'AQ_DATE')[1:-1]) #[1:-1] pour supprimer les <>
    raw_mz_scale = tof2mass(DELAY + np.arange(TD) * DW, ML1, ML2, ML3).tolist()
    raw_intensite = np.fromstring(fid, dtype = np.int32).tolist()
    #print("mz0",raw_mz_scale[0])
    # for i in range(len(raw_mz_scale)):
    #     if raw_mz_scale[i]>1998 and raw_mz_scale[i]<2002:
    #         print(i, raw_mz_scale[i],raw_intensite [i])
    return raw_mz_scale, raw_intensite, DATE

#%%

def define_peaks(liste_masse, liste_intensite,liss = 6):
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
    
def linearize_spectrum(list_pairs_mz_montee,debut=2000, min_montee =20):
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

def select_point_pairs(liste_mz_montee_linearisee, max_diff=10000, taille_produit=1):#liste de tuples ou de listes de 2 elements mz montees
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

def preparation_spectre(liste_masse, liste_intensite):
    if liste_masse == None :
        return None
    spectre=select_point_pairs(linearize_spectrum(define_peaks(liste_masse, liste_intensite,liss = 6),debut=2000,min_montee=20), max_diff=10000, taille_produit=1)
    # print("prepare", spectre[:2])
    return spectre

#%%

def scorage(spectre, reference, seuil2 = 400, seuil_score=5):#avec while
    if reference=='[]' or reference==[''] or reference=='' or reference == None:
        #print("ref vide")
        return 0
    elif spectre == '[0,0,0]' or spectre == None:
        return 0
    else:
        lenA = len(spectre)
        lenB = len(reference)
        #print("scorage", lenA,lenB)
        score = 0
        # casA0infB0=0
        # casA0supB1=0
        # casA0inside=0
        # casfabsOK=0
        # casfabspasOK=0
        i = 0
        j = 0
        #analyse=[]
        #print(spectre[:30],reference[:40])
        while i < lenA-1 and j < lenB-2:
            if i >= 400 and score == 0:
                #print("abandon",i)
                #analyse.append("abandon")
                return score
            A0 = int(spectre[i])
            A1 = int(spectre[i+1])
            B0 = int(round(float(reference[j])))
            B1 = int(round(float(reference[j+1])))
            B2 = int(round(float(reference[j+2])))

            if A0 < B0 :

                #casA0infB0+=1
                #print("A0<B0", i, j, A0, B0, B1,"+i")
                i += 2
                #analyse.append(("A0<B0",i,j,A0,B0,"+i"))
            elif A0 > B1 :

                #casA0supB1+=1
                #print("A0>B1", i, j, A0, B0, B1,"+j")
                j += 3
                #analyse.append(("A0>B1", i, j, A0, B0, B1,"+j"))
            else:
                #analyse.append(("B0<A0<B1 ", i, j, A0, B0, B1))
                #casA0inside++1
                #print("B0<A0<B1 ", i, j, A0, B0, B1)
                if fabs(A1 - B2) < seuil2:

                    #casfabsOK++1
                    #print("fabs", fabs(A2 - B3), i, j, A2, B3, score, "+i+j+score")
                    score += 1
                    i += 2
                    j += 3
                    #analyse.append(("fabs OK", fabs(A1 - B2), i, j, A1, B2, score, "+i+j+score"))
                else :
                    #analyse.append(("fabspasOK",i,j))
                    #casfabspasOK+=1
                    if j+3>=lenB:
                        score += 1
                        i += 2
                        j += 2
                    else:
                        if (A0>=float(reference[j+3]) and A0<=float(reference[j+4])) and fabs(A1 - float(reference[j+4])) < seuil2:

                            score += 1
                            i += 2
                            j += 3
                            #analyse.append(("fabs OK j suivant",i,j,score,A0, float(reference[j+3]), float(reference[j+4]),fabs(A1 - float(reference[j+4])),"+i+j+score"))
                        else:

                            #print("fabspasOK", fabs(A2 - B3), i, j, A2, B3, score, "+i")
                            i += 2
                        #analyse.append(("fabs pas OJ ni avec le j suivant", i,j, A0,B0,B1,fabs(A1-B2),A1,B2,score,"+i"))
    #print("casA0infB0", casA0infB0, ", casA0supB1", casA0supB1, ", casA0inside", casA0inside, ", casfabsOK", casfabsOK, ", casfabspasOK", casfabspasOK)
    #print(analyse)
    # print("score2", round(((4*score)+100)/9,2))
    return  round(((4*score)+100)/9,2)

def hist_scorage(spectre, reference, seuil2 = 400, seuil_score=5):#avec while
    if reference=='[]' or reference==[''] or reference=='' or reference== None:
        #print("ref vide")
        return 0
    elif spectre == '[0,0,0]' or spectre == None:
        return 0
    else:
        lenA = len(spectre)
        lenB = len(reference)
        #print("scorage", lenA,lenB)
        score = 0
        # casA0infB0=0
        # casA0supB1=0
        # casA0inside=0
        # casfabsOK=0
        # casfabspasOK=0
        i = 0
        j = 0
        #analyse=[]
        #print(spectre[:30],reference[:40])
        while i < lenA-1 and j < lenB-1:
            if i >= 400 and score == 0:
                #print("abandon",i)
                #analyse.append("abandon")
                return score
            A0 = int(spectre[i])
            A1 = int(spectre[i+1])
            B0 = int(round(float(reference[j])*0.9997))
            B1 = int(round(float(reference[j])*1.0003))
            B2 = int(round(float(reference[j+1])))

            if A0 < B0 :

                #casA0infB0+=1
                #print("A0<B0", i, j, A0, B0, B1,"+i")
                i += 2
                #analyse.append(("A0<B0",i,j,A0,B0,"+i"))
            elif A0 > B1 :

                #casA0supB1+=1
                #print("A0>B1", i, j, A0, B0, B1,"+j")
                j += 2
                #analyse.append(("A0>B1", i, j, A0, B0, B1,"+j"))
            else:
                #analyse.append(("B0<A0<B1 ", i, j, A0, B0, B1))
                #casA0inside++1
                #print("B0<A0<B1 ", i, j, A0, B0, B1)
                if fabs(A1 - B2) < seuil2:

                    #casfabsOK++1
                    #print("fabs", fabs(A2 - B3), i, j, A2, B3, score, "+i+j+score")
                    score += 1
                    i += 2
                    j += 2
                    #analyse.append(("fabs OK", fabs(A1 - B2), i, j, A1, B2, score, "+i+j+score"))
                else :
                    #analyse.append(("fabspasOK",i,j))
                    #casfabspasOK+=1
                    if j+2>=lenB:
                        score += 1
                        i += 2
                        j += 2
                    else:

                        if (A0>=float(reference[j+2])*0.9997 and A0<=float(reference[j+2])*1.0003) and fabs(A1 - float(reference[j+2])*1.0003) < seuil2:

                            score += 1
                            i += 2
                            j += 2
                            #analyse.append(("fabs OK j suivant",i,j,score,A0, float(reference[j+3]), float(reference[j+4]),fabs(A1 - float(reference[j+4])),"+i+j+score"))
                        else:

                            #print("fabspasOK", fabs(A2 - B3), i, j, A2, B3, score, "+i")
                            i += 2
                        #analyse.append(("fabs pas OJ ni avec le j suivant", i,j, A0,B0,B1,fabs(A1-B2),A1,B2,score,"+i"))
    #print("casA0infB0", casA0infB0, ", casA0supB1", casA0supB1, ", casA0inside", casA0inside, ", casfabsOK", casfabsOK, ", casfabspasOK", casfabspasOK)
    #print(analyse)
    # print("score2", round(((4*score)+100)/9,2))
    return  round(((4*score)+100)/9,2)