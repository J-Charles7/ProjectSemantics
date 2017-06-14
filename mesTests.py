#Creation de liste de listes
x = []
x = [1, 2, 3, 4, 7, 5, 6, ['int', 'rien']]
x.append(['int', 'rien'])
x.append(['float', 'tout'])
x.insert(0, 0)
y = x[9]
for ob in x:
    print(ob)

monSet = {'X;1', 'Z;2', 's;2', 'X;2', 'Y;1', 's;3', 'X;4', 'X;0'}
monSetPerfect = []
corr = []
com1 = 0
monSet = list(monSet)
for i in range(len(monSet)):
    mesTokens1 = str.split(monSet[i], ';')
    lines = set()
    trouve = 0
    for j in range (i + 1, len(monSet)):
        mesTokens2 = str.split(monSet[j], ';')
        if mesTokens1[0] == mesTokens2[0]:
            trouve = 1
            lines.update(mesTokens1[1])
            lines.update(mesTokens2[1])
            corr.append(j)
    if trouve == 1:
        lines = list(lines)
        lines.sort()
        lignes = lines[0]
        for item in lines:
            if item != lines[0]:
                lignes = lignes + ', ' + item
        monSet[i] = mesTokens1[0] + ';' + lignes

print(monSet)
print(corr)
for i in range(len(monSet)):
    if not corr.__contains__(i):
        monSetPerfect.append(monSet[i])
print('Perfect %s' % (monSetPerfect))
for i in corr:
    monSet[i] = 'NULL'
monSet.remove('NULL')
# print(monSet)
for item in monSet:
    if item == 'NULL':
        pass
# print(monSet)





# for item in monSet:
#     mesTokens1 = str.split(item, ';')
#     com2 = com1
#     for item2 in monSet:
#         mesTokens2 = str.split(item2, ';')
#         if mesTokens1[0] == mesTokens2[0]:
#             print(mesTokens1[0] + ' est egal à ' + mesTokens2[0])
#             if mesTokens1[1] != mesTokens2[1]:
#                 monSetPerfect.append(mesTokens1[0] + ';' + mesTokens1[1] + ', ' + mesTokens2[1])
#                 # mesTokens1[1] = mesTokens1[1] + ', ' + mesTokens2[1]
#             print(mesTokens1[1])
#             corr.append(com2)
#         com2 = com2 + 1
#     com1 = com1 + 1
# print('First : %s' % (monSetPerfect))
# print('First : %s' % (monSet))
# monSet = list(monSet)
# com1 = 0
# com2 = 0
# for item in monSet:
#     if not corr.__contains__(com1):
#        monSetPerfect.append(item)
#     com1 = com1 + 1
# print('Second : %s' % (monSetPerfect))


# for item in monSet:
#     mesTokens = str.split(item,';')
#     print('Nom : %s - Ligne : %s' % (mesTokens[0], mesTokens[1]))
#     if
# if x.__contains__(7):
#     print('Je contiens 7 : %2s fois' % (x.count(7)))
# print(type(x), x)
# print(type(y[0]))
