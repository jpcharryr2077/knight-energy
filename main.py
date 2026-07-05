"""
main.py
Punto de entrada de Knight Energy.

Flujo:
  1. Menú de dificultad
  2. Partida completa
  3. ¿Jugar de nuevo?
"""

import os
from game.game_engine import GameEngine
from ai.minimax import MinimaxAI
from ui.display import Display, SEP_MAJOR

DIFFICULTIES = {
    "1": ("principiante", 2),
    "2": ("amateur",      4),
    "3": ("experto",      6),
}


def select_difficulty() -> tuple[str, int]:
    os.system("cls" if os.name == "nt" else "clear")
    print("\n" + SEP_MAJOR)
    print("│" + "    ♞   K N I G H T   E N E R G Y   ♘    ".center(52) + "│")
    print("│" + "   Universidad del Valle · IA 2026-I   ".center(52)   + "│")
    print(SEP_MAJOR)
    print()
    print("  Selecciona el nivel de dificultad:\n")
    print("    \033[1m[1]\033[0m  Principiante  —  Minimax profundidad 2")
    print("    \033[1m[2]\033[0m  Amateur       —  Minimax profundidad 4")
    print("    \033[1m[3]\033[0m  Experto       —  Minimax profundidad 6")
    print()

    while True:
        choice = input("  Tu elección (1 / 2 / 3): ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("  ⚠  Opción inválida. Escribe 1, 2 o 3.")


def main():
    display = Display()

    while True:
        difficulty, depth = select_difficulty()
        ai     = MinimaxAI(depth=depth)
        engine = GameEngine(difficulty=difficulty, ai_player=ai)
        engine.run()

        if not display.ask_play_again():
            break

    display.show_goodbye()


if __name__ == "__main__":
    main()
