# Informe: Función de Utilidad Heurística — Knight Energy

**Universidad del Valle**  
Escuela de Ingeniería de Sistemas y Computación  
Inteligencia Artificial — Proyecto 2

---

## 1. Introducción

El algoritmo **Minimax con decisiones imperfectas** requiere una función de evaluación
heurística para valorar estados no terminales del juego. Sin esta función, el árbol
solo podría valorar estados finales (victoria, derrota o empate), lo cual es inviable
dada la profundidad limitada del árbol (2, 4 o 6 niveles según la dificultad).

La función heurística `h(s)` asigna un valor numérico a cada estado `s` del juego
desde la perspectiva de la **máquina (jugador MAX)**:

- Un valor **positivo** indica que el estado es favorable para la máquina.
- Un valor **negativo** indica que el estado es favorable para el humano (jugador MIN).
- Un valor de **±∞** corresponde a un estado terminal (victoria o derrota definitiva).

---

## 2. Definición formal de la función heurística

```
h(s) = w₁·ΔPuntos(s)
     + w₂·ΔEnergía(s)
     + w₃·ΔEstrellas_alcanzables(s)
     + w₄·ΔEnergía_alcanzable(s)
     + w₅·ΔMovilidad(s)
     + w₆·Bonus_terminal(s)
```

Donde `Δ(s) = valor_máquina(s) − valor_humano(s)` para cada componente.

### Valores de los pesos

| Peso | Valor | Componente                        |
|------|-------|-----------------------------------|
| w₁   | 10.0  | Diferencia de puntos acumulados   |
| w₂   |  2.0  | Diferencia de energía disponible  |
| w₃   |  4.0  | Estrellas ★ alcanzables en 1 salto|
| w₄   |  1.5  | Energía ⚡ alcanzable en 1 salto  |
| w₅   |  0.8  | Diferencia de movilidad total     |
| w₆   | 50.0  | Bonus/penalización por estado crítico |

---

## 3. Justificación de cada componente

### 3.1 · ΔPuntos — peso w₁ = 10.0

```
ΔPuntos(s) = puntos_máquina − puntos_humano
```

La diferencia de puntos es el **indicador directo del objetivo del juego**. Un valor
alto de `w₁` garantiza que la IA priorice siempre maximizar su ventaja en puntuación
por encima de cualquier consideración secundaria. Es el componente de mayor peso.

**Ejemplo:** Si la máquina tiene 8 pts y el humano 3 pts → contribución = 10 × 5 = +50.

---

### 3.2 · ΔEnergía — peso w₂ = 2.0

```
ΔEnergía(s) = energía_máquina − energía_humano
```

La energía determina cuántos movimientos futuros puede realizar cada jugador. Un
jugador con más energía tiene **mayor horizonte de acción**, puede planificar más
turnos y evita la penalización de −3 puntos por turno perdido. Se pondera menos que
los puntos porque la energía es un medio, no un fin.

**Ejemplo:** Máquina con 5 de energía vs humano con 2 → contribución = 2 × 3 = +6.

---

### 3.3 · ΔEstrellas_alcanzables — peso w₃ = 4.0

```
ΔEstrellas_alcanzables(s) = |★ a 1 salto de máquina| − |★ a 1 salto de humano|
```

Cuenta cuántas casillas de puntos (★) puede capturar cada jugador en su **próximo
movimiento**. Este componente permite a la IA anticipar capturas inmediatas, que son
la única fuente de puntuación. Se pondera con valor medio-alto porque tener acceso
a estrellas cercanas es una ventaja táctica directa.

Una casilla ★ con valor alto (8 o 9) alcanzable en el siguiente turno representa
una ventaja significativa que la heurística debe detectar.

**Ejemplo:** Máquina puede alcanzar 2 estrellas, humano solo 1 → contribución = 4 × 1 = +4.

---

### 3.4 · ΔEnergía_alcanzable — peso w₄ = 1.5

```
ΔEnergía_alcanzable(s) = |⚡ a 1 salto de máquina| − |⚡ a 1 salto de humano|
```

Casillas de energía (⚡) alcanzables en el siguiente movimiento. La recarga de energía
es crucial para mantener la capacidad de juego, especialmente en etapas avanzadas
donde la energía escasea. Se pondera ligeramente por debajo de las estrellas ya que
la energía es instrumental, no directamente puntuable.

---

### 3.5 · ΔMovilidad — peso w₅ = 0.8

```
ΔMovilidad(s) = movimientos_válidos_máquina − movimientos_válidos_humano
```

Mide la **libertad de movimiento** de cada jugador en la posición actual. Una mayor
movilidad implica más opciones estratégicas y menor riesgo de quedar bloqueado. El
peso bajo refleja que la movilidad es un factor de largo plazo, menos urgente que
los puntos o la energía inmediata.

---

### 3.6 · Bonus_terminal — peso w₆ = 50.0

```
Bonus_terminal(s) ∈ {−1.0, −0.3, 0.0, +0.3, +1.0}
```

Este componente detecta **situaciones críticas** que el árbol Minimax podría no
anticipar correctamente a profundidades bajas:

| Situación                              | Bonus     |
|----------------------------------------|-----------|
| Máquina sin movimientos o sin energía  | −1.0      |
| Máquina con solo 1 de energía          | −0.3      |
| Situación neutral                      |  0.0      |
| Humano con solo 1 de energía           | +0.3      |
| Humano sin movimientos o sin energía   | +1.0      |

El peso de 50.0 es elevado para que la IA **evite activamente** llegar a estados
donde pierde el turno (penalización de −3 pts), lo cual sería particularmente
perjudicial.

---

## 4. Casos especiales

### Estado terminal real

Si `state.game_over == True`, la función retorna valores extremos:

```python
+∞   si ganó la máquina
-∞   si ganó el humano
 0   si hubo empate
```

Esto garantiza que el Minimax siempre prefiera una victoria real sobre cualquier
evaluación heurística positiva.

### Energía negativa

La penalización de −3 puntos por turno perdido puede hacer que los puntos sean
negativos. La heurística maneja correctamente valores negativos de puntos ya que
trabaja con diferencias.

---

## 5. Ejemplo de evaluación

Dado el siguiente estado hipotético:

| Atributo                     | Máquina | Humano |
|------------------------------|---------|--------|
| Puntos acumulados            | 11      | 6      |
| Energía disponible           | 4       | 2      |
| ★ alcanzables (1 salto)      | 2       | 0      |
| ⚡ alcanzables (1 salto)     | 1       | 1      |
| Movimientos válidos          | 5       | 3      |

```
h(s) = 10.0 × (11−6)  →  +50.0
     +  2.0 × (4−2)   →   +4.0
     +  4.0 × (2−0)   →   +8.0
     +  1.5 × (1−1)   →    0.0
     +  0.8 × (5−3)   →   +1.6
     + 50.0 × 0.0     →    0.0
     ─────────────────────────
                           +63.6  (favorable para la máquina)
```

---

## 6. Integración con Minimax

La función `evaluate(state)` es invocada por el algoritmo Minimax en dos casos:

1. Cuando se alcanza la **profundidad límite** del árbol (2, 4 o 6).
2. Cuando el estado es **terminal** (fin de juego real).

En nodos MAX (turno de la máquina) se busca **maximizar** `h(s)`.  
En nodos MIN (turno del humano) se busca **minimizar** `h(s)`.

La poda alfa-beta no afecta la función heurística sino únicamente cuáles nodos
se evalúan, reduciendo el costo computacional sin alterar la decisión óptima.

---

## 7. Conclusiones

La función heurística diseñada combina cinco dimensiones del estado del juego:

- **Puntuación** (objetivo directo)
- **Energía** (capacidad de acción futura)
- **Alcanzabilidad inmediata** de estrellas y recargas (táctica a corto plazo)
- **Movilidad** (flexibilidad estratégica)
- **Estado crítico** (anticipación de penalizaciones)

La jerarquía de pesos refleja la importancia relativa de cada factor: los puntos
son lo más importante (w₁ = 10), seguido de la anticipación de estados críticos
(w₆ = 50, pero su bonus ∈ [−1, 1] limita su influencia), las estrellas alcanzables
(w₃ = 4), la energía (w₂ = 2), la energía alcanzable (w₄ = 1.5) y la movilidad
(w₅ = 0.8).

