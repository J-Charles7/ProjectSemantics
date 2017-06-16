import enfloat.EntierFloat as entFo

test = [['int'], [['int', 'int'], ['True', ['True', [['float', 'int'], [['float', 'int'], ['int', 'int']]]]]]]
# print(test)
# print(test[0])
def parcoursRecursifListe(listeAParcourir):
    if isinstance(listeAParcourir, list) and len(listeAParcourir) != 0:
        for i in range(len(listeAParcourir)):
            if isinstance(listeAParcourir[i], list):
                return parcoursRecursifListe(listeAParcourir[i])
            else:
                if listeAParcourir[i] == 'True':
                    print ('True')
    else:
        pass
parcoursRecursifListe(test)
