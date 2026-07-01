"""
game_engine.py
Motor principal de Knight Energy.

Orquesta el flujo completo de la partida:
- Turnos alternados (máquina siempre inicia)
- Validación de energía antes de mover
- Penalización por turno perdido
- Detección de fin de juego
- Interfaz de entrada para el jugador humano
"""

from __future__ import annotations

from game.board import Board
from game.game_state import GameState
from game.knight import get_valid_moves, has_moves
from ui.display import Display


class GameEngine:
    """
    Motor de la partida.

    Parámetros
    ----------
    difficulty : str  — 'principiante' | 'amateur' | 'experto'
    ai_player  : objeto con método choose_move(state) -> tuple | None
                 (se inyectará en Día 5; por ahora acepta None para modo demo)
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
        self.difficulty  = difficulty
        self.depth       = self.DEPTH_MAP[difficulty]
        self.ai_player   = ai_player          # Se conecta en Día 5
        self.state       = GameState()
        self.display     = Display()

    # ── Bucle principal ──────────────────────────────────────────────────────

    def run(self):
        """Ejecuta la partida completa."""
        self.display.show_welcome(self.difficulty, self.depth)
        self.display.show_board(self.state)

        while not self.state.game_over:
            self._play_turn()

        self._show_result()

    # ── Turno ────────────────────────────────────────────────────────────────

    def _play_turn(self):
        """Procesa un turno completo del jugador activo."""
        player_id = self.state.current_turn
        player    = self.state.current_player

        self.display.show_status(self.state)

        # ── Sin movimientos posibles en el tablero ───────────────────────────
        if not has_moves(self.state.board, player_id):
            if not player.can_move():
                # Sin energía Y sin casillas → skip con penalización
                self.display.show_no_energy(player)
                self.state.apply_skip()
            else:
                # Con energía pero bloqueado → skip sin penalización
                # (el otro jugador aún puede moverse; el juego continúa)
                self.display.show_blocked(player)
                self._skip_no_penalty()
            return

        # ── Sin energía (pero hay casillas alcanzables) ──────────────────────
        if not player.can_move():
            self.display.show_no_energy(player)
            self.state.apply_skip()
            return

        # ── Elegir movimiento ────────────────────────────────────────────────
        if player_id == 0:
            move = self._machine_move()
        else:
            move = self._human_move()

        if move is None:
            # Seguridad: no debería ocurrir en este punto
            return

        summary = self.state.apply_move(move)
        self.display.show_move_summary(summary, self.state.players)
        self.display.show_board(self.state)

    # ── Turno de la máquina ──────────────────────────────────────────────────

    def _machine_move(self) -> tuple | None:
        """Delega la decisión al motor de IA (o elige aleatoriamente si aún no está conectado)."""
        if self.ai_player is not None:
            move = self.ai_player.choose_move(self.state)
        else:
            # Modo demo (Días 3-4): elige el primer movimiento disponible
            moves = get_valid_moves(self.state.board, 0)
            move  = moves[0] if moves else None

        if move:
            self.display.show_machine_thinking(self.difficulty)
        return move

    # ── Turno del humano ─────────────────────────────────────────────────────

    def _human_move(self) -> tuple | None:
        """Solicita al humano que elija un movimiento válido."""
        valid_moves = get_valid_moves(self.state.board, 1)
        self.display.show_valid_moves(valid_moves)

        while True:
            raw = input("\n  Tu movimiento (fila col): ").strip()
            parsed = self._parse_input(raw)

            if parsed is None:
                print("  ⚠  Formato inválido. Escribe dos números: fila col  (ej: 3 5)")
                continue

            if parsed not in valid_moves:
                print(f"  ⚠  Movimiento {parsed} no válido. Elige de la lista.")
                continue

            return parsed

    # ── Skip sin penalización ────────────────────────────────────────────────

    def _skip_no_penalty(self):
        """
        El jugador está bloqueado por el tablero (no por falta de energía).
        Pierde el turno pero NO se le descuentan puntos.
        """
        player = self.state.current_player
        event  = (
            f"Turno {self.state.turn_number} | {player.name}: "
            "BLOQUEADO — sin casillas alcanzables (sin penalización)"
        )
        self.state.history.append(event)
        self.state.turn_number  += 1
        self.state.current_turn  = 1 - self.state.current_turn
        if self.state.is_terminal():
            self.state._resolve_winner()

    # ── Resultado final ──────────────────────────────────────────────────────

    def _show_result(self):
        self.display.show_game_over(self.state)

    # ── Utilidades ───────────────────────────────────────────────────────────

    @staticmethod
    def _parse_input(raw: str) -> tuple | None:
        """Convierte '3 5' → (3, 5). Retorna None si el formato es inválido."""
        try:
            parts = raw.split()
            if len(parts) != 2:
                return None
            r, c = int(parts[0]), int(parts[1])
            if not (0 <= r <= 7 and 0 <= c <= 7):
                return None
            return (r, c)
        except (ValueError, IndexError):
            return None
