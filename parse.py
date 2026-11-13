import ply.yacc as yacc
import lexer as lexmod

tokens = lexmod.tokens

# PRECEDENCIA

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'NOT', 'LEN'),
)

# REGLA INICIAL

start = 'program'


def p_program(p):
    'program : statements'
    p[0] = p[1]


def p_statements_multiple(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]


def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]


# DECLARACION LOCAL CON ATRIBUTOS

def p_statement_local(p):
    'statement : LOCAL name_attribute_list optional_assign'
    p[0] = ('local', p[2], p[3])


def p_name_attribute_list_multiple(p):
    'name_attribute_list : name_attribute_list COMMA name_attribute'
    p[0] = p[1] + [p[3]]


def p_name_attribute_list_single(p):
    'name_attribute_list : name_attribute'
    p[0] = [p[1]]


def p_name_attribute(p):
    'name_attribute : ID optional_attribute'
    p[0] = (p[1], p[2])


def p_optional_attribute(p):
    '''optional_attribute : LT ID GT
                          | empty'''
    p[0] = p[2] if len(p) == 4 else None


def p_optional_assign(p):
    '''optional_assign : ASSIGN expression_list
                       | empty'''
    p[0] = p[2] if len(p) == 3 else None



# DECLARACION GLOBAL

def p_statement_global(p):
    'statement : GLOBAL name_list optional_assign'
    p[0] = ('global', p[2], p[3])


def p_name_list_multiple(p):
    'name_list : name_list COMMA ID'
    p[0] = p[1] + [p[3]]


def p_name_list_single(p):
    'name_list : ID'
    p[0] = [p[1]]


# LISTA DE EXPRESIONES

def p_expression_list_multiple(p):
    'expression_list : expression_list COMMA expression'
    p[0] = p[1] + [p[3]]


def p_expression_list_single(p):
    'expression_list : expression'
    p[0] = [p[1]]


def p_empty(p):
    'empty :'
    p[0] = None


# FOR NUMERICO

def p_statement_for_numerico(p):
    '''statement : FOR ID ASSIGN expression COMMA expression DO block END
                 | FOR ID ASSIGN expression COMMA expression COMMA expression DO block END'''

    if len(p) == 9:
        paso = None
        cuerpo = p[7]
    else:
        paso = p[7]
        cuerpo = p[9]

    p[0] = ('for_numerico', p[2], p[4], p[6], paso, cuerpo)



# FOR GENERICO

def p_statement_for_generico(p):
    'statement : FOR name_list IN expression_list DO block END'
    p[0] = ('for_generico', p[2], p[4], p[6])


# BLOQUE

def p_block_multiple(p):
    'block : block statement'
    p[0] = p[1] + [p[2]]


def p_block_single(p):
    'block : statement'
    p[0] = [p[1]]



# PILA

def p_statement_pila(p):
    '''statement : ID ASSIGN LBRACE RBRACE
                 | ID LBRACKET LEN ID RBRACKET ASSIGN expression'''
    if len(p) == 5:
        p[0] = ('crear_pila', p[1])
    else:
        p[0] = ('insertar_pila', p[1], p[7])



# LISTA ENLAZADA

def p_statement_lista_enlazada(p):
    'statement : ID ASSIGN table_constructor'
    p[0] = ('lista_enlazada', p[1], p[3])


# ACCESOS A ESTRUCTURAS

def p_access_attribute(p):
    'access : access DOT ID'
    p[0] = ('acceso_atributo', p[1], p[3])


def p_access_index(p):
    'access : access LBRACKET expression RBRACKET'
    p[0] = ('acceso_indice', p[1], p[3])


def p_access_id(p):
    'access : ID'
    p[0] = ('identificador', p[1])


def p_statement_access_assignment(p):
    'statement : access ASSIGN expression'
    p[0] = ('asignacion_acceso', p[1], p[3])



# TABLAS PARA LISTAS ENLAZADAS

def p_table_constructor(p):
    'table_constructor : LBRACE field_list RBRACE'
    p[0] = ('tabla', p[2])


def p_field_list_multiple(p):
    'field_list : field_list COMMA field'
    p[0] = p[1] + [p[3]]


def p_field_list_single(p):
    'field_list : field'
    p[0] = [p[1]]


def p_field_named(p):
    'field : ID ASSIGN expression'
    p[0] = (p[1], p[3])


# FUNCIONES VARIADICAS

def p_statement_function_variadica(p):
    'statement : FUNCTION ID LPAREN VARARG RPAREN block END'
    p[0] = ('funcion_variadica', p[2], p[6])


def p_statement_function_variadica_parametros(p):
    'statement : FUNCTION ID LPAREN parameter_list COMMA VARARG RPAREN block END'
    p[0] = ('funcion_variadica_parametros', p[2], p[4], p[8])


def p_parameter_list_multiple(p):
    'parameter_list : parameter_list COMMA ID'
    p[0] = p[1] + [p[3]]


def p_parameter_list_single(p):
    'parameter_list : ID'
    p[0] = [p[1]]


# TONUMBER Y TOSTRING

def p_expression_conversion(p):
    '''expression : ID LPAREN expression RPAREN'''
    if p[1] == 'tonumber':
        p[0] = ('tonumber', p[3])
    elif p[1] == 'tostring':
        p[0] = ('tostring', p[3])
    else:
        p[0] = ('llamada_funcion', p[1], p[3])


# BREAK

def p_statement_break(p):
    'statement : BREAK'
    p[0] = ('break',)

# GOTO

def p_statement_goto(p):
    'statement : GOTO ID'
    p[0] = ('goto', p[2])
