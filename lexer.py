import re
import ply.lex as lex
from datetime import datetime

#---------------Christian-------------------
reservadas = {
    'and': 'AND', 'break': 'BREAK', 'do': 'DO', 'else': 'ELSE',
    'elseif': 'ELSEIF', 'end': 'END', 'false': 'FALSE', 'for': 'FOR',
    'function': 'FUNCTION', 'global': 'GLOBAL', 'goto': 'GOTO', 'if': 'IF',
    'in': 'IN', 'local': 'LOCAL', 'nil': 'NIL', 'not': 'NOT', 'or': 'OR',
    'repeat': 'REPEAT', 'return': 'RETURN', 'then': 'THEN', 'true': 'TRUE',
    'until': 'UNTIL', 'while': 'WHILE',
}

errores = []

tokens = ['ID', 'INTEGER', 'FLOAT', 'STRING'] + list(reservadas.values())
 
 
# Cadenas largas: [[ ... ]]  (pueden tener varias líneas)
def t_STRING_LARGA(t):
    r'\[\[[\s\S]*?\]\]'
    t.type = 'STRING'
    t.lexer.lineno += t.value.count('\n')
    return t
 
 
# Cadenas con comillas dobles: "hola\n"
def t_STRING_DOBLE(t):
    r'"([^"\\\n]|\\.)*"'
    t.type = 'STRING'
    return t
 
 
# Cadenas con comillas simples: 'hola'
def t_STRING_SIMPLE(t):
    r"'([^'\\\n]|\\.)*'"
    t.type = 'STRING'
    return t

# Números decimales 
def t_FLOAT(t):
    r'(\d+\.\d*|\.\d+)([eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t
 
 
# Números enteros y hexadecimales 
def t_INTEGER(t):
    r'0[xX][0-9a-fA-F]+|\d+'
    if t.value[:2] in ('0x', '0X'):
        t.value = int(t.value, 16)
    else:
        t.value = int(t.value)
    return t
 

#------------------------Romina-----------------------

# --- Variables e identificadores ---
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reservadas.get(t.value, 'ID')
    return t


# --- Comentarios largos: --[[ ... ]], --[=[ ... ]=], etc. ---
def t_COMENTARIO_LARGO(t):
    r'--\[(=*)\[[\s\S]*?\]\1\]'
    t.lexer.lineno += t.value.count('\n')


# --- Comentarios largos sin cerrar ---
def t_COMENTARIO_SIN_CERRAR(t):
    r'--\[(=*)\[[\s\S]*'
    errores.append(
        f"Error léxico en la línea {t.lexer.lineno}: comentario largo sin cerrar."
    )
    t.lexer.lineno += t.value.count('\n')


# --- Comentarios de una línea ---
def t_COMENTARIO_CORTO(t):
    r'--[^\n]*'
    pass



#-- Funciones Generales del analizador---

errores = []   # cada error es una tupla (linea, columna, mensaje)
 
def columna(texto, posicion):
    inicio_linea = texto.rfind('\n', 0, posicion) + 1
    return posicion - inicio_linea + 1
 
 
def agregar_error(lexer, posicion, mensaje):
    linea = lexer.lexdata.count('\n', 0, posicion) + 1
    errores.append((linea, columna(lexer.lexdata, posicion), mensaje))

def t_error(t):
    agregar_error(t.lexer, t.lexpos, 'carácter ilegal ' + repr(t.value[0]))
    t.lexer.skip(1)
 
lexer = lex.lex()
 
def analizar(texto):
    # Devuelve (lista de tokens, lista de errores).
    # Cada token es una tupla (tipo, lexema, valor, linea, columna).
    del errores[:]
    lexer.lineno = 1
    lexer.input(texto)
    lista = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        lexema = texto[tok.lexpos:lexer.lexpos]
        lista.append((tok.type, lexema, tok.value, tok.lineno, columna(texto, tok.lexpos)))
    return lista, list(errores)