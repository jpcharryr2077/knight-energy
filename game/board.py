"""
board.py
Tablero de ajedrez 8x8.

Contiene la definición de las casillas y la clase Board que maneja
la colocación aleatoria de caballos, estrellas y energías.
"""

import random
import copy


# ── Tipos de casillas ────────────────────────────────────────────────────────

class Cell:
    """Casilla base del tablero."""
    pass


class EmptyCell(Cell):
    """Casilla vacía."""
    def __repr__(self):
        return "  .  "


class StarCell(Cell):
    """Casilla con puntos (★). Se consume al ser pisada."""
    def __init__(self, value: int):
        self.value = value
        self.consumed = False

    def __repr__(self):
        return f" ★{self.value} "


class EnergyCell(Cell):
    """Casilla de energía (⚡). Se consume al ser pisada."""
    def __init__(self, value: int):
        self.value = value
        self.consumed = False

    def __repr__(self):
        return f" ⚡{self.value} "


class KnightCell(Cell):
    """Posición de un caballo sobre el tablero."""
    def __init__(self, player: int):
        # player=0 → máquina (blanco), player=1 → humano (negro)
        self.player = player

    def __repr__(self):
        return " ♘ " if self.player == 0 else " ♞ "


# ── Tablero ──────────────────────────────────────────────────────────────────

STAR_VALUES   = [2, 3, 4, 5, 6, 8, 9]   # 7 casillas de puntos
ENERGY_VALUES = [2, 3, 4, 5]             # 4 casillas de energía
BOARD_SIZE    = 8


class Board:
    """
    Tablero 8x8.

    Atributos
    ---------
    grid : list[list[Cell]]
        Matriz de casillas. grid[row][col].
    knight_positions : dict
        {0: (row, col), 1: (row, col)} — posiciones actuales de cada caballo.
    star_cells : dict
        {(row, col): StarCell} — casillas de puntos aún disponibles.
    energy_cells : dict
        {(row, col): EnergyCell} — casillas de energía aún disponibles.
    """

    def __init__(self):
        self.grid: list[list[Cell]] = [
            [EmptyCell() for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]
        self.knight_positions: dict[int, tuple[int, int]] = {}
        self.star_cells:   dict[tuple[int, int], StarCell]   = {}
        self.energy_cells: dict[tuple[int, int], EnergyCell] = {}
        self._place_all()

    # ── Inicialización ───────────────────────────────────────────────────────

    def _all_positions(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)]

    def _place_all(self):
        """Coloca aleatoriamente caballos, estrellas y energías sin solapamiento."""
        positions = self._all_positions()
        random.shuffle(positions)

        idx = 0

        # Caballos: 0 = máquina, 1 = humano
        for player in range(2):
            pos = positions[idx]; idx += 1
            self.knight_positions[player] = pos
            self.grid[pos[0]][pos[1]] = KnightCell(player)

        # Casillas de puntos ★
        star_vals = STAR_VALUES[:]
        random.shuffle(star_vals)
        for val in star_vals:
            pos = positions[idx]; idx += 1
            cell = StarCell(val)
            self.star_cells[pos] = cell
            self.grid[pos[0]][pos[1]] = cell

        # Casillas de energía ⚡
        energy_vals = ENERGY_VALUES[:]
        random.shuffle(energy_vals)
        for val in energy_vals:
            pos = positions[idx]; idx += 1
            cell = EnergyCell(val)
            self.energy_cells[pos] = cell
            self.grid[pos[0]][pos[1]] = cell

    # ── Consultas ────────────────────────────────────────────────────────────

    def get_cell(self, row: int, col: int) -> Cell:
        return self.grid[row][col]

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def has_stars_remaining(self) -> bool:
        return len(self.star_cells) > 0

    def total_special_cells(self) -> int:
        return len(self.star_cells) + len(self.energy_cells)

    # ── Mutaciones ───────────────────────────────────────────────────────────

    def move_knight(self, player: int, new_pos: tuple[int, int]):
        """
        Mueve el caballo del jugador a new_pos.
        Devuelve (points_gained, energy_gained).
        """
        old_pos = self.knight_positions[player]
        points_gained = 0
        energy_gained = 0

        # Liberar casilla anterior
        self.grid[old_pos[0]][old_pos[1]] = EmptyCell()

        # Procesar casilla destino
        dest_cell = self.grid[new_pos[0]][new_pos[1]]

        if isinstance(dest_cell, StarCell):
            points_gained = dest_cell.value
            del self.star_cells[new_pos]

        elif isinstance(dest_cell, EnergyCell):
            energy_gained = dest_cell.value
            del self.energy_cells[new_pos]

        # Colocar caballo en nueva posición
        self.grid[new_pos[0]][new_pos[1]] = KnightCell(player)
        self.knight_positions[player] = new_pos

        return points_gained, energy_gained

    # ── Copia profunda ───────────────────────────────────────────────────────

    def copy(self) -> "Board":
        return copy.deepcopy(self)

    # ── Representación ───────────────────────────────────────────────────────

    def __str__(self) -> str:
        col_header = "     " + "  ".join(str(c) for c in range(BOARD_SIZE))
        separator  = "   +" + "-----+" * BOARD_SIZE
        lines = [col_header, separator]
        for r in range(BOARD_SIZE):
            row_str = f" {r} |"
            for c in range(BOARD_SIZE):
                row_str += repr(self.grid[r][c]) + "|"
            lines.append(row_str)
            lines.append(separator)
        return "\n".join(lines)
