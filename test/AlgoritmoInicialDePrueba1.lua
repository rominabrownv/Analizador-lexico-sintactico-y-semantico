-- Algoritmo de prueba: Romina Brown (rominabrownv)
-- Tema: registro de calificaciones de un estudiante

-- Comentario de una línea

--[[
Comentario de varias líneas:
este bloque no se ejecuta.
]]

--[=[ comentario con ]] adentro ]=]

-- Variables y tipos de datos
local nombre = "Romina"
local apellido = 'Brown'
local edad = 20
local promedio = 85.5
local grande = 1e3
local hexa = 0xFF
local aprobado = true
local retirado = false
local observacion = nil

-- Variable global (Lua 5.5)
global materias = 4

-- Constante
local NOTA_MINIMA <const> = 60

-- Arreglo, matriz y tabla con campos
local notas = { 90, 75, 58, 88 }
local horario = { {8, 10}, {14, 16} }
local persona = { nombre = "Ana", edad = 19 }

-- Asignaciones simples: variable, índice y campo
promedio = promedio + 1
notas[1] = 95
persona.edad = 20

-- Condicional
if promedio >= 90 then
    print("Sobresaliente")
elseif promedio >= NOTA_MINIMA and not retirado then
    print("Aprobado")
else
    print("Reprobado")
end

-- Ciclo while: suma las notas
local i = 1
local total = 0
while i <= 4 do
    total = total + notas[i]
    i = i + 1
end

-- Ciclo repeat: cuenta hasta 3
local intentos = 0
repeat
    intentos = intentos + 1
until intentos >= 3

-- Ciclo for numérico
for k = 1, 10, 2 do
    print(k)
end

-- Función con parámetros y retorno
function estado(nota)
    if nota >= NOTA_MINIMA then
        return "ok"
    end
    return "reprobado"
end

local numero_combinado = 12abc

print(nombre, apellido, estado(promedio), total, intentos, hexa, grande, materias, persona.nombre)