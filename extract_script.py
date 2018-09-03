import pymysql as mdb
import sys



query_full_table = "SELECT * FROM Sejour\
            WHERE idUser in (SELECT idUser FROM Sejour_Corrected);\
            "
query_listeVilles = "SELECT listeVilles FROM Sejour\
                WHERE idUser in (SELECT idUser FROM Sejour_Corrected);\
            "
query_listeSpots = "SELECT listeSpots FROM Sejour\
                WHERE idUser in (SELECT idUser FROM Sejour_Corrected);\
            "

query_full_table_v1 = "SELECT * FROM Sejour_Corrected\
            WHERE idUser in (SELECT idUser FROM Sejour);\
            "
query_listeVilles_v1 = "SELECT listeVilles FROM Sejour_Corrected\
                WHERE idUser in (SELECT idUser FROM Sejour);\
            "
query_listeSpots_v1 = "SELECT listeSpots FROM Sejour_Corrected\
                WHERE idUser in (SELECT idUser FROM Sejour);\
            "

query_full_table_v2 = "SELECT * FROM Sejour_Corrected_v2\
            WHERE idUser in (SELECT idUser FROM Sejour);\
            "
query_listeVilles_v2 = "SELECT listeVilles FROM Sejour_Corrected_v2\
                WHERE idUser in (SELECT idUser FROM Sejour);\
            "
query_listeSpots_v2 = "SELECT listeSpots FROM Sejour_Corrected_v2\
                WHERE idUser in (SELECT idUser FROM Sejour);\
            "

query_addIndex = "ALTER TABLE Sejour_Corrected ADD INDEX (idUser);"

connection = mdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        autocommit=True
                    )



def addIndex():
    try:
        print("Adding index")
        cursor.execute(query_addIndex)
        print("added index")
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)


def exportResult():
    try:
        cursor.execute(query_full_table)
        result = cursor.fetchall()
        for tmp in result:
            print(tmp[0])
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)

def exportResultTest():
    try:
        cursor.execute(query_full_table)
        result = cursor.fetchall()
        for tmp in result:
            print(tmp[0])
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)


if(__name__ == "__main__"):
    cursor = connection.cursor()
    addIndex()
    print("Done ! ")
    if connection:
        connection.close()
