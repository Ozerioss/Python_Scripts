import pymysql as mdb
import sys
import pandas
import numpy as np
import matplotlib.dates as mdates


query_flickr = "SELECT gadm2.gadm2.name_0, count(name_0) as nbr             \
                FROM Flickr_F                                                 \
                JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Flickr_F.shape_gid      \
                WHERE owner_id = %s                                         \
                GROUP BY name_0                                             \
                ORDER BY nbr desc;                                          \
            "

query_random_users_Flickr = "SELECT owner_id FROM Flickr_F\
                                ORDER BY rand() LIMIT 500000;\
                            "


query_insert_Flickr = "INSERT INTO Flickr_F (topCountry, secondCountry) VALUES (%s, %s);"

connection = mdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        autocommit=True
                    )


def GetRandomFlickrUsers():
    try:
        print("querying random users")
        cursor.execute(query_random_users_Flickr)
        result = cursor.fetchall()
        print("done")
        newLine = open("users_Flickr.txt", "w", encoding = "utf8")
        for tmp in result:
            print(tmp[0])
            newLine.write(tmp[0])
            newLine.write("\n")
    except mdb.Error:
        print("Error : {}".format(mdb.Error.args))




def getListCountries(user):
    top2Countries = []
    try:
        print("Querying .. Top countries visited for {}".format(user))
        cursor.execute(query_flickr, user)
        print("OK")
        result = cursor.fetchall()

        for tmp in result:
            listCountries.append(tmp[0])
            listValues.append(tmp[1])

    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listCountries, listValues

def insertFlickr():
    with open("users_Flickr.txt", encoding = "utf8") as infile:
        content = infile.read().splitlines()
        for user in content:
            listCountries, listValues = getListCountries(user)
            try:
                cursor.execute(insertFlickr, (listCountries[0], listCountries[1]))
                print("inserted : {} and {}".format(listCountries[0], listCountries[1]))
            except mdb.Error:
                print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
                sys.exit(1)

                




if(__name__ == "__main__"):
    cursor = connection.cursor()
    GetMaxCountry()
    print("Done ! ")
    if connection:
        connection.close()