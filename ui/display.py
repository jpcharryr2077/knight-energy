"""
display.py
Capa de presentación en terminal para Knight Energy.

Mejoras del Día 6:
- Tablero con resaltado de posiciones de los caballos y casillas especiales
- Selección de movimiento por número índice (no coordenadas brutas)
- Leyenda visual de símbolos
- Barra de energía visual
- Separación clara entre turnos con líneas decorativas
- Pantalla de victoria mejorada
"""

from __future__ import annotations
import time
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_state import GameState, PlayerState

from game.board import StarCell, EnergyCell, KnightCell, EmptyCell

# ── Constantes de presentación ────────────────────────────────────────────────

SEP_MAJOR = "═" * 54
SEP_MINOR = "─" * 54
BOX_LINE  = "│" + " " * 52 + "│"

# Representaciones de celda enriquecidas (5 chars c/u para alineación)
def _cell_str(cell, highlight: bool = False) -> str:
    """Devuelve la representación de una celda con 5 caracteres."""
    if isinstance(cell, KnightCell):
        sym = " ♘ " if cell.player == 0 else " ♞ "
        return f"\033[1;33m{sym}\033[0m" if cell.player == 0 else f"\033[1;36m{sym}\033[0m"
    if isinstance(cell, StarCell):
        return f"\033[1;32m ★{cell.value} \033[0m"
    if isinstance(cell, EnergyCell):
        return f"\033[1;35m ⚡{cell.value}\033[0m"
    return "  .  "


def _energy_bar(energy: int, max_energy: int = 15) -> str:
    """Barra visual de energía: ████░░░░"""
    filled  = min(energy, max_energy)
    empty   = max(max_energy - filled, 0)
    bar     = "█" * filled + "░" * empty
    color   = "\033[32m" if energy >= 4 else ("\033[33m" if energy >= 2 else "\033[31m")
    return f"{color}{bar}\033[0m [{energy}]"


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


class Display:
    """Métodos de presentación en terminal."""

    def __init__(self, clear_screen: bool = True):
        self.clear_screen = clear_screen

    # ── Bienvenida ───────────────────────────────────────────────────────────

    def show_welcome(self, difficulty: str, depth: int):
        if self.clear_screen:
            _clear()
        print("\n" + SEP_MAJOR)
        print("│" + "    ♞   K N I G H T   E N E R G Y   ♘    ".center(52) + "│")
        print("│" + "   Universidad del Valle · IA 2026-I   ".center(52) + "│")
        print(SEP_MAJOR)
        print(f"│  {'Dificultad':<20} {difficulty.capitalize():<30}│")
        print(f"│  {'Profundidad Minimax':<20} {depth:<30}│")
        print(f"│  {'Turno inicial':<20} {'Máquina ♘ (siempre)':<30}│")
        print(SEP_MAJOR)
        print()
        self._show_legend()
        print()
        input("  Presiona ENTER para comenzar la partida...")

    def _show_legend(self):
        print("  LEYENDA:")
        print("  \033[1;33m ♘ \033[0m Máquina (MAX)     "
              "\033[1;36m ♞ \033[0m Humano  (MIN)")
        print("  \033[1;32m ★N\033[0m  Casilla de puntos  "
              "\033[1;35m ⚡N\033[0m Casilla de energía")
        print("   .   Casilla vacía")

    # ── Tablero ──────────────────────────────────────────────────────────────

    def show_board(self, state: "GameState",
                   highlighted: list[tuple[int,int]] | None = None):
        """
        Muestra el tablero 8×8.
        Si se pasa `highlighted`, resalta esas casillas como movimientos válidos.
        """
        highlighted = set(highlighted or [])

        print()
        # Cabecera de columnas
        col_hdr = "      " + "  ".join(f"\033[90m{c}\033[0m " for c in range(8))
        print(col_hdr)
        sep = "    +" + "─────+" * 8
        print(sep)

        for r in range(8):
            row_str = f" \033[90m{r}\033[0m  │"
            for c in range(8):
                cell = state.board.grid[r][c]
                if (r, c) in highlighted:
                    # Casilla destino válida: fondo resaltado
                    row_str += f"\033[48;5;236m{_cell_str(cell)}\033[0m│"
                else:
                    row_str += f"{_cell_str(cell)}│"
            print(row_str)
            print(sep)
        print()

    # ── Panel de estado ───────────────────────────────────────────────────────

    def show_status(self, state: "GameState"):
        p0, p1    = state.players[0], state.players[1]
        arrow0    = "\033[1;33m►\033[0m" if state.current_turn == 0 else " "
        arrow1    = "\033[1;36m►\033[0m" if state.current_turn == 1 else " "
        stars_rem = len(state.board.star_cells)
        nrg_rem   = len(state.board.energy_cells)

        print("┌" + "─" * 52 + "┐")
        print(f"│  \033[1mTURNO {state.turn_number}\033[0m" +
              " " * (46 - len(str(state.turn_number))) + "│")
        print("├" + "─" * 52 + "┤")
        print(f"│ {arrow0} \033[1;33m♘ Máquina\033[0m   "
              f"Pts: \033[1m{p0.points:>4}\033[0m   "
              f"Energía: {_energy_bar(p0.energy, 10):<30}│")
        print(f"│ {arrow1} \033[1;36m♞ Humano \033[0m   "
              f"Pts: \033[1m{p1.points:>4}\033[0m   "
              f"Energía: {_energy_bar(p1.energy, 10):<30}│")
        print("├" + "─" * 52 + "┤")
        print(f"│   \033[1;32m★\033[0m Casillas de puntos restantes : {stars_rem}"
              + " " * (21 - len(str(stars_rem))) + "│")
        print(f"│   \033[1;35m⚡\033[0m Casillas de energía restantes: {nrg_rem}"
              + " " * (21 - len(str(nrg_rem))) + "│")
        print("└" + "─" * 52 + "┘")

    # ── Selección de movimiento (por número) ──────────────────────────────────

    def show_valid_moves(self, moves: list[tuple[int, int]],
                         board_stars: dict, board_energy: dict) -> None:
        """
        Muestra la lista numerada de movimientos disponibles,
        indicando si la casilla destino tiene ★ o ⚡.
        """
        print("\n  \033[1mMovimientos disponibles:\033[0m")
        for i, (r, c) in enumerate(moves):
            dest = ""
            if (r, c) in board_stars:
                val  = board_stars[(r, c)].value
                dest = f"  \033[1;32m[★ +{val} pts]\033[0m"
            elif (r, c) in board_energy:
                val  = board_energy[(r, c)].value
                dest = f"  \033[1;35m[⚡ +{val} energía]\033[0m"
            print(f"    \033[1m[{i}]\033[0m  ({r}, {c}){dest}")

    # ── Máquina pensando ─────────────────────────────────────────────────────

    def show_machine_thinking(self, difficulty: str, stats: dict | None = None):
        delays = {"principiante": 0.4, "amateur": 0.8, "experto": 1.2}
        delay  = delays.get(difficulty, 0.6)
        print(f"\n  \033[1;33m♘ Máquina analizando\033[0m", end="", flush=True)
        steps = 5
        for _ in range(steps):
            time.sleep(delay / steps)
            print(".", end="", flush=True)
        print()
        if stats:
            print(f"     \033[90mNodos evaluados: {stats['nodes_evaluated']}"
                  f"  |  Ramas podadas: {stats['nodes_pruned']}\033[0m")

    # ── Resumen de movimiento ────────────────────────────────────────────────

    def show_move_summary(self, summary: dict, players: list):
        pid    = summary["player"]
        name   = players[pid].name
        color  = "\033[1;33m" if pid == 0 else "\033[1;36m"
        symbol = "♘" if pid == 0 else "♞"
        gains  = ""
        if summary["points_gained"]:
            gains += f"  \033[1;32m✦ +{summary['points_gained']} pts ★\033[0m"
        if summary["energy_gained"]:
            gains += f"  \033[1;35m✦ +{summary['energy_gained']} ⚡\033[0m"
        print(f"\n  {color}{symbol} {name}\033[0m: "
              f"\033[90m{summary['from']}\033[0m → "
              f"\033[1m{summary['to']}\033[0m{gains}")

    # ── Eventos especiales ───────────────────────────────────────────────────

    def show_no_energy(self, player: "PlayerState"):
        symbol = "♘" if player.player_id == 0 else "♞"
        color  = "\033[1;33m" if player.player_id == 0 else "\033[1;36m"
        print(f"\n  \033[1;31m⚠  {color}{symbol} {player.name}\033[0m"
              f"\033[1;31m sin energía — pierde turno \033[0m(\033[31m−3 pts\033[0m)")

    def show_blocked(self, player: "PlayerState"):
        symbol = "♘" if player.player_id == 0 else "♞"
        color  = "\033[1;33m" if player.player_id == 0 else "\033[1;36m"
        print(f"\n  \033[33m⚠  {color}{symbol} {player.name}\033[0m"
              f"\033[33m bloqueado — sin casillas alcanzables\033[0m")

    def show_turn_divider(self, turn_number: int):
        print(f"\n  \033[90m{'─'*20} turno {turn_number} {'─'*20}\033[0m\n")

    # ── Fin de juego ─────────────────────────────────────────────────────────

    def show_game_over(self, state: "GameState"):
        p0, p1 = state.players[0], state.players[1]

        print("\n" + SEP_MAJOR)
        print("│" + "  F I N   D E L   J U E G O  ".center(52) + "│")
        print(SEP_MAJOR)
        print(f"│  \033[1;33m♘ {p0.name:<14}\033[0m →  {p0.points:>5} puntos"
              + " " * (23 - len(str(p0.points))) + "│")
        print(f"│  \033[1;36m♞ {p1.name:<14}\033[0m →  {p1.points:>5} puntos"
              + " " * (23 - len(str(p1.points))) + "│")
        print("├" + "─" * 52 + "┤")

        if state.winner is None:
            msg = "  🤝  EMPATE — puntuación igualada"
        elif state.winner == 0:
            diff = p0.points - p1.points
            msg = f"  🏆  ¡GANÓ LA MÁQUINA!   (ventaja: +{diff} pts)"
        else:
            diff = p1.points - p0.points
            msg = f"  🏆  ¡GANASTE!  ¡Felicitaciones!  (+{diff} pts)"

        print(f"│{msg:<52}│")
        print(SEP_MAJOR)
        print()

        # Historial colapsado
        print("  \033[1mHistorial de la partida:\033[0m")
        for event in state.history:
            print(f"    \033[90m{event}\033[0m")
        print()

    # ── Pregunta de nueva partida ─────────────────────────────────────────────

    def ask_play_again(self) -> bool:
        while True:
            ans = input("  ¿Jugar otra partida? (s/n): ").strip().lower()
            if ans in ("s", "si", "sí", "y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print("  ⚠  Escribe 's' para sí o 'n' para no.")

    def show_goodbye(self):
        print()
        print(SEP_MAJOR)
        print("│" + "  ¡Gracias por jugar Knight Energy!  ".center(52) + "│")
        print(SEP_MAJOR)
        print()
