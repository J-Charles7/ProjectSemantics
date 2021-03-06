import ply.lex as lex
mots_cle = {'while' : 'WHILE', 'main' : 'MAIN', 'return': 'RETURN', 'print' : 'PRINT'}
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
    r'(^[+-]?0|[0-9][0-9]*)([.][0-9]*)?([eE][+-]?[0-9]+)?'
    if '.' in t.value or 'e' in t.value or '-' in t.value:
        t.value = float(t.value)
    else:
        t.value = (int)(t.value)

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

def t_error(t):
    print("Caractère illégal '%s' à la ligne %s" % (t.value[0], t.lineno))
    t.lexer.skip(1)

t_ignore = " \t"
lexer = lex.lex()

uncode = " while (x) { int float x = z + 33+45 ; x = 18 }"
lexer.input("main(z, t) { %s ; print (y) ; return 72;}" % uncode)

# while True:
#     tok = lexer.token()
#     if tok:
#         print(tok)
#     else:
#         break

import ply.yacc as yacc
import ast

def p_error(p):
    print("Erreur de syntaxe dans l'écriture du programme MINI-C ! \n "
          "Ligne %s : mot '%s'" % (p.lineno, p.value))

def p_expression(p):
    '''expression : NUMBER
                  | ID
                  | expression OPBIN expression'''
    if len(p) > 2:
        p[0] = ast.AST('OPBIN', p[2])
        p[0].sons = [p[1], p[3], p.lineno(2)]
    elif isinstance(p[1], str):
        p[0] = ast.AST('ID', p[1])
        p[0].sons = [p.lineno(1)]
    else:
        p[0] = ast.AST('NUMBER', p[1])
        p[0].sons = [p.lineno(1)]

def p_commande(p):
    '''commande : ID EQUAL expression
                | commande SEQ commande
                | WHILE LP expression RP LB commande RB
    '''
    if len(p) > 4:
        p[0] = ast.AST('commande', 'while')
        p[0].sons = [p[3], p[6], p.lineno(1)]
    else:
        if p[2] == '=':
            p[0] = ast.AST('commande', 'asgnt')
            p[0].sons = [p[1], p[3], p.lineno(2)]
        else:
            p[0] = ast.AST('commande', 'seq')
            p[0].sons = [p[1], p[3], p.lineno(1)]

def p_declaration(p):
    '''
    declaration : INT ID
                | FLOAT ID
    '''
    if p[1] == 'int':
        p[0] = ast.AST('declaration', 'int')
        p[0].sons = [p[2], p.lineno(1), p.lineno(2)]
    elif p[1] == 'float':
        p[0] = ast.AST('declaration', 'float')
        p[0].sons = [p[2], p.lineno(1), p.lineno(2)]

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
    p[0] = [p[1], p.lineno(1)]

def p_returnmainvalue(p):
    '''
    returnmainvalue : RETURN NUMBER SEQ
    '''
    if isinstance(p[2], int):
        p[0] = ast.AST('return', 'int')
        p[0].sons = [p[2], p.lineno(2)]
    elif isinstance(p[2], float):
        p[0] = ast.AST('return', 'float')
        p[0].sons = [p[2], p.lineno(2)]

def p_main(p):
    '''
    main : typeetmain LP listeparamsmain RP LB listedeclarations commande SEQ PRINT LP expression RP SEQ returnmainvalue RB
    '''

    p[0] = ast.AST('prog', 'main')
    p[0].sons = [p[1], p[3], p[6], p[7], p[11], p[14]]
start = 'main'
parser = yacc.yacc()
precedence = ('left', 'SEQ')
arbre = parser.parse("int main(int rien) {int t;"
                     "\n float v; int gil; float s;"
                     "\n float u; int X; float Z; float titi; int Y; while (X) { Y = Y * 0 ; "
                     "\n u = u - v; "
                     "\n X = X - 6; "
                     "\n s = X * 3; "
                     "\n rien = X / 3; "
                     "\n gil = 0} ; print (X * 0) ; return 10;} ")
# arbre = parser.parse("int main(int rien, float rien) {int t; int t; "
#                      "\n float t; float v; int gil;"
#                      "\n float u; int X; float Z; float titi; int Y; while (X) { Y = Y + 5 ; "
#                      "\n t = u - v; "
#                      "\n X = s - 6; "
#                      "\n s = X * 3; "
#                      "\n gil = 0.0} ; print (2) ; return 10.0;} ")
# arbre = parser.parse("float main(int rien, float tout, int affaire, float affaire) {float Z; int Z; float rien; int autre; float titi; while (X) { Y = Y + 5 ; "
#                      "\n t = u - v; \n X = s - 6; \n s = X * 3 } ; print (Z) ; return 0;} ")
# print(arbre)
# print(arbre.verifier_variables())
# print(arbre.verifier_valeur_retour())
# arbre.verifier_valeur_retour()
arbre.analyses()




