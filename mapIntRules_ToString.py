import sys
import numpy
import pickle
import json



def save_obj(obj, name):
    with open('dict/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, 0)

def load_obj(name):
    with open('dict/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def decodeRules(fname):
    integerRules = []
    rules = open("remapped_rules.txt", "w", encoding = "utf8") 
    referenceDico = load_obj('testDico')
    with open(fname, encoding = "utf8") as f:
        content = f.read().splitlines()
        for item in content:
            stringRules = []
            tmp = item.split('#SUP')
            spam = tmp[0].strip().split("  ==> ")
            print(spam)
            for number in spam:
                stringRules.append(list(referenceDico.keys())[list(referenceDico.values()).index(int(number))])
            #print("{} #SUP: {}".format('  ==> '.join(stringRules), ''.join(tmp[1])))
            rules.write("{} #SUP: {}\n".format('  ==> '.join(stringRules), ''.join(tmp[1])))
            #rules.append("{} #SUP: {}".format('  ==> '.join(stringRules), ''.join(tmp[1])))
            


if(__name__ == "__main__"):
    fname = 'outputTopK.txt'
    decodeRules(fname)
    print("Done ! ")