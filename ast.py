# import enfloat
# from entierFloatException import EntierFloatException as enReelException

#Exception lancée lors d'une tentative d'affectation de valeur float a une variable int
class EntierFloat(Exception):
    def __init__(self, message, value):
        self.message = message
        self.value = value

        def __str__(self):
            return (repr(self.value))

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

    def init_var_int(self, var, i):
        return '''mov ebx, [eax + %s]
push eax
push ebx
call atoi
add esp, 4
mov [%s], eax
pop eax
''' % (str(4*(i+1)), var)

    def init_var_float(self, var, i):
            return '''mov ebx, [eax + %s]
push eax
push ebx
call atof
fadd esp, 4
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

    def est_division_par_zero_exp(self):
        if self.type == 'ID':
            return False
        elif self.type == 'NUMBER':
            return  False
        elif self.type == 'OPBIN':
            print("Opérateur = %s - Type = %s" % (self.value, type(self.value)))
            if self.value == '/' :
                print("Division présente")
                if (isinstance(self.sons[1], float) and float(self.sons[1]) == float(0)) or \
                        (isinstance(self.sons[1], int) and int(self.sons[1]) == int(0)):
                    print('Erreur : tentative de division par \'zéro\': ligne %s' %
                          (self.sons[2]))
                return True
            else:
                return self.sons[1].est_division_par_zero_exp()

    def est_division_par_zero_com(self):
        if self.type == 'commande':
            if self.value == 'asgnt':
                return False
            elif self.value == 'seq':
                return self.sons[0].est_division_par_zero_com() or self.sons[1].est_division_par_zero_com()
            elif self.value == 'while':
                return self.sons[0].est_division_par_zero_exp() or self.sons[1].est_division_par_zero_com()

    # Fonction transformant une declaration en liste
    # : typeVariable, nomVariable, ligneTypeVariable, ligneNomVariable
    def dec2List(self):
        if self.type == 'declaration':
            return [self.value, self.sons[0], self.sons[1], self.sons[2]]

    # Variables passees en parametre a la fonction main
    def vars_main(self):
        var_params_main = []
        if self.type == 'prog':
            if len(self.sons) != 0:
                for paramItem in self.sons[1]:
                    var_params_main.append(paramItem.dec2List())
        return var_params_main

    #Variables declarees dans le programme main
    def vars_decl(self):
        var_declarees = []
        if self.type == 'prog':
            if len(self.sons) != 0:
                for declItem in self.sons[2]:
                    var_declarees.append(declItem.dec2List())
        return var_declarees + self.vars_main()


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
        erreur_trouvee = False
        var_util = self.epurerListeVarsDecl(self.pvars())
        var_params = self.vars_main()
        var_decl = self.vars_decl()

        #Verification de variables utilisees dans le corps du programme declarees au prealable
        for var_utilisee in var_util:
            declaree = 0
            infos_var_utilisee = str.split(var_utilisee,';')
            for var_declaree in var_decl:
                if infos_var_utilisee[0] == var_declaree[1]:
                    declaree = 1
            if declaree == 0:
                print('Erreur : variable \'%s\' non déclarée : ligne(s) %s' %
                      (infos_var_utilisee[0], infos_var_utilisee[1]))
                erreur_trouvee = True

        #Verification de la declaration des variables passees en paramètre dans le main
        # var_params = self.vars_main()
        # for param in var_params:
        #     declaree = 0
        #     for var_declaree in var_decl:
        #         if param[1] == var_declaree[1]:
        #             declaree = 1
        #             if param[0] == var_declaree[0]:
        #                 declaree = 2
        #     if declaree == 1:
        #         print('Erreur : variable \'%s\' déclarée (ligne %s) et utilisée en paramètre (ligne %s) '
        #               'dans le main mais avec des types différents'%
        #               (param[1], var_declaree[3], param[3]))
        #         erreur_trouvee = True
        #     if declaree == 0:
        #         print('Erreur : variable \'%s\' non déclarée et utilisée en paramètre dans le main'
        #               ' : ligne(s) %s' %
        #               (param[1], param[3]))
        #         erreur_trouvee = True

        #Verification de non redondance des variables passees en paramètre dans le main
        for i in range(len(var_params)):
            for j in range(i + 1, len(var_params)):
                if var_params[i][1] == var_params[j][1]:
                    print('Erreur : repassage en paramètre au main de la variable \'%s\' '
                          '(ligne %s) déjà utilisée (ligne %s)' %
                          ((var_params[j][1]), var_params[j][3], var_params[i][3]))
                    erreur_trouvee = True

        # Verification de non redondante dans les declarations des variables
        for i in range(len(var_decl)):
            for j in range(i + 1, len(var_decl)):
                if var_decl[i][1] == var_decl[j][1]:
                    print('Erreur : redéclaration de la variable \'%s\' (ligne %s) déjà déclarée (ligne %s)' %
                          ((var_decl[j][1]), var_decl[j][3], var_decl[i][3]))
                    erreur_trouvee = True
        return erreur_trouvee

    def verifier_valeur_retour(self):
        erreur_trouvee = False
        if self.type == 'prog':
            if self.sons[0][0] == 'int' and self.sons[5].value == 'float':
                print('Erreur : valeur de attendue attendue de type \'%s\' (ligne %s) et '
                      'valeur de retour trouvée de type \'%s\' (ligne %s)' %
                      (self.sons[0][0], self.sons[0][1], self.sons[5].value, self.sons[5].sons[1]))
                erreur_trouvee = True
        return erreur_trouvee

    def verifier_division(self):
        if self.type == 'prog':
            un = self.sons[4].est_division_par_zero_exp()
            deux = self.sons[3].est_division_par_zero_com()
        return (un or deux)

    #Fonction pour retrouver le type d'une variable a partir de son nom
    def trouverType(self, maVar, var_declarees):
        trouve = 0
        for item in var_declarees:
            if item[1] == maVar:
                return item[0]
        return []

    def type_operandes_expression(self, var_declarees):
        if self.type == 'ID':
            return [self.trouverType(self.value, var_declarees)]
        elif self.type == 'NUMBER':
            if isinstance(self.value, int):
                return ['int']
            else:
                return ['float']
        else:
            lop = self.sons[0].type_operandes_expression(var_declarees)
            rop = self.sons[1].type_operandes_expression(var_declarees)
            if lop[0] != rop[0]:
                return ['float']
            else:
                return lop

    def type_operandes_commande(self, var_declarees):
        if self.type == 'commande':
            if self.value == 'asgnt':
                lop = self.trouverType(self.sons[0], var_declarees)
                rop = self.sons[1].type_operandes_expression(var_declarees)
                if lop == 'int' and rop[0] == 'float':
                    print('Erreur : tentative d\'affectation de valeur '
                                               'de type \'float\' à '
                              'une variable (\'%s\') de type \'int\' : ligne %s' %
                          (self.sons[0], self.sons[2]))
                    raise EntierFloat('DIVISION PAR ZERO','Erreur : tentative d\'affectation de valeur '
                                               'de type \'float\' à '
                              'une variable (\'%s\') de type \'int\' : ligne %s' %
                          (self.sons[0], self.sons[2]))
                else:
                    return [lop, rop[0]]
            elif self.value == 'seq':
                return [self.sons[0].type_operandes_commande(var_declarees),
                        self.sons[1].type_operandes_commande(var_declarees)]
            elif self.value == 'while':
                return [self.sons[0].type_operandes_expression(var_declarees),
                        self.sons[1].type_operandes_commande(var_declarees)]


    def verifier_typage_commandes(self, com, var_declarees):
        typesOperandes = []
        typesOperandes = com.type_operandes_commande(var_declarees)

    def verifier_typage_operations(self, expr, var_declarees):
       typesOperandes = []
       typesOperandes = expr.type_operandes_expression(var_declarees)


    def verifier_operations_main(self):
        if self.type == 'prog':
            var_declarees = []
            var_declarees = self.vars_decl()
            self.verifier_typage_operations(self.sons[4], var_declarees)
            self.verifier_typage_commandes(self.sons[3], var_declarees)

    def init_vars(self, moule, vars_decl_int, vars_decl_float, vars_params):
        moule = moule.replace('LEN_INPUT_INT',str(1+len(vars_decl_int)))
        init_var_int = []
        for i in range(len(vars_decl_int)):
            for j in range(len(vars_params)):
                if vars_decl_int[i] != vars_params[i][1]:
                    init_var_int.append(self.init_var_int(vars_decl_int[i],i))
                else:
                    init_var_int.append(self.init_var_int_main(vars_decl_int[i], i, valeur))

        moule = moule.replace('VAR_INIT_INT', '\n'.join(init_var_int))

        moule = moule.replace('LEN_INPUT_FLOAT', str(1 + len(vars_decl_float)))
        init_var_float = [self.init_var(vars_decl_float[i], i) for i in range(len(vars_decl_float))]
        moule = moule.replace('VAR_INIT_FLOAT', '\n'.join(init_var_float))
        return moule

    def p_toAsm(self):
        f = open('moule.asm')
        moule = f.read()
        vars_declarees_int = []
        vars_declarees_float = []
        vars_declarees_intASM = set()
        vars_declarees_floatASM = set()
        vars_declarees = self.vars_decl()
        for item in vars_declarees:
            if item[0] == 'int':
                vars_declarees_int.append(item[1])
            elif item[0] == 'float':
                vars_declarees_float.append(item[1])
        vars_declarees_intASM = {'%s: dd 0' % v for v in vars_declarees_int}
        vars_declarees_floatASM = {'%s: dd 0' % v for v in vars_declarees_float}
        var_decl_int = '\n'.join(vars_declarees_intASM)
        var_decl_float = '\n'.join(vars_declarees_floatASM)
        moule = moule.replace('VAR_DECL_INT', var_decl_int)
        moule = moule.replace('VAR_DECL_FLOAT', var_decl_float)
        moule = self.init_vars(moule, vars_declarees_int, vars_declarees_float, self.vars_main())
        moule = moule.replace('COMMAND_EXEC', self.sons[3].c_toAsm())
        moule = moule.replace('EVAL_OUTPUT', self.sons[4].e_toAsm())
        return moule

    def analyses (self):
        if self.type == 'prog':
            un = self.verifier_variables()
            # deux = self.verifier_division()
            self.verifier_operations_main()
            trois = self.verifier_valeur_retour()
            if un is False and trois is False:
                print(self.p_toAsm())