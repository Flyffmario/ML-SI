# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 11:31:10 2018

@author: Renaud
"""


import os
import numpy as np
from math import fabs, sqrt



def tof2mass(tof, ML1, ML2, ML3):
    A = ML3
    B = np.sqrt(1E12/ML1)
    C = ML2 - tof
    if (A == 0): return ((C * C)/(B * B))
    else: return (((-B + np.sqrt((B * B) - (4 * A * C))) / (2 * A))**2)
    


def list_dir_to1SLin(my_path): 
    # my_path = 'C:\\Users\\...\\MonDossierDeSpectres_a_Analyser'
    from os import walk
    folder = []    
    for (dirpath, dirnames, filenames) in walk(my_path):
        if '1SLin' in dirpath:
            if 'pdata' in dirpath:
                pass
            else:
                folder.append(dirpath)  
    return folder
#%%

#%%
def lire_spectre_Bruker(folder,ijk,mindelta):#mindelta = 20 puis 1000
    #folder=list_dir_to1SLin('C:\\Users\\...\\MonDossierDeSpectres_a_Analyser') 
    #folder=list_dir_to1SLin('my_path_panel')
    files=os.listdir(folder)
    spectrelu=[]
    parameters = open(folder  + "\\acqu").read()
    if parameters =='' or np.fromfile(folder  +'\\fid', dtype = np.int32).size==0:
        DATE=''
        motifs = [[0,0,0,1]]
        return motifs
        
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
#        parse_var = parameters.find('$AQ_DATE= ')
#        DATE = parameters[parse_var + 11:parse_var + 21].split(' ')[0]
        raw_mz_scale = tof2mass(DELAY + np.arange(TD) * DW, ML1, ML2, ML3)
        raw_mz_scale2= raw_mz_scale.tolist()
        raw_intensite = np.zeros((len(files), TD), dtype = np.int32)
        raw_intensite = np.fromfile(folder  +'\\fid', dtype = np.int32)
        raw_intensite2=raw_intensite.tolist() 
        spectrelu = [raw_mz_scale2,raw_intensite2]
#    print("splu_mz",spectrelu[0][:10],"splu_int",spectrelu[1][:10],)  
        
    spectre_liss = []
    liss = 6 # 300 en mz transformé
    a = len(spectrelu[1])#intens
#    print("a",a)
    
    for i in range(a-liss):


        if spectrelu[0][i]>=2000:
            j = 0
            somme = 0
            while j < liss:
                somme = somme + spectrelu[1][i+j]
                j += 1
            spectre_liss.append([spectrelu[0][i],int(somme/liss), i])
        else:
            pass
#    print("spliss",spectre_liss[:10])

#    
#    spectre = []
#    i = 0
#    montee = 0
#    while i < len(spectre_liss)- 1:
#        if spectre_liss[i+1] > spectre_liss[i]:
#            montee = montee + spectre_liss[i+1][0] - spectre_liss[i][0]
#        else:
#            montee = 0            
#        spectre.append([montee, spectrelu[0][i]]) #intens, mz       
#        i += 1
#        
#    pic_list = []
#    i = 0
    relief = []
    epsilon=0#ligne de base
    i = 0
    pente = False
    while i < len(spectre_liss)- 1:
        
        if spectre_liss[i+1][1] > spectre_liss[i][1] +epsilon :#
            pente = True
        elif spectre_liss[i+1][1] +epsilon < spectre_liss[i][1]:
            pente = False
                      
        #parties_montantes.append([montee, profil[i+1][1], profil[i+1][0]])
        #parties_descendantes.append([descente, profil[i+1][1], profil[i+1][0]]) 
        relief.append([spectre_liss[i+1][0], spectre_liss[i+1][1], pente])  #mz int     
        i += 1#
    
#    print("relief",relief[:10])
    changement = []
    i = 0
    while i < len(relief) - 1:
        if relief[i][2] is True and relief[i+1][2] is False:
            changement.append(relief[i])
        elif relief[i][2] is False and relief[i+1][2] is True:
            changement.append(relief[i])
        i += 1#mz int pente
#    print("chang",changement[:10])    
    pic_list = []
    i = 1
    while i < len(changement) - 1:
        intensite = changement[i][1]-(0.5*(changement[i-1][1] + changement[i+1][1]))
        if changement[i][2] is True and intensite > mindelta :
            pic_list.append([changement[i][0], intensite])
        i += 1
#    while i < len(spectre) - 1:
#        if spectre[i][0] > spectre[i+1][0] and spectre[i][0]>20:
#            pic_list.append(spectre[i])
#        i += 1
#    print("piclist0",pic_list[:10])
    pic_list = sorted(pic_list, key=lambda pic_list:pic_list[1],reverse = True)#tri par intensite
    #print("1",folder.split('\\')[-5:],pic_list[:20])
#    print("piclist1",pic_list[:10])
    i = 0
    while i < len(pic_list):
        pic_list[i][0] = int(10000*sqrt(pic_list[i][0]))
        pic_list[i][1] = i/(i+10)#intens
        i += 1
    #print("2",folder.split('\\')[-5:],pic_list2[:20])
#    pic_list2 = []
#    for elt in pic_list:
#        if elt[1] > 2000:
#            pic_list2.append(elt)
#    print("piclist2",pic_list[:10])
    pic_list = pic_list[0: 50]#50 plus fortes intensites
    #print("3",folder.split('\\')[-5:],pic_list2)
#    spectre_final = []
#    i = 0
#    while i < len(pic_list) :       
#        spectre_final.append([int(10000*sqrt(pic_list[i][0])), pic_list[i][1]])#mz, intens
#        i += 1
    
#    spectre_final.sort()#tri par mz
#    spectre_final.insert(0, folder.split('\\')[-5:])
#    spectre_final.insert(1,DATE)
    #print("4",spectre_final)
    pic_list.sort()

#    pic_list.insert(1,DATE)
#    print("piclist3",pic_list[:10])

    motifs = []
    i = 2
    lenght = len(pic_list)
    while i < lenght:
        j = 1#1
        while j < lenght - i:
            k = 1 #1
            while k < lenght - i - j:
                if pic_list[i + j + k][1] + pic_list[i + j][1] + pic_list[i][1] < ijk :
                    a = pic_list[i][0]
                    b = pic_list[i + j][0] - pic_list[i][0]
                    c = pic_list[i + j + k][0] - pic_list[i + j][0]
                    motifs.append([a, b, c, 1])
                k += 1    
            j += 1
        i += 1
#    print("motifs",motifs[:10])
                    
    motifs.insert(0, folder)
    #motifs.insert(0, "Groupe1")
    
    return motifs 




#%%


#%%
def motifs_building(list_dirs,ijk,mindelta):
    print(ijk, time.time())
    liste_motifs=[]
    t=time.time()
    i = 0
    while i < len(list_dirs):
        liste_motifs.append(lire_spectre_Bruker(list_dirs[i],ijk,mindelta)) 
        
        if i % 1000 == 0:
            print("i =", i,time.time()-t)
            t=time.time()
        i += 1
    
    return liste_motifs
#%%

#%%
def scorer(panelspectre,bq,ecart,coeff,epsilon):
    #ecart=500#passer à 300
    liste_score=[]    
    
    for bqsp in bq:
        #print(bqsp[0])
        score=0
        #listeval=[bqsp[0]]
 
        i = 3
        j = 1
        lenpansp = len(panelspectre)
        
        lenbqsp = len(bqsp)
        #print(lenpansp,lenbqsp)
        while i < lenpansp and j < lenbqsp:
            #listeval.append(("newij",i,j))
            A0 = panelspectre[i][0] #enlever
            B0 = bqsp[j][0]
            if abs(A0 - B0) < ecart:#les deux points A sont proches 
                #listeval.append(("abs00<",i,j,A0,B0))
                A1 = panelspectre[i][1]
                B1 = bqsp[j][1]
                if ((1-coeff)*A1)-epsilon < B1 and B1 < ((1+coeff)*A1)+epsilon:# AB identiques
                    #listeval.append(("abs00<,abs11<",i,j,A1,B1))
                    A2 = panelspectre[i][2]
                    B2 = bqsp[j][2]
                    if ((1-coeff)*A2)-epsilon < B2 and B2 < ((1+coeff)*A2)+epsilon:#BC identiques
                        #listeval.append(("abs00<,abs11<,abs22<",i,j,A0,B0,A1,B1,A2,B2))
                        score += 1
                        i += 1
                        j += 1

                    elif B2  >= ((1+coeff)*A2)+epsilon:
                        #listeval.append(("abs00<,abs11<, B2>",i,j,A0,B0,A1,B1,A2,B2))
                    #elif B2-A2  >= ecart:

                        i += 1

                    elif  B2 <= ((1-coeff)*A2)-epsilon:
                        #listeval.append(("abs00<,abs11<,B2<",i,j,A0,B0,A1,B1,A2,B2))
                        #elif A2-B2  >= ecart:

                        j += 1
                    else:
                        #listeval.append(("erreur2<",i,j))
                        print("erreur2", i, j, A2,B2)
                        i+=1
                        j+=1
    
                elif B1  >= ((1+coeff)*A1)+epsilon:
                    #listeval.append(("abs00<,B1>",i,j,A0,B0,A1,B1,panelspectre[i][2],bqsp[j][2]))
                #elif B1-A1  >= ecart:

                    i += 1

                elif B1 <= ((1-coeff)*A1)-epsilon:
                    #listeval.append(("abs00<,B1<",i,j,A0,B0,A1,B1,panelspectre[i][2],bqsp[j][2]))
                #elif A1-B1  >= ecart:

                    j += 1 

                else:
                    #listeval.append(("erreur1",i,j))
                    print("erreur1", i, j)
                    i+=1
                    j+=1
    
            elif A0 - B0 >= ecart:
                #listeval.append(("A0>",i,j,A0,B0,panelspectre[i][1],bqsp[j][1],panelspectre[i][2],bqsp[j][2]))

                j += 1

            elif B0 - A0 >= ecart:
                #listeval.append(("A0<",i,j,A0,B0,panelspectre[i][1],bqsp[j][1],panelspectre[i][2],bqsp[j][2]))


                i += 1

            else:
                #listeval.append(("erreur0",i,j))
                print("erreur0",i,j)
                i+=1
                j+=1
        


        if score>=1:
             liste_score.append((bqsp[0],score))#,listeval
    liste_score2=sorted(liste_score, key= lambda liste_score:liste_score[1],reverse=True)
    return liste_score2
         

#%%


#%%
t=time.time()
sc_300_0003_pan1_3_bqsou1_3_800=[]
for elt in pan_1_3:
    sc=scorer(elt,bqsouche800_1_3,500,0.0005,100)
    sc_300_0003_pan1_3_bqsou1_3_800.append((elt[1],sc))
    if pan_1_3.index(elt) % 50 == 0:
        print("i",pan_1_3.index(elt))

print(time.time()-t)
#%%*
#%%
nom_csv='sc_300_0003_pan1_3_bqsou1_3_800'
nom_fichier=sc_300_0003_pan1_3_bqsou1_3_800

fileresult = pathout+'\\'+nom_csv+'.csv'
file3 = open(fileresult, "w")
cwr = csv.writer(file3, delimiter=';', lineterminator='\n') # delimiter \t est possible aussi; delimiter=';' permet une ouverture spontanée par Excel
for i in range(len(nom_fichier)): 
    cwr.writerow(nom_fichier[i])
file3.close()
