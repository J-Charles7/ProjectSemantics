import ply.lex as lex
mots_cle = {'while' : 'WHILE', 'main' : 'MAIN', 'return' : 'RETURN', 'print' : 'PRINT'}
types = {'float' : 'FLOAT', 'int' : 'INT'}
tokens = ['NUMBER', 'ID', 'OPBIN', 'LP', 'RP', 'LB', 'RB', 'EQUAL', 'SEQ', 'COMMA'] \
         + list(types.values())\
         + list(mots_cle.values())
def t_OPBIN(t):
    r"[\+\-\*\=\<\>\!\/]+"
    if t.value == '=':
        t.type = 'EQUAL'
    return t

t_LP = r'\('
t_RP = r'\)'
t_LB = r'\{'
t_RB = r'\}'
t_SEQ = r';'
t_COMMA = r','

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    #t.lineno = t.lineno + 1
    return t

def t_newline(t):
    r"\n"
    t.lexer.lineno = t.lexer.lineno + 1

def t_ID(t):
    r"[a-zA-Z_]+"
    if t.value in mots_cle:
        t.type = mots_cle[t.value]
    if t.value in types:
        t.type = types[t.value]
    return t

t_ignore = " \t"
lexer = lex.lex()

uncode = " while (x) { int float x = z + 33+45 ; x = 18 }"
lexer.input("main(z, t) { %s ; print (y) ;}" % uncode)

while True:
    tok = lexer.token()
    if tok:
        print(tok)
    else:
        break

import ply.yacc as yacc
import ast

def p_expression(p):
    '''expression : NUMBER
                | ID
                | expression OPBIN expression'''
    if len(p) > 2:
        p[0] = ast.AST('OPBIN', p[2])
        p[0].sons = [p[1], p[3]]
    elif isinstance(p[1], str):
        p[0] = ast.AST('ID', p[1])
    else:
        p[0] = ast.AST('NUMBER', p[1])

def p_commande(p):
    '''commande : ID EQUAL expression
                | commande SEQ commande
                | WHILE LP expression RP LB commande RB
    '''
    if len(p) > 4:
        p[0] = ast.AST('commande', 'while')
        p[0].sons = [p[3], p[6]]
    else:
        if p[2] == '=':
            p[0] = ast.AST('commande', 'asgnt')
            p[0].sons = [p[1], p[3]]
        else:
            p[0] = ast.AST('commande', 'seq')
            p[0].sons = [p[1], p[3]]

def p_declaration(p):
    '''
    declaration : INT ID
                | FLOAT ID
    '''
    if p[1] == 'int':
        p[0] = ast.AST('declaration', 'int')
        p[0].sons = [p[2]]
    elif p[1] == 'float':
        p[0] = ast.AST('declaration', 'float')
        p[0].sons = [p[2]]
    else:
        p[0] = ast.AST('declaration', 'multiple')
        p[0].sons = [p[1], p[3]]

def p_listedeclarations(p):
    '''
    listedeclarations : declaration SEQ
                      | declaration SEQ listedeclarations
    '''
    if len(p) > 3:
        p[0] = p[3]
        p[0].insert(0, p[1])
    else :
        p[0] = [ p[1]]


# def p_listevariables(p):
#     '''
#     listevariables : ID
#                    | ID COMMA listevariables
#     '''
#     if len(p)>2:
#         p[0] = p[3]
#         p[0].insert(0,p[1])
#     else:
#         p[0] = [ p[1]]

def p_listeparamsmain(p):
    '''
    listeparamsmain : declaration
                   | declaration COMMA listeparamsmain
    '''
    if len(p)>2:
        p[0] = p[3]
        p[0].insert(0,p[1])
    else:
        p[0] = [ p[1]]

def p_typeetmain(p):
    '''
    typeetmain : INT MAIN
         | FLOAT MAIN
    '''
    p[0] = p[1]

# '''
# main : MAIN LP listevariables RP LB listedeclarations commande SEQ PRINT LP expression RP SEQ RB
# '''
def p_main(p):
    '''
    main : typeetmain LP listeparamsmain RP LB listedeclarations commande SEQ PRINT LP expression RP SEQ RB
    '''

    p[0] = ast.AST('prog', 'main')
    p[0].sons = [p[1], p[3], p[6], p[7], p[11]]
start = 'main'
parser = yacc.yacc()
precedence = ('left', 'SEQ')
print(parser.parse("float main(int rien, float tout) {  int autre; float titi; while (X) { Y = Y + 1 ; X = X - 1 } ; print (Y) ; } "))




