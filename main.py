"""
main.py
Punto de entrada de Knight Energy.

Uso:
    python main.py
"""

from game.board import Board


def main():
    print("=" * 50)
    print("       ♞  KNIGHT ENERGY  ♘")
    print("=" * 50)
    print("\n[Día 1] Tablero de prueba — colocación aleatoria\n")

    board = Board()
    print(board)

    print("\nPosición caballo máquina (♘):", board.knight_positions[0])
    print("Posición caballo humano  (♞):", board.knight_positions[1])
    print(f"\nCasillas ★ disponibles : {len(board.star_cells)}")
    print(f"Casillas ⚡ disponibles : {len(board.energy_cells)}")


if __name__ == "__main__":
    main()
