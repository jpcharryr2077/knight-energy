"""
test_heuristic.py
Pruebas unitarias — función heurística y sus componentes.
"""

import sys, os, random, unittest, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameState
from game.board import StarCell, EnergyCell
from game.knight import get_valid_moves, KNIGHT_MOVES
from ai.heuristic import (
    evaluate, evaluate_verbose,
    _reachable_specials, _count_valid_moves, _terminal_bonus,
    W_POINTS, W_ENERGY, W_STARS_REACHABLE,
)


class TestEvaluateTerminal(unittest.TestCase):

    def _terminal(self, winner):
        random.seed(0)
        gs = GameState()
        gs.game_over = True
        gs.winner    = winner
        return gs

    def test_machine_wins_returns_inf(self):
        self.assertEqual(evaluate(self._terminal(0)), math.inf)

    def test_human_wins_returns_neg_inf(self):
        self.assertEqual(evaluate(self._terminal(1)), -math.inf)

    def test_draw_returns_zero(self):
        self.assertEqual(evaluate(self._terminal(None)), 0.0)


class TestEvaluateSign(unittest.TestCase):

    def setUp(self):
        random.seed(1)
        self.gs = GameState()

    def test_machine_ahead_in_points_positive(self):
        self.gs.players[0].points = 20
        self.gs.players[1].points = 5
        self.assertGreater(evaluate(self.gs), 0)

    def test_human_ahead_in_points_negative(self):
        self.gs.players[0].points = 5
        self.gs.players[1].points = 20
        self.assertLess(evaluate(self.gs), 0)

    def test_equal_points_near_zero_or_small(self):
        self.gs.players[0].points = 10
        self.gs.players[1].points = 10
        # Puede no ser exactamente 0 por los otros componentes,
        # pero no debe ser un valor extremo
        val = evaluate(self.gs)
        self.assertFalse(math.isinf(val))

    def test_machine_more_energy_positive_contribution(self):
        gs = GameState()
        gs.players[0].points = 0
        gs.players[1].points = 0
        gs.players[0].energy = 10
        gs.players[1].energy = 1
        self.assertGreater(evaluate(gs), 0)

    def test_value_scales_with_point_difference(self):
        gs1 = GameState()
        gs2 = GameState()
        gs1.players[0].points = 10; gs1.players[1].points = 0
        gs2.players[0].points = 20; gs2.players[1].points = 0
        self.assertGreater(evaluate(gs2), evaluate(gs1))


class TestEvaluateComponents(unittest.TestCase):

    def setUp(self):
        random.seed(2)
        self.gs = GameState()

    def test_reachable_specials_returns_tuple(self):
        result = _reachable_specials(self.gs, 0)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_reachable_specials_non_negative(self):
        s, e = _reachable_specials(self.gs, 0)
        self.assertGreaterEqual(s, 0)
        self.assertGreaterEqual(e, 0)

    def test_count_valid_moves_non_negative(self):
        self.assertGreaterEqual(_count_valid_moves(self.gs, 0), 0)

    def test_count_valid_moves_at_most_8(self):
        self.assertLessEqual(_count_valid_moves(self.gs, 0), 8)

    def test_terminal_bonus_range(self):
        for pid in (0, 1):
            mm = _count_valid_moves(self.gs, 0)
            hm = _count_valid_moves(self.gs, 1)
            bonus = _terminal_bonus(self.gs, mm, hm)
            self.assertGreaterEqual(bonus, -1.0)
            self.assertLessEqual(bonus,    +1.0)

    def test_machine_no_moves_negative_bonus(self):
        bonus = _terminal_bonus(self.gs, machine_moves=0, human_moves=5)
        self.assertLess(bonus, 0)

    def test_human_no_moves_positive_bonus(self):
        bonus = _terminal_bonus(self.gs, machine_moves=5, human_moves=0)
        self.assertGreater(bonus, 0)

    def test_adjacent_star_increases_score(self):
        """
        Mismos puntos/energía, pero con ★9 adyacente a la máquina → h mayor.
        Ambos estados parten del mismo tablero; en gs_star se reemplaza una
        casilla vacía adyacente a la máquina por ★9 (y se elimina de gs_base).
        La diferencia proviene exclusivamente del componente Δ★_alcanzables.
        """
        random.seed(2)
        gs_base = GameState()

        knight_pos = gs_base.board.knight_positions[0]
        other_pos  = gs_base.board.knight_positions[1]

        # Encontrar destino en L adyacente que sea casilla vacía en ambos estados
        target = None
        for dr, dc in KNIGHT_MOVES:
            nr, nc = knight_pos[0]+dr, knight_pos[1]+dc
            if not (0 <= nr < 8 and 0 <= nc < 8):
                continue
            if (nr, nc) == other_pos:
                continue
            if (nr, nc) not in gs_base.board.star_cells and \
               (nr, nc) not in gs_base.board.energy_cells:
                target = (nr, nc)
                break

        if target is None:
            self.skipTest("No se encontró casilla vacía adyacente al caballo")

        from game.board import EmptyCell
        gs_star = gs_base.copy()
        # gs_base: casilla vacía (no aporta al componente ★_alcanzables)
        gs_base.board.grid[target[0]][target[1]] = EmptyCell()

        # gs_star: misma casilla con ★9 → sube Δ★_alcanzables en +1
        gs_star.board.grid[target[0]][target[1]] = StarCell(9)
        gs_star.board.star_cells[target] = gs_star.board.grid[target[0]][target[1]]

        self.assertGreater(evaluate(gs_star), evaluate(gs_base),
            msg="Añadir ★9 adyacente debe aumentar la evaluación heurística")

    def test_evaluate_verbose_returns_same_as_evaluate(self):
        import io, contextlib
        gs = GameState()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            verbose_val = evaluate_verbose(gs)
        self.assertAlmostEqual(verbose_val, evaluate(gs), places=5)


class TestWeightsConsistency(unittest.TestCase):
    """Verifica que los pesos tienen los valores documentados."""

    def test_points_weight_dominates(self):
        self.assertGreater(W_POINTS, W_ENERGY)
        self.assertGreater(W_POINTS, W_STARS_REACHABLE)

    def test_stars_weight_greater_than_energy_weight(self):
        self.assertGreater(W_STARS_REACHABLE, W_ENERGY)

    def test_all_weights_positive(self):
        from ai.heuristic import (W_ENERGY_REACHABLE, W_MOBILITY,
                                   W_TERMINAL_BONUS)
        for w in [W_POINTS, W_ENERGY, W_STARS_REACHABLE,
                  W_ENERGY_REACHABLE, W_MOBILITY, W_TERMINAL_BONUS]:
            self.assertGreater(w, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
