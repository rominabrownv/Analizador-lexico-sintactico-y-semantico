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

-- Casos de prueba de error
local @caracter_invalido = 99
local numero_malformado = 123abc