

import unittest
from solver import Square, SudokuBoard 




class TestSquare(unittest.TestCase):
	
	def setUp(self):
		self.s = Square(0)

	def test_init(self):
		s = Square(9)
		self.assertEquals(s.value, 9)
		self.assertEquals(s.options, set())

		s = Square(0)
		self.assertEquals(s.value, 0)
		self.assertEquals(s.options, set(range(1,10)))

		s = Square('1')
		self.assertEquals(s.value, 1)
		self.assertEquals(s.options, set())

	def test_eq(self):
		s = Square(4)
		self.assertEquals(s, 4)
		self.assertNotEquals(s, 3)

	def test_nonzero(self):
		s = Square(1)
		self.assertFalse(self.s)
		self.assertTrue(s)

	def test_repr(self):
		s = Square(3)
		self.assertEquals("%r" % self.s, "_")
		self.assertEquals("%s" % s, "3")

	def test_set(self):
		options = set([1,4,5])
		self.assertFalse(self.s.set(options))
		self.assertEquals(self.s.options, options)

		self.assertTrue(self.s.set(set([1])))
		self.assertEquals(self.s.options, set([]))
		self.assertEquals(self.s.value, 1)

	def test_check(self):
		s = Square(0)
		s.options = set([1])
		self.assertTrue(s.check())
		self.assertFalse(Square(0).check())

class TestSudobuBoard(unittest.TestCase):


	_input = [
	'104  000  306',
	'809  030  570',
	'000  070  100',

	'426  000  003',
	'087  006  012',
	'300  000  009',

	'241  900  030',
	'000  200  080',
	'700  503  000'
	]

	_solved = [
	'174 895 326', 
	'869 132 574', 
	'532 674 198', 

	'426 719 853', 
	'987 356 412', 
	'315 428 769', 

	'241 987 635', 
	'653 241 987', 
	'798 563 241', 
	]

	def setUp(self):
		self.board = SudokuBoard(self._input)


	def test_init(self):
		self.assertEquals(type(self.board.rows[0][2]), type(Square(4)))
		self.assertEquals(self.board.rows[8][3], Square(5))


	def test_repr(self):
		" only test that it does not throw errors. "
		repr(self.board)

	def test_show_options(self):
		" only test that it does not throw errors. "
		self.board.show_options()


	def test_find_options_for(self):
		""
		# TODO
	
	def test_identify_only_possibility(self):
		""
		# TODO

	def test_find_isolation_lines(self):
		""
		# TODO

	def test_get_cube(self):
		self.assertEquals(self.board.get_cube(2, 1, self.board.rows), [1,0,4,8,0,9,0,0,0])
		self.assertEquals(self.board.get_cube(8,8, self.board.rows), [0,3,0,0,8,0,0,0,0])


	def test_solved(self):
		solved = SudokuBoard(self._solved)
		self.assertTrue(solved.solved())
		self.assertFalse(self.board.solved())

	def test_get_status(self):
		solved = SudokuBoard(self._solved)
		self.assertEquals(self.board.get_status(), (32,441))
		self.assertEquals(solved.get_status(), (81, 0))

	def test_all_squares(self):
		self.assertEquals(len(list(self.board.all_squares())), 81)

	def test_check_board(self):
		" check no errors thrown. "
		self.board.check_board()

if __name__ == "__main__":
	unittest.main()
