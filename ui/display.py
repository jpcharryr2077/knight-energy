"""
display.py
Capa de presentación en terminal para Knight Energy.

Centraliza todos los mensajes y el renderizado del tablero,
manteniendo el motor y la UI completamente desacoplados.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_state import GameState, PlayerState

# Columnas del tablero (índices 0-7)
COL_HEADER = "     " + "   ".join(str(c) for c in range(8))
SEPARATOR  = "   +" + "-----+" * 8


class Display:
    """Métodos de presentación en terminal."""

    # ── Bienvenida ───────────────────────────────────────────────────────────

    def show_welcome(self, difficulty: str, depth: int):
        print("\n" + "═" * 52)
        print("          ♞   K N I G H T   E N E R G Y   ♘")
        print("═" * 52)
        print(f"  Dificultad : {difficulty.capitalize()}")
        print(f"  Profundidad Minimax : {depth}")
        print(f"  La Máquina (♘) inicia siempre")
        print("═" * 52 + "\n")
        input("  Presiona ENTER para comenzar...")

    # ── Tablero ──────────────────────────────────────────────────────────────

    def show_board(self, state: "GameState"):
        print("\n" + COL_HEADER)
        print(SEPARATOR)
        for r in range(8):
            row_str = f" {r} |"
            for c in range(8):
                row_str += repr(state.board.grid[r][c]) + "|"
            print(row_str)
            print(SEPARATOR)
        print()

    # ── Estado (puntos y energía) ────────────────────────────────────────────

    def show_status(self, state: "GameState"):
        p0, p1 = state.players[0], state.players[1]
        turn_label = "→" if state.current_turn == 0 else " "
        turn_label2 = "→" if state.current_turn == 1 else " "
        print("┌─────────────────────────────────────────────┐")
        print(f"│  TURNO {state.turn_number:<3}                                    │")
        print(f"│  {turn_label} ♘ {p0.name:<10} Pts: {p0.points:>4}  Energía: {p0.energy:>2}   │")
        print(f"│  {turn_label2} ♞ {p1.name:<10} Pts: {p1.points:>4}  Energía: {p1.energy:>2}   │")
        print(f"│    ★ restantes: {len(state.board.star_cells)}   "
              f"⚡ restantes: {len(state.board.energy_cells)}           │")
        print("└─────────────────────────────────────────────┘")

    # ── Movimientos disponibles ───────────────────────────────────────────────

    def show_valid_moves(self, moves: list[tuple[int, int]]):
        print("\n  Movimientos disponibles:")
        for i, (r, c) in enumerate(moves):
            print(f"    [{i}]  fila {r}, col {c}  →  escribe: {r} {c}")

    # ── Máquina pensando ─────────────────────────────────────────────────────

    def show_machine_thinking(self, difficulty: str, stats: dict | None = None):
        delays = {"principiante": 0.3, "amateur": 0.6, "experto": 1.0}
        delay  = delays.get(difficulty, 0.5)
        print("\n  ♘ Máquina calculando", end="", flush=True)
        for _ in range(3):
            time.sleep(delay / 3)
            print(".", end="", flush=True)
        print()
        if stats:
            print(f"     Nodos evaluados: {stats['nodes_evaluated']}  "
                  f"| Ramas podadas: {stats['nodes_pruned']}")

    # ── Resumen de movimiento ────────────────────────────────────────────────

    def show_move_summary(self, summary: dict, players: list):
        pid    = summary["player"]
        name   = players[pid].name
        symbol = "♘" if pid == 0 else "♞"
        print(f"\n  {symbol} {name}: {summary['from']} → {summary['to']}", end="")
        if summary["points_gained"]:
            print(f"  ✦ +{summary['points_gained']} puntos ★", end="")
        if summary["energy_gained"]:
            print(f"  ✦ +{summary['energy_gained']} energía ⚡", end="")
        print()

    # ── Eventos especiales ───────────────────────────────────────────────────

    def show_no_energy(self, player: "PlayerState"):
        symbol = "♘" if player.player_id == 0 else "♞"
        print(f"\n  ⚠  {symbol} {player.name} sin energía — pierde turno (−3 pts)")

    def show_blocked(self, player: "PlayerState"):
        symbol = "♘" if player.player_id == 0 else "♞"
        print(f"\n  ⚠  {symbol} {player.name} bloqueado — sin casillas alcanzables")

    # ── Fin de juego ─────────────────────────────────────────────────────────

    def show_game_over(self, state: "GameState"):
        p0, p1 = state.players[0], state.players[1]
        print("\n" + "═" * 52)
        print("              F I N   D E L   J U E G O")
        print("═" * 52)
        print(f"  ♘ {p0.name:<12} →  {p0.points:>4} puntos")
        print(f"  ♞ {p1.name:<12} →  {p1.points:>4} puntos")
        print("─" * 52)

        if state.winner is None:
            print("  🤝  ¡EMPATE!")
        elif state.winner == 0:
            print(f"  🏆  ¡Ganó la MÁQUINA!")
        else:
            print(f"  🏆  ¡Ganó el HUMANO!  ¡Felicitaciones!")

        print("═" * 52)
        print("\n  Historial de la partida:")
        for event in state.history:
            print(f"    {event}")
        print()
