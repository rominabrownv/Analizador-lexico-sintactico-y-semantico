import os
import sys
from datetime import datetime, timedelta, timezone

import lexer
import parser as analizador_sintactico


# Crear carpeta de logs
carpeta_logs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(carpeta_logs, exist_ok=True)

# Leer archivo de prueba
if len(sys.argv) > 1:
    ruta = sys.argv[1]
    if not os.path.exists(ruta) and os.path.exists(os.path.join("test", ruta)):
        ruta = os.path.join("test", ruta)
    if not os.path.isfile(ruta):
        sys.exit(f"No se encuentra el archivo: {sys.argv[1]}")
else:
    ruta = input("Ingrese la ruta del archivo a analizar: ")

with open(ruta, "r", encoding="utf-8") as archivo:
    codigo = archivo.read()

# Usuario de GitHub
usuario = sys.argv[2] if len(sys.argv) > 2 else input("Ingrese su usuario de GitHub: ")

# Fecha y hora UTC-5
zona_horaria = timezone(timedelta(hours=-5))
fecha_hora = datetime.now(zona_horaria).strftime("%Y%m%d-%Hh%M")

# Ejecutar análisis léxico
tokens, errores_lexicos = lexer.analizar(codigo)

# Ejecutar análisis sintáctico
errores_sintacticos = analizador_sintactico.analizar_sintaxis(codigo)

# Crear nombre del log sintáctico
ruta_log = os.path.join(carpeta_logs, f"sintactico-{usuario}-{fecha_hora}.txt")
if os.path.exists(ruta_log):
    sufijo = 2
    while os.path.exists(
        os.path.join(carpeta_logs, f"sintactico-{usuario}-{fecha_hora}-{sufijo}.txt")
    ):
        sufijo += 1
    ruta_log = os.path.join(
        carpeta_logs, f"sintactico-{usuario}-{fecha_hora}-{sufijo}.txt"
    )

# Guardar errores sintácticos
with open(ruta_log, "w", encoding="utf-8") as archivo:
    archivo.write("========== ANALISIS SINTACTICO ==========\n")
    archivo.write(f"Usuario: {usuario}\n")
    archivo.write(f"Fecha: {fecha_hora}\n")
    archivo.write(f"Archivo analizado: {ruta}\n")
    archivo.write("\n========== ERRORES SINTACTICOS ==========\n")

    if errores_sintacticos:
        for error in errores_sintacticos:
            archivo.write(f"{error}\n")
    else:
        archivo.write("No se encontraron errores sintacticos.\n")

# Mostrar resultados
print("\n========== RESULTADOS ==========")
print(f"Tokens encontrados: {len(tokens)}")
print(f"Errores léxicos: {len(errores_lexicos)}")
print(f"Errores sintácticos: {len(errores_sintacticos)}")
print(f"\nLog sintáctico generado: {ruta_log}")
