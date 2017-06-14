maListe = [['int', 'rien', 1, 1], ['float', 'tout', 1, 1], ['int', 'affaire', 1, 1],
           ['float', 'affaire', 1, 2],  ['int', 'affaire', 1, 4],  ['int', 'tout', 1, 7],
           ['int', 'truc', 1, 10]]
for i in range(len(maListe)):
    for j in range(i + 1, len(maListe)):
        if maListe[i][1] == maListe[j][1]:
            print('Erreur : redéclaration de la variable %s (ligne %s) déjà déclarée (ligne %s)' %
                  ((maListe[j][1]), maListe[j][3], maListe[i][3]))
