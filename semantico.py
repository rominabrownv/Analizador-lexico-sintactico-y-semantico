
errores_control = []   # cada error: (linea, mensaje)


def error_control(linea, mensaje):
    errores_control.append((linea, mensaje))


def linea_de(nodo):
    # La línea es el último elemento del nodo; si el nodo no la trae, devuelve 0
    ultimo = nodo[-1]
    if isinstance(ultimo, int):
        return ultimo
    return 0

# Punto de entrada
def verificar_control(programa):
    del errores_control[:]
    if programa:
        revisar_bloque(programa, 0, [])
    errores_control.sort()
    resultado = []
    for linea, mensaje in errores_control:
        resultado.append('Error semántico (control) en la línea %d: %s' % (linea, mensaje))
    return resultado



# Bloques y sentencias
def revisar_bloque(bloque, profundidad_de_bucles, etiquetas_visibles):
    # etiquetas_visibles
    propias = {}
    for sentencia in bloque:
        if es_nodo(sentencia, 'declarar_etiqueta'):
            nombre = sentencia[1]
            linea = linea_de(sentencia)
            if nombre in propias:
                error_control(linea, "la etiqueta '%s' ya fue declarada en este ámbito "
                                     "(línea %d)." % (nombre, propias[nombre]))
            else:
                propias[nombre] = linea

    visibles = etiquetas_visibles + [propias]

    # 2) Revisar cada sentencia del bloque
    for sentencia in bloque:
        revisar_sentencia(sentencia, profundidad_de_bucles, visibles)


def revisar_sentencia(s, profundidad_de_bucles, visibles):
    if not isinstance(s, tuple):
        return
    tipo = s[0]

    # --- Regla 5: break ---
    if tipo == 'romper_ciclo':
        if profundidad_de_bucles == 0:
            error_control(linea_de(s), "'break' fuera de un bucle.")

    # --- Regla 6: goto ---
    elif tipo == 'saltar_a_etiqueta':
        if not etiqueta_visible(s[1], visibles):
            error_control(linea_de(s), "la etiqueta '%s' no está visible para goto." % s[1])

    # --- Bucles: el cuerpo tiene un nivel más de profundidad ---
    elif tipo == 'ciclo_for_numerico':          # (tipo, var, inicio, fin, paso, cuerpo)
        buscar_funciones_anonimas([s[2], s[3], s[4]])
        revisar_bloque(s[5], profundidad_de_bucles + 1, visibles)

    elif tipo == 'ciclo_for_generico':          # (tipo, nombres, expresiones, cuerpo)
        buscar_funciones_anonimas(s[2])
        revisar_bloque(s[3], profundidad_de_bucles + 1, visibles)

    elif tipo == 'bucle_while':                 # (tipo, condicion, cuerpo)
        buscar_funciones_anonimas(s[1])
        revisar_bloque(s[2], profundidad_de_bucles + 1, visibles)

    elif tipo == 'bucle_repeat':                # (tipo, cuerpo, condicion)
        buscar_funciones_anonimas(s[2])
        revisar_bloque(s[1], profundidad_de_bucles + 1, visibles)

    # --- if: sus bloques siguen en el mismo nivel de bucle y ven las mismas etiquetas ---
    elif tipo == 'condicional_if':              # (tipo, cond, bloque, lista_elseif, parte_else)
        buscar_funciones_anonimas(s[1])
        revisar_bloque(s[2], profundidad_de_bucles, visibles)
        for condicion, bloque_elseif in s[3]:
            buscar_funciones_anonimas(condicion)
            revisar_bloque(bloque_elseif, profundidad_de_bucles, visibles)
        if s[4] is not None:
            revisar_bloque(s[4], profundidad_de_bucles, visibles)

    # --- Funciones: dentro de una función se empieza de cero ---
    elif tipo in ('funcion', 'funcion_local', 'funcion_variadica',
                  'funcion_variadica_con_parametros'):
        revisar_bloque(s[-1], 0, [])           

    # --- Cualquier otra sentencia: solo puede esconder funciones anónimas en sus expresiones ---
    else:
        buscar_funciones_anonimas(s[1:])


def es_nodo(nodo, tipo):
    return isinstance(nodo, tuple) and len(nodo) > 0 and nodo[0] == tipo


def etiqueta_visible(nombre, visibles):
    for etiquetas in visibles:
        if nombre in etiquetas:
            return True
    return False


def buscar_funciones_anonimas(dato):
    if es_nodo(dato, 'funcion_anonima'):
        revisar_bloque(dato[-1], 0, [])
    elif isinstance(dato, (list, tuple)):
        for parte in dato:
            buscar_funciones_anonimas(parte)



# ============ Romina (reglas semánticas 1 y 2) ============

GLOBALES_LUA = {
    'print', 'tonumber', 'tostring', 'type', 'pairs', 'ipairs', 'next', 'select',
    'error', 'assert', 'pcall', 'xpcall', 'load', 'require', 'setmetatable',
    'getmetatable', 'rawget', 'rawset', 'rawequal', 'rawlen',
    'io', 'os', 'string', 'table', 'math', 'coroutine', 'utf8', 'debug', '_G', '_ENV',
}

errores_ident = []   # cada error: (linea, mensaje)


def error_ident(linea, mensaje):
    errores_ident.append((linea, mensaje))


class Ambito:
    def __init__(self, padre=None):
        self.simbolos = {}      # nombre -> atributo ('const', 'close' o None)
        self.padre = padre

    def declarar(self, nombre, atributo=None):
        self.simbolos[nombre] = atributo

    def buscar(self, nombre):
        # Busca desde el ámbito actual hacia los externos
        ambito = self
        while ambito is not None:
            if nombre in ambito.simbolos:
                return True, ambito.simbolos[nombre]
            ambito = ambito.padre
        return False, None

    def raiz(self):
        ambito = self
        while ambito.padre is not None:
            ambito = ambito.padre
        return ambito


# Punto de entrada: recibe el árbol del parser y devuelve la lista de mensajes
def verificar_identificadores(programa):
    del errores_ident[:]
    globales = Ambito()
    for nombre in GLOBALES_LUA:
        globales.declarar(nombre)
    if programa:
        predeclarar_funciones(programa, globales)
        revisar_bloque_ident(programa, Ambito(globales))
    errores_ident.sort()
    return ['Error semántico (identificadores) en la línea %d: %s' % (l, m)
            for l, m in errores_ident]


def predeclarar_funciones(programa, globales):
    # Solo las funciones globales del nivel principal; permite llamarlas
    # desde funciones definidas antes que ellas.
    for s in programa:
        if isinstance(s, tuple) and s and s[0] in (
                'funcion', 'funcion_variadica', 'funcion_variadica_con_parametros'):
            globales.declarar(s[1])


def revisar_bloque_ident(bloque, ambito):
    for sentencia in bloque:
        revisar_sentencia_ident(sentencia, ambito)


def revisar_funcion(parametros, cuerpo, ambito):
    nuevo = Ambito(ambito)
    for p in parametros:
        nuevo.declarar(p)
    revisar_bloque_ident(cuerpo, nuevo)


def usar(nombre, linea, ambito, clase):
    # REGLA 1: toda variable o función usada debe estar declarada
    encontrado, _ = ambito.buscar(nombre)
    if not encontrado:
        error_ident(linea, "la %s '%s' no ha sido declarada." % (clase, nombre))


def linea_ident(nodo):
    return nodo[2] if len(nodo) > 2 and isinstance(nodo[2], int) else 0


def asignar_a(destino, amb):
    # Revisa un destino de asignación (simple o múltiple)
    if isinstance(destino, tuple) and destino and destino[0] == 'identificador':
        nombre = destino[1]
        encontrado, atributo = amb.buscar(nombre)
        if not encontrado:
            error_ident(linea_ident(destino),
                        "la variable '%s' no ha sido declarada." % nombre)
        elif atributo == 'const':
            # REGLA 2: una constante no puede recibir otra asignación
            error_ident(linea_ident(destino),
                        "no se puede modificar la constante '%s'." % nombre)
    else:
        revisar_expr(destino, amb)          # notas[1] = ..., persona.edad = ...


def revisar_sentencia_ident(s, amb):
    if not isinstance(s, tuple) or not s:
        return
    tipo = s[0]

    if tipo == 'declaracion_local':               # (tipo, [(nombre, attr)], valores)
        revisar_expr(s[2], amb)                   # primero los valores, luego se declara
        for nombre, atributo in s[1]:
            amb.declarar(nombre, atributo)

    elif tipo == 'declaracion_global':            # (tipo, [nombres], valores)
        revisar_expr(s[2], amb)
        for nombre in s[1]:
            amb.raiz().declarar(nombre)

    elif tipo == 'crear_pila':                    # (tipo, nombre, es_local, linea)
        if s[2]:
            amb.declarar(s[1])                    # local pila = {}  -> declara
        else:                                     # pila = {}  -> debe existir y no ser const
            asignar_a(('identificador', s[1], s[3]), amb)
            

    elif tipo == 'crear_lista_enlazada':          # (tipo, nombre, tabla, linea)
        revisar_expr(s[2], amb)
        asignar_a(('identificador', s[1], s[3]), amb)


    elif tipo == 'insertar_en_pila':              # (tipo, nombre, valor, linea)
        revisar_expr(s[2], amb)
        linea = s[3] if len(s) > 3 and isinstance(s[3], int) else 0
        usar(s[1], linea, amb, 'variable')

    elif tipo == 'asignacion_simple':             # (tipo, destino, valor)
        revisar_expr(s[2], amb)
        asignar_a(s[1], amb)

    elif tipo == 'multi_asignacion':              # (tipo, [destinos], [valores])
        revisar_expr(s[2], amb)
        for destino in s[1]:
            asignar_a(destino, amb)

    elif tipo in ('llamada_funcion', 'io_write', 'io_read',
                  'convertir_a_numero', 'convertir_a_cadena'):
        revisar_expr(s, amb)

    elif tipo == 'funcion':                       # (tipo, nombre, parametros, cuerpo)
        amb.raiz().declarar(s[1])
        revisar_funcion(s[2], s[3], amb)

    elif tipo == 'funcion_local':                 # (tipo, nombre, parametros, cuerpo)
        amb.declarar(s[1])                        # visible dentro de sí misma
        revisar_funcion(s[2], s[3], amb)

    elif tipo == 'funcion_variadica':             # (tipo, nombre, cuerpo)
        amb.raiz().declarar(s[1])
        revisar_funcion([], s[2], amb)

    elif tipo == 'funcion_variadica_con_parametros':   # (tipo, nombre, parametros, cuerpo)
        amb.raiz().declarar(s[1])
        revisar_funcion(s[2], s[3], amb)

    elif tipo == 'ciclo_for_numerico':            # (tipo, var, inicio, fin, paso, cuerpo)
        revisar_expr([s[2], s[3], s[4]], amb)
        nuevo = Ambito(amb)
        nuevo.declarar(s[1])
        revisar_bloque_ident(s[5], nuevo)

    elif tipo == 'ciclo_for_generico':            # (tipo, nombres, expresiones, cuerpo)
        revisar_expr(s[2], amb)
        nuevo = Ambito(amb)
        for nombre in s[1]:
            nuevo.declarar(nombre)
        revisar_bloque_ident(s[3], nuevo)

    elif tipo == 'bucle_while':                   # (tipo, condicion, cuerpo)
        revisar_expr(s[1], amb)
        revisar_bloque_ident(s[2], Ambito(amb))

    elif tipo == 'bucle_repeat':                  # (tipo, cuerpo, condicion)
        nuevo = Ambito(amb)                       # la condición ve las locales del cuerpo
        revisar_bloque_ident(s[1], nuevo)
        revisar_expr(s[2], nuevo)

    elif tipo == 'condicional_if':                # (tipo, cond, bloque, elseifs, else)
        revisar_expr(s[1], amb)
        revisar_bloque_ident(s[2], Ambito(amb))
        for condicion, bloque in s[3]:
            revisar_expr(condicion, amb)
            revisar_bloque_ident(bloque, Ambito(amb))
        if s[4] is not None:
            revisar_bloque_ident(s[4], Ambito(amb))

    elif tipo in ('romper_ciclo', 'saltar_a_etiqueta', 'declarar_etiqueta'):
        pass
    elif tipo == 'bloque_do':                     # (tipo, cuerpo)
        revisar_bloque_ident(s[1], Ambito(amb))
    else:                                         # retorno, etc.
        revisar_expr(list(s[1:]), amb)


def revisar_expr(dato, amb):
    if isinstance(dato, tuple) and dato:
        tipo = dato[0]
        if tipo == 'identificador':
            usar(dato[1], linea_ident(dato), amb, 'variable')
        elif tipo == 'llamada_funcion':           # (tipo, callee, argumentos)
            callee = dato[1]
            if isinstance(callee, tuple) and callee[0] == 'identificador':
                usar(callee[1], linea_ident(callee), amb, 'función')
            else:
                revisar_expr(callee, amb)
            revisar_expr(dato[2], amb)
        elif tipo == 'funcion_anonima':           # (tipo, parametros, cuerpo)
            revisar_funcion(dato[1], dato[2], amb)
        else:
            for parte in dato[1:]:
                revisar_expr(parte, amb)
    elif isinstance(dato, list):
        for parte in dato:
            revisar_expr(parte, amb)
            
# ========================


# ============ Joseph (reglas semánticas 3 y 4) ============

OPERADORES_ARITMETICOS = {'+', '-', '*', '/', '//', '%', '^'}
OPERADORES_COMPARACION = {'<', '>', '<=', '>='}

errores_operaciones = []

def error_operacion(linea, mensaje):
    errores_operaciones.append((linea, mensaje))

def es_cadena_numerica(valor_str):
    texto = valor_str.strip()
    if (texto.startswith('"') and texto.endswith('"')) or (
            texto.startswith("'") and texto.endswith("'")):
        texto = texto[1:-1].strip()
    elif texto.startswith('[[') and texto.endswith(']]'):
        texto = texto[2:-2].strip()
    if not texto:
        return False
    try:
        float(texto)
        return True
    except ValueError:
        try:
            int(texto, 16)
            return True
        except ValueError:
            return False


def obtener_linea_expr(nodo):
    if isinstance(nodo, tuple) and nodo:
        # Si el nodo binario/unario trae la línea al final
        if nodo[0] in OPERADORES_ARITMETICOS | OPERADORES_COMPARACION | {'..'} and len(nodo) >= 4 and isinstance(nodo[-1], int):
            return nodo[-1]
        if nodo[0] == '-' and len(nodo) == 3 and isinstance(nodo[-1], int):
            return nodo[-1]
        if nodo[0] == 'identificador' and len(nodo) >= 3 and isinstance(nodo[2], int):
            return nodo[2]
        for elem in nodo[1:]:
            linea = obtener_linea_expr(elem)
            if linea > 0:
                return linea
    elif isinstance(nodo, list):
        for elem in nodo:
            linea = obtener_linea_expr(elem)
            if linea > 0:
                return linea
    return 0


def inferir_tipo(expr, tabla_tipos):
    """
    Infere el tipo estático de una expresión cuando es posible determinarlo.
    Posibles retornos: 'number', 'string', 'boolean', 'nil', 'table', 'function', o None.
    """
    if expr is None:
        return 'nil'
    if isinstance(expr, bool):
        return 'boolean'
    if isinstance(expr, (int, float)):
        return 'number'
    if isinstance(expr, str):
        if expr == 'nil':
            return 'nil'
        if expr in ('true', 'false'):
            return 'boolean'
        return 'string'

    if not isinstance(expr, tuple) or not expr:
        return None

    op = expr[0]

    if op == 'identificador':
        return tabla_tipos.get(expr[1])

    if op in ('arreglo', 'tabla'):
        return 'table'

    if op == 'funcion_anonima':
        return 'function'

    if op == 'convertir_a_numero':
        return 'number'

    if op == 'convertir_a_cadena':
        return 'string'

    if op == '#':
        return 'number'

    if op == 'not':
        return 'boolean'

    if op in {'==', '~='} | OPERADORES_COMPARACION:
        return 'boolean'

    if op == '..':
        return 'string'

    # Menos unario: ('-', operando) o ('-', operando, linea)
    if op == '-' and (len(expr) == 2 or (len(expr) == 3 and isinstance(expr[2], int))):
        t = inferir_tipo(expr[1], tabla_tipos)
        if t == 'number' or (t == 'string' and isinstance(expr[1], str) and es_cadena_numerica(expr[1])):
            return 'number'
        return None

    # Operadores aritméticos binarios
    if op in OPERADORES_ARITMETICOS and len(expr) >= 3:
        t_izq = inferir_tipo(expr[1], tabla_tipos)
        t_der = inferir_tipo(expr[2], tabla_tipos)
        izq_valido = (t_izq == 'number') or (
            t_izq == 'string' and isinstance(expr[1], str) and es_cadena_numerica(expr[1])
        )
        der_valido = (t_der == 'number') or (
            t_der == 'string' and isinstance(expr[2], str) and es_cadena_numerica(expr[2])
        )
        if izq_valido and der_valido:
            return 'number'
        return None

    return None


def validar_expresion_ops(nodo, tabla_tipos):
    if isinstance(nodo, list):
        for item in nodo:
            validar_expresion_ops(item, tabla_tipos)
        return

    if not isinstance(nodo, tuple) or not nodo:
        return

    op = nodo[0]

    # Si el primer elemento no es un string (ej. es una sub-tupla o lista), recorrer sus elementos
    if not isinstance(op, str):
        for parte in nodo:
            validar_expresion_ops(parte, tabla_tipos)
        return

    # Caso especial: menos unario ('-', operando) o ('-', operando, linea)
    if op == '-' and (len(nodo) == 2 or (len(nodo) == 3 and isinstance(nodo[2], int))):
        operando = nodo[1]
        validar_expresion_ops(operando, tabla_tipos)
        tipo_op = inferir_tipo(operando, tabla_tipos)
        if tipo_op is not None:
            es_num_str = (tipo_op == 'string' and isinstance(operando, str) and es_cadena_numerica(operando))
            if tipo_op != 'number' and not es_num_str:
                error_operacion(
                    obtener_linea_expr(nodo),
                    "no se puede aplicar '-' unario a '%s'." % tipo_op
                )
        return

    # Operadores binarios
    if op in (OPERADORES_ARITMETICOS | OPERADORES_COMPARACION | {'..'}) and len(nodo) >= 3:
        izq, der = nodo[1], nodo[2]
        validar_expresion_ops(izq, tabla_tipos)
        validar_expresion_ops(der, tabla_tipos)

        tipo_izq = inferir_tipo(izq, tabla_tipos)
        tipo_der = inferir_tipo(der, tabla_tipos)
        linea = obtener_linea_expr(nodo)

        # REGLA 3: Operandos aritméticos válidos
        if op in OPERADORES_ARITMETICOS:
            izq_ok = (tipo_izq is None or tipo_izq == 'number' or
                      (tipo_izq == 'string' and isinstance(izq, str) and es_cadena_numerica(izq)))
            der_ok = (tipo_der is None or tipo_der == 'number' or
                      (tipo_der == 'string' and isinstance(der, str) and es_cadena_numerica(der)))

            if not izq_ok or not der_ok:
                t1 = tipo_izq if tipo_izq is not None else 'desconocido'
                t2 = tipo_der if tipo_der is not None else 'desconocido'
                error_operacion(
                    linea,
                    "no se puede aplicar '%s' entre '%s' y '%s'." % (op, t1, t2)
                )

        # REGLA 4A: Concatenación (..) solo admite string o number
        elif op == '..':
            izq_ok = tipo_izq is None or tipo_izq in ('string', 'number')
            der_ok = tipo_der is None or tipo_der in ('string', 'number')
            if not izq_ok or not der_ok:
                t1 = tipo_izq if tipo_izq is not None else 'desconocido'
                t2 = tipo_der if tipo_der is not None else 'desconocido'
                error_operacion(
                    linea,
                    "no se puede concatenar '%s' con '%s'." % (t1, t2)
                )

        # REGLA 4B: Comparación (<, >, <=, >=) exige ambos number o ambos string
        elif op in OPERADORES_COMPARACION:
            if tipo_izq is not None and tipo_der is not None:
                ambos_num = (tipo_izq == 'number' and tipo_der == 'number')
                ambos_str = (tipo_izq == 'string' and tipo_der == 'string')
                if not (ambos_num or ambos_str):
                    error_operacion(
                        linea,
                        "no se puede comparar '%s' con '%s'." % (tipo_izq, tipo_der)
                    )
        return

    # Recorrer cualquier otro nodo tupla (llamadas, tablas, etc.)
    for parte in nodo[1:]:
        validar_expresion_ops(parte, tabla_tipos)


def revisar_bloque_ops(bloque, tabla_tipos):
    if not bloque:
        return
    for s in bloque:
        revisar_sentencia_ops(s, tabla_tipos)


def revisar_sentencia_ops(s, tabla_tipos):
    if not isinstance(s, tuple) or not s:
        return
    tipo = s[0]

    if tipo in ('declaracion_local', 'declaracion_global'):
        nombres = s[1]
        valores = s[2]
        if valores:
            validar_expresion_ops(valores, tabla_tipos)
            for idx, item in enumerate(nombres):
                nombre = item[0] if isinstance(item, tuple) else item
                if idx < len(valores):
                    tabla_tipos[nombre] = inferir_tipo(valores[idx], tabla_tipos)
                else:
                    tabla_tipos[nombre] = 'nil'
        else:
            for item in nombres:
                nombre = item[0] if isinstance(item, tuple) else item
                tabla_tipos[nombre] = 'nil'

    elif tipo == 'asignacion_simple':
        destino, valor = s[1], s[2]
        validar_expresion_ops(destino, tabla_tipos)
        validar_expresion_ops(valor, tabla_tipos)
        if isinstance(destino, tuple) and destino[0] == 'identificador':
            tabla_tipos[destino[1]] = inferir_tipo(valor, tabla_tipos)

    elif tipo == 'multi_asignacion':
        destinos, valores = s[1], s[2]
        validar_expresion_ops(destinos, tabla_tipos)
        validar_expresion_ops(valores, tabla_tipos)
        for idx, destino in enumerate(destinos):
            if isinstance(destino, tuple) and destino[0] == 'identificador':
                if idx < len(valores):
                    tabla_tipos[destino[1]] = inferir_tipo(valores[idx], tabla_tipos)
                else:
                    tabla_tipos[destino[1]] = 'nil'

    elif tipo == 'crear_pila':
        tabla_tipos[s[1]] = 'table'

    elif tipo == 'crear_lista_enlazada':
        validar_expresion_ops(s[2], tabla_tipos)
        tabla_tipos[s[1]] = 'table'

    elif tipo == 'insertar_en_pila':
        validar_expresion_ops(s[2], tabla_tipos)

    elif tipo == 'ciclo_for_numerico':
        validar_expresion_ops([s[2], s[3], s[4]], tabla_tipos)
        ambito_local = dict(tabla_tipos)
        ambito_local[s[1]] = 'number'
        revisar_bloque_ops(s[5], ambito_local)

    elif tipo == 'ciclo_for_generico':
        validar_expresion_ops(s[2], tabla_tipos)
        ambito_local = dict(tabla_tipos)
        for nombre in s[1]:
            ambito_local[nombre] = None
        revisar_bloque_ops(s[3], ambito_local)

    elif tipo == 'bucle_while':
        validar_expresion_ops(s[1], tabla_tipos)
        revisar_bloque_ops(s[2], dict(tabla_tipos))

    elif tipo == 'bucle_repeat':
        ambito_local = dict(tabla_tipos)
        revisar_bloque_ops(s[1], ambito_local)
        validar_expresion_ops(s[2], ambito_local)

    elif tipo == 'condicional_if':
        validar_expresion_ops(s[1], tabla_tipos)
        revisar_bloque_ops(s[2], dict(tabla_tipos))
        for cond, bloque_elseif in s[3]:
            validar_expresion_ops(cond, tabla_tipos)
            revisar_bloque_ops(bloque_elseif, dict(tabla_tipos))
        if s[4] is not None:
            revisar_bloque_ops(s[4], dict(tabla_tipos))

    elif tipo in ('funcion', 'funcion_local', 'funcion_variadica', 'funcion_variadica_con_parametros'):
        if tipo != 'funcion_variadica':
            tabla_tipos[s[1]] = 'function'
        ambito_fn = dict(tabla_tipos)
        if tipo in ('funcion', 'funcion_local', 'funcion_variadica_con_parametros'):
            for param in s[2]:
                ambito_fn[param] = None
        revisar_bloque_ops(s[-1], ambito_fn)

    else:
        validar_expresion_ops(list(s[1:]), tabla_tipos)


def verificar_operaciones(programa):
    del errores_operaciones[:]
    if programa:
        revisar_bloque_ops(programa, {})
    errores_operaciones.sort()
    return [
        'Error semántico (operaciones) en la línea %d: %s' % (l, m)
        for l, m in errores_operaciones
    ]

def analizar_semantica(programa):
    errores = []
    errores.extend(verificar_identificadores(programa))
    errores.extend(verificar_operaciones(programa))
    errores.extend(verificar_control(programa))
    return errores