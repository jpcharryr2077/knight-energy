"""
main.py
Punto de entrada de Knight Energy.
"""

from game.board import Board
from game.game_state import GameState
from game.knight import get_valid_moves


def main():
    print("=" * 50)
    print("       ♞  KNIGHT ENERGY  ♘")
    print("=" * 50)
    print("\n[Día 2] Prueba de estado del juego y movimientos\n")

    state = GameState()

    # Mostrar tablero inicial
    print(state.board)
    print(state)

    # Mostrar movimientos válidos de cada caballo
    for player_id, label in [(0, "Máquina ♘"), (1, "Humano ♞")]:
        moves = get_valid_moves(state.board, player_id)
        pos   = state.board.knight_positions[player_id]
        print(f"  {label} en {pos} → {len(moves)} movimiento(s): {moves}")

    # Simular un movimiento de la máquina (primer movimiento válido)
    print("\n--- Simulando un movimiento de la Máquina ---")
    machine_moves = get_valid_moves(state.board, 0)
    if machine_moves:
        chosen = machine_moves[0]
        summary = state.apply_move(chosen)
        print(f"  Movió a {summary['to']}")
        print(f"  Puntos ganados: {summary['points_gained']}")
        print(f"  Energía ganada: {summary['energy_gained']}")
        print(f"  Energía: {summary['energy_before']} → {summary['energy_after']}")
        print(state.board)
        print(state)

    print("\nHistorial de turnos:")
    for event in state.history:
        print(f"  {event}")

    print("\n¿Juego terminado?", state.game_over)


if __name__ == "__main__":
    main()
