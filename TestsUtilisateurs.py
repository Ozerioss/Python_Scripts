import pymysql as mdb
import sys
import numpy as np
import statistics
            

def getRandomUsers():
    query_rndm_users = "SELECT idUser  \
                FROM  Instagram_F                                        \
                ORDER BY RAND() LIMIT 10;              \
            "

    return query_rndm_users


query_rndm_users = "SELECT DISTINCT idUser                               \
                FROM  Instagram_F                               \
                ORDER BY RAND() LIMIT 2000;                       \
            "

query_rndmUsers_excludingHome = " SELECT id, str_to_date(concat(annee, '/', mois, '/', jour), '%%Y/%%m/%%d') as date, name, gadm2.gadm2.name_0, gadm2.gadm2.name_1, gadm2.gadm2.name_2 \
                                            FROM Instagram_F \
                                            JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Instagram_F.shape_gid \
                                            WHERE idUser = %s AND name_0 != %s \
                                            ORDER BY annee, mois, jour;  \
                        "

query_nrPhoto_User_World = " SELECT gadm2.gadm2.name_0, count(name_0) as nbr                                 \
                                        FROM Instagram_F                                                    \
                                        JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Instagram_F.shape_gid         \
                                        WHERE idUser = %s                                                   \
                                        GROUP BY name_0                                                     \
                                        ORDER BY nbr desc;                                                  \
                        "



connection = mdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        autocommit=True
                    )



def getRandomUsersList():
    listUsers = []
    try:
        print("Querying ... \nRandom users") 
        
        cursor.execute(query_rndm_users)
        print("OK")
        result = cursor.fetchall()
        for tmp in result:
            listUsers.append(tmp[0])

    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listUsers

#Returns all countries visited  
def getListCountries(user):
    listCountries = []
    listValues = []
    try:
        #print("Querying ... Top countries visited ")

        cursor.execute(query_nrPhoto_User_World, user)
        #print("OK")

        result = cursor.fetchall()

        for tmp in result:
            #print(tmp[0], tmp[1])
            listCountries.append(tmp[0])
            listValues.append(tmp[1])
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listCountries, listValues


def ComputeStatistics():
    listUsers = getRandomUsersList()
    for user in listUsers:
        print(user)
        listCountries, listValues = getListCountries(user)
        if(len(listValues) > 2):
            median = statistics.median(listValues)
            max = listValues[0]
            min = listValues[len(listValues)-1]
            second = listValues[1]
            if(second >= max*0.80 and (max-min) != 0):
                print("second homeCountry : ", listCountries[1])



if(__name__ == "__main__"):
    cursor = connection.cursor()
    ComputeStatistics()
    print("Done ! ")
    if connection:
        connection.close()