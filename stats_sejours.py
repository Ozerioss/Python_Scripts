import pymysql as mdb
import sys
import pandas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

query_stats_sejour = "SELECT paysOrigine, avg(dureeJ) as avgSejourLength\
                    FROM Sejour_Corrected\
                    WHERE dureeJ > 1 \
                    GROUP BY paysOrigine\
                    ORDER BY count(nbPhotoTotal) desc\
                    LIMIT 15;\
                "

query_nbrSejours_avg = "SELECT paysOrigine, count(*)/count(DISTINCT idUser) as nombreSejoursAvg\
                            FROM Sejour\
                            WHERE Common = 1\
                            GROUP BY paysOrigine\
                            ORDER BY count(*) desc\
                            LIMIT 15;\
                    "

query_nbrSejours_avg_Corrected = "SELECT paysOrigine, count(*)/count(DISTINCT idUser) as nombreSejoursAvg\
                            FROM Sejour_Corrected\
                            GROUP BY paysOrigine\
                            ORDER BY count(*) desc\
                            LIMIT 15;\
                    "


connection = mdb.connect(host="127.0.0.1", 
                        user="KarimKidiss", 
                        passwd= "stageDVRC2018", 
                        db = "KidissBD", 
                        port = 3305,
                        charset = 'utf8',
                        autocommit=True
                    )

#Helper function to make custom percentage in graphs
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = float(round(pct*total/100.0))
        if(pct>6):
            return '{p:.1f}% ({v:d})'.format(p=pct,v=val)
        else:
            return '{p:.1f}%'.format(p=pct)
    return my_autopct


#Pour faire des graphiques et les enregistrer en photo .png
def statsSejours():
    try:
        cursor.execute(query_nbrSejours_avg_Corrected)
        result = cursor.fetchall()

        df = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])

        if(not df.empty):
            print("Plotting ...")

            df.nombreSejoursAvg = df.nombreSejoursAvg.astype(float)
            currentPlot = df.plot(x=df.columns[0], kind='bar', color='k') #définit quel type de graphe

            plt.title("Nombre moyen de séjours par pays d'origine")
            fig = currentPlot.get_figure()
            plt.tight_layout()          #Fixes label size

            print("Saving figure..")
            fig.savefig('nbrSejourAvg_Sejour_Corrected.png')

            print("No data found.")
    except mdb.Error:
        print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
        sys.exit(1)


def executeCommune():
    listCommunes = getPopularCommunes()
    for commune in listCommunes:
        pp = PdfPages('Plots/Plots_Instagram/NbrUser_Departement_{}_{}_{}.pdf'.format(commune, "2011", "2015"))
        try:
            cursor.execute(query_nbrUser_Temps, commune)
            #cursor.execute(query_nbrPhoto_Dpt(year, month, dpt))
            result = cursor.fetchall()

            df = pandas.DataFrame.from_records([row for row in result], columns = [desc[0] for desc in cursor.description])

            print("avant : ")
            print(df.head())

            df[['month', 'year']] = df.date.str.split('/', expand = True)
            df = df.pivot(index = 'month', columns='year', values='nombreUser')
            #df.sort_values('month', 0, True, True)
            df.index = df.index.astype(int)
            df = df.sort_index()
            print("df.columns : ", df.columns)
            print(df.head())

            if(not df.empty):
                print("Plotting ...")
                #currentPlot = df.plot(x=df.columns[0], kind='bar')
                currentPlot = df.plot.bar()

                plt.title("Nombre de User(ayant fait une photo) par Departement : \n {}. Année : 2011 - 2015 ".format(commune))
                fig = currentPlot.get_figure()
                plt.tight_layout()          #Fixes label size

                print("Saving figure..")

                pp.savefig()
            else:
                print("No data found.")
                

        except mdb.Error:
            print("Exception {} : {} ".format(mdb.Error.args[0], mdb.Error.args[1]))
            sys.exit(1)
        pp.close()

if(__name__ == "__main__"):
    cursor = connection.cursor()
    statsSejours()
    print("Done !")