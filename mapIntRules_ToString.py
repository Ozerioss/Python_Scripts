import sys
import numpy
import pickle
import json


#save_obj et load_obj sont les fonctions principales pour sauvegarder et loader un dictionnaire
def save_obj(obj, name):
    with open('dict/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, 0)

def load_obj(name):
    with open('dict/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def is_number(a):
    # will be True also for 'NaN'
    try:
        number = float(a)
        return True
    except ValueError:
        return False


#deprecated
def decodeRules(fname, country):
    integerRules = []
    rules = open("remapped_rules{}.txt".format(country), "w", encoding = "utf8") 
    referenceDico = load_obj('dico_villes_Sejour_{}'.format(country))
    with open(fname, encoding = "utf8") as f:
        content = f.read().splitlines()
        for item in content:
            stringRules = []
            tmp = item.split('#SUP')
            spam = tmp[0].strip().split("  ==> ")
            print(spam)
            for number in spam:
                stringRules.append(list(referenceDico.keys())[list(referenceDico.values()).index(int(number))])
            rules.write("{} #SUP: {}\n".format('  ==> '.join(stringRules), ''.join(tmp[1])))
            

#Fonction pour load le dictionnaire et faire la mise en forme du nouveau fichier décodé
def decodeRulesv2(fname, country):
    integerRules = []
    rules = open("remapped_rules{}.txt".format(country), "w", encoding = "utf8")
    referenceDico = load_obj('dico_villes_SejourCorrected_Fr_{}'.format(country))
    with open(fname, encoding = "utf8") as f:
        content = f.read().splitlines()
        for item in content:
            stringRules = []
            stringLeftSide = []
            stringRightSide = []
            tmp = item.split('  ==> ')
            leftSide = tmp[0].split(' ')
            rightSide = tmp[1].split('  #SUP')
            print(leftSide)
            print(rightSide)
            for number in leftSide:
                stringLeftSide.append(list(referenceDico.keys())[list(referenceDico.values()).index(int(number))])
            for number in rightSide:
                if(is_number(number)):
                    stringRightSide.append(list(referenceDico.keys())[list(referenceDico.values()).index(int(number))])
            

            rules.write("{}   ==> {}   #SUP: {}\n".format(', '.join(stringLeftSide), ' '.join(stringRightSide), rightSide[1]))


if(__name__ == "__main__"):
    listCountry = ['Australia', 'Belgium', 'Brazil', 'Italy', 'Russia', 'South Korea', 'Spain', 'Sweden', 'Thailand', 'United Kingdom', 'United States']
    for country in listCountry:
        fname = 'spmf_results_TOPK_v2_France/output_Fr_{}.txt'.format(country)
        decodeRulesv2(fname, country)
    print("Done ! ")