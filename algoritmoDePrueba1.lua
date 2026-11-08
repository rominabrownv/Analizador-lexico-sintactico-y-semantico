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