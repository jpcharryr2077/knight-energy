"""
test_board.py
Pruebas unitarias — Board, celdas y colocación aleatoria.
"""

import sys, os, random, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.board import (
    Board, StarCell, EnergyCell, KnightCell, EmptyCell,
    STAR_VALUES, ENERGY_VALUES, BOARD_SIZE,
)


class TestCells(unittest.TestCase):

    def test_star_value(self):
        self.assertEqual(StarCell(9).value, 9)

    def test_star_repr_contains_symbol(self):
        self.assertIn("★", repr(StarCell(5)))

    def test_energy_value(self):
        self.assertEqual(EnergyCell(3).value, 3)

    def test_energy_repr_contains_symbol(self):
        self.assertIn("⚡", repr(EnergyCell(4)))

    def test_empty_repr_contains_dot(self):
        self.assertIn(".", repr(EmptyCell()))

    def test_knight_player0_symbol(self):
        self.assertIn("♘", repr(KnightCell(0)))

    def test_knight_player1_symbol(self):
        self.assertIn("♞", repr(KnightCell(1)))

    def test_knight_player_attribute(self):
        self.assertEqual(KnightCell(1).player, 1)


class TestBoardInitialization(unittest.TestCase):

    def setUp(self):
        random.seed(0)
        self.b = Board()

    def test_grid_dimensions(self):
        self.assertEqual(len(self.b.grid), BOARD_SIZE)
        for row in self.b.grid:
            self.assertEqual(len(row), BOARD_SIZE)

    def test_star_count_is_7(self):
        self.assertEqual(len(self.b.star_cells), 7)

    def test_energy_count_is_4(self):
        self.assertEqual(len(self.b.energy_cells), 4)

    def test_star_values_exact_set(self):
        self.assertEqual(
            sorted(c.value for c in self.b.star_cells.values()),
            sorted(STAR_VALUES),
        )

    def test_energy_values_exact_set(self):
        self.assertEqual(
            sorted(c.value for c in self.b.energy_cells.values()),
            sorted(ENERGY_VALUES),
        )

    def test_both_knights_placed(self):
        self.assertIn(0, self.b.knight_positions)
        self.assertIn(1, self.b.knight_positions)

    def test_knights_distinct_positions(self):
        self.assertNotEqual(
            self.b.knight_positions[0], self.b.knight_positions[1]
        )

    def test_knights_not_on_stars(self):
        for pid in (0, 1):
            self.assertNotIn(self.b.knight_positions[pid], self.b.star_cells)

    def test_knights_not_on_energy(self):
        for pid in (0, 1):
            self.assertNotIn(self.b.knight_positions[pid], self.b.energy_cells)

    def test_no_position_overlap_among_all_specials(self):
        all_pos = (
            list(self.b.star_cells) +
            list(self.b.energy_cells) +
            list(self.b.knight_positions.values())
        )
        self.assertEqual(len(all_pos), len(set(all_pos)))

    def test_grid_reflects_star_dict(self):
        for pos, cell in self.b.star_cells.items():
            self.assertIs(self.b.grid[pos[0]][pos[1]], cell)

    def test_grid_reflects_energy_dict(self):
        for pos, cell in self.b.energy_cells.items():
            self.assertIs(self.b.grid[pos[0]][pos[1]], cell)

    def test_different_seeds_produce_different_boards(self):
        random.seed(9999)
        b2 = Board()
        self.assertNotEqual(self.b.knight_positions, b2.knight_positions)

    def test_has_stars_remaining_initially_true(self):
        self.assertTrue(self.b.has_stars_remaining())

    def test_total_special_cells_is_11(self):
        self.assertEqual(self.b.total_special_cells(), 11)


class TestMoveKnight(unittest.TestCase):

    def setUp(self):
        random.seed(1)
        self.b = Board()

    def _empty_pos(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = (r, c)
                if (p not in self.b.star_cells
                        and p not in self.b.energy_cells
                        and p not in self.b.knight_positions.values()):
                    return p
        self.fail("No empty cell found")

    def test_move_to_empty_returns_zero_pts_nrg(self):
        pts, nrg = self.b.move_knight(0, self._empty_pos())
        self.assertEqual(pts, 0)
        self.assertEqual(nrg, 0)

    def test_move_updates_position(self):
        dest = self._empty_pos()
        self.b.move_knight(0, dest)
        self.assertEqual(self.b.knight_positions[0], dest)

    def test_move_old_cell_becomes_empty(self):
        old = self.b.knight_positions[0]
        self.b.move_knight(0, self._empty_pos())
        self.assertIsInstance(self.b.grid[old[0]][old[1]], EmptyCell)

    def test_move_to_star_returns_correct_points(self):
        pos, cell = next(iter(self.b.star_cells.items()))
        self.b.knight_positions[0] = (0, 0)
        pts, nrg  = self.b.move_knight(0, pos)
        self.assertEqual(pts, cell.value)
        self.assertEqual(nrg, 0)

    def test_move_to_star_removes_from_dict(self):
        pos = next(iter(self.b.star_cells))
        self.b.knight_positions[0] = (0, 0)
        self.b.move_knight(0, pos)
        self.assertNotIn(pos, self.b.star_cells)

    def test_move_to_star_removes_from_grid(self):
        pos = next(iter(self.b.star_cells))
        self.b.knight_positions[0] = (0, 0)
        self.b.move_knight(0, pos)
        self.assertNotIsInstance(self.b.grid[pos[0]][pos[1]], StarCell)

    def test_move_to_energy_returns_correct_energy(self):
        pos, cell = next(iter(self.b.energy_cells.items()))
        self.b.knight_positions[0] = (0, 0)
        pts, nrg  = self.b.move_knight(0, pos)
        self.assertEqual(pts, 0)
        self.assertEqual(nrg, cell.value)

    def test_move_to_energy_removes_from_dict(self):
        pos = next(iter(self.b.energy_cells))
        self.b.knight_positions[0] = (0, 0)
        self.b.move_knight(0, pos)
        self.assertNotIn(pos, self.b.energy_cells)

    def test_has_stars_remaining_false_when_all_consumed(self):
        b = Board()
        b.star_cells.clear()
        self.assertFalse(b.has_stars_remaining())

    def test_move_places_knight_cell_in_grid(self):
        dest = self._empty_pos()
        self.b.move_knight(0, dest)
        self.assertIsInstance(self.b.grid[dest[0]][dest[1]], KnightCell)


class TestBoundsAndCopy(unittest.TestCase):

    def setUp(self):
        random.seed(2)
        self.b = Board()

    def test_within_bounds_valid_corners(self):
        for r, c in [(0,0),(0,7),(7,0),(7,7)]:
            self.assertTrue(self.b.is_within_bounds(r, c))

    def test_outside_bounds_negative(self):
        self.assertFalse(self.b.is_within_bounds(-1, 0))
        self.assertFalse(self.b.is_within_bounds(0, -1))

    def test_outside_bounds_overflow(self):
        self.assertFalse(self.b.is_within_bounds(8, 0))
        self.assertFalse(self.b.is_within_bounds(0, 8))

    def test_copy_knight_move_independent(self):
        b2  = self.b.copy()
        orig = self.b.knight_positions[0]
        empty = next(
            (r, c) for r in range(8) for c in range(8)
            if (r,c) not in self.b.star_cells
            and (r,c) not in self.b.energy_cells
            and (r,c) not in self.b.knight_positions.values()
        )
        b2.move_knight(0, empty)
        self.assertEqual(self.b.knight_positions[0], orig)

    def test_copy_star_capture_independent(self):
        b2      = self.b.copy()
        star_pos = next(iter(b2.star_cells))
        b2.knight_positions[0] = (0, 0)
        b2.move_knight(0, star_pos)
        self.assertIn(star_pos, self.b.star_cells)

    def test_copy_energy_capture_independent(self):
        b2      = self.b.copy()
        nrg_pos = next(iter(b2.energy_cells))
        b2.knight_positions[0] = (0, 0)
        b2.move_knight(0, nrg_pos)
        self.assertIn(nrg_pos, self.b.energy_cells)


if __name__ == "__main__":
    unittest.main(verbosity=2)
