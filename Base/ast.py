
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
        if self.type =='prog':
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

