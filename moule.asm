global main
extern printf, atoi

section .data
message: db 'Hello world %d',10,0
message_erreur: db 'Il faut rentrer %d entrees', 10, 0
VAR_DECL_INT
VAR_DECL_FLOAT

section .text
main: 
mov eax, [esp + 4] ; eax = argc
cmp eax, LEN_INPUT
jne erreur_nb_entree
mov eax, [esp + 8] ; eax = argv
VAR_INIT
jmp debut_prog
erreur_nb_entree:
mov eax, LEN_INPUT
dec eax
push eax
lea eax, [message_erreur]
push eax
call printf
add esp, 8
jmp fin

debut_prog:
COMMAND_EXEC

EVAL_OUTPUT

push eax ; eax contient le nombre calcule
lea eax, [message]
push eax
call printf
add esp, 8
fin: ret ; fin du prog
