"""
game_engine.py
Motor principal.

Integración completa con la UI mejorada.
- Tablero con movimientos resaltados durante el turno del humano
- Selección de movimiento por número índice
- Divisores visuales entre turnos
- Soporte para jugar múltiples partidas
"""

from __future__ import annotations

from game.game_state import GameState
from game.knight import get_valid_moves, has_moves
from ui.display import Display


class GameEngine:
    """
    Motor de la partida.

    Parámetros
    ----------
    difficulty : str       — 'principiante' | 'amateur' | 'experto'
    ai_player  : MinimaxAI — agente IA inyectado desde main.py
    """

    DEPTH_MAP = {
        "principiante": 2,
        "amateur":      4,
        "experto":      6,
    }

    def __init__(self, difficulty: str = "principiante", ai_player=None):
        if difficulty not in self.DEPTH_MAP:
            raise ValueError(f"Dificultad inválida: '{difficulty}'. "
                             f"Opciones: {list(self.DEPTH_MAP)}")
        self.difficulty = difficulty
        self.depth      = self.DEPTH_MAP[difficulty]
        self.ai_player  = ai_player
        self.display    = Display(clear_screen=False)

    # ── Punto de entrada ─────────────────────────────────────────────────────

    def run(self):
        """Ejecuta una partida completa."""
        self.state = GameState()
        self.display.show_welcome(self.difficulty, self.depth)
        self.display.show_board(self.state)

        while not self.state.game_over:
            self._play_turn()

        self.display.show_game_over(self.state)

    # ── Turno ────────────────────────────────────────────────────────────────

    def _play_turn(self):
        """Procesa un turno completo del jugador activo."""
        player_id = self.state.current_turn
        player    = self.state.current_player

        self.display.show_turn_divider(self.state.turn_number)
        self.display.show_status(self.state)

        # ── Sin casillas alcanzables ─────────────────────────────────────────
        if not has_moves(self.state.board, player_id):
            if not player.can_move():
                self.display.show_no_energy(player)
                self.state.apply_skip()
            else:
                self.display.show_blocked(player)
                self._skip_no_penalty()
            return

        # ── Sin energía (hay casillas pero no puede moverse) ─────────────────
        if not player.can_move():
            self.display.show_no_energy(player)
            self.state.apply_skip()
            return

        # ── Elegir y aplicar movimiento ──────────────────────────────────────
        move = self._machine_move() if player_id == 0 else self._human_move()

        if move is None:
            return

        summary = self.state.apply_move(move)
        self.display.show_move_summary(summary, self.state.players)
        self.display.show_board(self.state)

    # ── Turno de la máquina ──────────────────────────────────────────────────

    def _machine_move(self) -> tuple | None:
        if self.ai_player is not None:
            move  = self.ai_player.choose_move(self.state)
            stats = self.ai_player.get_stats()
            self.display.show_machine_thinking(self.difficulty, stats=stats)
        else:
            moves = get_valid_moves(self.state.board, 0)
            move  = moves[0] if moves else None
            if move:
                self.display.show_machine_thinking(self.difficulty)
        return move

    # ── Turno del humano ─────────────────────────────────────────────────────

    def _human_move(self) -> tuple | None:
        """
        Muestra el tablero con los movimientos resaltados,
        lista numerada y permite elegir por índice.
        """
        valid_moves = get_valid_moves(self.state.board, 1)

        # Mostrar tablero con destinos resaltados
        self.display.show_board(self.state, highlighted=valid_moves)

        # Listar movimientos con información de casillas especiales
        self.display.show_valid_moves(
            valid_moves,
            board_stars  = self.state.board.star_cells,
            board_energy = self.state.board.energy_cells,
        )

        while True:
            raw = input("\n  Tu movimiento (número): ").strip()

            # Aceptar tanto número índice como coordenadas "fila col"
            chosen = self._parse_index(raw, valid_moves)
            if chosen is None:
                chosen = self._parse_coords(raw)

            if chosen is None:
                print("  ⚠  Entrada inválida. Escribe el número del movimiento "
                      "o las coordenadas (fila col).")
                continue

            if chosen not in valid_moves:
                print(f"  ⚠  Posición {chosen} no está en la lista. Intenta de nuevo.")
                continue

            return chosen

    # ── Skip sin penalización ────────────────────────────────────────────────

    def _skip_no_penalty(self):
        player = self.state.current_player
        self.state.history.append(
            f"Turno {self.state.turn_number} | {player.name}: "
            "BLOQUEADO — sin casillas alcanzables (sin penalización)"
        )
        self.state.turn_number  += 1
        self.state.current_turn  = 1 - self.state.current_turn
        if self.state.is_terminal():
            self.state._resolve_winner()

    # ── Parseo de entrada ────────────────────────────────────────────────────

    @staticmethod
    def _parse_index(raw: str,
                     moves: list[tuple[int,int]]) -> tuple | None:
        """'2' → moves[2] si es un índice válido."""
        try:
            idx = int(raw.strip())
            if 0 <= idx < len(moves):
                return moves[idx]
        except ValueError:
            pass
        return None

    @staticmethod
    def _parse_coords(raw: str) -> tuple | None:
        """'3 5' → (3, 5). Retorna None si el formato es inválido."""
        try:
            parts = raw.split()
            if len(parts) != 2:
                return None
            r, c = int(parts[0]), int(parts[1])
            if 0 <= r <= 7 and 0 <= c <= 7:
                return (r, c)
        except (ValueError, IndexError):
            pass
        return None
