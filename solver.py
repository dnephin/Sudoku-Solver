"""
 Sudoku model and solver.

 author: Daniel Nephin
"""

import re
from itertools import ifilterfalse, chain, ifilter

class Square(object):
	""" 
	A square on the board.
	This object is used so that there is a reference to the area, and i can 
	index by both rows and columns. It evaluates to the number it holds to 
	simplify checks for complete games, and possible moves.
	"""
	def __init__(self, num):
		self.value = int(num)
		self.options = set() if self.value else set(range(1,10))
		
	def __eq__(self, other):
		if hasattr(other, 'value'):
			return self.value == other.value
		return self.value == other
	def __ne__(self, other):
		return not self.__eq__(other)
	def __hash__(self):
		return self.value
	def __nonzero__(self):
		return bool(self.value)
	def __repr__(self):
		return "%r" % (self.value) if self.value else "_"
	def set(self, options):
		self.options = options
		return self.check()
	def check(self):
		if len(self.options) == 1:
			self.value = self.options.pop() 
			return True
		return False
		

class SudokuBoard(object):
	" Model of a Sudoku board, with convenience functions "

	def __init__(self, initial_state=None):
		self.rows = self.load_board(initial_state)

		if not self.rows:
			self.rows = [[Square(int(0)) for s in range(9)] for row in range(9)]

		# index cols
		self.cols = []
		for c in range(9):
			self.cols.append([])
			for r in range(9):
				self.cols[c].append(self.rows[r][c])


	def load_board(self, board):
		"""
		Load a board from a list of strings.
		"""
		if not board:
			return None
		if len(board) < 9:
			return None

		sboard = []
		for r in range(9):
			sboard.append([Square(s) for s in re.sub('\s+', '', board[r])])
		return sboard

	def __repr__(self):
		" return the board as a string "
		s = ""
		for r in range(9):
			s += ("%s%s%s " * 3) % tuple("%s" % s for s in self.rows[r]) + "\n"
			if r % 3 == 2:
				s += "\n"
		return s


	def show_options(self):
		" return a representation of the board based on the options per square "
		s = ""
		row_string = "[%9s] [%9s] [%9s]   " * 3 + "\n"
		for i in range(9):
			r = self.rows[i]
			s += row_string % tuple([("%s" * len(s.options)) % tuple(s.options) for s in r])
			if i % 3 ==  2:
				s += "\n"
		return s

	def find_options_for(self, r, c):
		"""
		Return a list of possible options for a square on the board. Checks
		the row, column, and cube for existing numbers. 
		"""
		options = self.rows[r][c].options
		options -= set(self.rows[r])
		options -= set(self.cols[c])
		options -= set(self.get_cube(r, c))
		return options


	def identify_only_possibility(self, r, c):
		"""
		Determines if one of the options for this square is the only possibility
		for that option in a row, column, or cube. Making it the correct option.
		"""
		target = self.rows[r][c]

		for related_list in (self.rows[r], self.cols[c], self.get_cube(r, c)):
			others_options = set()
			for square in ifilterfalse(lambda s: s is target, related_list):
				others_options |= set(square.options)
			options = target.options - others_options
			if len(options) == 1:
				return options
		return False


	def find_isolation_lines(self, cube_r, cube_c):
		"""
		Given a coordinate in a cube, find any isolated rows or column which 
		restrict an option to that row or column.  Then remove that number as 
		an option from any other cubes that are aligned with this cube.
		"""
		row_min = cube_r * 3
		col_min = cube_c * 3
		empty_rows = set()
		empty_cols = set()

		solved_count = 0

		for r in range(row_min, 3):
			for c in range(col_min, 3):
				if not self.rows[r][c]:	
					empty_rows.add(r)
					empty_rows.add(c)

		if len(empty_rows) == 1:
			restricted_options = set(
					s.options for s in self.rows[empty_rows[0]][col_min:col_min+3])

			# get the other rows of cubes that share this cubes rows
			for r in ifilter(lambda i: i < row_min and i > row_min+2, range(9)):
				for c in range(9):
					square = self.rows[r][c]
					if square:
						square.options -= restricted_options
						if square.check():
							solved_count += 1

		# TODO: refactor to function
		if len(empty_cols) == 1:
			restricted_options = set(
					s.options for s in self.cols[empty_cols[0]][row_min:row_min+3])

			# get the other rows of cubes that share this cubes rows
			for c in ifilter(lambda i: i < col_min and i > col_min+2, range(9)):
				for r in range(9):
					square = self.cols[c][r]
					if square:
						square.options -= restricted_options
						if square.check():
							solved_count += 1
		

	def get_cube(self, r, c):
		" Return the local cube of 9 squares for a given row and column, as a list. "
		row_min = r / 3 * 3
		col_min = c / 3 * 3
		cube = list(chain(
			*(r[col_min:col_min+3] for r in self.rows[row_min:row_min+3])))
		return cube


	def solved(self):
		" Returns true when the puzzle is complete "
		good_set = set(range(1,10))
		for r in self.rows:
			if set(r) != good_set:
				return False
		for c in self.cols:
			if set(c) != good_set:
				return False
		for r in range(0,9,3):
			for c in range(0,9,3):
				if set(self.get_cube(r,c)) != good_set:
					return False
		return True

	def get_status(self):
		"""
		Return a status tuple which represents the current state of the board
		being solved. The tuple is in the form (num_solved_squares, num_options).
		"""
		total_solved = 0
		total_options = 0
		
		for r in self.rows:
			for s in r:
				total_solved += int(bool(s))
				total_options += len(s.options)
		return (total_solved, total_options)


def solve(board, print_cycle=10):
	" Solve the puzzle "

	prev_status = None

	counter = 0

	while True:
		for r in range(9):
			for c in range(9):
				square = board.rows[r][c]
				# skip solved squares
				if square:
					continue
				if square.set(board.find_options_for(r, c)):
					print "found %s,%s through find_options" % (r,c)
					continue
				option = board.identify_only_possibility(r, c)
				if option:
					print "found %s,%s through identify_only" % (r,c)
					square.set(option)

		for cube_r in range(3):
			for cube_c in range(3):
				solved = board.find_isolation_lines(cube_r, cube_c)
				if solved:
					print "found %d using find isolation lines." % solved
		
		counter += 1
		if board.solved():
			print "Solved in %d rounds." % counter
			return board

		status = board.get_status()
		if status  == prev_status:
			print "Failed in %d rounds." % counter
			print board
			print board.show_options()
			return None

		prev_status = status

		if counter % print_cycle == print_cycle - 1:
			print board
			print board.show_options()



if __name__ == "__main__":
	import boards
	import sys

	board = solve(SudokuBoard(boards.board_erica))
	print board
	print "Game won!" if board else "Lost!"

