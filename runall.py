

import boards
import sys
import logging
from solver import solve, SudokuBoard
logging.basicConfig(level=logging.WARN)

for n, b in boards.__dict__.iteritems():
	if not n.startswith('board'):
		continue
	print "\n\n%s" % n
	board = solve(SudokuBoard(b))
	print board
	print "Game won!" if board else "Lost!"

