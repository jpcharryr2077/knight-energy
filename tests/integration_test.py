"""
integration_test.py
Pruebas de integración módulo a módulo — Knight Energy.

Verifica contratos internos entre capas:
  Board ↔ GameState ↔ Knight ↔ Minimax ↔ Heuristic

Uso:
    python tests/integration_test.py
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.board import Board, StarCell, EnergyCell, EmptyCell
from game.game_state import GameState
from game.knight import get_valid_moves, KNIGHT_MOVES
from ai.minimax import MinimaxAI
from ai.heuristic import evaluate

GREEN = "\033[1;32m"; RED = "\033[1;31m"; RESET = "\033[0m"

results = []

def check(name: str, condition: bool, detail: str = ""):
    ok = "✓" if condition else "✗"
    color = GREEN if condition else RED
    msg = f"  {color}{ok}{RESET}  {name}"
    if detail and not condition:
        msg += f"  →  {RED}{detail}{RESET}"
    print(msg)
    results.append(condition)


# ── Board ─────────────────────────────────────────────────────────────────────
print("\n── Board ─────────────────────────────────────────────")

random.seed(0)
b = Board()

check("7 casillas ★ en el tablero",
      len(b.star_cells) == 7,
      f"encontradas: {len(b.star_cells)}")

check("4 casillas ⚡ en el tablero",
      len(b.energy_cells) == 4,
      f"encontradas: {len(b.energy_cells)}")

check("Valores ★ son {2,3,4,5,6,8,9}",
      set(c.value for c in b.star_cells.values()) == {2,3,4,5,6,8,9})

check("Valores ⚡ son {2,3,4,5}",
      set(c.value for c in b.energy_cells.values()) == {2,3,4,5})

pos0, pos1 = b.knight_positions[0], b.knight_positions[1]
check("Caballos en posiciones distintas", pos0 != pos1)
check("Caballos no coinciden con ★ ni ⚡",
      pos0 not in b.star_cells and pos0 not in b.energy_cells and
      pos1 not in b.star_cells and pos1 not in b.energy_cells)

# Mover a casilla vacía
empty_pos = next(
    (r, c)
    for r in range(8) for c in range(8)
    if (r,c) not in [pos0, pos1]
    and (r,c) not in b.star_cells
    and (r,c) not in b.energy_cells
)
b2 = b.copy()
pts, nrg = b2.move_knight(0, empty_pos)
check("Mover a casilla vacía → 0 pts, 0 energía", pts == 0 and nrg == 0)
check("Posición actualizada tras move_knight",
      b2.knight_positions[0] == empty_pos)

# Mover a casilla ★
random.seed(1)
b3 = Board()
star_pos, star_cell = next(iter(b3.star_cells.items()))
# Forzar caballo 0 a una posición adyacente (o directamente al destino)
b3.knight_positions[0] = (0,0)
pts3, _ = b3.move_knight(0, star_pos)
check("Capturar ★ retorna su valor", pts3 == star_cell.value,
      f"esperado {star_cell.value}, obtenido {pts3}")
check("★ eliminada del tablero tras captura", star_pos not in b3.star_cells)

# ── GameState ─────────────────────────────────────────────────────────────────
print("\n── GameState ──────────────────────────────────────────")

random.seed(2)
gs = GameState()

check("Turno inicial = 0 (Máquina)",     gs.current_turn == 0)
check("Energía inicial Máquina = 7",     gs.players[0].energy == 7)
check("Energía inicial Humano  = 7",     gs.players[1].energy == 7)
check("Puntos iniciales = 0",
      gs.players[0].points == 0 and gs.players[1].points == 0)
check("Estado no terminal al inicio",    not gs.is_terminal())

# apply_move
moves = get_valid_moves(gs.board, 0)
if moves:
    nrg_before = gs.players[0].energy
    summary    = gs.apply_move(moves[0])
    check("apply_move descuenta 1 energía",
          gs.players[0].energy == summary["energy_after"])
    check("Turno avanza a 1 tras apply_move",  gs.current_turn == 1)
    check("turn_number incrementa",            gs.turn_number == 2)

# apply_skip
random.seed(3)
gs2 = GameState()
gs2.players[0].energy = 0
pts_before = gs2.players[0].points
gs2.apply_skip()
check("apply_skip resta 3 pts",
      gs2.players[0].points == pts_before - 3,
      f"esperado {pts_before - 3}, obtenido {gs2.players[0].points}")
check("Turno avanza tras apply_skip",  gs2.current_turn == 1)

# copy() independiente
random.seed(4)
gs3  = GameState()
gs3c = gs3.copy()
if get_valid_moves(gs3.board, 0):
    gs3.apply_move(get_valid_moves(gs3.board, 0)[0])
check("copy() — original y copia son independientes",
      gs3.turn_number != gs3c.turn_number or
      gs3.board.knight_positions[0] != gs3c.board.knight_positions[0])

# ── Knight ────────────────────────────────────────────────────────────────────
print("\n── Knight ─────────────────────────────────────────────")

random.seed(5)
b4 = Board()
# Caballo en centro del tablero → debe tener exactamente 8 - bloqueos
from game.board import BOARD_SIZE
b4.knight_positions[0] = (4, 4)
b4.knight_positions[1] = (0, 0)   # Lejos
moves_center = get_valid_moves(b4, 0)
expected = [(4+dr, 4+dc) for dr,dc in KNIGHT_MOVES
            if 0 <= 4+dr < 8 and 0 <= 4+dc < 8 and (4+dr, 4+dc) != (0,0)]
check("Caballo en (4,4) tiene movimientos correctos",
      set(moves_center) == set(expected),
      f"obtenido {moves_center}")

# Caballo en esquina → máximo 2 movimientos
b4.knight_positions[0] = (0, 0)
b4.knight_positions[1] = (7, 7)
moves_corner = get_valid_moves(b4, 0)
check("Caballo en esquina (0,0) tiene ≤ 2 movimientos",
      len(moves_corner) <= 2,
      f"obtenido {len(moves_corner)}: {moves_corner}")

# No puede moverse sobre el otro caballo
b4.knight_positions[0] = (0, 0)
b4.knight_positions[1] = (1, 2)   # Exactamente en L desde (0,0)
moves_blocked = get_valid_moves(b4, 0)
check("No puede moverse sobre el otro caballo",
      (1, 2) not in moves_blocked)

# ── Heurística ────────────────────────────────────────────────────────────────
print("\n── Heurística ─────────────────────────────────────────")

random.seed(6)
hs = GameState()
val_neutral = evaluate(hs)
check("Estado inicial es aproximadamente neutro",
      abs(val_neutral) < 100,
      f"valor={val_neutral}")

# Máquina con más puntos → heurística positiva
hs2 = GameState()
hs2.players[0].points = 20
hs2.players[1].points = 5
check("Máquina con más puntos → h > 0",
      evaluate(hs2) > 0,
      f"h={evaluate(hs2)}")

# Humano con más puntos → heurística negativa
hs3 = GameState()
hs3.players[0].points = 5
hs3.players[1].points = 20
check("Humano con más puntos → h < 0",
      evaluate(hs3) < 0,
      f"h={evaluate(hs3)}")

# Estado terminal
hs4 = GameState()
hs4.game_over = True
hs4.winner = 0
check("Terminal Máquina gana → h = +inf",  evaluate(hs4) == float("inf"))
hs4.winner = 1
check("Terminal Humano gana → h = -inf",   evaluate(hs4) == float("-inf"))
hs4.winner = None
check("Terminal empate → h = 0",           evaluate(hs4) == 0.0)

# ── Minimax ───────────────────────────────────────────────────────────────────
print("\n── Minimax ────────────────────────────────────────────")

random.seed(7)
ms = GameState()
ai2 = MinimaxAI(depth=2)
move = ai2.choose_move(ms)
check("choose_move retorna una tupla válida",
      isinstance(move, tuple) and len(move) == 2)
check("Movimiento está dentro del tablero",
      move is None or (0 <= move[0] <= 7 and 0 <= move[1] <= 7))
check("Movimiento está en la lista de válidos",
      move in get_valid_moves(ms.board, 0))

stats = ai2.get_stats()
check("Nodos evaluados > 0",    stats["nodes_evaluated"] > 0)
check("Nodos podados ≥ 0",      stats["nodes_pruned"]   >= 0)

# Minimax prefiere capturar estrella de alto valor sobre no hacer nada
random.seed(8)
ms2 = GameState()
# Colocar una estrella de valor 9 adyacente al caballo blanco
from game.board import StarCell as SC
knight_pos = ms2.board.knight_positions[0]
other_pos  = ms2.board.knight_positions[1]
# Encontrar un destino en L desde knight_pos que no sea el otro caballo
for dr, dc in KNIGHT_MOVES:
    nr, nc = knight_pos[0]+dr, knight_pos[1]+dc
    if 0<=nr<8 and 0<=nc<8 and (nr,nc) != other_pos:
        # Limpiar esa casilla y poner estrella 9
        from game.board import EmptyCell
        ms2.board.grid[nr][nc] = SC(9)
        ms2.board.star_cells[(nr,nc)] = ms2.board.grid[nr][nc]
        target = (nr, nc)
        break

ai3   = MinimaxAI(depth=2)
move3 = ai3.choose_move(ms2)
check("Minimax elige capturar estrella de valor 9 adyacente",
      move3 == target,
      f"esperado {target}, elegido {move3}")

# ── Resumen ───────────────────────────────────────────────────────────────────
print("\n" + "═" * 54)
passed = sum(results)
total  = len(results)
color  = GREEN if passed == total else RED
print(f"  {color}Resultado: {passed}/{total} verificaciones pasaron{RESET}")
print("═" * 54 + "\n")

sys.exit(0 if passed == total else 1)
