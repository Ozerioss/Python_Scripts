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

query_rndmUsers_excludingHome = "SELECT concat(jour, '-', mois, '-', annee) as date, count(1) as nbrPhoto             \
                                        FROM Instagram_F                                                        \
                                        JOIN gadm2.gadm2 ON gadm2.gadm2.gid = Instagram_F.shape_gid             \
                                        WHERE idUser = %s AND gadm2.gadm2.name_0 != %s                                    \
                                        AND annee between '2011' and '2015'                                     \
                                        GROUP BY annee, mois, jour                                            \
                                        ORDER BY annee, mois, jour;                                             \
                        "

                        

query_rndmUsers_excludingHome_v2 = " SELECT id, str_to_date(concat(annee, '/', mois, '/', jour), '%%Y/%%m/%%d') as date, name, gadm2.gadm2.name_0, gadm2.gadm2.name_1, gadm2.gadm2.name_2 \
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
        df_calendrier = pandas.DataFrame({"Dates" : calendar, "nbrPhoto": nbrPhoto})
        df_calendrier.Dates = pandas.to_datetime(df_calendrier.Dates)

        cursor.execute(query_rndmUsers_excludingHome_v2, (user, homeCountry))
        result = cursor.fetchall()

        
        try:
            df = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])
                #photo +1
            #print(df.head())

            #fill dataframe old style
            """ for i, row in df.iterrows():
                countPhoto = 0
                if(i+1 == len(df.index)):
                    break
                currentDate = df.at[i, 'date']
                nextDate = df.at[i+1, 'date']
                print("Current Date : {}  i : {} \n Next Date : {}  i+1 : {}".format(currentDate, i, nextDate, i+1))
            print(len(df.index)) """

            #print(df_calendrier.at[i, 'Dates'])
            """ for i, row in df.iterrows():
                df_calendrier.loc[df_calendrier['Dates'] == df.at[i, 'date'], 'nbrPhoto'] += 1
                #print(row)
                if(df.at[i, 'date'] in df_calendrier.values):
                    print("WTF") """

            df_calendrier.loc[df_calendrier['Dates'].isin(df['date']), 'nbrPhoto'] += 1

            df_calendrier['nextDay'] = df_calendrier['Dates'].shift(-1)
            df_calendrier['nextDayCount'] = df_calendrier['nbrPhoto'].shift(-1)

            #print(df_calendrier.head())
            
            #faire requete pour group by ou bien utiliser df.gpby
            counter = 0
            d = {}
            listeJours = []
            """ for i, row in df_calendrier.iterrows():
                currentDateCount = df_calendrier.at[i, 'nbrPhoto']
                nextDateCount = df_calendrier.at[i, 'nextDayCount']

                currentDate = df_calendrier.at[i, 'Dates'].strftime('%Y-%m-%d')
                nextDate = df_calendrier.at[i, 'nextDay']

                if(currentDateCount > 0):
                    #Début séjour
                    listeJours.append(currentDate)
                    counter += 1
                    d['sejour{}'.format(len(d))] = currentDate
                if(currentDateCount = 0): """
                    #offTime
                    
                    
                    #print(row)

            #df_calendrier.reset_index().groupby('Dates')['index'].apply(np.array)

            df_calendrier['temp'] = (df_calendrier.nbrPhoto.diff(1) != 0).astype('int').cumsum()

            df_sejour = pandas.DataFrame({'BeginDate' : df_calendrier.groupby('temp').Dates.first(), 
                                            'EndDate': df_calendrier.groupby('temp').Dates.last(), 
                                            'Consecutive' : df_calendrier.groupby('temp').size(),
                                            })
            df_sejour['isSejour'] = False

            df_sejour.loc[df_sejour['BeginDate'].isin(df['date']), 'isSejour'] = True

            #df_sejour.loc[df_sejour['BeginDate'].isin(df['date']), 'paysVisited'] = df.name_0
            
            #dunno = df.loc[df['date'].astype('datetime64[ns]') == df_sejour.BeginDate, 'name_0'].iloc[0]

            df.date = pandas.to_datetime(df.date)
            #print(df.date)
            #print(df_sejour.BeginDate)
            #df_sejour['paysVisités'] = []
            #mask = 0
            df_sejour['countriesVisited'] = ""
            for i, row in df_sejour.iterrows():
                #print(row)
                mask = (df['date'] >= df_sejour.at[i, 'BeginDate']) & (df.date <= df_sejour.at[i, 'EndDate'])
                #print(df.name_0.loc[mask])
                tmpList = df.name_0.loc[mask]
                newList = list(dict.fromkeys(tmpList))
                #df_sejour.loc[df_sejour['countriesVisited']]
                
                
                if(len(newList) > 0):
                    tmpString = ', '.join(newList)
                    print("tmpString : ", tmpString)
                    #df_sejour.loc[df_sejour['isSejour'] == True, 'countriesVisited'] += tmpString
                    df_sejour.at[i, 'countriesVisited'] = tmpString
                #df_sejour.at[i, 'countriesVisited'] = newList[0]

                


            #print(df_sejour.head())

            for i, row in df_sejour.iterrows():
                print(row)

            #print(df_sejour.head())
            #print(dunno)
            #print(df_calendrier.head())

            


            """ for i, row in df_calendrier.iterrows():
                print(row) """
            #soit faire les sejours directement
            """ print(currentDateCount)
            print(d) """
            #plotting stuff
            """ if(not df.empty):
                print("Plotting ...")

                fig, ax = plt.subplots()
                ax.plot(df["Dates"], df["nbrPhoto"], linewidth=.2)


                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_minor_locator(mdates.DayLocator())
                monthFmt = mdates.DateFormatter('%b')
                ax.xaxis.set_major_formatter(monthFmt)

                plt.title("User : \n {} Année : {} ".format(user, year))

                plt.tight_layout()          #Fixes label size

                print("Saving figure..")

                pp.savefig()
            else:
                print("No data found.") """
            

        except mdb.Error:
            print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
            sys.exit(1)
        #pp.close()



def executeRndmUsersTest():
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
        df_calendrier = pandas.DataFrame({"Dates" : calendar, "nbrPhoto": nbrPhoto})
        df_calendrier.Dates = pandas.to_datetime(df_calendrier.Dates)

        cursor.execute(query_rndmUsers_excludingHome_v2, (user, homeCountry))
        result = cursor.fetchall()

        
        try:
            df = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])

            df_calendrier.loc[df_calendrier['Dates'].isin(df['date']), 'nbrPhoto'] += 1


            df_calendrier['temp'] = (df_calendrier.nbrPhoto.diff(1) != 0).astype('int').cumsum()

            df_sejour = pandas.DataFrame({'BeginDate' : df_calendrier.groupby('temp').Dates.first(), 
                                            'EndDate': df_calendrier.groupby('temp').Dates.last(), 
                                            'Consecutive' : df_calendrier.groupby('temp').size(),
                                            })
            df_sejour['isSejour'] = False

            df_sejour.loc[df_sejour['BeginDate'].isin(df['date']), 'isSejour'] = True

            df.date = pandas.to_datetime(df.date)

            for tmp in result:
                df_calendrier.loc[df_calendrier['Dates'] == pandas.to_datetime(tmp[1]), 'nbrPhoto'] += 1

            df_calendrier.loc[df_calendrier.nbrPhoto != 0, 'nbrPhoto'] -= 1

            df_sejour['countriesVisited'] = ""
            for i, row in df_sejour.iterrows():
                #print(row)
                mask = (df['date'] >= df_sejour.at[i, 'BeginDate']) & (df.date <= df_sejour.at[i, 'EndDate'])
                #print(df.name_0.loc[mask])
                tmpList = df.name_0.loc[mask]
                newList = list(dict.fromkeys(tmpList))
                #df_sejour.loc[df_sejour['countriesVisited']]
                
                
                if(len(newList) > 0):
                    tmpString = ', '.join(newList)
                    print("tmpString : ", tmpString)
                    #df_sejour.loc[df_sejour['isSejour'] == True, 'countriesVisited'] += tmpString
                    df_sejour.at[i, 'countriesVisited'] = tmpString

            
            for i, row in df_calendrier.iterrows():
                if(df_calendrier.at[i, 'nbrPhoto'] != 0):
                    print(row)

            """ for i, row in df_sejour.iterrows():
                print(row) """

            

        except mdb.Error:
            print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
            sys.exit(1)



def executeRndmUsers_deprecated():
    for user in userList:
        pp = PdfPages('Plots/Plots_Instagram/009TestYearly_Rndm_Users_{}_{}_{}_World.pdf'.format(user, "2011", "2015"))

        listCountries = getListCountries(user)
        homeCountry = listCountries[0]

        cursor.execute(query_rndmUsers_excludingHome, user, homeCountry)
        result = cursor.fetchall()

        for year in yearList:
            nbrPhoto = 0
            dates = pandas.date_range("01-01-{}".format(year), "01-01-{}".format(str(int(year)+1)))
            df = pandas.DataFrame({"Dates" : dates, "nbrPhoto": nbrPhoto})
            try:
                for tmp in result:
                    print("tmp0 : {}, tmp1 : {}".format(tmp[0], tmp[1]))
                    df.loc[df['Dates'] == tmp[0], 'nbrPhoto'] = tmp[1]

                print(df.head())

                if(not df.empty):
                    print("Plotting ...")

                    fig, ax = plt.subplots()
                    ax.plot(df["Dates"], df["nbrPhoto"], linewidth=.2)


                    ax.xaxis.set_major_locator(mdates.MonthLocator())
                    ax.xaxis.set_minor_locator(mdates.DayLocator())
                    monthFmt = mdates.DateFormatter('%b')
                    ax.xaxis.set_major_formatter(monthFmt)

                    plt.title("User : \n {} Année : {} ".format(user, year))

                    plt.tight_layout()          #Fixes label size

                    print("Saving figure..")

                    pp.savefig()
                else:
                    print("No data found.")
                

            except mdb.Error:
                print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
                sys.exit(1)
        pp.close()





cursor.execute("""INSERT INTO Sejour(idUser, dateDebut, dateFin, dureeJ) VALUES('test', 'test', 'test', 'test')""")


print("Done ! ")


if connection:
    connection.close()


