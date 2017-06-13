
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
                vars.add(self.sons[0])
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
                vars.add(self.value)
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

    # def exp2List(self):
    #     var_exp = []
    #
    #     if self.type == 'ID':
    #         var_exp.append([self.value, self.sons[0]])
    #         return  var_exp
    #     elif self.type == 'OPBIN':
    #         var_exp.append(self.sons[0].exp2List())
    #         var_exp.append(self.sons[1].exp2List())
    #         var_exp.append(self.sons[2])
    #         return var_exp
    #     elif self.type == 'NUMBER':
    #         return var_exp
    #     return var_exp

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

    # Variables (pas les declarations) apparaissant dans le programme (declarees ou non)
    def vars_util(self):
        vars_utilisees = []
        if self.type == 'prog':
            # vars_utilisees.append(self.sons[3].com2List())
            # vars_utilisees.append(self.sons[4].exp2List())
            vars_utilisees = self.sons[3].com2List() + list(self.sons[4].exp2List())
        return vars_utilisees


    def verifier_variables(self):
        pass

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

