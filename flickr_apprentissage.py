import pymysql as mdb
import sys
import pandas
import numpy as np
import matplotlib.dates as mdates


query_flickr = "SELECT gadm2.gadm2.name_0, count(name_0) as nbr\
                FROM Flickr\
                JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Flickr.shape_gid\
                WHERE owner_id = '58225608@N06'\
                GROUP BY name_0\
                ORDER BY nbr desc;\
            "

query_random_users_Flickr = "SELECT owner_id FROM Flickr\
                                ORDER BY rand() LIMIT 1000000;\
                            "



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
        cursor.execute(query_random_users_Flickr)
        result = cursor.fetchall()
        newLine = open("users_Flickr.txt", "w", encoding = "utf8")
        for tmp in result:
            print(tmp[0])
            newLine.write(tmp[0])
            newLine.write("\n")
    except mdb.Error:
        print("Error : {}".format(mdb.Error.args))



if(__name__ == "__main__"):
    cursor = connection.cursor()
    GetRandomFlickrUsers()
    print("Done ! ")
    if connection:
        connection.close()