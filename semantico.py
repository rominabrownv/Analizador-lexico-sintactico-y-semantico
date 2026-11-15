
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