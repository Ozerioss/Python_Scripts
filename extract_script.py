import pymysql as mdb
import sys
import re


query_full_table = "SELECT * FROM Sejour\
            WHERE idUser in (SELECT idUser FROM Sejour_Corrected);\
            "

query_sejour_homecountry = "SELECT listeVilles FROM Sejour WHERE Common = 1\
                        AND listeVilles != '' AND paysOrigine = %s\
                        "

query_sejour_France = "SELECT listeVilles FROM Sejour WHERE Common = 1\
                        AND listeVilles != '' AND paysOrigine = %s\
                        AND (pays1 = 'France' OR pays2 = 'France');\
                        "


query_sejourCorrected_France = "SELECT listeVilles FROM Sejour_Corrected\
                        WHERE listeVilles != '' AND paysOrigine = %s\
                        AND (pays1 = 'France' OR pays2 = 'France');\
                        "

query_sejourCorrected_homecountry = "SELECT listeVilles FROM Sejour_Corrected\
                        WHERE listeVilles != '' AND paysOrigine = %s\
                        "

connection = mdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        autocommit=True
                    )




def exportResult():
    try:
        cursor.execute(query_full_table)
        result = cursor.fetchall()
        for tmp in result:
            print(tmp[0])
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)


def testRegex():
    regex1 = re.compile('^, ')
    #regex2 = 
    with open('regex_test.txt', 'w+', encoding = "utf8") as infile:
        for line in infile:
            line = regex1.sub('', line)

def exportResultHomeCountry():
    with open('list_countries.txt') as infile:
        header = infile.readline()
        for line in infile:
            country = line.strip()
            try:
                print("Querying sejour for : {}".format(country))
                cursor.execute(query_sejourCorrected_France, country)
                result = cursor.fetchall()
                newLine = open("QueryResults_France_Sejour_Corrected/result_sejour_homecountry_{}.txt".format(country), "w", encoding = "utf8")
                for tmp in result:
                    newLine.write(tmp[0])
                    newLine.write("\n")
            except mdb.Error:
                print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
                sys.exit(1)




if(__name__ == "__main__"):
    cursor = connection.cursor()
    exportResultHomeCountry()
    print("Done ! ")
    if connection:
        connection.close()
