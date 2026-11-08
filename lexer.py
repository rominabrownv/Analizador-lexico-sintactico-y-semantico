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

errores = []   # cada error es una tupla (linea, columna, mensaje)

tokens_id_tipos = ['ID', 'INTEGER', 'FLOAT', 'STRING']
 
 
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

# Detección de números mal formados
def t_ERROR_NUMERO(t):
    r'\d+[a-zA-Z_]\w*'
    agregar_error(t.lexer, t.lexpos, f"número mal formado '{t.value}'")
    t.lexer.skip(len(t.value))

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
 
# ----------------------Joseph-----------------------
tokens_operadores_delimitadores = [
    # Operadores aritméticos
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD', 'POW',
    # Operadores relacionales
    'EQ', 'NE', 'LE', 'GE', 'LT', 'GT',
    # Operadores lógicos y de bits
    'BITAND', 'BITOR', 'BITXOR', 'LSHIFT', 'RSHIFT',
    # Asignación, concatenación y longitud
    'ASSIGN', 'CONCAT', 'LEN',
    # Delimitadores y puntuación
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMMA', 'DOT', 'VARARG', 'COLON', 'DBLCOLON'
]

tokens = tokens_id_tipos + tokens_operadores_delimitadores + list(reservadas.values())

# --- Reglas de Expresiones Regulares para Operadores y Delimitadores ---

# Operadores aritméticos
t_FLOORDIV = r'//'
t_POW      = r'\^'
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/'
t_MOD      = r'%'

# Operadores relacionales
t_EQ       = r'=='
t_NE       = r'~='
t_LE       = r'<='
t_GE       = r'>='
t_LT       = r'<'
t_GT       = r'>'

# Operadores de bits y lógicos adicionales
t_BITAND   = r'&'
t_BITOR    = r'\|'
t_BITXOR   = r'~'
t_LSHIFT   = r'<<'
t_RSHIFT   = r'>>'

# Asignación, concatenación y longitud
t_ASSIGN   = r'='
t_CONCAT   = r'\.\.'
t_LEN      = r'\#'

# Delimitadores y puntuación
t_DBLCOLON = r'::'
t_VARARG   = r'\.\.\.'
t_COLON    = r':'
t_DOT      = r'\.'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACE   = r'\{'
t_RBRACE   = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON= r';'
t_COMMA    = r','

#------------------------Romina-----------------------

# --- Variables e identificadores ---
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reservadas.get(t.value, 'ID')
    return t


# --- Comentarios largos: --[[ ... ]], --[=[ ... ]=], etc. ---
def t_COMENTARIO_LARGO(t):
    r'--\[\[[\s\S]*?\]\]|--\[=\[[\s\S]*?\]=\]|--\[==\[[\s\S]*?\]==\]'
    t.lexer.lineno += t.value.count('\n')


# --- Comentarios largos sin cerrar ---
def t_COMENTARIO_SIN_CERRAR(t):
    r'--\[=*\[[\s\S]*'
    agregar_error(t.lexer, t.lexpos, 'comentario largo sin cerrar')
    t.lexer.lineno += t.value.count('\n')


# --- Comentarios de una línea ---
def t_COMENTARIO_CORTO(t):
    r'--[^\n]*'
    pass



#-- Funciones Generales del analizador---
 
def columna(texto, posicion):
    inicio_linea = texto.rfind('\n', 0, posicion) + 1
    return posicion - inicio_linea + 1
 
 
def agregar_error(lexer, posicion, mensaje):
    linea = lexer.lexdata.count('\n', 0, posicion) + 1
    errores.append((linea, columna(lexer.lexdata, posicion), mensaje))

def t_error(t):
    agregar_error(t.lexer, t.lexpos, 'carácter ilegal ' + repr(t.value[0]))
    t.lexer.skip(1)

# --- Saltos de línea y espacios (parte común) ---
t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
 
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

