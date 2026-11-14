import ply.yacc as yacc
import lexer as analizador_lexico

# CONFIGURACION DEL ANALIZADOR SINTACTICO

tokens = analizador_lexico.tokens

start = 'programa'

# PRECEDENCIA DE OPERADORES

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE', 'LT', 'GT', 'LE', 'GE'),
    ('right', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'NOT', 'LEN'),
    ('right', 'POW'),
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
    nombres, valores = p[2], p[3]
    if (len(nombres) == 1 and es_nombre_pila(nombres[0][0])
            and valores == [('arreglo', [])]):
        p[0] = ('crear_pila', nombres[0][0])
    else:
        p[0] = ('declaracion_local', nombres, valores)


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

    if len(p) == 10:
        paso = None
        cuerpo = p[8]
    else:
        paso = p[8]
        cuerpo = p[10]

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


def es_nombre_pila(nombre):
    # Convención: pila, pila_datos, pilaNumeros, stack, stack1, ...
    return nombre.lower().startswith(('pila', 'stack'))


def p_sentencia_asignacion_acceso(p):
    'sentencia : acceso ASSIGN expresion'
    destino, valor = p[1], p[3]

    # (Christian) CREAR pila:  pila = {}   (por convención de nombre)
    if (destino[0] == 'identificador'
            and es_nombre_pila(destino[1])
            and valor == ('arreglo', [])):
        p[0] = ('crear_pila', destino[1])

    # (Christian) INSERTAR en pila:  pila[#pila + 1] = v
    elif (destino[0] == 'acceso_indice'
            and destino[1][0] == 'identificador'
            and isinstance(destino[2], tuple) and destino[2][0] == '+'
            and isinstance(destino[2][1], tuple) and destino[2][1][0] == '#'
            and destino[2][1][1] == destino[1]):
        p[0] = ('insertar_en_pila', destino[1][1], valor)

    # (Christian) LISTA ENLAZADA:  nodo = { valor = 5, siguiente = nil }
    elif (destino[0] == 'identificador'
          and isinstance(valor, tuple) and valor[0] == 'tabla'
          and {'valor', 'siguiente'} <= {c[1] for c in valor[1] if c[0] == 'campo'}):
        p[0] = ('crear_lista_enlazada', destino[1], valor)

    # (Romina) ASIGNACIÓN SIMPLE: x = 20, notas[1] = 95, pila = {}, persona = {...}
    else:
        p[0] = ('asignacion_acceso', destino, valor)


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


#EXPRESIONES BASICAS 

def p_expresion_basica(p):
    '''expresion : NIL
                 | TRUE
                 | FALSE
                 | INTEGER
                 | FLOAT
                 | STRING
                 | acceso'''
    p[0] = p[1]


def p_expresion_binaria(p):
    '''expresion : expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion FLOORDIV expresion
                 | expresion MOD expresion
                 | expresion POW expresion
                 | expresion CONCAT expresion
                 | expresion EQ expresion
                 | expresion NE expresion
                 | expresion LT expresion
                 | expresion GT expresion
                 | expresion LE expresion
                 | expresion GE expresion
                 | expresion AND expresion
                 | expresion OR expresion'''
    p[0] = (p[2], p[1], p[3])


def p_expresion_unaria(p):
    '''expresion : NOT expresion
                 | LEN expresion
                 | MINUS expresion %prec NOT'''
    p[0] = (p[1], p[2])


def p_expresion_parentesis(p):
    'expresion : LPAREN expresion RPAREN'
    p[0] = p[2]

# ============ INICIO APORTE: Romina Brown ============

# --- Asignación simple: la maneja p_sentencia_asignacion_acceso ---

# --- Condicional if / elseif / else (guarda TODOS los bloques) ---
def p_sentencia_if(p):
    'sentencia : IF expresion THEN bloque lista_elseif parte_else END'
    p[0] = ('condicional_if', p[2], p[4], p[5], p[6])


def p_lista_elseif_multiple(p):
    'lista_elseif : lista_elseif ELSEIF expresion THEN bloque'
    p[0] = p[1] + [(p[3], p[5])]


def p_lista_elseif_vacia(p):
    'lista_elseif : vacio'
    p[0] = []


def p_parte_else(p):
    'parte_else : ELSE bloque'
    p[0] = p[2]


def p_parte_else_vacia(p):
    'parte_else : vacio'
    p[0] = None


# --- Arreglo, matriz y tablas anidadas ---
def p_expresion_constructor_tabla(p):
    'expresion : constructor_tabla'
    p[0] = p[1]


def p_constructor_tabla(p):
    '''constructor_tabla : LBRACE RBRACE
                         | LBRACE lista_campos RBRACE
                         | LBRACE lista_campos separador_campo RBRACE'''
    campos = [] if len(p) == 3 else p[2]
    if all(c[0] == 'elemento' for c in campos):
        p[0] = ('arreglo', [c[1] for c in campos])
    else:
        p[0] = ('tabla', campos)


def p_separador_campo(p):
    '''separador_campo : COMMA
                       | SEMICOLON'''
    p[0] = p[1]


def p_lista_campos_multiple(p):
    'lista_campos : lista_campos separador_campo campo'
    p[0] = p[1] + [p[3]]


def p_lista_campos_uno(p):
    'lista_campos : campo'
    p[0] = [p[1]]


def p_campo_elemento(p):
    'campo : expresion'
    p[0] = ('elemento', p[1])


def p_campo_nombrado(p):
    'campo : ID ASSIGN expresion'
    p[0] = ('campo', p[1], p[3])


def p_campo_indexado(p):
    'campo : LBRACKET expresion RBRACKET ASSIGN expresion'
    p[0] = ('campo_indexado', p[2], p[5])


# --- Función con parámetros y retorno ---
def p_sentencia_funcion_sin_parametros(p):
    'sentencia : FUNCTION ID LPAREN RPAREN bloque END'
    p[0] = ('funcion', p[2], [], p[5])


def p_sentencia_funcion_con_parametros(p):
    'sentencia : FUNCTION ID LPAREN lista_parametros RPAREN bloque END'
    p[0] = ('funcion', p[2], p[4], p[6])


def p_sentencia_retorno(p):
    '''sentencia : RETURN
                 | RETURN lista_expresiones'''
    p[0] = ('retorno', p[2] if len(p) == 3 else [])


# --- local function ---
def p_sentencia_local_function_sin_parametros(p):
    'sentencia : LOCAL FUNCTION ID LPAREN RPAREN bloque END'
    p[0] = ('funcion_local', p[3], [], p[6])


def p_sentencia_local_function_con_parametros(p):
    'sentencia : LOCAL FUNCTION ID LPAREN lista_parametros RPAREN bloque END'
    p[0] = ('funcion_local', p[3], p[5], p[7])


# --- Llamada a función (print incluido), guarda los argumentos ---
def p_llamada(p):
    '''llamada : acceso LPAREN RPAREN
               | acceso LPAREN lista_expresiones RPAREN'''
    p[0] = ('llamada', p[1], [] if len(p) == 4 else p[3])


def p_sentencia_llamada(p):
    'sentencia : llamada'
    p[0] = p[1]


def p_expresion_llamada(p):
    'expresion : llamada'
    nombre, args = p[1][1], p[1][2]
    if nombre == ('identificador', 'tonumber') and len(args) == 1:
        p[0] = ('convertir_a_numero', args[0])
    elif nombre == ('identificador', 'tostring') and len(args) == 1:
        p[0] = ('convertir_a_cadena', args[0])
    else:
        p[0] = p[1]

# ============ FIN APORTE: Romina Brown ============

#ERRORES Y EJECUCION

def p_error(p):
    if p is None:
        errores_sintacticos.append("Error sintáctico: fin de archivo inesperado.")
    else:
        errores_sintacticos.append(
            f"Error sintáctico en la línea {p.lineno}: token inesperado '{p.value}'."
        )

parser = yacc.yacc(write_tables=False, debug=False)

def analizar_sintaxis(codigo):
    del errores_sintacticos[:]
    analizador_lexico.lexer.lineno = 1
    parser.parse(codigo, lexer=analizador_lexico.lexer)
    return list(errores_sintacticos)