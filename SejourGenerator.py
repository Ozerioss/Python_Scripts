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


userList = ['181874912']

def executeRndmUsers():

    #userList = getRandomUsers()         #Random users for testing purposes

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
            df_query = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])     #Fill dataframe with results of query

            df_calendrier.loc[df_calendrier['Dates'].isin(df_query['date']), 'nbrPhoto'] += 1         #Increment number of pictures for each date found in query result

            counter = 0
            d = {}
            listeJours = []

            df_calendrier['temp'] = (df_calendrier.nbrPhoto.diff(1) != 0).astype('int').cumsum()    #temp will increment by one whenever nbrPhoto value changes

            #We can now extract the group results and add that to our final "sejour" dataframe
            df_sejour = pandas.DataFrame({'BeginDate' : df_calendrier.groupby('temp').Dates.first(), 
                                            'EndDate': df_calendrier.groupby('temp').Dates.last(), 
                                            'Consecutive' : df_calendrier.groupby('temp').size(),
                                            })
            #An entry is a 'sejour' if the date exists in our main dataframe (the one containing the results of the query)
            df_sejour['isSejour'] = False
            df_sejour.loc[df_sejour['BeginDate'].isin(df_query['date']), 'isSejour'] = True

            df_query.date = pandas.to_datetime(df_query.date)

            df_sejour[df_sejour.isSejour == True]

            #We now can add a column to the 'sejour' dataframe containing the countries visited by the user
            df_sejour['countriesVisited'] = ""
            df_sejour['statesVisited'] = ""
            df_sejour['citiesVisited'] = ""
            df_sejour['specificSpots'] = ""
            for i, row in df_sejour.iterrows():
                mask = (df_query['date'] >= df_sejour.at[i, 'BeginDate']) & (df_query['date'] <= df_sejour.at[i, 'EndDate'])     #This creates a mask spanning the begin and end dates

                list_name_0 = list(dict.fromkeys(df_query.name_0.loc[mask]))
                list_name_1 = list(dict.fromkeys(df_query.name_1.loc[mask]))
                list_name_2 = list(dict.fromkeys(df_query.name_2.loc[mask]))
                list_name_specific = list(dict.fromkeys(df_query.name.loc[mask]))
                
                if(len(list_name_0) > 0):
                    countries = ', '.join(list_name_0)
                    states = ', '.join(list_name_1)
                    cities =', '.join(list_name_2)
                    specificSpots = ', '.join(list_name_specific)
                    #print("countries: {}, states : {}, cities : {}, specific spots : {} ".format(countries, states, cities, specificSpots))
                    df_sejour.at[i, 'countriesVisited'] = countries         #We add list of countries visited during one single 'sejour'
                    df_sejour.at[i, 'statesVisited'] = states
                    df_sejour.at[i, 'citiesVisited'] = cities
                    df_sejour.at[i, 'specificSpots'] = specificSpots

            #Print content of the sejour dataframe
            """ for i, row in df_sejour.iterrows():
                print(row) """
            print(df_sejour.head())
        except mdb.Error:
            print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
            sys.exit(1)


if(__name__ == "__main__"):
    cursor = connection.cursor()
    executeRndmUsers()
    print("Done ! ")
    if connection:
        connection.close()






