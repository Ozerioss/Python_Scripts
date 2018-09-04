import sys
import pickle
import json



def save_obj(obj, name):
    with open('dict/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, 0)

def load_obj(name):
    with open('dict/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def printDictionary(d):
    for key, value in d.items():
        print(value, key)


def saveDico(d):
     with open('testJson_topK.txt', 'w', encoding = "utf8") as tmpFile:
        tmpFile.write(json.dumps(d))


def readCitiesFile(fname):
    anotherList = []
    with open(fname, encoding = "utf8") as f:
        content = f.read().splitlines()
        for item in content:
            for x in item.split('\n'):
                anotherList.append(x.split(','))
    return anotherList

def mapToInt(fname, country):
    d = {}
    seen = {}
    listOfCities = readCitiesFile(fname)
    idx = 1
    for items in listOfCities:
        for word in items:
            if word not in seen:
                seen[word] = idx
                idx += 1
    
    finalList = []
    for transaction in listOfCities:
        tmpList = []
        for city in transaction:
            tmpList.append(seen[city])
        finalList.append(tmpList)
    print(finalList)

    newMap = open("TOPK_villes_Sejour_{}.txt".format(country), "w", encoding = "utf8")
    for tmp in finalList:
        tmpIndex = 0
        for city in tmp:
            tmpIndex += 1
            if(tmpIndex == len(tmp)):
                newMap.write(str(city))
            else:
                newMap.write(str(city) + " ")
        newMap.write("\n")
    """ for item in listOfCities:
        d = dict([(y, x+1) for x,y in enumerate(sorted(set(item)))])
        print(d) """
    
    dictionaryAsDict = open("TOPK_villes_Sejour_Dico_{}.txt".format(country), "w", encoding = "utf8")
    for key, value in seen.items():
        tmp = "key : &{}&, value : \"{}\" \n".format(key, value)
        dictionaryAsDict.write(tmp)
    dictionaryAsDict.close()
    #saveDico(d)
    save_obj(seen, 'dico_villes_Sejour_{}'.format(country))

def printSavedDico(dicoName):
    d = load_obj(dicoName)
    print(d)

if(__name__ == "__main__"):
    country = 'United Kingdom'
    fname = 'topKFiles/result_sejour_homecountry_{}.txt'.format(country)
    mapToInt(fname, country)
    print("Done ! ")
