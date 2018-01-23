#!/usr/bin/env python3

# Solver for "The Ultimate Puzzle", YMIR, Inc

# Problem definition
#
# This is a simple tile puzzle where each piece has 8 different
# orientations (4 rotations, 2 sides). The objective is to find 4x4 tile
# solutions using all available pieces


# Approach
#
# Come up with a string representation for each of the pieces
# Use a 2D array to represent the "board" of pieces
#
# Brute force search.
# For each board on the work queue:
#  Try fit 1 new piece beside an existing piece in the board. 
#  If a piece fits, add the new board and list of remaining pieces to the
#  workqueue.
# Accept if all pieces are used, meaning the board is full


# Sample output

## Depth first search
# Found solutions:  189
# Solutions per second: 47.25
# Layouts explored:  79866
# Layouts per second: 19966.50
# Layouts queued:  165
# FDGE GHFC GDBG ABDC
# HGAF EEDH ACFF CCFD
# BFGG CDFE EBDC EFDA
# HACD EAGB CGDB CGBH

## Breadth first search
# Layouts explored:  480000
# Layouts queued:  443378
# Best solution found so far:
# DCAB CCFD GCBD BGGD
# BECD    _    _    _
#    _    _    _    _
#    _    _    _    _
# ['ACDH', 'ACFF', 'ADFE', 'AEBG', 'AFHG', 'BFGG', 'BGCH', 'CDFE', 'CFHG', 'DEEH', 'DFEG']


# The order that we push and pop boards from the workqueue determines
# whether the search is breadth first or depth first.
# 
# With depth-first, the next board to be taken from the queue is one that
# we recently added: e.g. if we have 12 pieces down, add 1 and push it
# to the queue, the next board has 13. In this way we explore the end of
# deep solution branches in the problem space first before either finding
# a solution, or having the trail run dry and backtracking a bit before
# continuing with other nearby solutions. The nice feature of this is low
# memory usage, as dead ends are quickly discarded before exploring more.
# 
# With breadth-first search, we end up enumerating every possible partially
# completed board combination on the queue before we ever reach a full 4x4
# square, which quickly runs out of memory. If memory weren't a problem,
# I think this would have the same runtime as depth first, except all
# the solutions would be found near the end of the program run.

########################################

import collections
import datetime

# pieces
# A = cross
# B = cross socket
# C = circle
# D = circle socket
# E = tree
# F = tree socket
# G = boat
# H = boat socket

#pidx = {
#        'north': 0,
#        (0, -1): 0,
#        'east': 1,
#        (1, 0): 1,
#        'south': 2,
#        (0, 1): 2,
#        'west': 3,
#        (-1, 0): 3
#        }

# TODO: Verify piece inputs and outputs against known good results online
input_pieces = [
        'EAGB',
        'CABD',
        'GCHB',
        'GEFD',
        'EADF',
        'CAHD',
        'CEFD',
        'CEBD',
        'CGDB',
        'CCFD',
        'AGHF',
        'GGBD',
        'GGBF',
        'EEDH',
        'GCFH',
        'ACFF'
        ]

matches = {
        'A': 'B',
        'B': 'A',
        'C': 'D',
        'D': 'C',
        'E': 'F',
        'F': 'E',
        'G': 'H',
        'H': 'G'
        }


def rotate_piece(piece):
    return piece[1:] + piece[0]


def flip_piece(piece):
    return piece[0] + piece[3] + piece[2] + piece[1]


def orientations(piece):
    results = [piece]
    for _ in range(3):
        results.append(rotate_piece(results[-1]))
    results.append(flip_piece(piece))
    for _ in range(3):
        results.append(rotate_piece(results[-1]))
    return results


def piece_identity(piece):
    return sorted(orientations(piece))[0]


def board_to_str(board):
    return '\n'.join(' '.join('{:>4}'.format(piece) for piece in row) for row in board)


def check_piece_fits(board, piece, x, y):
    if (    # north
            (y == 0 or board[y-1][x] == '_' or board[y-1][x][2] == matches[piece[0]])
            # east
            and (x == len(board[y])-1 or board[y][x+1] == '_' or board[y][x+1][3] == matches[piece[1]])
            # south
            and (y == len(board)-1 or board[y+1][x] == '_' or board[y+1][x][0] == matches[piece[2]])
            # west
            and (x == 0 or board[y][x-1] == '_' or board[y][x-1][1] == matches[piece[3]])):
        return True
    return False


def next_free(board):
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] == '_':
                return x, y


def next_piece(pieces):
    for piece_idx in range(len(pieces)):
        npiece = pieces[piece_idx]
        npieces = pieces[:piece_idx] + pieces[piece_idx+1:]
        yield npiece, npieces


def possible_moves(board, pieces):
    x, y = next_free(board)
    for npiece, npieces in next_piece(pieces):
        for piece in orientations(npiece):
            if check_piece_fits(board, piece, x, y):
                nboard = list(map(list, board))
                nboard[y][x] = piece
                yield nboard, npieces


def accept(board, pieces):
    if len(pieces) == 0:
        return True
    return False


def solve(board, pieces):
    worklist = collections.deque([(board, pieces)])

    min_board = board
    min_pieces = pieces
    n_explored = 0

    while worklist:
        wboard, wpieces = worklist.pop()
        for nboard, npieces in possible_moves(wboard, wpieces):
            n_explored += 1

            if accept(nboard, npieces):
                yield nboard, n_explored, len(worklist)
                continue

            worklist.append((nboard, npieces))     # Depth first search
#            worklist.appendleft((nboard, npieces))     # Breadth first search

            if len(npieces) <= len(min_pieces):
                min_board = nboard
                min_pieces = npieces
            if n_explored % 10000 == 0:
#                print('\033[H\033[J') # clear screen
                print('Layouts explored: ', n_explored)
                print('Layouts queued: ', len(worklist))
                print('Best solution found so far:')
                print(board_to_str(min_board))
                print(npieces)
                print()
    return


def main():
    print('Starting...')
        # board[0][0]
    start_board = [
            ['_', '_', '_', '_'],
            ['_', '_', '_', '_'],
            ['_', '_', '_', '_'],
            ['_', '_', '_', '_']]
                       # board[3][3]
    print(board_to_str(start_board))
    pieces = sorted(piece_identity(p) for p in input_pieces)
    print(pieces)

    start_time = datetime.datetime.now() 
    n_solutions = 0
    for solved_board, n_explored, n_queued in solve(start_board, pieces):
        n_solutions += 1
        seconds = (datetime.datetime.now() - start_time).seconds + 1
        print('Found solutions: ', n_solutions)
        print('Solutions per second: {0:.2f}'.format(n_solutions / seconds))
        print('Layouts explored: ', n_explored)
        print('Layouts per second: {0:.2f}'.format(n_explored / seconds))
        print('Layouts queued: ', n_queued)
        print(board_to_str(solved_board))
        print()
    return


if __name__ == '__main__':
    main()
