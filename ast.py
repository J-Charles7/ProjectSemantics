
class AST:
    identifiant = 0
    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.sons = []

    def __str__(self):
        return '%s%s' % (self.value, self.sons)

    def __repr__(self):
        return '%s%s' % (self.value, self.sons)

    def e_toAsm(self):
        if self.type == 'NUMBER':
            return "mov eax, %s\n" % self.value
        elif self.type == 'ID':
            return "mov eax, [%s]\n" % self.value
        elif self.type == 'OPBIN':
            op1 = self.sons[0].e_toAsm()
            op2 = self.sons[1].e_toAsm()
            if self.value == '+':
                res = "%s\npush eax\n%s\npop ebx\nadd eax, ebx\n" % (op1, op2)
            else: # suppose que l'op est un -
                res = "%s\npush eax\n%s\npop ebx\nsub eax, ebx\n" % (op2, op1)
            return res

    def c_toAsm(self):
        if self.value == 'asgnt':
            return '%s\nmov [%s], eax\n' % (self.sons[1].e_toAsm(), self.sons[0])
        elif self.value == 'seq':
            return '%s%s' % (self.sons[0].c_toAsm(), self.sons[1].c_toAsm())
        else:
            AST.identifiant = AST.identifiant + 1
            id = AST.identifiant
            return '''debutboucle%s:
%s
cmp eax, 0
jz finboucle%s
%s
jmp debutboucle%s
finboucle%s:
''' % (id, self.sons[0].e_toAsm(), id, self.sons[1].c_toAsm(), id, id)

    def pvars(self):
        vars = set()
        if self.type == 'prog':
            vars.update(self.sons[3].pvars())
            vars.update(self.sons[4].pvars())
            return vars
        elif self.type == 'commande':
            if self.value == 'asgnt':
                vars.add(self.sons[0]+';'+str(self.sons[2]))
                vars.update(self.sons[1].pvars())
                return vars
            else:
                vars.update(self.sons[0].pvars())
                vars.update(self.sons[1].pvars())
                return vars
        else:
            if self.type == 'OPBIN':
                vars.update(self.sons[0].pvars())
                vars.update(self.sons[1].pvars())
                return vars
            elif self.type == 'NUMBER':
                return vars
            else:
                vars.add(self.value+';'+str(self.sons[0]))
                return vars

    def init_var(self, var, i):
        return '''mov ebx, [eax + %s]
push eax
push ebx
call atoi
add esp, 4
mov [%s], eax
pop eax
''' % (str(4*(i+1)), var)

    def com2List(self):
        vars = []
        if self.type == 'commande':
            if self.value == 'asgnt':
                vars.append(list(self.sons[0]))
                vars.append(self.sons[1].exp2List())
                return vars
            elif self.value == 'while':
                vars.append(self.sons[0].exp2List())
                vars.append(self.sons[1].com2List())
                return vars
            elif self.value == 'seq':
                vars.append(self.sons[0].com2List())
                vars.append(self.sons[1].com2List())
                return vars


    def exp2List(self):
        var_exp = set()
        if self.type == 'ID':
            var_exp.update([self.value, self.sons[0]])
        elif self.type == 'OPBIN':
            var_exp.update(self.sons[0].exp2List())
            var_exp.update(self.sons[1].exp2List())
        return  var_exp

    def dec2List(self):
        if self.type == 'declaration':
            #retourne : typeVariable, nomVariable, ligneTypeVariable, ligneNomVariable
            return [self.value, self.sons[0], self.sons[1], self.sons[2]]

    # Variables passees en parametre a la fonction main
    def vars_main(self):
        var_params_main = []
        if self.type == 'prog':
            if len(self.sons) != 0:
                for paramItem in self.sons[1]:
                    var_params_main.append(paramItem.dec2List())
        return var_params_main

    def afficherListe(self, listeA):
        for var in listeA:
            print(var)

    #Variables declarees dans le programme main
    def vars_decl(self):
        var_declarees = []
        if self.type == 'prog':
            if len(self.sons) != 0:
                for declItem in self.sons[2]:
                    var_declarees.append(declItem.dec2List())
        return var_declarees


    def epurerListeVarsDecl (self, monSet):
        monSetPerfect = []
        corr = []
        monSet = list(monSet)
        for i in range(len(monSet)):
            mesTokens1 = str.split(monSet[i], ';')
            lines = set()
            trouve = 0
            for j in range(i + 1, len(monSet)):
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

        for i in range(len(monSet)):
            if not corr.__contains__(i):
                monSetPerfect.append(monSet[i])
        return monSetPerfect

    def verifier_variables(self):
        var_util = self.epurerListeVarsDecl(self.pvars())
        var_params = self.vars_main()
        print('Variables du main : %s ' % var_params)
        var_decl = self.vars_decl()

        #Verification de variables utilisees declarees au prealable
        for var_utilisee in var_util:
            declaree = 0
            infos_var_utilisee = str.split(var_utilisee,';')
            for var_declaree in var_decl:
                if infos_var_utilisee[0] == var_declaree[1]:
                    declaree = 1
            if declaree == 0:
                print('Erreur : variable %s non déclarée : ligne(s) %s' %
                      (infos_var_utilisee[0], infos_var_utilisee[1]))

        #Verification de la declaration des variables passees en paramètre dans le main
        var_params = self.vars_main()
        for param in var_params:
            declaree = 0
            for var_declaree in var_decl:
                if param[1] == var_declaree[1]:
                    declaree = 1
                    if param[0] == var_declaree[0]:
                        declaree = 2
            if declaree == 1:
                print('Erreur : variable %s déclarée (ligne %s) et utilisée en paramètre (ligne %s) '
                      'dans le main mais avec des types différents'%
                      (param[1], var_declaree[3], param[3]))
            if declaree == 0:
                print('Erreur : variable %s non déclarée et utilisée en paramètre dans le main'
                      ' : ligne(s) %s' %
                      (param[1], param[3]))

        #Verification de non redondance des variables passees en paramètre dans le main
        for i in range(len(var_params)):
            for j in range(i + 1, len(var_params)):
                if var_params[i][1] == var_params[j][1]:
                    print('Erreur : repassage en paramètre au main de la variable %s '
                          '(ligne %s) déjà utilisée (ligne %s)' %
                          ((var_params[j][1]), var_params[j][3], var_params[i][3]))

        # Verification de non redondante dans les declarations des variables
        for i in range(len(var_decl)):
            for j in range(i + 1, len(var_decl)):
                if var_decl[i][1] == var_decl[j][1]:
                    print('Erreur : redéclaration de la variable %s (ligne %s) déjà déclarée (ligne %s)' %
                          ((var_decl[j][1]), var_decl[j][3], var_decl[i][3]))

    def verifier_valeur_retour(self):
        if self.type == 'prog':
            print('Type attendu : %s et Type reçu : %s' % (self.sons[0][0], self.sons[5].value))
            if self.sons[0][0] == 'int' and self.sons[5].value == 'float':
                print('Erreur : valeur de retour trouvée de type %s (ligne %s) et '
                      'valeur de retour attendue de type %s (ligne %s)' %
                      (self.sons[5].value, self.sons[5].sons[1], self.sons[0][0], self.sons[0][1]))

    #Fonction pour retrouver le type d'une variable a partir de son nom
    def trouverType(self, maVar):
        var_declarees = []
        var_declarees = self.vars_decl()
        trouve = 0
        for item in var_declarees:
            if item[1] == maVar:
                return item[0]
        return False

    def type_operandes_expression(self):
        if self.sons[4].type == 'ID':
            return list(self.trouverType(self.sons[4].value))
        elif self.sons[4].type == 'NUMBER':
            if isinstance(self.sons[4].type, int):
                return ['int']
            else:
                return ['float']
        else:
            return [self.sons[4][0].type_operandes_expression(), self.sons[4][1].type_operandes_expression()]


    def verifier_typage_operations(self, expr):
       typesOperandes = []
       print('Lop : %s; Rop : %s' % (typesOperandes[0], typesOperandes[1]))
       typesOperandes = expr.type_operandes_expression()
       if len(typesOperandes) > 1:
           if typesOperandes[0] == 'int' and typesOperandes[1] == 'float':
               print('Erreur : tentative d\'affectation de valeur de type float à '
                     'une variable de type int (ligne %s)' % (expr.sons[2]))


                # if str(self.sons[4].value).__contains__('.') or
                #    str(self.sons[4].value).__contains__('e') or

        #AST.type = OPBIN - expression
        #AST.type = commande, AST.value = asgnt
        # if self.type == 'prog':
        #     if self.sons[3].type == 'OPBIN':
        #         if self.sons[3][0].type == 'ID':
        #             if self.trouverType(self.sons[3][0].value) is not False:
        #                 typeOperandeG = self.trouverType(self.sons[3][0].value)
        #         else

    def init_vars(self, moule):
        moule = moule.replace('LEN_INPUT',str(1+len(self.sons[0])))
        init_var = [self.init_var(self.sons[0][i],i) for i in range (len(self.sons[0]))]
        moule = moule.replace('VAR_INIT', '\n'.join(init_var))
        return moule

    def p_toAsm(self):
        f = open('moule.asm')
        moule = f.read()
        vars = self.pvars()
        dvars = {'%s: dd 0' % v for v in vars }
        var_decl = '\n'.join(dvars)
        moule = moule.replace('VAR_DECL', var_decl)
        moule = self.init_vars(moule)
        moule = moule.replace('COMMAND_EXEC', self.sons[1].c_toAsm())
        moule = moule.replace('EVAL_OUTPUT', self.sons[2].e_toAsm())
        return moule

