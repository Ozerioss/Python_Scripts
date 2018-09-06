Entrée : user ID
Sortie : pays originel du user

Fonction : GetListCountries
    (1)QueryNbrPicturesPerCountry
    homeCountry = (2)GetCountryWithMaxPictures
    return homeCountry

Entrée : user ID, pays originel
Sortie : Insertion dans la base

Fonction : GenerateSejour
    Pour tous les utilisateurs Faire :
        (3)QueryAllPictures(user, paysOrigine)
        (4)FillDataframe
        (5)Calculation
        Pour tous les séjours Faire :
            DetermineBeginDate
            DetermineEndDate
            DetermineConsecutiveDays
        (6)InsertInDatabase

#v2

Entrée : user ID
Sortie : pays originel du user

Fonction : GetListCountries
    (1)QueryNbrPicturesPerCountry
    homeCountry = (2)GetCountryWithMaxPictures
    return homeCountry

Entrée : user ID, pays originel
Sortie : Insertion dans la base

Fonction : GenerateSejour
    Pour tous les utilisateurs Faire :
        (3)QueryAllPictures(user, paysOrigine)
        (4)FillDataframe
        (5)Calculation
        Pour tous les séjours Faire :
            DetermineBeginDate
            DetermineEndDate
            DetermineConsecutiveDays
        Pour tous les séjours après calcul Faire :
            Si la condition est respectée : 
                (7)Calculation
                (8)MergeSejour
            (6)InsertInDatabase