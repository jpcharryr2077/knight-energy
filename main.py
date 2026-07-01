"""
main.py
Punto de entrada de Knight Energy.
"""

from game.game_engine import GameEngine


DIFFICULTIES = {
    "1": "principiante",
    "2": "amateur",
    "3": "experto",
}


def select_difficulty() -> str:
    print("\n" + "═" * 52)
    print("          ♞   K N I G H T   E N E R G Y   ♘")
    print("═" * 52)
    print("  Selecciona el nivel de dificultad:\n")
    print("    [1]  Principiante  (Minimax profundidad 2)")
    print("    [2]  Amateur       (Minimax profundidad 4)")
    print("    [3]  Experto       (Minimax profundidad 6)")
    print()
    while True:
        choice = input("  Tu elección (1/2/3): ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("  ⚠  Opción inválida. Escribe 1, 2 o 3.")


def main():
    difficulty = select_difficulty()
    engine     = GameEngine(difficulty=difficulty, ai_player=None)
    engine.run()


if __name__ == "__main__":
    main()
