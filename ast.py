
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

    #Rendre ma classe iterable
    def __iter__(self):
        for each in self.__dict__.keys():
            yield  self.__getattribute__(each)
        return self

    # def __next__(self):
    #     if self.index == 0:
    #         raise StopIteration
    #     self

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
            vars.update(self.sons[0])
            vars.update(self.sons[1].pvars())
            vars.update(self.sons[2].pvars())
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

    def dec2ID(self):
        if self.type == 'declaration':
            return self.sons[0]

    def dec2List(self):
        if self.type == 'declaration':
            #retourne : typeVariable, nomVariable, ligneTypeVariable, lignenomVariable
            return [self.value, self.sons[0], self.sons[1], self.sons[2]]

    def vars_main(self):
        var_params_main = set()
        if self.type == 'prog':
            var_params_main.add(self.sons[1])
        return var_params_main

    def afficherListe(self, listeA):
        for var in listeA:
            print(var)


    def vars_decl(self):
        var_declarees = []
        if self.type == 'prog':
            if len(self.sons) != 0:
                print('Variable(s) declarees dans le programme\nType de la liste : %s'
                      %(type(self.sons[2])))
                for declItem in self.sons[2]:
                    var_declarees.append(declItem.dec2List())
                # self.afficherListe(self.sons[2])
                # for declItem in self.sons[2]:
                    # print(type(declItem), end='  ')
                    # i = 0
                    # for i in range(len(declItem)):
                    #     if i == 0:
                    #         print('Type : %s' % (type(declItem[0]) ))
                    #     elif i == 2:
                    #         print(' - Nom : %s' %(declItem[0]), end='\n')
                    # for decl in declItem:
                    #     print(type(decl), end=' ')
                        # print('Type = %s et nom = %s' % (decl[0], decl[1]), end=' ')
                        # print('Type : %s (%s)- Nom : %s(%s)' %
                        #       (decl.value, type(decl.value), decl.sons, type(decl.sons)),
                        #       end='')
                    # print()
        return var_declarees

    def vars_util(self):
        vars_utilisees = set()
        if self.type == 'commande':
            if self.value == 'asgnt':
                vars_utilisees.add(self.sons[0])
                vars_utilisees.update(self.sons[1].vars_util())
                return vars_utilisees
            else:
                vars_utilisees.update(self.sons[0].vars_util())
                vars_utilisees.update(self.sons[1].vars_util())
        elif self.type == 'expression':
            if self.type == 'OPBIN':
                vars_utilisees.update(self.sons[0].vars_util())
                vars_utilisees.update(self.sons[1].vars_util())
                return vars_utilisees
            elif self.type == 'NUMBER':
                return vars_utilisees
            else:
                vars_utilisees.add(self.value)
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

