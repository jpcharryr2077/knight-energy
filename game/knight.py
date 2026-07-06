"""
knight.py
Lógica de movimientos del caballo.

El caballo se mueve en L siguiendo las reglas del ajedrez:
los 8 posibles desplazamientos (±1,±2) y (±2,±1).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.board import Board

# Los 8 deltas de movimiento válidos para un caballo de ajedrez
KNIGHT_MOVES = [
    (-2, -1), (-2, +1),
    (-1, -2), (-1, +2),
    (+1, -2), (+1, +2),
    (+2, -1), (+2, +1),
]


def get_valid_moves(board: "Board", player: int) -> list[tuple[int, int]]:
    """
    Devuelve todas las posiciones válidas a las que puede moverse
    el caballo del jugador dado desde su posición actual.

    Una posición es válida si:
    - Está dentro de los límites del tablero (0-7, 0-7).
    - No está ocupada por el otro caballo.

    Parámetros
    ----------
    board  : Board  — estado actual del tablero.
    player : int    — 0 = máquina, 1 = humano.

    Retorna
    -------
    list[tuple[int,int]] — lista de (fila, columna) alcanzables.
    """
    row, col = board.knight_positions[player]
    other_pos = board.knight_positions[1 - player]
    moves = []

    for dr, dc in KNIGHT_MOVES:
        new_row, new_col = row + dr, col + dc
        if not board.is_within_bounds(new_row, new_col):
            continue
        if (new_row, new_col) == other_pos:
            continue          # No se puede caer sobre el otro caballo
        moves.append((new_row, new_col))

    return moves


def has_moves(board: "Board", player: int) -> bool:
    """Indica si el jugador tiene al menos un movimiento disponible."""
    return len(get_valid_moves(board, player)) > 0
