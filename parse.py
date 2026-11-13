import ply.yacc as yacc
import lexer as analizador_lexico

# CONFIGURACION DEL ANALIZADOR SINTACTICO

tokens = analizador_lexico.tokens

inicio = 'programa'

# PRECEDENCIA DE OPERADORES

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'NOT', 'LEN'),
)


# LISTA DE ERRORES SINTACTICOS

errores_sintacticos = []


# REGLA PRINCIPAL

def p_programa(p):
    'programa : lista_sentencias'
    p[0] = p[1]


def p_lista_sentencias_multiple(p):
    'lista_sentencias : lista_sentencias sentencia'
    p[0] = p[1] + [p[2]]


def p_lista_sentencias_una(p):
    'lista_sentencias : sentencia'
    p[0] = [p[1]]


# DECLARACION LOCAL CON ATRIBUTOS

def p_sentencia_local(p):
    'sentencia : LOCAL lista_atributos_locales asignacion_opcional'
    p[0] = ('declaracion_local', p[2], p[3])


def p_lista_atributos_locales_multiple(p):
    'lista_atributos_locales : lista_atributos_locales COMMA atributo_local'
    p[0] = p[1] + [p[3]]


def p_lista_atributos_locales_uno(p):
    'lista_atributos_locales : atributo_local'
    p[0] = [p[1]]


def p_atributo_local(p):
    'atributo_local : ID atributo_opcional'
    p[0] = (p[1], p[2])


def p_atributo_opcional(p):
    '''atributo_opcional : LT ID GT
                         | vacio'''
    p[0] = p[2] if len(p) == 4 else None


def p_asignacion_opcional(p):
    '''asignacion_opcional : ASSIGN lista_expresiones
                           | vacio'''
    p[0] = p[2] if len(p) == 3 else None


# DECLARACION GLOBAL

def p_sentencia_global(p):
    'sentencia : GLOBAL lista_nombres asignacion_opcional'
    p[0] = ('declaracion_global', p[2], p[3])


def p_lista_nombres_multiple(p):
    'lista_nombres : lista_nombres COMMA ID'
    p[0] = p[1] + [p[3]]


def p_lista_nombres_uno(p):
    'lista_nombres : ID'
    p[0] = [p[1]]


# LISTA DE EXPRESIONES

def p_lista_expresiones_multiple(p):
    'lista_expresiones : lista_expresiones COMMA expresion'
    p[0] = p[1] + [p[3]]


def p_lista_expresiones_una(p):
    'lista_expresiones : expresion'
    p[0] = [p[1]]


def p_vacio(p):
    'vacio :'
    p[0] = None



# FOR NUMERICO

def p_sentencia_for_numerico(p):
    '''sentencia : FOR ID ASSIGN expresion COMMA expresion DO bloque END
                 | FOR ID ASSIGN expresion COMMA expresion COMMA expresion DO bloque END'''

    if len(p) == 9:
        paso = None
        cuerpo = p[7]
    else:
        paso = p[7]
        cuerpo = p[9]

    p[0] = (
        'ciclo_for_numerico',
        p[2],
        p[4],
        p[6],
        paso,
        cuerpo
    )

# FOR GENERICO

def p_sentencia_for_generico(p):
    'sentencia : FOR lista_nombres IN lista_expresiones DO bloque END'
    p[0] = (
        'ciclo_for_generico',
        p[2],
        p[4],
        p[6]
    )


# BLOQUES DE SENTENCIAS

def p_bloque_multiple(p):
    'bloque : bloque sentencia'
    p[0] = p[1] + [p[2]]


def p_bloque_uno(p):
    'bloque : sentencia'
    p[0] = [p[1]]



# ESTRUCTURA DE DATOS: 
#PILA

def p_sentencia_crear_pila(p):
    'sentencia : ID ASSIGN LBRACE RBRACE'
    p[0] = ('crear_pila', p[1])


def p_sentencia_insertar_pila(p):
    'sentencia : ID LBRACKET LEN ID RBRACKET ASSIGN expresion'
    p[0] = ('insertar_en_pila', p[1], p[7])


# LISTA ENLAZADA

def p_sentencia_lista_enlazada(p):
    'sentencia : ID ASSIGN constructor_tabla'
    p[0] = ('crear_lista_enlazada', p[1], p[3])



# ACCESO A ESTRUCTURAS DE DATOS

def p_acceso_atributo(p):
    'acceso : acceso DOT ID'
    p[0] = ('acceso_atributo', p[1], p[3])


def p_acceso_indice(p):
    'acceso : acceso LBRACKET expresion RBRACKET'
    p[0] = ('acceso_indice', p[1], p[3])


def p_acceso_identificador(p):
    'acceso : ID'
    p[0] = ('identificador', p[1])


def p_sentencia_asignacion_acceso(p):
    'sentencia : acceso ASSIGN expresion'
    p[0] = ('asignacion_acceso', p[1], p[3])



# CONSTRUCTOR DE TABLAS

def p_constructor_tabla(p):
    'constructor_tabla : LBRACE lista_campos RBRACE'
    p[0] = ('tabla', p[2])


def p_lista_campos_multiple(p):
    'lista_campos : lista_campos COMMA campo'
    p[0] = p[1] + [p[3]]


def p_lista_campos_uno(p):
    'lista_campos : campo'
    p[0] = [p[1]]


def p_campo_nombrado(p):
    'campo : ID ASSIGN expresion'
    p[0] = ('campo', p[1], p[3])



# FUNCIONES VARIADICAS

def p_sentencia_funcion_variadica(p):
    'sentencia : FUNCTION ID LPAREN VARARG RPAREN bloque END'
    p[0] = (
        'funcion_variadica',
        p[2],
        p[6]
    )


def p_sentencia_funcion_variadica_parametros(p):
    'sentencia : FUNCTION ID LPAREN lista_parametros COMMA VARARG RPAREN bloque END'
    p[0] = (
        'funcion_variadica_con_parametros',
        p[2],
        p[4],
        p[8]
    )


def p_lista_parametros_multiple(p):
    'lista_parametros : lista_parametros COMMA ID'
    p[0] = p[1] + [p[3]]


def p_lista_parametros_uno(p):
    'lista_parametros : ID'
    p[0] = [p[1]]


# FUNCIONES DE CONVERSION

def p_expresion_conversion(p):
    '''expresion : ID LPAREN expresion RPAREN'''

    if p[1] == 'tonumber':
        p[0] = ('convertir_a_numero', p[3])

    elif p[1] == 'tostring':
        p[0] = ('convertir_a_cadena', p[3])

    else:
        p[0] = ('llamada_funcion', p[1], p[3])


# BREAK

def p_sentencia_break(p):
    'sentencia : BREAK'
    p[0] = ('romper_ciclo',)



# GOTO

def p_sentencia_goto(p):
    'sentencia : GOTO ID'
    p[0] = ('saltar_a_etiqueta', p[2])


# ETIQUETAS PARA GOTO

def p_sentencia_etiqueta(p):
    'sentencia : DBLCOLON ID DBLCOLON'
    p[0] = ('declarar_etiqueta', p[2])