import pymysql as mdb
import sys
import numpy as np
import pandas
import matplotlib.dates as mdates
import statistics
            

def getRandomUsers():
    query_rndm_users = "SELECT idUser  \
                FROM  Instagram_F                                        \
                ORDER BY RAND() LIMIT 10;              \
            "

    return query_rndm_users


query_rndm_users = "SELECT DISTINCT idUser                               \
                FROM  Instagram_F;                       \
            "


query_allUsers = "SELECT DISTINCT idUser  \
            FROM  Instagram_F; \
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

""" connectionMySQL = MySQLdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        cursorclass = MySQLdb.cursors.SSCursor
                    ) """

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
        print("Querying ... Top countries visited ")

        cursor.execute(query_nrPhoto_User_World, user)
        print("OK")

        result = cursor.fetchall()

        for tmp in result:
            listCountries.append(tmp[0])
            listValues.append(tmp[1])

    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listCountries, listValues


def saveAllUsers():
    try:
        print("Querying ... \n All users") 
        #cursor = connection.cursor(mdb.cursors.SSCursor)
        cursor.execute(query_allUsers)
        size = 100000
        result = cursor.fetchmany(size)
        with open('listUsers.txt', 'w') as f:
            while result is not None:
                for row in result:
                    f.write("{}\n".format(row[0]))
                result = cursor.fetchmany(size)
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)


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


def TestMethod():
    user = '10000464'
    listCountries, listValues = getListCountries(user)
    print(user)
    print(listCountries)

def GenerateSejoursTest():
    user = '10000464'
    listCountries, listValues = getListCountries(user)
    if(len(listCountries) > 1):
        homeCountry = listCountries[0]   #We suppose the homecountry of the user is the country where he made most of his pictures
        secondCountry = ''
        #checks for second home country
        if(len(listValues) > 2):
            max = listValues[0]
            min = listValues[len(listValues)-1]
            second = listValues[1]
            if(second >= max*0.80 and (max-min) != 0):
                secondCountry = listCountries[1]
                del listCountries[1]


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

            #Increment number of pictures for each date found in query result
            df_calendrier.loc[df_calendrier['Dates'].isin(df_query['date']), 'nbrPhoto'] += 1

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

            #Small hack to not mess up the creation of 'sejour' above
            for tmp in result:
                df_calendrier.loc[df_calendrier['Dates'] == pandas.to_datetime(tmp[1]), 'nbrPhoto'] += 1

            df_calendrier.loc[df_calendrier.nbrPhoto != 0, 'nbrPhoto'] -= 1

            df_calendrier['jours'] = df_calendrier['Dates'].dt.dayofweek

            #We now can add a column to the 'sejour' dataframe containing the countries visited by the user
            df_sejour['countriesVisited'] = ""
            df_sejour['statesVisited'] = ""
            df_sejour['citiesVisited'] = ""
            df_sejour['specificSpots'] = ""
            df_sejour['nbrPhotos'] = 0
            df_sejour['nbrPhotoAvg'] = 0
            df_sejour['nbrPhotoMax'] = 0
            df_sejour['nbrPhotoMin'] = 0
            df_sejour['daysOfWeek'] = ""

            for i, row in df_sejour.iterrows():
                mask = (df_query['date'] >= df_sejour.at[i, 'BeginDate']) & (df_query['date'] <= df_sejour.at[i, 'EndDate'])     #This creates a mask spanning the begin and end dates
                maskPictures = (df_calendrier['Dates'] >= df_sejour.at[i, 'BeginDate']) & (df_calendrier['Dates'] <= df_sejour.at[i, 'EndDate'])  #mask for calendar
                list_name_0 = list(dict.fromkeys(df_query.name_0.loc[mask]))
                list_name_1 = list(dict.fromkeys(df_query.name_1.loc[mask]))
                list_name_2 = list(dict.fromkeys(df_query.name_2.loc[mask]))
                list_name_specific = list(dict.fromkeys(df_query.name.loc[mask]))

                nbrPictures = df_calendrier.nbrPhoto.loc[maskPictures].sum() 
                nbrPicturesAvg = df_calendrier.nbrPhoto.loc[maskPictures].mean()
                nbrPicturesMax = df_calendrier.nbrPhoto.loc[maskPictures].max()
                nbrPicturesMin = df_calendrier.nbrPhoto.loc[maskPictures].min()
                
                
                if(len(list_name_0) > 0):
                    countries = ', '.join(list_name_0)
                    states = ', '.join(list_name_1)
                    cities =', '.join(list_name_2)
                    specificSpots = ', '.join(list_name_specific)
                    list_days = list(df_calendrier.jours.loc[maskPictures])
                    days = ', '.join(str(x) for x in list_days)

                    #We add list of countries, states, cities and specific spots visited during one single 'sejour'
                    df_sejour.at[i, 'countriesVisited'] = countries         
                    df_sejour.at[i, 'statesVisited'] = states
                    df_sejour.at[i, 'citiesVisited'] = cities
                    df_sejour.at[i, 'specificSpots'] = specificSpots
                    df_sejour.at[i, 'nbrPhotos'] = nbrPictures
                    df_sejour.at[i, 'nbrPhotoAvg'] = nbrPicturesAvg
                    df_sejour.at[i, 'nbrPhotoMax'] = nbrPicturesMax
                    df_sejour.at[i, 'nbrPhotoMin'] = nbrPicturesMin
                    df_sejour.at[i, 'daysOfWeek'] = days


            #Print content of the sejour dataframe
            """ for i, row in df_sejour.iterrows():
                #Insert logic here
                print(row) """
            """ for i, row in df_calendrier.iterrows():
                if(df_calendrier.at[i, 'nbrPhoto'] != 0):
                    print(row) """
            
            df_sejour['nbJoursAvant'] = 0
            df_sejour['nbJoursApres'] = 0
            sejour_size = df_sejour.shape[0]
            for i in range(sejour_size):
                if(sejour_size > 1):
                    if(df_sejour['isSejour'].iloc[i]):
                        #Mettre -1 pour nbrJoursAvant pour 1er sejour
                        #Mettre -1 pour nbrJoursApres pour le dernier sejour
                        last = -1
                        next = -1

                        if(i == 0 or i == 1): #ie 1er sejour
                            next = df_sejour.Consecutive.iloc[i+1]
                        elif(i == (sejour_size - 1) or i == (sejour_size - 2)):
                            last = df_sejour.Consecutive.iloc[i-1]     
                        else:
                            last = df_sejour.Consecutive.iloc[i-1]
                            next = df_sejour.Consecutive.iloc[i+1]
                        
                        df_sejour.at[i + 1, 'nbJoursAvant'] = last
                        df_sejour.at[i + 1, 'nbJoursApres'] = next

                    """ if(i==0):
                        last = -1
                        next = df_sejour.Consecutive.iloc[i+1]
                        df_sejour.at[i + 1, 'nbJoursAvant'] = last
                        df_sejour.at[i + 1, 'nbJoursApres'] = next

                    last = df_sejour.Consecutive.iloc[i-1]
                    next = -1
                    if(i==df_sejour.shape[0]-1):
                        next = -1 #last sejour
                        df_sejour.at[i + 1, 'nbJoursAvant'] = last
                        df_sejour.at[i + 1, 'nbJoursApres'] = next

                    elif(df_sejour['isSejour'].iloc[i]):
                        next = df_sejour.Consecutive.iloc[i+1]
                        df_sejour.at[i + 1, 'nbJoursAvant'] = last
                        df_sejour.at[i + 1, 'nbJoursApres'] = next """

            # To remove timestamps
            df_sejour['BeginDate'] = df_sejour['BeginDate'].dt.date 
            df_sejour['EndDate'] = df_sejour['EndDate'].dt.date

            df_sejour['homeCountry'] = homeCountry + secondCountry
            for i, row in df_sejour.iterrows():
                print(row)
                

        except mdb.Error as e:
            print("Exception : {} ".format(e))
            sys.exit(1)



if(__name__ == "__main__"):
    cursor = connection.cursor()
    #cursor = connectionMySQL.cursor()
    GenerateSejoursTest()
    print("Done ! ")
    if connection:
        connection.close()