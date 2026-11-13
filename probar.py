import os
import sys
from datetime import datetime, timedelta, timezone
import lexer
import parser as analizador_sintactico


CARPETA_LOGS = 'logs'


# Verificar que se haya indicado un archivo
if len(sys.argv) < 2:
    print('Uso: python probar.py test/algoritmo1.lua usuarioGit')
    sys.exit(1)


archivo = sys.argv[1]

# Si el archivo no está en la carpeta actual, buscarlo en test/
if not os.path.exists(archivo):
    archivo = os.path.join('test', archivo)

if not os.path.exists(archivo):
    print('No encuentro el archivo: ' + sys.argv[1])
    sys.exit(1)


# Obtener el usuario de Git
if len(sys.argv) >= 3:
    usuario = sys.argv[2]
else:
    usuario = input('Usuario de Git: ')


# Leer el código Lua
with open(archivo, encoding='utf-8') as f:
    codigo = f.read()


# EJECUTAR EL ANALISIS LEXICO

tokens, errores_lexicos = lexer.analizar(codigo)


# EJECUTAR EL ANALISIS SINTACTICO

resultado, errores_sintacticos = analizador_sintactico.analizar_sintaxis(codigo)

zona_horaria = timezone(timedelta(hours=-5))
ahora = datetime.now(zona_horaria)

fecha_hora = ahora.strftime('%Y%m%d-%Hh%M')


# CREAR LA CARPETA DE LOGS SI NO EXISTE

if not os.path.exists(CARPETA_LOGS):
    os.makedirs(CARPETA_LOGS)


# GENERAR LOG DEL ANALISIS LEXICO

nombre_lexico = 'lexico-' + usuario + '-' + fecha_hora + '.txt'
ruta_lexico = os.path.join(CARPETA_LOGS, nombre_lexico)

if os.path.exists(ruta_lexico):
    print('Ya existe un log con esta fecha y hora. Espera un minuto y vuelve a ejecutar.')
    sys.exit(1)


with open(ruta_lexico, 'w', encoding='utf-8') as log:
    log.write('LOG DE PRUEBA DEL ANALIZADOR LEXICO (Lua 5.5)\n')
    log.write('Usuario: ' + usuario + '\n')
    log.write('Fecha: ' + ahora.strftime('%d/%m/%Y %H:%M:%S') + '\n')
    log.write('Algoritmo: ' + archivo + '\n\n')

    log.write('TOKENS RECONOCIDOS (' + str(len(tokens)) + ')\n')

    for tipo, lexema, valor, linea, col in tokens:
        log.write(
            'Linea %d, col %d: %s  %s\n'
            % (linea, col, tipo, lexema.replace('\n', '\\n'))
        )

    log.write('\nERRORES (' + str(len(errores_lexicos)) + ')\n')

    if len(errores_lexicos) == 0:
        log.write('Ninguno\n')

    for linea, col, mensaje in errores_lexicos:
        log.write('Linea %d, col %d: %s\n' % (linea, col, mensaje))


# GENERAR LOG DEL ANALISIS SINTACTICO

nombre_sintactico = 'sintactico-' + usuario + '-' + fecha_hora + '.txt'
ruta_sintactico = os.path.join(CARPETA_LOGS, nombre_sintactico)

with open(ruta_sintactico, 'w', encoding='utf-8') as log:
    log.write('LOG DE PRUEBA DEL ANALIZADOR SINTACTICO (Lua 5.5)\n')
    log.write('Usuario: ' + usuario + '\n')
    log.write('Fecha: ' + ahora.strftime('%d/%m/%Y %H:%M:%S') + '\n')
    log.write('Algoritmo: ' + archivo + '\n\n')

    log.write('RESULTADO DEL ANALISIS SINTACTICO\n')

    if len(errores_sintacticos) == 0 and resultado is not None:
        log.write('El codigo no presenta errores sintacticos.\n')
    else:
        log.write('Se encontraron errores sintacticos.\n')

    log.write('\nERRORES SINTACTICOS (' + str(len(errores_sintacticos)) + ')\n')

    if len(errores_sintacticos) == 0:
        log.write('Ninguno\n')

    for mensaje in errores_sintacticos:
        log.write(mensaje + '\n')


# MOSTRAR RESULTADOS EN CONSOLA

print('\nRESULTADOS DEL ANALISIS')
print('Tokens reconocidos:', len(tokens))
print('Errores lexicos:', len(errores_lexicos))
print('Errores sintacticos:', len(errores_sintacticos))

print('\nLogs generados:')
print(ruta_lexico)
print(ruta_sintactico)
