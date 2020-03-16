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
# def scorage(spectre, ref, seuil2 = 400, seuil_score=5):#pour quadruplets seuil1 = 0.9997,
#     ## print("dans scorage",spectre[0],ref[0])
#     if ref=='[]' or ref==[''] or ref=='':
#         #print("ref vide")
#         return 0
#     elif spectre == '[0,0]' or spectre == None:
#         return 0
#     # if type(ref)==str:
#     #     print("error str bq")
#     else:
#         lenA = len(spectre)
#         lenB = len(ref)
#         finref=int(round(float(ref[-1])))
#         # for i in range(lenB):
#         #     ref[i]=float(ref[i])
#         # if sum(ref)==0:
#         #     return 0
#         print("scorage len spectre", lenA,"len ref", lenB)
#         score = 0
#         debut=0
#         analyse=[]
#
#         for i in range(0,lenA-2,2):
#             analyse.append(i)
#             if i >= 400 and score == 0:
#                 print("abandon",i)
#                 analyse.append("abandon")
#                 return score
#             else:
#                 analyse.append((i,"sp",int(float(spectre[i])),int(float(spectre[i+1]))))
#                 #print("sp",i, int(float(spectre[i])),int(float(spectre[i+1])))
#                 A0 = int(float(spectre[i]))#diff
#                 A1 = int(round(float(spectre[i+1])))# pointA
#                 for j in range(debut,lenB-3,3):
#                     analyse.append((i,j,"ref",int(float(ref[j])),int(float(ref[j+1])),int(float(ref[j+2]))))
#                     #if j==0:
#                     #print("ref", j, int(float(ref[j])),int(float(ref[j+1])),int(float(ref[j+2])))
#                     B0 = int(float(ref[j]))#mindiff
#                     B1 = int(float(ref[j+1]))
#                     B2 = int(round(float(ref[j+2])))# pointB
#                     if A0 < B0 :
#                         debut = j
#                         analyse.append("A0<B0")
#                         break
#                     else :
#                         analyse.append("A0>B0")
#                         if A0 <= B1:
#                             analyse.append("distance OK")
#                             if fabs(A1 - B2) < seuil2:#+i+j
#                                 debut=j+3
#                                 score += 1
#                                 analyse.append(("distance OK score+1", score))
#                                 #listij+=[(i,j,score,'+i+j+score2')]
#                                 break
#                             else :#+i
#                                 analyse.append(("distance OK pas le même point", score))
#                                 debut = j
#                                 break
#                         else:# A0 > B1
#                             analyse.append("A0>B1")
#                             if B1 > finref:
#                                 analyse.append("A0>fin ref")
#                                 break
#                             else:
#                                 analyse.append("A0>B1 continue")
#                                 debut = j+3
#                                 continue
#
#
#             #listijs.append(listij)
#             #print("score",score)
#         print(analyse)
#         return round(((4*score)+100)/9,2)

# def lisse_spectre(liste_masse, liste_intensite,liss = 6
# def preparation_spectre_while(liste_masse, liste_intensite,liss = 6,debut=2000,max_diff=10000, taille_produit=1):
#     if liste_masse == []:#None:
#         return [0,0,0]#None
#     spectre_liss = np.convolve(liste_intensite, np.ones(liss)/liss,"valid")
#     couples_mz_montee = []
#     montee = 0
#     i = 0
#     while i < len(spectre_liss)- 1:
#         if spectre_liss[i+1] > spectre_liss[i]:
#             montee = montee + spectre_liss[i+1] - spectre_liss[i]# delta d'intensités entre X voisins tant que augmente
#             i+=1
#         else:
#             montee = 0#se remet à zéro si descend
#             i+=1
#         couples_mz_montee.append([liste_masse[i+2],montee])
#     #print("lisse",spectre[-20:])
# #     return spectre
# # def montees(spectre,):
# #     if spectre == None:
# #         return None
#     len1=len(couples_mz_montee)
#     linear=[]
#     j=0
#     while j < len1-1:
#         if couples_mz_montee[j][0] < debut: # 490000à peu près m/z à 2400 et 450000 à 2000
#             j+=1#linear+=[[0,0]]
#         elif couples_mz_montee[j+1][1] < couples_mz_montee[j][1] and couples_mz_montee[j][1]>20:
#             if j<len1:
#                 linear+= [[int(10000*sqrt(couples_mz_montee[j][0])),sqrt(couples_mz_montee[j][1])]]  # linearisation des j+=mz #idem pour les montees
#                 j+=1
#             else:
#                 j+=1
#                 #linear+=[[0,0]]
#         else:
#             j+=1
#
#         #     else:
#         #         linear[j-1][0]=0
#         #         linear[j-1][1]=0
#         # else:
#
# #     return spectre
#
# def lignage(liste, max_diff=10000, taille_produit=1):#liste de tuples ou de listes de 2 elements mz montees
#     # max_diff = 10000
#     # taille_produit = 1
#     if liste == [[0,0]] or liste== None:
#         #print("couples vides")
#         return None #[0,0,0]
#     else:
#     triplets = []
#     len2 = len(linear)
#     #print("length", length)
#     for i in range(len2):#1 pour le nom
#         for j in range(i+1,len2):#1 parceque on commece à i+1
#             #print("monteedanslignage",liste[i][1] * liste[j][1])
#             produit = (linear[i][1] * linear[j][1])#produit des montées
#             difference = linear[j][0] - linear[i][0]#distance entre pics
#             if difference > max_diff and produit > taille_produit:
#                 pointA = linear[i][0] #emplacement du premier pic
#                 triplets+=[[difference, produit, pointA]]#essayer avec 200 au lieu de 100
#                  #couples.append([(difference*0.9997)-100, (difference*1.0003)+100, produit, pointA ])#essayer avec 200 au lieu de 100
#     triplets = sorted(triplets, key=lambda triplets: triplets[1], reverse = True)[:200]
#     #print("couples",couples)
#     triplets=sorted(triplets, key=lambda triplets: triplets[0])
#     #.split("_")[0]+"_"+liste[0].split("_")[1]+"_"+liste[0].split("_")[2]+"_"+liste[0].split("_")[3])
#     spectre_ligne=[]
#     for elt in triplets:
#         spectre_ligne+=elt
#     #print("lignage", spectre_ligne)
#     return spectre_ligne

#
# # def lignage(liste, max_diff=10000, taille_produit=1):#liste de tuples ou de listes de 2 elements mz montees
# #     # max_diff = 10000
# #     # taille_produit = 1
# #     if liste == [[0,0]] or liste== None:
# #         #print("couples vides")
# #         return None #[0,0,0]
#     # else:
#     triplets = [[0,0,0]]*200
#     len2 = len(linearized)
#     len3 = 0
#     #ijs=[]
#     #print("length", length)
#     for i in range(len2):
#         for j in range(i+1,len2):
#             #print("monteedanslignage",liste[i][1] * liste[j][1])
#             produit = (linearized[i][1] * linearized[j][1])#produit des montées
#             if produit > triplets [199][1]:
#                 difference = linearized[j][0] - linearized[i][0]#distance entre pics
#                 if difference > max_diff and produit > taille_produit:
#                     pointA = linearized[i][0] #emplacement du premier pic
#                     triplets.append([difference, produit, pointA])
#                     del triplets[0]
#                     #ijs.append([i,j,"boucle0 OK produit max",[difference, produit, pointA],[triplet for triplet in triplets]])
#                 else:
#                     continue
#                     #ijs.append([i,j,"boucle0 diff pas OK",difference,produit])
#             elif produit <= triplets[0][1]:
#                 #ijs.append([i,j,"boucle1 produit < min"])
#                 pass
#             else:
#                 for k in range(199):#len-1
#                     difference = linearized[j][0] - linearized[i][0]#distance entre pics
#                     if difference > max_diff and produit > taille_produit:
#                         if produit>triplets[k][1] and produit<=triplets[k+1][1]:
#                             pointA = linearized[i][0] #emplacement du premier pic
#                             triplets.insert(k+1,[difference, produit, pointA])
#                             del triplets[0]
#                             #ijs.append([i,j,k,"boucle1 OK",[triplet for triplet in triplets]])
#                             break
#                         else:
#                             #ijs.append([i,j,k,produit,"boucle 1 produit cherche sa place "])
#                             continue
#                     else:
#                         #ijs.append([i,j,k,produit,"boucle 1 produit OK diff pas OK"])
#                         break
#
#     triplets = sorted(triplets, key=lambda triplets: triplets[1])
#
#     #print("couples",couples)
#     triplets=sorted(triplets, key=lambda triplets: triplets[0])
#     #.split("_")[0]+"_"+liste[0].split("_")[1]+"_"+liste[0].split("_")[2]+"_"+liste[0].split("_")[3])
#     spectre_ligne=[]
#     for elt in triplets:
#         spectre_ligne+=[elt[0],elt[2]]
#     #print(ijs)
#     #print("lignage", spectre_ligne)
#     return spectre_ligne



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

# def scoragearray():
#     return None
# def scorage_array(spectre, reference, seuil2 = 400, seuil_score=20):#pour arrays 4 fois plus lent
#     if reference=='[]' or reference==[''] or reference=='' or sum(reference)==0:
#         return 0
#     elif np.mean(spectre) == 0 :
#         return 0
#     else:
#         mat=0
#         score = 0
#         debut=0
#         for i  in range(len(spectre[:,0])):
#             if mat>=20 and score ==0:
#                 break
#             for j in range(len(reference[:,0])):
#                 mat+=1
#                 if mat>=20 and score ==0:
#                     break
#                 if spectre[i,0] < reference[j,0] :
#                     debut=j
#                     break
#
#                 else:
#                     if spectre[i,0] <=reference[j,1]:
#                         if fabs(spectre[i,2] - reference[j,3]) < seuil2:#+i+j
#                             score += 1
#                             debut=j+1
#                             break
#                         else :#+i
#                             debut=j
#                             break
#                     else:#A0>B1 :
#                         debut=j+1
#                         continue
#
#         return score
    # montees=[]
    # for j in range (len(spectre)-1):
    #     if spectre[j][1] > spectre[j+1][1] and spectre[j][1]>20:# si montee s'arrete et est > 20
    #         if spectre[j][1] > debut: # 490000à peu près m/z à 2400 et 450000 à 2000
    #             #spectre[j][0] = int(10000*sqrt(spectre[j][0])) # linearisation des mz
    #             #spectre[j][1] = sqrt(spectre[j][1])#idem pour les montees
    #             montees.append([int(10000*sqrt(spectre[j][0])),sqrt(spectre[j][1])])
    #         else:
    #             pass
    #             # spectre[j][0]=0
    #             # spectre[j][1]=0
    #     else:
    #         # spectre[j][0]=0
    #         # spectre[j][1]=0
    #         if j+1==len(spectre):
    #             montees.append([int(10000*sqrt(spectre[j+1][0])),sqrt(spectre[j+1][1])])
    #             # spectre[j+1][0] = int(10000*sqrt(spectre[j+1][0])) # linearisation des mz
    #             # spectre[j+1][1] = sqrt(spectre[j+1][1])#idem pour les montees
    #         else:
    #             pass
    #
    #
    #
    # #print("piclist0",spectre[100:110])# delta d'intensités (montee) et dernier mz de la série qui monte
    # #return pic_list
    # montees = sorted(montees,key=lambda montees: montees[1],reverse = True)[:50] # les plus fortes montees d'abord
    # montees = sorted(montees,key=lambda montees: montees[1])#retri selon mz
    # somme = 0
    # for elt in montees:
    #     somme+=elt[1]#somme des intensites
    # if somme==0:
    #     return [[0,0]]
    # for i in range(len(montees)):
    #     montees[i][1]=montees[i][1]*100/somme # normalisation (en % du total)de la valeur de la montee
    # #print("montees",montees)
    # return montees

    # def lignagearray(spectre):
    #     if spectre[0][0]==0:
    #         return [0]
    #     couples = np.array(np.zeros((length*(length-1)/2,3)))
    #         #print(couples[0])
    #         max_diff=10
    #         taille_produit=1
    #         for i in range(length):
    #             for j in range(1,length-i):
    #                 ind=int((i*(2*length-3)/2-(i*(i-2)/2)+j-1))
    #                 spectrei1=spectre[i,1]
    #                 produit = spectrei1 * spectre[i+j,1]#produit des intensites
    #                 #print("produit",i,j,produit)
    #                 difference = spectre[i+j,0] - spectre[i,0]#distance entre mz
    #
    #                 if difference > max_diff and produit > taille_produit:
    #                     #print("new",i,j, spectre_array[1][i][1],produit,difference,)
    #                     couples[ind,0]=difference
    #                     couples[ind,1]=-produit
    #                     couples[ind,2]=spectre[i,0]#point A
    #                     #test+=[(couples[i*j][0],couples[i*j][1],couples[i*j][2],couples[i*j][3])]
    #                     #print("cp",couples[i][3])
    #                     #couples.append([(difference*0.9997)-100, (difference*1.0003)+100, produit, pointA ])
    #         w = np.argsort(couples[:,1])[:200] # tri sur produit
    #         couples=couples[w]
    #         #mysort=[(couples[i,0],couples[i,1], couples[i,2]) for i in np.argsort(couples[:,2])[:200]]
    #         spectrepret=''
    #         for i in range(200):
    #             spectrepret=spectrepret+','+str(couples[i,0])+','+str(couples[i,1])+','+str(couples[i,2])
    #            #.split("_")[0]+"_"+liste[0].split("_")[1]+"_"+liste[0].split("_")[2]+"_"+liste[0].split("_")[3])
    #         return spectrepret
    #         return couples
    #     return spectre

    # def etape1bis_spectre(liste_masse, liste_intensite, debut=2000,liss = 6):
    #     t1=time.time()
    #     spectre_liss = np.convolve(liste_intensite, np.ones(liss)/liss,"valid")
    #     len_liss=len(spectre_liss)
    #     spectre = np.zeros(len_liss-1,2)
    #     montee = 0
    #     for i in range(len_liss - 1):
    #         if liste_masse [i]> début:
    #
    #
    #             if spectre_liss[i+1] > spectre_liss[i]:
    #                 spectre[i,0]=int(10000*sqrt(liste_masse[0][i]))#  lineraisation des mz
    #                 montee = montee + spectre_liss[i+1] - spectre_liss[i]# delta d'intensités entre X voisins tant que augmente
    #             else:
    #                 montee = 0
    #                 spectre[i,0]=0
    #                 #se remet à zéro si descend
    #             spectre[i,1]=sqrt(montee)
    #
    #         else:
    #             continue
    #
    #
    #     for j in range (len_liss-2):
    #         if spectre[j,1] > spectre[j+1,1] and spectre[j,1] >= sqrt(20):# si montee s'arrete et est > 20
    #             continue
    #         else:
    #             spectre[j,0]=0
    #             spectre[j,1]=0
    #
    #     #print("piclist0",spectre[100:110])# delta d'intensités (montee) et dernier mz de la série qui monte
    #     #return pic_list
    #     y = np.argsort(-spectre[:,1])[:50] # les indices des plus fortes montees d'abord
    #     spectre=spectre[y]
    #     z = np.argsort(spectre[:,0]) # retri selon mz
    #     spectre=spectre[z]
    #     somme = np.sum(spectre, axis=0)[0]
    # #    print("sum", somme)
    #
    #     if somme == 0:
    #         return []
    #     spectre[0,:] *= 100/somme  # normalisation (en % du total)de la valeur de la montee
    #     #print("etape1fin mz", spectre[0][:10], "montee",spectre[1][:10])
    #     #return spectre# array de 50 [mz,montee]
    #     length = len(spectre[:,1])
    #     test=[]
    #     #print(length)
    #     couples = np.array(np.zeros((length*(length-1)/2,3)))
    #     #print(couples[0])
    #     max_diff=10
    #     taille_produit=1
    #     for i in range(length):
    #         for j in range(1,length-i):
    #             ind=int((i*(2*length-3)/2)-i*i/2+j-1)
    #             spectrei1=spectre[i,1]
    #             produit = spectrei1 * spectre[i+j,1]#produit des intensites
    #             #print("produit",i,j,produit)
    #             difference = spectre[i+j,0] - spectre[i,0]#distance entre mz
    #
    #             if difference > max_diff and produit > taille_produit:
    #                 #print("new",i,j, spectre_array[1][i][1],produit,difference,)
    #                 couples[ind,0]=difference
    #                 couples[ind,1]=-produit
    #                 couples[ind,2]=spectre[i,0]#point A
    #                 #test+=[(couples[i*j][0],couples[i*j][1],couples[i*j][2],couples[i*j][3])]
    #                 #print("cp",couples[i][3])
    #                 #couples.append([(difference*0.9997)-100, (difference*1.0003)+100, produit, pointA ])
    #     w = np.argsort(couples[:,1])[:200] # tri sur produit
    #     couples=couples[w]
    #     #mysort=[(couples[i,0],couples[i,1], couples[i,2]) for i in np.argsort(couples[:,2])[:200]]
    #     spectrepret=''
    #     for i in range(200):
    #         spectrepret=spectrepret+','+str(couples[i,0])+','+str(couples[i,1])+','+str(couples[i,2])
    #        #.split("_")[0]+"_"+liste[0].split("_")[1]+"_"+liste[0].split("_")[2]+"_"+liste[0].split("_")[3])
    #     return spectrepret
        #return couples
# def scorage2(spectre, ref, seuil1 = 0.9997, seuil2 = 400, seuil_score=20):#pour quadruplets
#     # spectre2=[]
#     #print("spectre",spectre[0])
#
#     if ref=='[]' or ref==[''] or ref=='':
#         return 0
#     else:
#         lenA = len(spectre)
#         lenB = len(ref)
#         score = 0
#         # couples_sp_utiles=[]
#         # couples_bq_utiles=[]
#         #listij=[]
#         debut=0
#
#         for i in range(lenA,3):
#             quadret_sp=spectre[i].replace(' ','').replace('[','').replace(']','').split(',')
#             A0 = float(quadret_sp[0])#mindiff devrait être différence
#             A1 = float(quadret_sp[1])
#             A3 = int(quadret_sp[3])# pointA
#             for j in range(debut,lenB):
#                 quadret_ref=ref[j].split(',')
#                 if i>=20 and score ==0:
#                     break
#                 B0 = float(quadret_ref[0])#mindiff devrait être difference
#                 B1 = float(quadret_ref[1])
#                 B3 = int(quadret_ref[3])# pointB
#                 if A0 < B0 :
#                     if A1<B0:
#                         #print(i,j,'+i0 A1<B0')
#                         #listij+=[(i,j,score,'+i1',)]
#                         break
#                     else :
#                         if fabs(A3 - B3) < seuil2:#+i+j
#                             score += 1
#                             #print(i,j,score,"+i+j+score1")
#                             #couples_sp_utiles.append(spectre[i])
#                             #couples_bq_utiles.append(ref[j])
#                             debut=j+1
#                                 #listij+=[(i,j,score,'+i+j+score2')]
#                             break
#                         else :#+i+j
#                             #print(i,j,"+i2 fabs trop large")
#                             debut=j+1
#                             #listij+=[(i,j,score,'+i+j3')]
#                             break
#                 elif A0 > B1:
#                     debut=j+1
#                     #print(i,j,'+j3 A0 > B1')
#                     #listij+=[(i,j,score,'+j4')]
#                     pass
#                 else:
#                     if fabs(A3 - B3) < seuil2:#+i+j
#                         score += 1
#                         #print(i,j,score,"+i+j+score4")
#                         #score = score + spectre[i][2]
#                         #couples_sp_utiles.append(spectre[i])
#                         #couples_bq_utiles.append(ref[j])
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j+score5')]
#                         break
#                     else :#+i+j match mais pas avec les bons points
#                         #print(i,j,"+i+j5 fabs trop grande")
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j6')]
#                         break
#
#             #listijs.append(listij)
#             #print(score)
#         return score
# def scorage3(spectre, ref, seuil1 = 0.9997, seuil2 = 400, seuil_score=20):#pour triplets
#     # spectre2=[]
#     #print("spectre",spectre[0])
#
#     if ref=='[]' or ref==[''] or ref=='':
#         return 0
#     else:
#         lenA = len(spectre)
#         lenB = len(ref)
#         score = 0
#         # couples_sp_utiles=[]
#         # couples_bq_utiles=[]
#         #listij=[]
#         debut=0
#
#         for i in range(lenA,2):
#             quadret_sp=spectre[i].replace(' ','').replace('[','').replace(']','').split(',')
#             A0 = float(quadret_sp[0])#diff
#
#             A2 = int(quadret_sp[2])# pointA
#             for j in range(debut,lenB):
#                 quadret_ref=ref[j].split(',')
#                 if i>=20 and score ==0:
#                     break
#                 B0 = float(quadret_ref[0])#mindiff devrait être difference
#                 B1 = float(quadret_ref[1])
#                 B3 = int(quadret_ref[3])# pointB
#                 if A0 < B0 :
#                     if A1<B0:
#                         #print(i,j,'+i0 A1<B0')
#                         #listij+=[(i,j,score,'+i1',)]
#                         break
#                     else :
#                         if fabs(A3 - B3) < seuil2:#+i+j
#                             score += 1
#                             #print(i,j,score,"+i+j+score1")
#                             #couples_sp_utiles.append(spectre[i])
#                             #couples_bq_utiles.append(ref[j])
#                             debut=j+1
#                                 #listij+=[(i,j,score,'+i+j+score2')]
#                             break
#                         else :#+i+j
#                             #print(i,j,"+i2 fabs trop large")
#                             debut=j+1
#                             #listij+=[(i,j,score,'+i+j3')]
#                             break
#                 elif A0 > B1:
#                     debut=j+1
#                     #print(i,j,'+j3 A0 > B1')
#                     #listij+=[(i,j,score,'+j4')]
#                     pass
#                 else:
#                     if fabs(A3 - B3) < seuil2:#+i+j
#                         score += 1
#                         #print(i,j,score,"+i+j+score4")
#                         #score = score + spectre[i][2]
#                         #couples_sp_utiles.append(spectre[i])
#                         #couples_bq_utiles.append(ref[j])
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j+score5')]
#                         break
#                     else :#+i+j match mais pas avec les bons points
#                         #print(i,j,"+i+j5 fabs trop grande")
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j6')]
#                         break
#
#             #listijs.append(listij)
#             #print(score)
#         return score
# def scorage4(spectre, ref, seuil1 = 0.9997, seuil2 = 400, seuil_score=20):#pour quadruplets
#     # spectre2=[]
#     #print("spectre",spectre[0])
#
#     if ref=='[]' or ref==[''] or ref=='':
#         return 0
#     else:
#         lenA = len(spectre)
#         lenB = len(ref)
#         score = 0
#         # couples_sp_utiles=[]
#         # couples_bq_utiles=[]
#         #listij=[]
#         debut=0
#
#         for i in range(lenA,3):
#             quadret_sp=spectre[i].replace(' ','').replace('[','').replace(']','').split(',')
#             A0 = float(quadret_sp[0])#mindiff devrait être différence
#             A1 = float(quadret_sp[1])
#             A3 = int(quadret_sp[3])# pointA
#             for j in range(debut,lenB):
#                 quadret_ref=ref[j].split(',')
#                 if i>=20 and score ==0:
#                     break
#                 B0 = float(quadret_ref[0])#mindiff devrait être difference
#                 B1 = float(quadret_ref[1])
#                 B3 = int(quadret_ref[3])# pointB
#                 if A0 < B0 :
#                     if A1<B0:
#                         #print(i,j,'+i0 A1<B0')
#                         #listij+=[(i,j,score,'+i1',)]
#                         break
#                     else :
#                         if fabs(A3 - B3) < seuil2:#+i+j
#                             score += 1
#                             #print(i,j,score,"+i+j+score1")
#                             #couples_sp_utiles.append(spectre[i])
#                             #couples_bq_utiles.append(ref[j])
#                             debut=j+1
#                                 #listij+=[(i,j,score,'+i+j+score2')]
#                             break
#                         else :#+i+j
#                             #print(i,j,"+i2 fabs trop large")
#                             debut=j+1
#                             #listij+=[(i,j,score,'+i+j3')]
#                             break
#                 elif A0 > B1:
#                     debut=j+1
#                     #print(i,j,'+j3 A0 > B1')
#                     #listij+=[(i,j,score,'+j4')]
#                     pass
#                 else:
#                     if fabs(A3 - B3) < seuil2:#+i+j
#                         score += 1
#                         #print(i,j,score,"+i+j+score4")
#                         #score = score + spectre[i][2]
#                         #couples_sp_utiles.append(spectre[i])
#                         #couples_bq_utiles.append(ref[j])
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j+score5')]
#                         break
#                     else :#+i+j match mais pas avec les bons points
#                         #print(i,j,"+i+j5 fabs trop grande")
#                         debut=j+1
#                         #listij+=[(i,j,score,'+i+j6')]
#                         break
#
#             #listijs.append(listij)
#             #print(score)
#         return score
