#Creation de liste de listes
x = []
x = [1, 2, 3, 4, 7, 5, 6, ['int', 'rien']]
x.append(['int', 'rien'])
x.append(['float', 'tout'])
x.insert(0, 0)
y = x[9]
for ob in x:
    print(ob)
# if x.__contains__(7):
#     print('Je contiens 7 : %2s fois' % (x.count(7)))
# print(type(x), x)
# print(type(y[0]))
