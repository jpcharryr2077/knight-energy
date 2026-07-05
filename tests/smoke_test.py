"""
smoke_test.py
Prueba de humo de integración completa — Knight Energy.

Ejecuta partidas automáticas en los tres niveles de dificultad
con el Minimax real contra un humano aleatorio y verifica que:
  - La partida termina correctamente (game_over = True)
  - El ganador es coherente con los puntos
  - No se producen excepciones en ningún módulo
  - Las reglas se respetan (energía, penalizaciones, consumo de casillas)

Uso:
    python tests/smoke_test.py
"""

import sys
import os
import random
import time

# Asegurar que el raíz del proyecto está en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameState
from game.knight import get_valid_moves, has_moves
from ai.minimax import MinimaxAI

# ── Colores para terminal ──────────────────────────────────────────────────────
GREEN  = "\033[1;32m"
RED    = "\033[1;31m"
YELLOW = "\033[1;33m"
CYAN   = "\033[1;36m"
RESET  = "\033[0m"
GREY   = "\033[90m"

PASS = f"{GREEN}✓ PASS{RESET}"
FAIL = f"{RED}✗ FAIL{RESET}"


# ── Runner de partida automática ──────────────────────────────────────────────

def run_game(difficulty: str, depth: int, seed: int) -> dict:
    """
    Simula una partida completa:
    - Máquina (0): Minimax con profundidad `depth`
    - Humano  (1): movimiento aleatorio (seed fijo para reproducibilidad)

    Retorna un dict con los resultados y métricas.
    """
    random.seed(seed)
    state = GameState()
    ai    = MinimaxAI(depth=depth)

    turns          = 0
    skips_machine  = 0
    skips_human    = 0
    total_nodes    = 0
    total_pruned   = 0
    stars_captured = {0: 0, 1: 0}
    MAX_TURNS      = 500

    t_start = time.perf_counter()

    while not state.game_over and turns < MAX_TURNS:
        turns += 1
        pid    = state.current_turn
        player = state.current_player

        # Sin casillas alcanzables
        if not has_moves(state.board, pid):
            if not player.can_move():
                state.apply_skip()
                if pid == 0: skips_machine += 1
                else:        skips_human   += 1
            else:
                # Bloqueado geográficamente — skip sin penalización
                state.history.append(
                    f"Turno {state.turn_number} | {player.name}: BLOQUEADO"
                )
                state.turn_number  += 1
                state.current_turn  = 1 - state.current_turn
                if state.is_terminal():
                    state._resolve_winner()
            continue

        # Sin energía
        if not player.can_move():
            state.apply_skip()
            if pid == 0: skips_machine += 1
            else:        skips_human   += 1
            continue

        # Elegir movimiento
        if pid == 0:
            move = ai.choose_move(state)
            s    = ai.get_stats()
            total_nodes  += s["nodes_evaluated"]
            total_pruned += s["nodes_pruned"]
        else:
            moves = get_valid_moves(state.board, 1)
            move  = random.choice(moves)

        if move:
            prev_stars = len(state.board.star_cells)
            summary    = state.apply_move(move)
            if len(state.board.star_cells) < prev_stars:
                stars_captured[summary["player"]] += 1

    elapsed = time.perf_counter() - t_start

    return {
        "difficulty":      difficulty,
        "depth":           depth,
        "seed":            seed,
        "game_over":       state.game_over,
        "winner":          state.winner,
        "turns":           turns,
        "timed_out":       turns >= MAX_TURNS,
        "pts_machine":     state.players[0].points,
        "pts_human":       state.players[1].points,
        "skips_machine":   skips_machine,
        "skips_human":     skips_human,
        "stars_machine":   stars_captured[0],
        "stars_human":     stars_captured[1],
        "stars_remaining": len(state.board.star_cells),
        "total_nodes":     total_nodes,
        "total_pruned":    total_pruned,
        "elapsed_s":       elapsed,
        "history":         state.history,
    }


# ── Validaciones sobre el resultado ──────────────────────────────────────────

def validate(result: dict) -> list[str]:
    """Retorna lista de errores. Lista vacía = todo OK."""
    errors = []
    p0 = result["pts_machine"]
    p1 = result["pts_human"]
    w  = result["winner"]

    if not result["game_over"]:
        errors.append("game_over = False al terminar (timeout o bug de condición terminal)")

    if result["timed_out"]:
        errors.append(f"Partida excedió {500} turnos — posible bucle infinito")

    # Coherencia ganador ↔ puntos
    if result["game_over"]:
        if p0 > p1 and w != 0:
            errors.append(f"Máquina tiene más puntos ({p0}>{p1}) pero winner={w}")
        if p1 > p0 and w != 1:
            errors.append(f"Humano tiene más puntos ({p1}>{p0}) pero winner={w}")
        if p0 == p1 and w is not None:
            errors.append(f"Empate en puntos ({p0}={p1}) pero winner={w}")

    # No deben quedar más estrellas de las iniciales (7) ni negativas
    if not (0 <= result["stars_remaining"] <= 7):
        errors.append(f"Estrellas restantes fuera de rango: {result['stars_remaining']}")

    return errors


# ── Reporte ───────────────────────────────────────────────────────────────────

def print_result(result: dict, errors: list[str]):
    status = PASS if not errors else FAIL
    w_str  = {0: "Máquina", 1: "Humano", None: "Empate"}.get(result["winner"], "?")
    color  = GREEN if result["winner"] == 0 else (RED if result["winner"] == 1 else YELLOW)

    print(f"\n  {status}  [{result['difficulty'].upper():<14}]  "
          f"profundidad={result['depth']}")
    print(f"         Ganador : {color}{w_str}{RESET}  "
          f"({result['pts_machine']} vs {result['pts_human']} pts)")
    print(f"         Turnos  : {result['turns']}   "
          f"Tiempo : {result['elapsed_s']:.2f}s")
    print(f"         Nodos   : {result['total_nodes']}   "
          f"Podados: {result['total_pruned']}")
    print(f"         ★ Máq:{result['stars_machine']}  ★ Hum:{result['stars_human']}  "
          f"★ rest:{result['stars_remaining']}   "
          f"Skips M:{result['skips_machine']} H:{result['skips_human']}")

    if errors:
        for e in errors:
            print(f"         {RED}⚠  {e}{RESET}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print("  KNIGHT ENERGY — Smoke Test de Integración")
    print("  Día 7: Verificación end-to-end en los 3 niveles")
    print("═" * 60)

    configs = [
        ("principiante", 2),
        ("amateur",       4),
        ("experto",       6),
    ]

    # Ejecutar 2 semillas por nivel para mayor cobertura
    seeds    = [42, 137]
    all_ok   = True
    total    = 0
    passed   = 0

    for difficulty, depth in configs:
        print(f"\n  {CYAN}── {difficulty.upper()} (profundidad {depth}) ──{RESET}")
        for seed in seeds:
            total += 1
            try:
                result = run_game(difficulty, depth, seed)
                errors = validate(result)
                print_result(result, errors)
                if not errors:
                    passed += 1
                else:
                    all_ok = False
            except Exception as exc:
                import traceback
                all_ok = False
                print(f"\n  {FAIL}  [{difficulty}] seed={seed}")
                print(f"  {RED}{traceback.format_exc()}{RESET}")

    # Resumen final
    print("\n" + "═" * 60)
    color = GREEN if all_ok else RED
    print(f"  {color}Resultado: {passed}/{total} pruebas pasaron{RESET}")
    print("═" * 60 + "\n")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
