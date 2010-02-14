"""
 Sudoku model
"""


class Square(object):
	""" 
	A square on the board.
	This object is used so that i have a reference to the area, and i can index by
	both rows and columns. It evaluates to the number it holds to simplify
	checks for complete games, and possible moves.
	"""
	def __init__(self, num):
		self.value = num
		if not num:
			self.options = set(range(1,10))
		else:
			self.options = set([num])
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
		if not self.value:
			return "_"
		return str(self.value)
	def set(self, options):
		if len(options) == 1:
			self.value = options.pop() 
			self.options = options
			return True
		self.options = options
		return False

class SudokuBoard(object):
	" Model of a Sudoku board, with convenience functions "

	def __init__(self, initial_state=None):
		if not initial_state:
			initial_state = []
			for i in range(9):
				initial_state.append(list(map(int, "0"*9)))
		# index rows
		self.rows = []
		for r in range(9):
			self.rows.append([])
			for c in range(9):
				self.rows[r].append(Square(initial_state[r][c]))
		# index cols
		self.cols = []
		for c in range(9):
			self.cols.append([])
			for r in range(9):
				self.cols[c].append(self.rows[r][c])

	def __repr__(self):
		" return the board as a string "
		s = ""
		for r in range(9):
			s += ("%s%s%s " * 3) % tuple(map(str, self.rows[r])) + "\n"
			if r % 3 == 2:
				s += "\n"
		return s


	def show_options(self):
		" return a representation of the board based on the options per square "
		s = ""
		for r in range(9):
			s += ("%s%s%s " * 3) % tuple(map(lambda sq: "["+str(len(sq.options))+"]", self.rows[r])) + "\n"
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
		Determins if one of the options for this square is the only possibily
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


class Solver(object):
	" Methods to solve the puzzle "
	def __init__(self, board):
		self.puzzle = board

	def run(self):
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
			
			#print self.puzzle
			#print self.puzzle.show_options()
			if self.puzzle.solved():
				print self.puzzle
				print "Game won!"
				return



if __name__ == "__main__":
	from boards import *
	s = Solver(SudokuBoard(board_hard))
	s.run()

