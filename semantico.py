
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
