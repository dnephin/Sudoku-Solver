"""
 Sudoku model and solver.

 author: Daniel Nephin
"""

import re
from itertools import ifilterfalse, chain, ifilter
import logging

log = logging

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

	def find_options_for(self, r, c, index):
		"""
		Return a list of possible options for a square on the board. Checks
		the row, column, and cube for existing numbers. 
		"""
		
		other_index = self.cols if index == self.rows else self.rows

		options = index[r][c].options
		options -= set(index[r])
		options -= set(other_index[c])
		options -= set(self.get_cube(r, c, index))
		return options


	def identify_only_possibility(self, r, c):
		"""
		Determines if one of the options for this square is the only possibility
		for that option in a row, column, or cube. Making it the correct option.
		"""
		target = self.rows[r][c]

		for related_list in (self.rows[r], self.cols[c], self.get_cube(r, c, self.rows)):
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
		solitary_rows = set()
		solitary_cols = set()

		solved_count = 0

		for r in range(row_min, row_min+3):
			for c in range(col_min, col_min+3):
				if not self.rows[r][c]:	
					solitary_rows.add(r)
					solitary_cols.add(c)
			
		if len(solitary_rows) == 1:
			solved_count += self._update_options(self.rows, self.cols, 
					solitary_rows.pop(), row_min, col_min)
			
		if len(solitary_cols) == 1:
			solved_count += self._update_options(self.cols, self.rows, 
					solitary_cols.pop(), col_min, row_min)

		return solved_count


	def _update_options(self, pri_dir, sec_dir, selected, pri_min, sec_min):
		"""
		Helper function for find_isolated_lines.  Updates the options for other
		rows/cols aligned with the isolated row/col that was identified by
		find_isolated_lines.
		"""
		solved_count = 0

		restricted_options = set()
		for sec_index in range(sec_min,sec_min+3):
			restricted_options |= self.find_options_for(
					selected, sec_index, pri_dir)

		# get the other (row/col) of cubes that share this cubes (row/col)
		log.debug("Current state of game board:\n%", self)
		for p in ifilter(lambda i: i < sec_min or i > sec_min+2, range(9)):
			square = sec_dir[p][selected]
			if not square:
				d =  "cols" if (pri_dir == self.rows) else "rows"
				log.debug("Removing %s from %s %d" % (restricted_options, d, selected))
				square.options -= restricted_options
				if square.check():
					solved_count += 1
		return solved_count


	def get_cube(self, r, c, index):
		" Return the local cube of 9 squares for a given row and column, as a list. "
		row_min = r / 3 * 3
		col_min = c / 3 * 3
		cube = list(chain(
			*(r[col_min:col_min+3] for r in index[row_min:row_min+3])))
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
				if set(self.get_cube(r,c, self.rows)) != good_set:
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


	def check_board(self):
		"""
		Check all squares for completion.
		"""
		((s.check() for s in r) for r in self.rows)

	def find_number_pairs_in_cube(self, cube_r, cube_c):
		"""
		If two numbers are options in only two places within a cube, then all
		other options in that square should be removed, and other items checked.
		"""
		row_min = cube_r * 3
		col_min = cube_c * 3

		options = []
		pairs = []
		for square in self.get_cube(row_min, col_min, self.rows):
			if square or len(square.options) != 2:
				continue

			if square.options in options:
				pairs.append((square, options.pop(options.index(square))))
				continue

			options.append(square)

		# now remove this options from other squares in the cube
		for items in pairs:
			remove_options = items[0].options
			for square in self.get_cube(row_min, col_min, self.rows):
				if square or square is items[0] or square is items[1]:
					log.info("Removing %s from square in cube (%d,%s)" % (
							remove_options, row_min, col_min))
					square.options -= remove_options
			
				



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
				if square.set(board.find_options_for(r, c, board.rows)):
					log.info("found %s,%s through find_options" % (r,c))
					continue
				option = board.identify_only_possibility(r, c)
				if option:
					log.info("found %s,%s through identify_only" % (r,c))
					square.set(option)

		for cube_r in range(3):
			for cube_c in range(3):
				solved = board.find_isolation_lines(cube_r, cube_c)
				if solved:
					log.debug("Current state of game board:\n%", board)
					log.debug(board.show_options())
					log.info("found %d using find_isolation_lines." % solved)

		for cube_r in range(3):
			for cube_c in range(3):
				board.find_number_pairs_in_cube(cube_r, cube_c)
	
		board.check_board()

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
	logging.basicConfig(level=logging.INFO)

	board = solve(SudokuBoard(boards.board_hard2))
	print board
	print "Game won!" if board else "Lost!"

