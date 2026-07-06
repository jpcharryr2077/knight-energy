"""
test_game_state.py
Pruebas unitarias — PlayerState, GameState, reglas de turno.
"""

import sys, os, random, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameState, PlayerState, INITIAL_ENERGY, NO_MOVE_PENALTY
from game.knight import get_valid_moves


class TestPlayerState(unittest.TestCase):

    def setUp(self):
        self.p = PlayerState(0, "Máquina")

    def test_initial_energy(self):
        self.assertEqual(self.p.energy, INITIAL_ENERGY)

    def test_initial_points(self):
        self.assertEqual(self.p.points, 0)

    def test_can_move_with_energy(self):
        self.assertTrue(self.p.can_move())

    def test_cannot_move_without_energy(self):
        self.p.energy = 0
        self.assertFalse(self.p.can_move())

    def test_spend_energy_decrements(self):
        self.p.spend_energy()
        self.assertEqual(self.p.energy, INITIAL_ENERGY - 1)

    def test_gain_points(self):
        self.p.gain_points(5)
        self.assertEqual(self.p.points, 5)

    def test_lose_points(self):
        self.p.gain_points(10)
        self.p.lose_points(3)
        self.assertEqual(self.p.points, 7)

    def test_lose_points_goes_negative(self):
        self.p.lose_points(5)
        self.assertEqual(self.p.points, -5)

    def test_gain_energy(self):
        self.p.gain_energy(4)
        self.assertEqual(self.p.energy, INITIAL_ENERGY + 4)

    def test_copy_is_independent(self):
        c = self.p.copy()
        c.energy = 0
        self.assertEqual(self.p.energy, INITIAL_ENERGY)

    def test_repr_contains_name(self):
        self.assertIn("Máquina", repr(self.p))


class TestGameStateInit(unittest.TestCase):

    def setUp(self):
        random.seed(10)
        self.gs = GameState()

    def test_machine_starts(self):
        self.assertEqual(self.gs.current_turn, 0)

    def test_turn_number_starts_at_1(self):
        self.assertEqual(self.gs.turn_number, 1)

    def test_not_game_over_initially(self):
        self.assertFalse(self.gs.game_over)

    def test_winner_is_none_initially(self):
        self.assertIsNone(self.gs.winner)

    def test_both_players_exist(self):
        self.assertEqual(len(self.gs.players), 2)

    def test_current_player_is_machine(self):
        self.assertEqual(self.gs.current_player.player_id, 0)

    def test_waiting_player_is_human(self):
        self.assertEqual(self.gs.waiting_player.player_id, 1)

    def test_not_terminal_initially(self):
        self.assertFalse(self.gs.is_terminal())

    def test_history_empty_initially(self):
        self.assertEqual(len(self.gs.history), 0)


class TestApplyMove(unittest.TestCase):

    def setUp(self):
        random.seed(20)
        self.gs = GameState()

    def _first_move(self, pid=0):
        return get_valid_moves(self.gs.board, pid)[0]

    def test_apply_move_decrements_energy(self):
        before = self.gs.players[0].energy
        self.gs.apply_move(self._first_move())
        self.assertEqual(self.gs.players[0].energy, before - 1)

    def test_apply_move_advances_turn(self):
        self.gs.apply_move(self._first_move())
        self.assertEqual(self.gs.current_turn, 1)

    def test_apply_move_increments_turn_number(self):
        self.gs.apply_move(self._first_move())
        self.assertEqual(self.gs.turn_number, 2)

    def test_apply_move_updates_knight_position(self):
        dest = self._first_move()
        self.gs.apply_move(dest)
        self.assertEqual(self.gs.board.knight_positions[0], dest)

    def test_apply_move_records_history(self):
        self.gs.apply_move(self._first_move())
        self.assertEqual(len(self.gs.history), 1)

    def test_apply_move_summary_keys(self):
        summary = self.gs.apply_move(self._first_move())
        for key in ("player","from","to","points_gained","energy_gained",
                    "energy_before","energy_after"):
            self.assertIn(key, summary)

    def test_apply_move_summary_player_is_0(self):
        summary = self.gs.apply_move(self._first_move())
        self.assertEqual(summary["player"], 0)

    def test_apply_move_star_adds_points(self):
        from game.board import StarCell
        gs = GameState()
        # Colocar estrella de valor 9 en primer destino válido
        dest = get_valid_moves(gs.board, 0)[0]
        gs.board.grid[dest[0]][dest[1]] = StarCell(9)
        gs.board.star_cells[dest] = gs.board.grid[dest[0]][dest[1]]
        summary = gs.apply_move(dest)
        self.assertEqual(summary["points_gained"], 9)
        self.assertEqual(gs.players[0].points, 9)

    def test_apply_move_energy_adds_energy(self):
        from game.board import EnergyCell, EmptyCell
        gs = GameState()
        dest = get_valid_moves(gs.board, 0)[0]
        # Asegurar casilla limpia y colocar energía
        if dest in gs.board.star_cells:
            del gs.board.star_cells[dest]
        gs.board.grid[dest[0]][dest[1]] = EnergyCell(5)
        gs.board.energy_cells[dest] = gs.board.grid[dest[0]][dest[1]]
        before = gs.players[0].energy
        summary = gs.apply_move(dest)
        self.assertEqual(summary["energy_gained"], 5)
        # energía_after = before - 1 (costo) + 5 (recarga) = before + 4
        self.assertEqual(gs.players[0].energy, before + 4)


class TestApplySkip(unittest.TestCase):

    def setUp(self):
        random.seed(30)
        self.gs = GameState()
        self.gs.players[0].energy = 0

    def test_skip_deducts_penalty(self):
        before = self.gs.players[0].points
        self.gs.apply_skip()
        self.assertEqual(self.gs.players[0].points, before - NO_MOVE_PENALTY)

    def test_skip_advances_turn(self):
        self.gs.apply_skip()
        self.assertEqual(self.gs.current_turn, 1)

    def test_skip_records_history(self):
        self.gs.apply_skip()
        self.assertTrue(any("SIN ENERGÍA" in e for e in self.gs.history))

    def test_skip_increments_turn_number(self):
        self.gs.apply_skip()
        self.assertEqual(self.gs.turn_number, 2)


class TestTerminalAndWinner(unittest.TestCase):

    def setUp(self):
        random.seed(40)
        self.gs = GameState()

    def test_terminal_when_no_stars(self):
        self.gs.board.star_cells.clear()
        self.assertTrue(self.gs.is_terminal())

    def test_resolve_winner_machine(self):
        self.gs.players[0].points = 20
        self.gs.players[1].points = 10
        self.gs.board.star_cells.clear()
        self.gs._resolve_winner()
        self.assertEqual(self.gs.winner, 0)

    def test_resolve_winner_human(self):
        self.gs.players[0].points = 5
        self.gs.players[1].points = 15
        self.gs.board.star_cells.clear()
        self.gs._resolve_winner()
        self.assertEqual(self.gs.winner, 1)

    def test_resolve_winner_draw(self):
        self.gs.players[0].points = 10
        self.gs.players[1].points = 10
        self.gs.board.star_cells.clear()
        self.gs._resolve_winner()
        self.assertIsNone(self.gs.winner)

    def test_resolve_winner_sets_game_over(self):
        self.gs.board.star_cells.clear()
        self.gs._resolve_winner()
        self.assertTrue(self.gs.game_over)


class TestGameStateCopy(unittest.TestCase):

    def setUp(self):
        random.seed(50)
        self.gs = GameState()

    def test_copy_turn_independent(self):
        c = self.gs.copy()
        moves = get_valid_moves(self.gs.board, 0)
        self.gs.apply_move(moves[0])
        self.assertEqual(c.turn_number, 1)

    def test_copy_board_independent(self):
        c    = self.gs.copy()
        dest = get_valid_moves(self.gs.board, 0)[0]
        orig = self.gs.board.knight_positions[0]
        self.gs.apply_move(dest)
        self.assertEqual(c.board.knight_positions[0], orig)

    def test_copy_players_independent(self):
        c = self.gs.copy()
        self.gs.players[0].energy = 0
        self.assertEqual(c.players[0].energy, INITIAL_ENERGY)

    def test_copy_history_not_shared(self):
        c = self.gs.copy()
        self.gs.history.append("test event")
        self.assertEqual(len(c.history), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
