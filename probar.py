import os
import sys
from datetime import datetime, timedelta, timezone
 
import lexer
 
CARPETA_LOGS = 'logs'
 
if len(sys.argv) < 2:
    print('Uso: python probar.py test/algoritmo1.lua usuarioGit')
    sys.exit(1)
 
archivo = sys.argv[1]
 
# Si el archivo no está en la carpeta actual, lo busca dentro de test/
if not os.path.exists(archivo):
    archivo = os.path.join('test', archivo)
 
if not os.path.exists(archivo):
    print('No encuentro el archivo: ' + sys.argv[1])
    sys.exit(1)
 
if len(sys.argv) >= 3:
    usuario = sys.argv[2]
else:
    usuario = input('Usuario de Git: ')
 
f = open(archivo, encoding='utf-8')
codigo = f.read()
f.close()
 
tokens, errores = lexer.analizar(codigo)
 
ahora = datetime.now(timezone.utc) - timedelta(hours=5)
nombre = 'lexico-' + usuario + '-' + ahora.strftime('%d-%m-%Y-%Hh%M') + '.txt'
if not os.path.exists(CARPETA_LOGS):
    os.makedirs(CARPETA_LOGS)
ruta = os.path.join(CARPETA_LOGS, nombre)
 
if os.path.exists(ruta):
    print('Ya existe ' + nombre + ' (mismo minuto). Espera un minuto y vuelve a ejecutar.')
    sys.exit(1)
 
log = open(ruta, 'w', encoding='utf-8')
log.write('LOG DE PRUEBA DEL ANALIZADOR LEXICO (Lua 5.5)\n')
log.write('Usuario: ' + usuario + '\n')
log.write('Fecha: ' + ahora.strftime('%d/%m/%Y %H:%M:%S') + '\n')
log.write('Algoritmo: ' + archivo + '\n\n')
 
log.write('TOKENS RECONOCIDOS (' + str(len(tokens)) + ')\n')
for tipo, lexema, valor, linea, col in tokens:
    log.write('Linea %d, col %d: %s  %s\n' % (linea, col, tipo, lexema.replace('\n', '\\n')))
 
log.write('\nERRORES (' + str(len(errores)) + ')\n')
if len(errores) == 0:
    log.write('Ninguno\n')
for linea, col, mensaje in errores:
    log.write('Linea %d, col %d: %s\n' % (linea, col, mensaje))
log.close()
 
print('%d tokens, %d errores -> %s' % (len(tokens), len(errores), ruta))
