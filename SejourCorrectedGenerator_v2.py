import pymysql as mdb
import sys
import pandas
import numpy as np
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
            

def getRandomUsers():
    query_rndm_users = "SELECT idUser  \
                FROM  Instagram_F                                        \
                ORDER BY RAND() LIMIT 100;              \
            "

    return query_rndm_users


query_allUsers = "SELECT DISTINCT idUser  \
            FROM  Instagram_F; \
            "


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

query_distance_countries = "SELECT distance_km FROM country_distances.distances_joined                      \
                                    WHERE country1_name_0_gadm2 = %s                                        \
                                    AND country2_name_0_gadm2 = %s;                                         \
                        "

#Make idSejour 
query_insert_sejour = "INSERT INTO Sejour_Corrected_v2(idUser, dateDebut, dateFin, dureeJ, nbPhotoAvg, nbPhotoMin, \
                            nbPhotoMax, nbPhotoTotal, nbJourPauseAvant, nbJourPauseApres, listeJours, listePays, \
                            listeEtats, listeVilles, listeSpots, listePaysExclus, Corrected)             \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"


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



def getDistance(country1, country2):
    try:
        print("Querying distance between : {} and {}".format(country1, country2))
        cursor.execute(query_distance_countries, (country1, country2))

        result = cursor.fetchall()
        distance = 0
        for tmp in result:
            distance = tmp[0]

    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)

    return distance


#Normalizes distance between 1 and 3
def getNormalizedDistance(distance):
    #do a bunch of stuff
    minValue = 0
    maxValue = 19798

    if(distance == 0):
        normalizedDistance = 0

    else:
        normalizedDistance = (3-1) * (distance / maxValue) + 1

    return round(normalizedDistance)


#Returns all countries visited  
def getListCountries(user):
    listCountries = []
    listValues = []
    try:
        print("Querying .. Top countries visited for {}".format(user))
        cursor.execute(query_nrPhoto_User_World, user)
        #print("OK")
        result = cursor.fetchall()

        for tmp in result:
            listCountries.append(tmp[0])
            listValues.append(tmp[1])

    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)
    return listCountries, listValues

            



def GenerateSejours():
    print("Opening file ..")
    linesInserted = 0 #To check number of lines inserted in logs
    with open('temppp.txt') as infile:
        header = infile.readline() #skip column name
        for line in infile:
            user = line.strip()
            listCountries, listValues = getListCountries(user)
            if(len(listCountries) > 1):
                homeCountry = listCountries[0]   #We suppose the homecountry of the user is the country where he made most of his pictures
                secondCountry = ''
                #checks for second home country
                if(len(listValues) > 2):
                    maxValue = listValues[0]
                    minValue = listValues[len(listValues)-1]
                    second = listValues[1]
                    if(second >= maxValue*0.80 and (maxValue-minValue) != 0):
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

                    
                    df_sejour['nbJoursAvant'] = 0
                    df_sejour['nbJoursApres'] = 0
                    sejour_size = df_sejour.shape[0]
                    #Sets for first and last sejour respectively -1 for days before and -1 for days after
                    for i in range(sejour_size):
                        if(sejour_size > 2):
                            if(df_sejour['isSejour'].iloc[i]):
                                last = -1
                                next = -1
                                if(i == 0 or i == 1): #ie 1er sejour
                                    next = df_sejour.Consecutive.iloc[i+1]
                                elif(i == (sejour_size - 1) or i == (sejour_size - 2)): # ie dernier sejour
                                    last = df_sejour.Consecutive.iloc[i-1]     
                                else:
                                    last = df_sejour.Consecutive.iloc[i-1]
                                    next = df_sejour.Consecutive.iloc[i+1]
                                
                                df_sejour.at[i + 1, 'nbJoursAvant'] = last
                                df_sejour.at[i + 1, 'nbJoursApres'] = next

                    # To remove timestamps
                    df_sejour['BeginDate'] = df_sejour['BeginDate'].dt.date 
                    df_sejour['EndDate'] = df_sejour['EndDate'].dt.date
                    
                    indexes_to_drop = []
                    mergedSejourDict = {}
                    for i in range(sejour_size - 2):
                        if(sejour_size > 3): # minimum 3 sejours avant qu'on merge
                            if(df_sejour.isSejour.iloc[i]):
                                firstSejour = df_sejour.iloc[i]           #Should be true
                                pause = df_sejour.iloc[i + 1]      #Should be false
                                secondSejour = df_sejour.iloc[i + 2]        #Should be true
                                #We get the last country visited during the sejour and the first one in the next sejour that we want to join
                                countriesFirstSejour = firstSejour.countriesVisited.split(', ')
                                lastCountrySejour1 = countriesFirstSejour[-1]
                                countriesSecondSejour = secondSejour.countriesVisited.split(', ')
                                firstCountrySejour2 = countriesSecondSejour[0]

                                statesFirstSejour = firstSejour.statesVisited.split(', ')
                                citiesFirstSejour = firstSejour.citiesVisited.split(', ')

                                statesSecondSejour = secondSejour.statesVisited.split(', ')
                                citiesSecondSejour = secondSejour.citiesVisited.split(', ')

                                #Case where country is different
                                if(lastCountrySejour1 != firstCountrySejour2):
                                    distancePays = getDistance(lastCountrySejour1, firstCountrySejour2)
                                    distanceNormalized = getNormalizedDistance(distancePays)
                                    if(pause.Consecutive <= firstSejour.Consecutive and 
                                                        pause.Consecutive <= secondSejour.Consecutive + distanceNormalized):
                                        print(firstSejour)
                                        print(pause)
                                        print(secondSejour)
                                        newRowBeginDate = firstSejour.BeginDate
                                        newRowEndDate = secondSejour.EndDate
                                        newRowConsecutive = firstSejour.Consecutive + pause.Consecutive + secondSejour.Consecutive
                                        newRowNbrPhotos = firstSejour.nbrPhotos + secondSejour.nbrPhotos

                                        newRowCountriesVisited = firstSejour.countriesVisited + ', ' + ', '.join(countriesSecondSejour)

                                        newRowStatesVisited = firstSejour.statesVisited + ', ' + secondSejour.statesVisited
                                        
                                        #Cities
                                        newRowCitiesVisited = firstSejour.citiesVisited + ', ' + secondSejour.citiesVisited
                                        
                                        newRowSpecificSpots = firstSejour.specificSpots + ', ' + secondSejour.specificSpots
                                        
                                        newRownbrPhotoAvg = (firstSejour.nbrPhotoAvg + secondSejour.nbrPhotoAvg) / 2
                                        newRownbrPhotoMin = min(firstSejour.nbrPhotoMin, secondSejour.nbrPhotoMin)
                                        newRownbrPhotoMax = max(firstSejour.nbrPhotoMax, secondSejour.nbrPhotoMax)
                                        
                                        newRowDaysOfWeek = firstSejour.daysOfWeek + ', ' + secondSejour.daysOfWeek
                                        newRowNbJoursAvant = firstSejour.nbJoursAvant
                                        newRowNbJoursApres = secondSejour.nbJoursApres


                                        mergedSejourDict[i] = [newRowBeginDate, newRowEndDate, newRowConsecutive, True, 
                                                newRowCountriesVisited, newRowStatesVisited, newRowCitiesVisited, newRowSpecificSpots, 
                                                newRowNbrPhotos, newRownbrPhotoAvg, newRownbrPhotoMax, newRownbrPhotoMin, 
                                                newRowDaysOfWeek, newRowNbJoursAvant, newRowNbJoursApres, homeCountry, 2]
                                        indexes_to_drop.extend((i, i+1, i+2))


                                elif(pause.Consecutive <= firstSejour.Consecutive and pause.Consecutive <= secondSejour.Consecutive 
                                        and lastCountrySejour1 == firstCountrySejour2):
                                    #merge
                                    newRowBeginDate = firstSejour.BeginDate
                                    newRowEndDate = secondSejour.EndDate
                                    newRowConsecutive = firstSejour.Consecutive + pause.Consecutive + secondSejour.Consecutive
                                    newRowNbrPhotos = firstSejour.nbrPhotos + secondSejour.nbrPhotos
                                    if(len(countriesSecondSejour) > 1): #To avoid getting the same country again
                                        newRowCountriesVisited = firstSejour.countriesVisited + ', ' + ', '.join(countriesSecondSejour[1:])
                                    else:
                                        newRowCountriesVisited = firstSejour.countriesVisited
                                    if(statesSecondSejour[0] != statesFirstSejour[-1]):
                                        newRowStatesVisited = firstSejour.statesVisited + ', ' + secondSejour.statesVisited
                                    elif(len(statesSecondSejour) > 1):
                                        newRowStatesVisited = firstSejour.statesVisited + ', ' + ', '.join(statesSecondSejour[1:])
                                    else:
                                        newRowStatesVisited = firstSejour.statesVisited
                                    
                                    #Cities
                                    if(citiesSecondSejour[0] != citiesFirstSejour[-1]):
                                        newRowCitiesVisited = firstSejour.citiesVisited + ', ' + secondSejour.citiesVisited
                                    elif(len(citiesSecondSejour) > 1):
                                        newRowCitiesVisited = firstSejour.citiesVisited + ', ' + ', '.join(citiesSecondSejour[1:])
                                    else:
                                        newRowCitiesVisited = firstSejour.citiesVisited
                                    
                                    newRowSpecificSpots = firstSejour.specificSpots + ', ' + secondSejour.specificSpots
                                    
                                    newRownbrPhotoAvg = (firstSejour.nbrPhotoAvg + secondSejour.nbrPhotoAvg) / 2
                                    newRownbrPhotoMin = min(firstSejour.nbrPhotoMin, secondSejour.nbrPhotoMin)
                                    newRownbrPhotoMax = max(firstSejour.nbrPhotoMax, secondSejour.nbrPhotoMax)
                                    
                                    newRowDaysOfWeek = firstSejour.daysOfWeek + ', ' + secondSejour.daysOfWeek
                                    newRowNbJoursAvant = firstSejour.nbJoursAvant
                                    newRowNbJoursApres = secondSejour.nbJoursApres


                                    mergedSejourDict[i] = [newRowBeginDate, newRowEndDate, newRowConsecutive, True, 
                                                newRowCountriesVisited, newRowStatesVisited, newRowCitiesVisited, newRowSpecificSpots, 
                                                newRowNbrPhotos, newRownbrPhotoAvg, newRownbrPhotoMax, newRownbrPhotoMin, 
                                                newRowDaysOfWeek, newRowNbJoursAvant, newRowNbJoursApres, homeCountry, 1]
                                    indexes_to_drop.extend((i, i+1, i+2))
                    
                    #If the user has 2 home countries we add it to the dataframe
                    if(secondCountry != ""):
                        df_sejour['homeCountry'] = homeCountry + ', ' + secondCountry
                    else:
                        df_sejour['homeCountry'] = homeCountry

                    df_sejour['Corrected'] = 0

                    if(len(indexes_to_drop) > 1): #Sejour to correct
                        for k in range(len(indexes_to_drop)):
                            if(k % 3 == 0):
                                df_sejour.loc[indexes_to_drop[k] + 1] = mergedSejourDict[indexes_to_drop[k]]
                                #df_sejour.drop(df_sejour.index[indexes_to_drop[k] + 1], inplace = True)
                                df_sejour.loc[indexes_to_drop[k] + 3, 'isSejour'] = False

                    for i, row in df_sejour.iterrows():
                        if(row.Corrected == 2):
                            print(row)
                    

                    for i, row in df_sejour.iterrows():
                        if(row.isSejour):
                            print(row)
                            cursor.execute(query_insert_sejour, (user, row.BeginDate, row.EndDate, row.Consecutive, 
                                row.nbrPhotoAvg, row.nbrPhotoMin, row.nbrPhotoMax, row.nbrPhotos, row.nbJoursAvant, row.nbJoursApres,
                                row.daysOfWeek, row.countriesVisited, row.statesVisited, row.citiesVisited, row.specificSpots, row.homeCountry, row.Corrected))
                            print("Inserted line : {}".format(linesInserted))
                            linesInserted += 1
                        

                except mdb.Error as e:
                    print("Exception : {} ".format(e))
                    sys.exit(1)




def GenerateSejoursTest(userList):
    for user in userList:
        listCountries, listValues = getListCountries(user)
        if(len(listCountries) > 1):
            homeCountry = listCountries[0]   #We suppose the homecountry of the user is the country where he made most of his pictures
            secondCountry = ''
            #checks for second home country
            if(len(listValues) > 2):
                maxValue = listValues[0]
                minValue = listValues[len(listValues)-1]
                second = listValues[1]
                if(second >= maxValue*0.80 and (maxValue-minValue) != 0):
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

                
                df_sejour['nbJoursAvant'] = 0
                df_sejour['nbJoursApres'] = 0
                sejour_size = df_sejour.shape[0]
                #Sets for first and last sejour respectively -1 for days before and -1 for days after
                for i in range(sejour_size):
                    if(sejour_size > 2):
                        if(df_sejour['isSejour'].iloc[i]):
                            last = -1
                            next = -1
                            if(i == 0 or i == 1): #ie 1er sejour
                                next = df_sejour.Consecutive.iloc[i+1]
                            elif(i == (sejour_size - 1) or i == (sejour_size - 2)): # ie dernier sejour
                                last = df_sejour.Consecutive.iloc[i-1]     
                            else:
                                last = df_sejour.Consecutive.iloc[i-1]
                                next = df_sejour.Consecutive.iloc[i+1]
                            
                            df_sejour.at[i + 1, 'nbJoursAvant'] = last
                            df_sejour.at[i + 1, 'nbJoursApres'] = next

                # To remove timestamps
                df_sejour['BeginDate'] = df_sejour['BeginDate'].dt.date 
                df_sejour['EndDate'] = df_sejour['EndDate'].dt.date
                
                indexes_to_drop = []
                mergedSejourDict = {}
                for i in range(sejour_size - 2):
                    if(sejour_size > 3): # minimum 3 sejours avant qu'on merge
                        if(df_sejour.isSejour.iloc[i]):
                            firstSejour = df_sejour.iloc[i]           #Should be true
                            pause = df_sejour.iloc[i + 1]      #Should be false
                            secondSejour = df_sejour.iloc[i + 2]        #Should be true
                            #We get the last country visited during the sejour and the first one in the next sejour that we want to join
                            countriesFirstSejour = firstSejour.countriesVisited.split(', ')
                            lastCountrySejour1 = countriesFirstSejour[-1]
                            countriesSecondSejour = secondSejour.countriesVisited.split(', ')
                            firstCountrySejour2 = countriesSecondSejour[0]

                            statesFirstSejour = firstSejour.statesVisited.split(', ')
                            citiesFirstSejour = firstSejour.citiesVisited.split(', ')

                            statesSecondSejour = secondSejour.statesVisited.split(', ')
                            citiesSecondSejour = secondSejour.citiesVisited.split(', ')

                            #Case where country is different
                            if(lastCountrySejour1 != firstCountrySejour2):
                                distancePays = getDistance(lastCountrySejour1, firstCountrySejour2)
                                distanceNormalized = getNormalizedDistance(distancePays)
                                if(pause.Consecutive <= firstSejour.Consecutive and 
                                                    pause.Consecutive <= secondSejour.Consecutive + distanceNormalized):
                                    print(firstSejour)
                                    print(pause)
                                    print(secondSejour)
                                    newRowBeginDate = firstSejour.BeginDate
                                    newRowEndDate = secondSejour.EndDate
                                    newRowConsecutive = firstSejour.Consecutive + pause.Consecutive + secondSejour.Consecutive
                                    newRowNbrPhotos = firstSejour.nbrPhotos + secondSejour.nbrPhotos

                                    newRowCountriesVisited = firstSejour.countriesVisited + ', ' + ', '.join(countriesSecondSejour)

                                    newRowStatesVisited = firstSejour.statesVisited + ', ' + secondSejour.statesVisited
                                    
                                    #Cities
                                    newRowCitiesVisited = firstSejour.citiesVisited + ', ' + secondSejour.citiesVisited
                                    
                                    newRowSpecificSpots = firstSejour.specificSpots + ', ' + secondSejour.specificSpots
                                    
                                    newRownbrPhotoAvg = (firstSejour.nbrPhotoAvg + secondSejour.nbrPhotoAvg) / 2
                                    newRownbrPhotoMin = min(firstSejour.nbrPhotoMin, secondSejour.nbrPhotoMin)
                                    newRownbrPhotoMax = max(firstSejour.nbrPhotoMax, secondSejour.nbrPhotoMax)
                                    
                                    newRowDaysOfWeek = firstSejour.daysOfWeek + ', ' + secondSejour.daysOfWeek
                                    newRowNbJoursAvant = firstSejour.nbJoursAvant
                                    newRowNbJoursApres = secondSejour.nbJoursApres


                                    mergedSejourDict[i] = [newRowBeginDate, newRowEndDate, newRowConsecutive, True, 
                                            newRowCountriesVisited, newRowStatesVisited, newRowCitiesVisited, newRowSpecificSpots, 
                                            newRowNbrPhotos, newRownbrPhotoAvg, newRownbrPhotoMax, newRownbrPhotoMin, 
                                            newRowDaysOfWeek, newRowNbJoursAvant, newRowNbJoursApres, homeCountry, 2]
                                    indexes_to_drop.extend((i, i+1, i+2))


                            elif(pause.Consecutive <= firstSejour.Consecutive and pause.Consecutive <= secondSejour.Consecutive 
                                    and lastCountrySejour1 == firstCountrySejour2):
                                #merge
                                newRowBeginDate = firstSejour.BeginDate
                                newRowEndDate = secondSejour.EndDate
                                newRowConsecutive = firstSejour.Consecutive + pause.Consecutive + secondSejour.Consecutive
                                newRowNbrPhotos = firstSejour.nbrPhotos + secondSejour.nbrPhotos
                                if(len(countriesSecondSejour) > 1): #To avoid getting the same country again
                                    newRowCountriesVisited = firstSejour.countriesVisited + ', ' + ', '.join(countriesSecondSejour[1:])
                                else:
                                    newRowCountriesVisited = firstSejour.countriesVisited
                                if(statesSecondSejour[0] != statesFirstSejour[-1]):
                                    newRowStatesVisited = firstSejour.statesVisited + ', ' + secondSejour.statesVisited
                                elif(len(statesSecondSejour) > 1):
                                    newRowStatesVisited = firstSejour.statesVisited + ', ' + ', '.join(statesSecondSejour[1:])
                                else:
                                    newRowStatesVisited = firstSejour.statesVisited
                                
                                #Cities
                                if(citiesSecondSejour[0] != citiesFirstSejour[-1]):
                                    newRowCitiesVisited = firstSejour.citiesVisited + ', ' + secondSejour.citiesVisited
                                elif(len(citiesSecondSejour) > 1):
                                    newRowCitiesVisited = firstSejour.citiesVisited + ', ' + ', '.join(citiesSecondSejour[1:])
                                else:
                                    newRowCitiesVisited = firstSejour.citiesVisited
                                
                                newRowSpecificSpots = firstSejour.specificSpots + ', ' + secondSejour.specificSpots
                                
                                newRownbrPhotoAvg = (firstSejour.nbrPhotoAvg + secondSejour.nbrPhotoAvg) / 2
                                newRownbrPhotoMin = min(firstSejour.nbrPhotoMin, secondSejour.nbrPhotoMin)
                                newRownbrPhotoMax = max(firstSejour.nbrPhotoMax, secondSejour.nbrPhotoMax)
                                
                                newRowDaysOfWeek = firstSejour.daysOfWeek + ', ' + secondSejour.daysOfWeek
                                newRowNbJoursAvant = firstSejour.nbJoursAvant
                                newRowNbJoursApres = secondSejour.nbJoursApres


                                mergedSejourDict[i] = [newRowBeginDate, newRowEndDate, newRowConsecutive, True, 
                                            newRowCountriesVisited, newRowStatesVisited, newRowCitiesVisited, newRowSpecificSpots, 
                                            newRowNbrPhotos, newRownbrPhotoAvg, newRownbrPhotoMax, newRownbrPhotoMin, 
                                            newRowDaysOfWeek, newRowNbJoursAvant, newRowNbJoursApres, homeCountry, 1]
                                indexes_to_drop.extend((i, i+1, i+2))
                
                #If the user has 2 home countries we add it to the dataframe
                if(secondCountry != ""):
                    df_sejour['homeCountry'] = homeCountry + ', ' + secondCountry
                else:
                    df_sejour['homeCountry'] = homeCountry

                df_sejour['Corrected'] = 0

                if(len(indexes_to_drop) > 1): #Sejour to correct
                    for k in range(len(indexes_to_drop)):
                        if(k % 3 == 0):
                            df_sejour.loc[indexes_to_drop[k] + 1] = mergedSejourDict[indexes_to_drop[k]]
                            #df_sejour.drop(df_sejour.index[indexes_to_drop[k] + 1], inplace = True)
                            df_sejour.loc[indexes_to_drop[k] + 3, 'isSejour'] = False

                for i, row in df_sejour.iterrows():
                    if(row.Corrected == 2):
                        print(row)
                

                """ for i, row in df_sejour.iterrows():
                    if(row.isSejour):
                        print("Inserting row")
                        print(row)
                        cursor.execute(query_insert_sejour, (user, row.BeginDate, row.EndDate, row.Consecutive, 
                            row.nbrPhotoAvg, row.nbrPhotoMin, row.nbrPhotoMax, row.nbrPhotos, row.nbJoursAvant, row.nbJoursApres,
                            row.daysOfWeek, row.countriesVisited, row.statesVisited, row.citiesVisited, row.specificSpots, row.homeCountry, row.Corrected))
                        print("Inserted line : {}".format(linesInserted))
                        linesInserted += 1 """
                    

            except mdb.Error as e:
                print("Exception : {} ".format(e))
                sys.exit(1)


if(__name__ == "__main__"):
    cursor = connection.cursor()
    #userList = ['10124937']
    GenerateSejours()
    print("Done ! ")
    if connection:
        connection.close()