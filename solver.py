"""
 Sudoku model and solver.

 author: Daniel Nephin
"""

import re

class Square(object):
	""" 
	A square on the board.
	This object is used so that there is a reference to the area, and i can 
	index by both rows and columns. It evaluates to the number it holds to 
	simplify checks for complete games, and possible moves.
	"""
	def __init__(self, num):
		self.value = int(num)
		self.options = set([self.value]) if self.value else set(range(1,10))
		
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
		if len(options) == 1:
			self.value = options.pop() 
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
		for r in range(9):
			s += ("%s%s%s " * 3) % tuple(
				"[%s]" % len(sq.options) for sq in self.rows[r]) + "\n"
			if r % 3 ==  2:
				s += "\n"
		return s

	def find_options_for(self, r, c):
		"""
		Return a list of possible options for a square on the board. Checks
		the row, column, and cube for existing numbers. 
		"""
		options = set(range(1,10))
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

		def deduce_options(related_list):
			others_options = set()
			for square in related_list:
				if square is target:
					continue
				others_options |= set(square.options)
			options = target.options - others_options
			if len(options) == 1:
				return options
			return False
			
		option = deduce_options(self.rows[r][0:c] + self.rows[r][c+1:10])
		if option:
			return option
		option = deduce_options(self.cols[c][0:r] + self.cols[c][r+1:10])
		if option:
			return option
		option = deduce_options(self.get_cube(r, c))
		if option:
			return option
		return False


	def get_cube(self, r, c):
		" Return the local cube of 9 squares for a given row and column, as a list. "
		row_min = r / 3 * 3
		col_min = c / 3 * 3
		cube = []
		for i in range(3):
			cube.extend(self.rows[row_min+i][col_min:col_min+3])
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


def solve(self, board):
	" Solve the puzzle "
	while True:
		for r in range(9):
			for c in range(9):
				square = self.puzzle.rows[r][c]
				# skip solved squares
				if square:
					continue
				options = self.puzzle.find_options_for(r, c)
				if square.set(options):
					print "found %s,%s through find_options" % (r,c)
					continue
				option = self.puzzle.identify_only_possibility(r, c)
				if option:
					print "found %s,%s through identify_only" % (r,c)
					square.set(option)
		
		print self.puzzle
		print self.puzzle.show_options()
		if self.puzzle.solved():
			print self.puzzle
			print "Game won!"
			return



if __name__ == "__main__":
	from boards import *
	solve(SudokuBoard(board_easy))

