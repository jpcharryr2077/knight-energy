"""
heuristic.py
Función de utilidad heurística para el árbol Minimax.

La función evalúa un estado del juego desde la perspectiva de la máquina
(jugador 0 = MAX). Un valor positivo favorece a la máquina; negativo, al humano.

Componentes de la heurística
─────────────────────────────
  h(s) = w1·ΔPuntos
       + w2·ΔEnergía
       + w3·ΔEstrellas_alcanzables
       + w4·ΔEnergía_alcanzable
       + w5·Bonus_terminal

Donde Δ = (valor_máquina − valor_humano).

Justificación de cada componente
──────────────────────────────────
  w1·ΔPuntos            → Diferencia de puntuación acumulada: objetivo directo del juego.
  w2·ΔEnergía           → Ventaja de energía: más energía = más movimientos futuros posibles.
  w3·ΔEstrellas_alc.    → Número de casillas ★ inmediatamente alcanzables (1 salto) por
                           cada jugador. Capturar estrellas es la única forma de ganar puntos.
  w4·ΔEnergía_alc.      → Casillas ⚡ alcanzables en 1 salto: anticipar recarga futura.
  w5·Bonus_terminal     → Penalización/bonus por estados casi terminales: si la máquina
                           está a punto de quedarse sin movimientos, penaliza fuerte.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_state import GameState

from game.board import StarCell, EnergyCell
from game.knight import KNIGHT_MOVES

# ── Pesos de la función heurística ───────────────────────────────────────────
# Ajustados empíricamente para balancear exploración y explotación.

W_POINTS          = 10.0   # Diferencia de puntos acumulados (objetivo primario)
W_ENERGY          = 2.0    # Diferencia de energía disponible
W_STARS_REACHABLE = 4.0    # Diferencia de estrellas alcanzables en 1 salto
W_ENERGY_REACHABLE= 1.5    # Diferencia de energía alcanzable en 1 salto
W_MOBILITY        = 0.8    # Diferencia de movilidad total (nº de movimientos válidos)
W_TERMINAL_BONUS  = 50.0   # Bonus/penalización por estados casi terminales


def evaluate(state: "GameState") -> float:
    """
    Evalúa el estado actual desde la perspectiva de la máquina (MAX).

    Parámetros
    ----------
    state : GameState — estado a evaluar.

    Retorna
    -------
    float — puntuación heurística.
             +inf → victoria segura de la máquina.
             -inf → victoria segura del humano.
    """
    # ── Estado terminal real ─────────────────────────────────────────────────
    if state.game_over:
        if state.winner == 0:
            return float("inf")
        elif state.winner == 1:
            return float("-inf")
        else:
            return 0.0

    machine = state.players[0]
    human   = state.players[1]

    # ── Componente 1: Diferencia de puntos ───────────────────────────────────
    delta_points = machine.points - human.points

    # ── Componente 2: Diferencia de energía ──────────────────────────────────
    delta_energy = machine.energy - human.energy

    # ── Componentes 3 y 4: Casillas alcanzables en 1 salto ───────────────────
    machine_stars, machine_energy_cells = _reachable_specials(state, player=0)
    human_stars,   human_energy_cells   = _reachable_specials(state, player=1)

    delta_stars_reachable  = machine_stars        - human_stars
    delta_energy_reachable = machine_energy_cells - human_energy_cells

    # ── Componente 5: Movilidad ───────────────────────────────────────────────
    machine_moves = _count_valid_moves(state, player=0)
    human_moves   = _count_valid_moves(state, player=1)
    delta_mobility = machine_moves - human_moves

    # ── Componente 6: Bonus/penalización por estado casi terminal ─────────────
    terminal_bonus = _terminal_bonus(state, machine_moves, human_moves)

    # ── Función final ────────────────────────────────────────────────────────
    score = (
        W_POINTS           * delta_points
      + W_ENERGY           * delta_energy
      + W_STARS_REACHABLE  * delta_stars_reachable
      + W_ENERGY_REACHABLE * delta_energy_reachable
      + W_MOBILITY         * delta_mobility
      + W_TERMINAL_BONUS   * terminal_bonus
    )

    return score


# ── Funciones auxiliares ──────────────────────────────────────────────────────

def _reachable_specials(state: "GameState", player: int) -> tuple[int, int]:
    """
    Cuenta cuántas casillas ★ y ⚡ puede alcanzar el jugador en exactamente 1 salto.

    Retorna (num_estrellas_alcanzables, num_energía_alcanzable).
    """
    row, col   = state.board.knight_positions[player]
    other_pos  = state.board.knight_positions[1 - player]
    stars      = 0
    energies   = 0

    for dr, dc in KNIGHT_MOVES:
        nr, nc = row + dr, col + dc
        if not (0 <= nr < 8 and 0 <= nc < 8):
            continue
        if (nr, nc) == other_pos:
            continue
        cell = state.board.grid[nr][nc]
        if isinstance(cell, StarCell):
            stars += 1
        elif isinstance(cell, EnergyCell):
            energies += 1

    return stars, energies


def _count_valid_moves(state: "GameState", player: int) -> int:
    """Cuenta los movimientos válidos disponibles para el jugador."""
    row, col  = state.board.knight_positions[player]
    other_pos = state.board.knight_positions[1 - player]
    count     = 0

    for dr, dc in KNIGHT_MOVES:
        nr, nc = row + dr, col + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and (nr, nc) != other_pos:
            count += 1

    return count


def _terminal_bonus(state: "GameState", machine_moves: int, human_moves: int) -> float:
    """
    Bonus/penalización cuando un jugador está cerca de quedarse sin movimientos
    o sin energía. Esto permite al Minimax anticipar situaciones críticas.

    Retorna un valor entre -1.0 y +1.0 que se multiplica por W_TERMINAL_BONUS.
    """
    machine = state.players[0]
    human   = state.players[1]
    bonus   = 0.0

    # Si la máquina no puede moverse o se queda sin energía → penalización
    if machine_moves == 0 or machine.energy == 0:
        bonus -= 1.0
    elif machine.energy == 1:
        # Último movimiento disponible → pequeña penalización
        bonus -= 0.3

    # Si el humano no puede moverse o se queda sin energía → bonus
    if human_moves == 0 or human.energy == 0:
        bonus += 1.0
    elif human.energy == 1:
        bonus += 0.3

    return bonus


# ── Utilidad de depuración ────────────────────────────────────────────────────

def evaluate_verbose(state: "GameState") -> float:
    """
    Igual que evaluate() pero imprime el desglose de cada componente.
    Útil para depuración y para el informe académico.
    """
    if state.game_over:
        result = evaluate(state)
        print(f"  [Heurística] Estado terminal → {result}")
        return result

    machine = state.players[0]
    human   = state.players[1]

    dp  = machine.points - human.points
    de  = machine.energy - human.energy
    ms, me = _reachable_specials(state, 0)
    hs, he = _reachable_specials(state, 1)
    ds  = ms - hs
    dea = me - he
    mm  = _count_valid_moves(state, 0)
    hm  = _count_valid_moves(state, 1)
    dm  = mm - hm
    tb  = _terminal_bonus(state, mm, hm)

    total = (
        W_POINTS           * dp
      + W_ENERGY           * de
      + W_STARS_REACHABLE  * ds
      + W_ENERGY_REACHABLE * dea
      + W_MOBILITY         * dm
      + W_TERMINAL_BONUS   * tb
    )

    print("  ┌─ Desglose heurístico ────────────────────────────")
    print(f"  │  ΔPuntos            = {dp:>+5}  × {W_POINTS}   = {W_POINTS*dp:>+8.1f}")
    print(f"  │  ΔEnergía           = {de:>+5}  × {W_ENERGY}   = {W_ENERGY*de:>+8.1f}")
    print(f"  │  Δ★ alcanzables     = {ds:>+5}  × {W_STARS_REACHABLE}   = {W_STARS_REACHABLE*ds:>+8.1f}")
    print(f"  │  Δ⚡ alcanzables    = {dea:>+5}  × {W_ENERGY_REACHABLE} = {W_ENERGY_REACHABLE*dea:>+8.1f}")
    print(f"  │  ΔMovilidad         = {dm:>+5}  × {W_MOBILITY} = {W_MOBILITY*dm:>+8.1f}")
    print(f"  │  Bonus terminal     = {tb:>+5.1f}  × {W_TERMINAL_BONUS}  = {W_TERMINAL_BONUS*tb:>+8.1f}")
    print(f"  │                                        {'─'*10}")
    print(f"  │  TOTAL              =                  {total:>+8.1f}")
    print("  └──────────────────────────────────────────────────")

    return total
