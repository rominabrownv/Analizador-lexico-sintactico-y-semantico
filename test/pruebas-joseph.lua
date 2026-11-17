-- Parte Léxica
-- Prueba de delimitadores y operadores: Joseph Carrera (Jecs86)

print("--- PRUEBA 1: Aritméticos, Relacionales y Lógicos ---")

local x = 10
local y = 3
local suma = x + y
local resta = x - y
local mult = x * y
local div = x / y
local div_entera = x // y
local modulo = x % y
local potencia = x ^ 2

local comparacion_eq = (x == 10)
local comparacion_ne = (y ~= 5)
local comparacion_lt = (y < x)
local comparacion_gt = (x > y)
local comparacion_le = (x <= 10)
local comparacion_ge = (y >= 3)

local logico_and = (x > 5) and (y < 5)
local logico_or = (x == 0) or (y == 3)
local logico_not = not (x == y)


print("--- PRUEBA 2: Bits, Concatenación, Longitud, Tablas y Errores ---")

local bit_and = 5 & 3
local bit_or = 5 | 3
local bit_xor = 5 ~ 3
local shift_izq = 2 << 1
local shift_der = 4 >> 1

local mensaje = "Hola " .. "Mundo"
local longitud_str = #mensaje

local matriz = { {1, 2}, {3, 4} }
local elemento = matriz[1][2]
local punto_acceso = matriz.campo

::etiqueta_prueba::
do
    local a, b, c = 10, 20, 30
    print(a, b, c)
end


-- Parte Sintáctica
-- Control de Flujo, Asignación Múltiple y Anónimas, Diccionarios, Registros y Entrada/Salida (I/O)

local x, y, mensaje = 10, 3, "Hola Mundo"
local puntaje, intentos = 100, 0

-- Bucle while con break y bloques do
while puntaje > 50 do
    puntaje = puntaje - 10
    do
        local temporal = 5
        if temporal == 5 then
            break
        end
    end
end

-- Bucle repeat hasta condición
repeat
    intentos = intentos + 1
    io.write("Intentos actuales: ")
    print(intentos)
until intentos >= 3

-- Uso de goto y etiquetas
goto salto_etiqueta
print("Esta línea debe ser omitida por el flujo.")

::salto_etiqueta::

-- Función anónima asignada a una variable
local calcular_doble = function(val)
    return val * 2
end

local resultado_anonimo = calcular_doble(25)

local nombre = "Lua 5.5"
local pi <const> = 3.14159

-- Diccionario y registro con pares clave-valor (índices directos e identificadores)
local inventario = {
    espada = 1,
    escudo = 2,
    [10] = "item_especial",
    [2 + 5] = "calculado"
}

local empleado = {
    nombre = "Juan",
    salidio = 1200,
    activo = true
}

-- Entrada y salida avanzada con io.write / io.read y asignaciones
io.write("Ingrese el código del nuevo empleado: ")
local codigo_entrada = io.read()

io.write("Ingrese el sueldo base: ")
local sueldo_leido = io.read()

-- Solicitud de datos directa a variable global y local
nombre_ingresado = io.read()
local edad_ingresada = io.read()

print("Datos procesados correctamente para la versión de Lua:", nombre)

-- Parte Semántica
-- Reglas 3 y 4: Operaciones permitidas (aritméticas, concatenación y comparación)

print("--- PRUEBA SEMÁNTICA 1: Operandos Aritméticos Válidos (Regla 3) ---")
local base_num = 25
local altura_num = 4
local area_valida = (base_num * altura_num) / 2
local coercion_valida = "70" + 5
local potencia_negativa = -base_num ^ 2

print("--- PRUEBA SEMÁNTICA 2: Concatenación y Comparación Compatibles (Regla 4) ---")
local etiqueta_total = "Total calculado: " .. 250
local comparacion_numerica = (base_num > altura_num) and (coercion_valida >= 75)
local comparacion_cadenas = ("alfa" < "beta") and ("Lua" <= "Lua 5.5")


-- Casos de prueba de error
--lexico
local @caracter_invalido = 99
local numero_malformado = 123abc
-- sintactico
if x > 5 then
    print("Falta el end de este bloque if")

local a = ,20

-- semantico
local error_aritmetico_bool = true + 5
local error_aritmetico_tabla = {} * 2
local error_aritmetico_str = "hola" - 10
local error_concat_nil = "Valor: " .. nil
local error_concat_bool = "Estado: " .. false
local error_comparacion_tipos = 3 < "cinco"