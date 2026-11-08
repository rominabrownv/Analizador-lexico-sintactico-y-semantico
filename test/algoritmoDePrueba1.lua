-- Algoritmo 1: factorial, fibonacci y numeros primos

local function factorial(n)
  if n < 0 then
    return nil
  elseif n == 0 or n == 1 then
    return 1
  end
  local resultado = 1
  for i = 2, n do
    resultado = resultado * i
  end
  return resultado
end

local function fibonacci(n)
  local a, b = 0, 1
  local i = 0
  while i < n do
    a, b = b, a + b
    i = i + 1
  end
  return a
end

local function es_primo(n)
  if n < 2 then
    return false
  end
  local d = 2
  while d * d <= n do
    if n % d == 0 then
      return false
    end
    d = d + 1
  end
  return true
end

for k = 1, 10 do
  print("fib(" .. k .. ") = " .. fibonacci(k))
end
print("10! = " .. factorial(10))

local primos = {}
local compuestos = 0
for n = 1, 30 do
  if es_primo(n) and not (n == 1) then
    primos[#primos + 1] = n
  else
    compuestos = compuestos + 1
  end
end
print("primos: " .. table.concat(primos, ", "))
print("no primos: " .. compuestos)

-- primer primo mayor que 100
local candidato = 100
while true do
  candidato = candidato + 1
  if es_primo(candidato) then
    break
  end
end
print("primer primo > 100: " .. candidato)

local enteros = { 0, 7, 42, 1000000, 9223372036854775807 }
local hexa = { 0xFF, 0x10, 0xdeadBEEF, 0XA }
local flotantes = { 3.14, .5, 5., 0.1e2, 6.02E23, 1e-9, 2E+3 }
local grande = 9223372036854775808
 
local function suma(...)
  local total = 0
  for _, v in ipairs({...}) do
    total = total + v
  end
  return total
end

-- Algoritmo 2: cadenas, repeat-until, goto y global (Lua 5.5)
 
do
  global contador, mensaje
  contador = 0
  mensaje = "Hola desde una variable global"
end
 
local function saludar(nombre)
  return "Hola, " .. nombre .. "!"
end
 
local texto = 'Lua 5.5: \"literales\" con tab \t y barra \\'
local largo = [[
Cadena larga
con varias lineas]]
local vacia = ""
 
print(texto)
print(largo)
print(#vacia == 0)
 
-- repeat-until con goto como "continue"
local i = 0
repeat
  i = i + 1
  if i % 2 == 0 then
    goto siguiente
  end
  print("impar: " .. i)
  ::siguiente::
until i >= 7
 
-- recorrer palabras de una cadena
for palabra in string.gmatch(largo, "%a+") do
  print(palabra, string.upper(palabra), #palabra)
end
 
local activo = true
local oculto = false
if activo and not oculto then
  print(saludar("Lua"))
end
 
print(suma(table.unpack(enteros)))
print(suma(table.unpack(hexa)))
print(7 // 2, 7 % 3, 2 ^ 10, 7 / 2)
print(5 & 3, 5 | 3, 5 ~ 3, ~5, 1 << 4, 256 >> 4)
print(grande, math.type(grande), math.type(7), math.type(3.14))
 
local mayor = nil
for _, lista in ipairs({ enteros, hexa, flotantes }) do
  for _, valor in ipairs(lista) do
    if mayor == nil or valor > mayor then
      mayor = valor
    end
  end
end
print("mayor:", mayor)

pint({Hola})
local numeroX = 3#x

-- Algoritmo con errores lexicos (para probar que el analizador los detecta)
 
local total = 0
 
-- ERROR: numeros mal formados
local a = 3x
local b = 0xG
local c = 1e
local d = 12abc
 
-- ERROR: caracteres que Lua no reconoce
local e = 10 @ 5
local f = $precio
local g = 8 ? 2
local h = !valor
 
-- ERROR: cadena sin cerrar
local mensaje = "hola mundo
 

local ok = 0xFF + 1e-9 + 42
print("termino", ok)
 
-- ERROR: comentario largo sin cerrar (debe ir al final, se come el resto)
--[[ este comentario nunca se cierra
local z = 1