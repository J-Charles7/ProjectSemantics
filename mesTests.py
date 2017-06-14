#Creation de liste de listes
x = []
x = [1, 2, 3, 4, 7, 5, 6, ['int', 'rien']]
x.append(['int', 'rien'])
x.append(['float', 'tout'])
x.insert(0, 0)
y = x[9]
for ob in x:
    print(ob)

monSet = {'X;1', 'Z;2', 's;2', 'X;2', 'Y;1'}
for item in monSet:
    mesTokens = str.split(item,';')
    print('Nom : %s - Ligne : %s' % (mesTokens[0], mesTokens[1]))
# if x.__contains__(7):
#     print('Je contiens 7 : %2s fois' % (x.count(7)))
# print(type(x), x)
# print(type(y[0]))
