"""
minimax.py
Algoritmo Minimax con poda Alfa-Beta para Knight Energy.

Arquitectura
────────────
  - La MÁQUINA es el jugador MAX (player_id = 0).
  - El HUMANO  es el jugador MIN (player_id = 1).
  - La profundidad límite depende del nivel de dificultad:
      principiante → 2 | amateur → 4 | experto → 6
  - En cada nodo hoja (profundidad 0 o estado terminal) se
    invoca la función heurística de heuristic.py.
  - La poda alfa-beta elimina ramas que no pueden influir en
    la decisión final, reduciendo el árbol sin perder optimidad.

Decisiones imperfectas
───────────────────────
  Al alcanzar la profundidad límite sin llegar a un estado
  terminal real, el nodo se evalúa con h(s) en lugar de un
  valor exacto. Esto introduce "imperfección" controlada que
  hace el juego manejable computacionalmente.
"""

from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_state import GameState

from game.knight import get_valid_moves, has_moves
from ai.heuristic import evaluate


# ── Constantes ────────────────────────────────────────────────────────────────

INF = math.inf


# ── Clase principal ───────────────────────────────────────────────────────────

class MinimaxAI:
    """
    Agente IA basado en Minimax con poda Alfa-Beta.

    Parámetros
    ----------
    depth : int — profundidad máxima del árbol de búsqueda.
    """

    def __init__(self, depth: int):
        if depth < 1:
            raise ValueError("La profundidad debe ser al menos 1.")
        self.depth = depth
        # Estadísticas de la última búsqueda (útil para depuración)
        self.nodes_evaluated: int = 0
        self.nodes_pruned:    int = 0

    # ── API pública ───────────────────────────────────────────────────────────

    def choose_move(self, state: "GameState") -> tuple[int, int] | None:
        """
        Elige el mejor movimiento para la máquina (MAX) dado el estado actual.

        Retorna la posición (fila, col) elegida, o None si no hay movimientos.
        """
        self.nodes_evaluated = 0
        self.nodes_pruned    = 0

        best_move  = None
        best_value = -INF
        alpha      = -INF
        beta       = +INF

        moves = get_valid_moves(state.board, 0)

        if not moves:
            return None

        # Ordenar movimientos: primero los que caen en casillas especiales
        # (mejora la poda al explorar ramas prometedoras antes)
        moves = _order_moves(state, moves, player=0)

        for move in moves:
            child = state.copy()
            child.apply_move(move)

            value = self._minimax(
                state    = child,
                depth    = self.depth - 1,
                alpha    = alpha,
                beta     = beta,
                is_max   = False,   # siguiente turno es el humano (MIN)
            )

            if value > best_value:
                best_value = value
                best_move  = move

            alpha = max(alpha, best_value)
            # No hay poda aquí porque evaluamos todos los hijos de la raíz
            # para poder comparar y elegir el mejor movimiento.

        return best_move

    def get_stats(self) -> dict:
        """Estadísticas de la última búsqueda."""
        return {
            "nodes_evaluated": self.nodes_evaluated,
            "nodes_pruned":    self.nodes_pruned,
        }

    # ── Núcleo recursivo ──────────────────────────────────────────────────────

    def _minimax(
        self,
        state:  "GameState",
        depth:  int,
        alpha:  float,
        beta:   float,
        is_max: bool,
    ) -> float:
        """
        Minimax recursivo con poda Alfa-Beta.

        Parámetros
        ----------
        state  : estado actual del juego.
        depth  : niveles restantes de búsqueda.
        alpha  : mejor valor garantizado para MAX hasta ahora.
        beta   : mejor valor garantizado para MIN hasta ahora.
        is_max : True si es turno de MAX (máquina), False si es MIN (humano).

        Retorna
        -------
        float — valor minimax del nodo.
        """
        # ── Caso base 1: estado terminal real ────────────────────────────────
        if state.game_over:
            self.nodes_evaluated += 1
            return evaluate(state)

        # ── Caso base 2: profundidad límite → heurística ─────────────────────
        if depth == 0:
            self.nodes_evaluated += 1
            return evaluate(state)

        player_id = 0 if is_max else 1
        player    = state.players[player_id]

        # ── Sin movimientos posibles en el tablero ────────────────────────────
        if not has_moves(state.board, player_id):
            # Jugador bloqueado: skip (con o sin penalización según energía)
            child = state.copy()
            if not player.can_move():
                child.apply_skip()           # −3 pts, avanza turno
            else:
                # Bloqueado geográficamente pero con energía: skip sin penalización
                child.turn_number  += 1
                child.current_turn  = 1 - child.current_turn
                if child.is_terminal():
                    child._resolve_winner()
            return self._minimax(child, depth - 1, alpha, beta, not is_max)

        # ── Sin energía (pero hay casillas alcanzables) ───────────────────────
        if not player.can_move():
            child = state.copy()
            child.apply_skip()
            return self._minimax(child, depth - 1, alpha, beta, not is_max)

        # ── Nodo MAX (turno de la máquina) ────────────────────────────────────
        if is_max:
            return self._max_value(state, depth, alpha, beta)

        # ── Nodo MIN (turno del humano) ───────────────────────────────────────
        return self._min_value(state, depth, alpha, beta)

    # ── MAX ───────────────────────────────────────────────────────────────────

    def _max_value(
        self,
        state: "GameState",
        depth: int,
        alpha: float,
        beta:  float,
    ) -> float:
        value = -INF
        moves = _order_moves(state, get_valid_moves(state.board, 0), player=0)

        for move in moves:
            child = state.copy()
            child.apply_move(move)

            child_value = self._minimax(child, depth - 1, alpha, beta, is_max=False)
            value       = max(value, child_value)
            alpha       = max(alpha, value)

            # Poda beta: el nodo MIN padre nunca elegirá este camino
            if value >= beta:
                self.nodes_pruned += 1
                return value

        return value

    # ── MIN ───────────────────────────────────────────────────────────────────

    def _min_value(
        self,
        state: "GameState",
        depth: int,
        alpha: float,
        beta:  float,
    ) -> float:
        value = +INF
        moves = _order_moves(state, get_valid_moves(state.board, 1), player=1)

        for move in moves:
            child = state.copy()
            child.apply_move(move)

            child_value = self._minimax(child, depth - 1, alpha, beta, is_max=True)
            value       = min(value, child_value)
            beta        = min(beta, value)

            # Poda alfa: el nodo MAX padre nunca elegirá este camino
            if value <= alpha:
                self.nodes_pruned += 1
                return value

        return value


# ── Ordenamiento de movimientos ───────────────────────────────────────────────

def _order_moves(
    state:   "GameState",
    moves:   list[tuple[int, int]],
    player:  int,
) -> list[tuple[int, int]]:
    """
    Ordena los movimientos para mejorar la eficiencia de la poda alfa-beta.

    Estrategia de ordenamiento (mayor prioridad primero):
      1. Movimientos que capturan una casilla ★ (bonus = valor de la estrella)
      2. Movimientos que capturan una casilla ⚡ (bonus = valor de energía)
      3. Resto de movimientos (bonus = 0)

    Un buen ordenamiento puede reducir el árbol explorado hasta en un 50 %.
    """
    from game.board import StarCell, EnergyCell

    def move_priority(pos: tuple[int, int]) -> float:
        cell = state.board.grid[pos[0]][pos[1]]
        if isinstance(cell, StarCell):
            return 100 + cell.value   # Prioridad máxima + valor de la estrella
        if isinstance(cell, EnergyCell):
            return 50  + cell.value   # Prioridad media
        return 0

    # MAX quiere explorar primero los movimientos de mayor valor
    # MIN también, porque ordenar bien beneficia la poda en ambos sentidos
    return sorted(moves, key=move_priority, reverse=True)
