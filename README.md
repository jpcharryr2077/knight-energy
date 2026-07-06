# ♞ Knight Energy

Proyecto 2 — Inteligencia Artificial  
Universidad del Valle · Escuela de Ingeniería de Sistemas y Computación

## Descripción

**Knight Energy** es un juego de dos adversarios (humano vs. máquina) donde cada uno controla un caballo sobre un tablero de ajedrez de 8×8. El objetivo es acumular la mayor cantidad de puntos recogiendo casillas especiales mientras se administra la energía disponible.

### Reglas principales

- Cada jugador inicia con **7 unidades de energía**.
- Cada movimiento cuesta **1 unidad de energía**.
- El tablero contiene:
  - 7 casillas de puntos (★) con valores: 2, 3, 4, 5, 6, 8, 9.
  - 4 casillas de energía (⚡) con valores: 2, 3, 4, 5.
- Si un jugador no tiene energía para moverse, **pierde el turno y se le descuentan 3 puntos**.
- El juego termina cuando no quedan casillas de puntos o ningún jugador puede moverse.
- Gana quien acumule más puntos.

### IA: Minimax con poda Alfa-Beta

La máquina usa un árbol minimax con decisiones imperfectas. La profundidad depende del nivel de dificultad:

| Nivel       | Profundidad |
|-------------|-------------|
| Principiante | 2          |
| Amateur      | 4          |
| Experto      | 6          |

## Requisitos

- Python 3.10+
- No se requieren dependencias externas (solo biblioteca estándar)

## Ejecución

```bash
python main.py
```

## Estructura del proyecto

```
knight_energy/
├── main.py               # Punto de entrada
├── game/
│   ├── board.py          # Tablero y casillas
│   ├── knight.py         # Movimientos del caballo
│   ├── game_state.py     # Estado del juego
│   └── game_engine.py    # Motor principal
├── ai/
│   ├── minimax.py        # Algoritmo minimax con alfa-beta
│   └── heuristic.py      # Función de utilidad heurística
├── ui/
│   └── display.py        # Visualización en terminal
├── tests/
│   └── test_board.py     # Pruebas unitarias
└── informe/
    └── informe_heuristica.md
```

## Autores

Proyecto académico — Ficha 3336052  
Análisis y Desarrollo de Software · Universidad del Valle
