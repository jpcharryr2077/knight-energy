"""
game_state.py
Estado completo del juego Knight Energy.

Encapsula toda la información mutable de una partida:
energía y puntos de cada jugador, turno actual,
y referencia al tablero.
"""

from __future__ import annotations
import copy

from game.board import Board
from game.knight import get_valid_moves, has_moves

# Energía inicial de cada jugador
INITIAL_ENERGY = 7

# Penalización por no poder moverse
NO_MOVE_PENALTY = 3

# Costo de energía por movimiento
MOVE_COST = 1


class PlayerState:
    """Estado individual de un jugador."""

    def __init__(self, player_id: int, name: str):
        self.player_id: int  = player_id
        self.name:      str  = name
        self.energy:    int  = INITIAL_ENERGY
        self.points:    int  = 0

    def can_move(self) -> bool:
        """Tiene energía suficiente para realizar un movimiento."""
        return self.energy >= MOVE_COST

    def spend_energy(self):
        """Descuenta el costo de un movimiento."""
        self.energy -= MOVE_COST

    def gain_points(self, amount: int):
        self.points += amount

    def lose_points(self, amount: int):
        self.points -= amount

    def gain_energy(self, amount: int):
        self.energy += amount

    def __repr__(self) -> str:
        symbol = "♘" if self.player_id == 0 else "♞"
        return (
            f"{symbol} {self.name:<10} "
            f"| Puntos: {self.points:>3}  "
            f"| Energía: {self.energy:>2}"
        )

    def copy(self) -> "PlayerState":
        return copy.copy(self)


class GameState:
    """
    Estado global de la partida.

    Atributos
    ---------
    board         : Board        — tablero actual.
    players       : list[PlayerState]
    current_turn  : int          — 0 = máquina, 1 = humano.
    turn_number   : int          — contador de turnos.
    game_over     : bool
    winner        : int | None   — 0, 1, o None (empate).
    history       : list[str]    — log de eventos.
    """

    def __init__(self, board: Board | None = None):
        self.board: Board = board if board is not None else Board()
        self.players: list[PlayerState] = [
            PlayerState(0, "Máquina"),
            PlayerState(1, "Humano"),
        ]
        self.current_turn: int  = 0   # La máquina siempre inicia
        self.turn_number:  int  = 1
        self.game_over:    bool = False
        self.winner:       int | None = None
        self.history:      list[str]  = []

    # ── Consultas ────────────────────────────────────────────────────────────

    @property
    def current_player(self) -> PlayerState:
        return self.players[self.current_turn]

    @property
    def waiting_player(self) -> PlayerState:
        return self.players[1 - self.current_turn]

    def get_valid_moves(self, player: int | None = None) -> list[tuple[int, int]]:
        """Movimientos válidos para el jugador indicado (o el turno actual)."""
        p = self.current_turn if player is None else player
        return get_valid_moves(self.board, p)

    def player_can_move(self, player: int | None = None) -> bool:
        """El jugador puede moverse (tiene energía Y hay casillas alcanzables)."""
        p = self.current_turn if player is None else player
        return (
            self.players[p].can_move()
            and has_moves(self.board, p)
        )

    def is_terminal(self) -> bool:
        """
        El juego termina cuando:
        - No quedan casillas de puntos, O
        - Ninguno de los dos jugadores puede moverse.
        """
        if not self.board.has_stars_remaining():
            return True
        both_stuck = (
            not self.player_can_move(0)
            and not self.player_can_move(1)
        )
        return both_stuck

    # ── Aplicar movimiento ───────────────────────────────────────────────────

    def apply_move(self, new_pos: tuple[int, int]) -> dict:
        """
        Aplica el movimiento del jugador actual a new_pos.

        Retorna un dict con el resumen del turno:
        {
            'player': int,
            'from': tuple,
            'to': tuple,
            'points_gained': int,
            'energy_gained': int,
            'energy_before': int,
            'energy_after': int,
        }
        """
        player    = self.current_player
        from_pos  = self.board.knight_positions[player.player_id]
        energy_before = player.energy

        # Gastar energía
        player.spend_energy()

        # Mover en el tablero y recoger beneficios
        pts, nrg = self.board.move_knight(player.player_id, new_pos)
        player.gain_points(pts)
        player.gain_energy(nrg)

        summary = {
            "player":        player.player_id,
            "from":          from_pos,
            "to":            new_pos,
            "points_gained": pts,
            "energy_gained": nrg,
            "energy_before": energy_before,
            "energy_after":  player.energy,
        }

        event = (
            f"Turno {self.turn_number} | {player.name}: "
            f"{from_pos} → {new_pos}"
        )
        if pts:
            event += f"  [+{pts} pts ★]"
        if nrg:
            event += f"  [+{nrg} ⚡]"
        self.history.append(event)

        self._advance_turn()
        return summary

    def apply_skip(self):
        """
        El jugador actual no tiene energía: pierde el turno y −3 puntos.
        El juego continúa si el otro jugador puede moverse.
        """
        player = self.current_player
        player.lose_points(NO_MOVE_PENALTY)

        event = (
            f"Turno {self.turn_number} | {player.name}: "
            f"SIN ENERGÍA — pierde turno (−{NO_MOVE_PENALTY} pts)"
        )
        self.history.append(event)
        self._advance_turn()

    # ── Avance de turno ──────────────────────────────────────────────────────

    def _advance_turn(self):
        self.turn_number  += 1
        self.current_turn  = 1 - self.current_turn

        if self.is_terminal():
            self._resolve_winner()

    def _resolve_winner(self):
        self.game_over = True
        p0 = self.players[0].points
        p1 = self.players[1].points
        if p0 > p1:
            self.winner = 0
        elif p1 > p0:
            self.winner = 1
        else:
            self.winner = None   # Empate

    # ── Copia para Minimax ───────────────────────────────────────────────────

    def copy(self) -> "GameState":
        new_state = GameState.__new__(GameState)
        new_state.board        = self.board.copy()
        new_state.players      = [p.copy() for p in self.players]
        new_state.current_turn = self.current_turn
        new_state.turn_number  = self.turn_number
        new_state.game_over    = self.game_over
        new_state.winner       = self.winner
        new_state.history      = []   # El historial no se necesita en el árbol
        return new_state

    # ── Representación ───────────────────────────────────────────────────────

    def __str__(self) -> str:
        lines = [
            f"\n{'─'*48}",
            f"  Turno {self.turn_number}  —  "
            f"Juega: {self.current_player.name}",
            f"{'─'*48}",
            f"  {self.players[0]}",
            f"  {self.players[1]}",
            f"{'─'*48}",
            f"  ★ restantes: {len(self.board.star_cells)}"
            f"   ⚡ restantes: {len(self.board.energy_cells)}",
            f"{'─'*48}",
        ]
        return "\n".join(lines)
