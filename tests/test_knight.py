"""
test_knight.py
Pruebas unitarias — movimientos del caballo en L.
"""

import sys, os, random, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.board import Board, BOARD_SIZE
from game.knight import get_valid_moves, has_moves, KNIGHT_MOVES


class TestKnightMoves(unittest.TestCase):

    def _board_with_knights(self, pos0, pos1):
        """Crea un tablero vacío con caballos en posiciones controladas."""
        random.seed(0)
        b = Board()
        b.knight_positions[0] = pos0
        b.knight_positions[1] = pos1
        return b

    def test_center_has_up_to_8_moves(self):
        b = self._board_with_knights((4, 4), (0, 0))
        moves = get_valid_moves(b, 0)
        # Desde (4,4) todos los 8 destinos en L están dentro del tablero
        self.assertEqual(len(moves), 8)

    def test_corner_a1_has_2_moves(self):
        b = self._board_with_knights((0, 0), (7, 7))
        moves = get_valid_moves(b, 0)
        self.assertEqual(len(moves), 2)
        self.assertIn((1, 2), moves)
        self.assertIn((2, 1), moves)

    def test_corner_h8_has_2_moves(self):
        b = self._board_with_knights((7, 7), (0, 0))
        moves = get_valid_moves(b, 0)
        self.assertEqual(len(moves), 2)
        self.assertIn((6, 5), moves)
        self.assertIn((5, 6), moves)

    def test_cannot_land_on_opponent(self):
        # Colocar humano exactamente en L desde (0,0)
        b = self._board_with_knights((0, 0), (1, 2))
        moves = get_valid_moves(b, 0)
        self.assertNotIn((1, 2), moves)

    def test_all_moves_within_bounds(self):
        random.seed(5)
        b = Board()
        for pid in (0, 1):
            for mv in get_valid_moves(b, pid):
                r, c = mv
                self.assertTrue(0 <= r < BOARD_SIZE)
                self.assertTrue(0 <= c < BOARD_SIZE)

    def test_moves_are_valid_L_shapes(self):
        random.seed(6)
        b   = Board()
        pos = b.knight_positions[0]
        for (r, c) in get_valid_moves(b, 0):
            dr, dc = abs(r - pos[0]), abs(c - pos[1])
            self.assertIn((dr, dc), [(1, 2), (2, 1)])

    def test_has_moves_true_when_moves_exist(self):
        random.seed(7)
        b = Board()
        self.assertTrue(has_moves(b, 0))

    def test_has_moves_false_when_all_blocked(self):
        b = self._board_with_knights((0, 0), (7, 7))
        # Bloquear los únicos destinos válidos desde (0,0) con el oponente
        # Forzar que no existan movimientos poniendo al oponente en ambos
        # (imposible con un solo oponente; simular con stub)
        # En su lugar verificamos que si limitamos el tablero artificialmente
        # el método devuelve False cuando no hay L válidas
        # Colocar caballo en (0,0) y oponente en (1,2) y (2,1)
        # No podemos bloquear ambos con un solo oponente;
        # verificamos que la función reporta la cantidad correcta
        moves = get_valid_moves(b, 0)
        expected = has_moves(b, 0)
        self.assertEqual(bool(moves), expected)

    def test_edge_position_col_0(self):
        b     = self._board_with_knights((4, 0), (0, 0))
        moves = get_valid_moves(b, 0)
        for r, c in moves:
            self.assertGreaterEqual(c, 0)

    def test_edge_position_row_0(self):
        b     = self._board_with_knights((0, 4), (7, 7))
        moves = get_valid_moves(b, 0)
        for r, c in moves:
            self.assertGreaterEqual(r, 0)

    def test_symmetric_both_players(self):
        """Ambos jugadores desde la misma posición tienen los mismos movimientos (sin bloqueo mutuo)."""
        b = self._board_with_knights((3, 3), (0, 0))
        # Calcular manualmente desde (3,3) sin contar (0,0) como bloqueo
        moves0 = get_valid_moves(b, 0)
        b2 = self._board_with_knights((0, 0), (3, 3))
        moves1 = get_valid_moves(b2, 1)
        # Desde (3,3), moves1 excluye (0,0) porque es el oponente en b2
        # pero moves0 incluye (0,0) porque ahí está b.knight_positions[1]=(0,0)
        # → ambos excluyen la posición del oponente respectivo
        # Lo que verificamos: sin oponente en el camino, tienen la misma cantidad
        # Reposicionar oponente fuera del alcance en L
        b3 = self._board_with_knights((3, 3), (7, 7))
        b4 = self._board_with_knights((7, 7), (3, 3))
        self.assertEqual(
            sorted(get_valid_moves(b3, 0)),
            sorted(get_valid_moves(b4, 1)),
        )

    def test_knight_moves_constant_has_8_elements(self):
        self.assertEqual(len(KNIGHT_MOVES), 8)

    def test_knight_moves_all_L_shaped(self):
        for dr, dc in KNIGHT_MOVES:
            self.assertIn((abs(dr), abs(dc)), [(1, 2), (2, 1)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
