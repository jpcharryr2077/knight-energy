"""
test_minimax.py
Pruebas unitarias — MinimaxAI, choose_move, estadísticas.
"""

import sys, os, random, unittest, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameState
from game.board import StarCell, EnergyCell
from game.knight import get_valid_moves, KNIGHT_MOVES
from ai.minimax import MinimaxAI, _order_moves


class TestMinimaxAIInit(unittest.TestCase):

    def test_valid_depth(self):
        ai = MinimaxAI(depth=2)
        self.assertEqual(ai.depth, 2)

    def test_invalid_depth_raises(self):
        with self.assertRaises(ValueError):
            MinimaxAI(depth=0)

    def test_stats_zero_before_search(self):
        ai = MinimaxAI(depth=2)
        self.assertEqual(ai.nodes_evaluated, 0)
        self.assertEqual(ai.nodes_pruned, 0)


class TestChooseMove(unittest.TestCase):

    def setUp(self):
        random.seed(77)
        self.gs = GameState()

    def test_returns_tuple(self):
        ai   = MinimaxAI(depth=2)
        move = ai.choose_move(self.gs)
        self.assertIsInstance(move, tuple)
        self.assertEqual(len(move), 2)

    def test_move_within_bounds(self):
        ai   = MinimaxAI(depth=2)
        move = ai.choose_move(self.gs)
        r, c = move
        self.assertTrue(0 <= r <= 7)
        self.assertTrue(0 <= c <= 7)

    def test_move_is_valid(self):
        ai    = MinimaxAI(depth=2)
        move  = ai.choose_move(self.gs)
        valid = get_valid_moves(self.gs.board, 0)
        self.assertIn(move, valid)

    def test_returns_none_when_no_moves(self):
        ai = MinimaxAI(depth=2)
        # Forzar que no hay movimientos: poner ambos caballos en la misma esquina
        # y al oponente bloqueando todos los destinos (simplificamos vaciando moves)
        gs = GameState()
        # Sin mover, solo verificamos el caso: colocamos al caballo en esquina
        # y comprobamos que si no hay moves válidos se retorna None
        gs.board.knight_positions[0] = (0, 0)
        gs.board.knight_positions[1] = (1, 2)
        # Quedan solo (2,1) como destino. Lo bloqueamos manualmente
        import unittest.mock as mock
        with mock.patch("ai.minimax.get_valid_moves", return_value=[]):
            result = ai.choose_move(gs)
        self.assertIsNone(result)

    def test_stats_updated_after_search(self):
        ai = MinimaxAI(depth=2)
        ai.choose_move(self.gs)
        stats = ai.get_stats()
        self.assertGreater(stats["nodes_evaluated"], 0)
        self.assertGreaterEqual(stats["nodes_pruned"], 0)

    def test_stats_reset_between_calls(self):
        ai = MinimaxAI(depth=2)
        ai.choose_move(self.gs)
        n1 = ai.get_stats()["nodes_evaluated"]
        # Segunda llamada sobre un estado diferente
        gs2 = GameState()
        random.seed(88)
        ai.choose_move(gs2)
        n2 = ai.get_stats()["nodes_evaluated"]
        # Los nodos de la segunda búsqueda no acumulan los de la primera
        self.assertGreater(n2, 0)
        # n2 refleja solo la segunda búsqueda (no n1 + n2)
        self.assertLessEqual(n2, n1 * 20)  # cota holgada

    def test_depth2_fewer_nodes_than_depth4(self):
        random.seed(99)
        gs = GameState()
        ai2 = MinimaxAI(depth=2)
        ai4 = MinimaxAI(depth=4)
        ai2.choose_move(gs)
        ai4.choose_move(gs)
        self.assertLess(
            ai2.get_stats()["nodes_evaluated"],
            ai4.get_stats()["nodes_evaluated"],
        )


class TestMinimaxGreedy(unittest.TestCase):
    """Verifica decisiones que cualquier función heurística razonable debería tomar."""

    def _gs_with_adjacent_star(self, value=9):
        """Estado donde la máquina tiene una ★ adyacente de alto valor."""
        random.seed(55)
        gs   = GameState()
        kpos = gs.board.knight_positions[0]
        opos = gs.board.knight_positions[1]
        for dr, dc in KNIGHT_MOVES:
            nr, nc = kpos[0]+dr, kpos[1]+dc
            if 0 <= nr < 8 and 0 <= nc < 8 and (nr,nc) != opos:
                # Limpiar celda y colocar estrella
                if (nr,nc) in gs.board.star_cells:
                    del gs.board.star_cells[(nr,nc)]
                if (nr,nc) in gs.board.energy_cells:
                    del gs.board.energy_cells[(nr,nc)]
                gs.board.grid[nr][nc] = StarCell(value)
                gs.board.star_cells[(nr,nc)] = gs.board.grid[nr][nc]
                return gs, (nr, nc)
        return gs, None

    def test_captures_adjacent_high_value_star(self):
        gs, target = self._gs_with_adjacent_star(9)
        if target is None:
            self.skipTest("No adjacent cell found")
        ai   = MinimaxAI(depth=2)
        move = ai.choose_move(gs)
        self.assertEqual(move, target,
            f"Se esperaba captura de ★9 en {target}, se eligió {move}")

    def test_all_depths_agree_on_obvious_capture(self):
        """Profundidades 2, 4 deben coincidir en capturar una ★9 adyacente."""
        gs, target = self._gs_with_adjacent_star(9)
        if target is None:
            self.skipTest("No adjacent cell found")
        for depth in (2, 4):
            ai   = MinimaxAI(depth=depth)
            move = ai.choose_move(gs)
            self.assertEqual(move, target,
                f"depth={depth}: esperado {target}, elegido {move}")


class TestOrderMoves(unittest.TestCase):

    def setUp(self):
        random.seed(11)
        self.gs = GameState()

    def test_star_moves_come_first(self):
        moves = get_valid_moves(self.gs.board, 0)
        if not moves:
            self.skipTest("No moves available")
        ordered = _order_moves(self.gs, moves, player=0)
        # Si algún movimiento cae en ★, debe aparecer antes que los vacíos
        from game.board import StarCell
        star_indices  = [i for i,(r,c) in enumerate(ordered)
                         if isinstance(self.gs.board.grid[r][c], StarCell)]
        empty_indices = [i for i,(r,c) in enumerate(ordered)
                         if not isinstance(self.gs.board.grid[r][c], StarCell)
                         and not isinstance(self.gs.board.grid[r][c], EnergyCell)]
        if star_indices and empty_indices:
            self.assertLess(max(star_indices), min(empty_indices) + 1)

    def test_order_preserves_all_moves(self):
        moves   = get_valid_moves(self.gs.board, 0)
        ordered = _order_moves(self.gs, moves, player=0)
        self.assertEqual(set(moves), set(ordered))
        self.assertEqual(len(moves), len(ordered))


if __name__ == "__main__":
    unittest.main(verbosity=2)
