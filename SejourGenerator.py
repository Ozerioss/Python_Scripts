import pymysql as mdb
import sys
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
            

def getRandomUsers():
    query_rndm_users = "SELECT idUser  \
                FROM  Instagram_F                                        \
                ORDER BY RAND() LIMIT 10;              \
            "

    return query_rndm_users



query_rndmUsers_World = "SELECT concat(jour, '-', mois, '-', annee), count(1) as nbrPhoto           \
                                        FROM Instagram_F                                                        \
                                        JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Instagram_F.shape_gid             \
                                        WHERE idUser = %s                                    \
                                        AND annee between '2011' and '2015'                                     \
                                        GROUP BY annee, mois, jour                                              \
                                        ORDER BY annee, mois, jour;                                             \
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
                        charset = 'utf8')



def getRandomUsersList():
    listUsers = []
    try:
        print("Querying ... \n Random users") 
        
        cursor.execute(getRandomUsers())
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
    try:
        print("Querying ... Top countries visited ")

        cursor.execute(query_nrPhoto_User_World, user)
        print("OK")

        result = cursor.fetchall()

        for tmp in result:
            print(tmp[0], tmp[1])
            listCountries.append(tmp[0])
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listCountries


yearList = ['2011', '2012', '2013', '2014', '2015']
monthList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
userList = ['181874912']
#commune = 'PARIS-1ER-ARRONDISSEMENT'

cursor = connection.cursor()


def executeRndmUsers():
    for user in userList:

        listCountries = getListCountries(user)
        homeCountry = listCountries[0]   #We suppose the homecountry of the user is the country where he made most of his pictures
        del listCountries[0]             #We remove it from the list so we don't check their stay there
        print("Home country is : {}".format(homeCountry))
        print("rest of countries : ")
        print(listCountries)

        calendar = pandas.date_range("01-01-2011", "31-12-2015")
        calendar = calendar.map(lambda t : t.strftime('%Y-%m-%d'))  #Make sure calendar is in the right format
        nbrPhoto = 0
        df_calendrier = pandas.DataFrame({"Dates" : calendar, "nbrPhoto": nbrPhoto}) #Fill dataframe with the calendar and 0's for number of pictures
        df_calendrier.Dates = pandas.to_datetime(df_calendrier.Dates)                #Convert dates to datetime objects

        try:
            cursor.execute(query_rndmUsers_excludingHome, (user, homeCountry))          #Execute query to fetch all pictures of the user without their home country
            result = cursor.fetchall()
            df = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])     #Fill dataframe with results of query

            df_calendrier.loc[df_calendrier['Dates'].isin(df['date']), 'nbrPhoto'] += 1         #Increment number of pictures for each date found in query result

            df_calendrier['nextDay'] = df_calendrier['Dates'].shift(-1)
            df_calendrier['nextDayCount'] = df_calendrier['nbrPhoto'].shift(-1)

            counter = 0
            d = {}
            listeJours = []

            df_calendrier['temp'] = (df_calendrier.nbrPhoto.diff(1) != 0).astype('int').cumsum()

            df_sejour = pandas.DataFrame({'BeginDate' : df_calendrier.groupby('temp').Dates.first(), 
                                            'EndDate': df_calendrier.groupby('temp').Dates.last(), 
                                            'Consecutive' : df_calendrier.groupby('temp').size(),
                                            })
            df_sejour['isSejour'] = False

            df_sejour.loc[df_sejour['BeginDate'].isin(df['date']), 'isSejour'] = True

            df.date = pandas.to_datetime(df.date)

            df_sejour['countriesVisited'] = ""
            for i, row in df_sejour.iterrows():
                mask = (df['date'] >= df_sejour.at[i, 'BeginDate']) & (df.date <= df_sejour.at[i, 'EndDate'])
                tmpList = df.name_0.loc[mask]
                newList = list(dict.fromkeys(tmpList))
                
                if(len(newList) > 0):
                    tmpString = ', '.join(newList)
                    print("tmpString : ", tmpString)
                    df_sejour.at[i, 'countriesVisited'] = tmpString


            for i, row in df_sejour.iterrows():
                print(row)
            
        except mdb.Error:
            print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
            sys.exit(1)


executeRndmUsers()


print("Done ! ")


if connection:
    connection.close()


