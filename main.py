import numpy as np

EMPTY = 0
HINT = -1
BLOCKED = -2

DOWN = 'down'
RIGHT = 'right'


class Cell:
    def __init__(self, loc, cat):
        self.loc = loc
        self.cat = cat


class Clue:
    def __init__(self, dir, length, goal_sum):
        self.dir = dir
        self.length = length
        self.goal_sum = goal_sum
        self.loc = None


class ClueCell(Cell):
    def __init__(self, loc, down_clue, right_clue):
        super().__init__(loc, cat=HINT)
        self.down_clue = down_clue
        if down_clue is not None:
            self.down_clue.loc = self.loc
        self.right_clue = right_clue
        if right_clue is not None:
            self.right_clue.loc = self.loc


class BlockCell(Cell):
    def __init__(self, loc):
        super().__init__(loc, cat=BLOCKED)


class NumberCell(Cell):
    def __init__(self, loc, val=0):
        super().__init__(loc, cat=EMPTY)
        self.val = val


class Puzzle:
    def __init__(self, h, w, cells):
        self.h = h
        self.w = w
        self.cells = cells
        self.clues = self.build_clues()
        self.board = self.setup_board()
        self.display_board()

    def display_board(self):
        for i in range(self.h):
            for j in range(self.w):
                print("|", end="")
                cell = self.board[i][j]
                if cell.cat == BLOCKED:
                    print(f"   X   ", end="")
                elif cell.cat == HINT:
                    if cell.down_clue is None:
                        print(f'   \{cell.right_clue.goal_sum if cell.right_clue.goal_sum > 9 else " " + str(cell.right_clue.goal_sum)} ', end="")
                    elif cell.right_clue is None:
                        print(f' {cell.down_clue.goal_sum if cell.down_clue.goal_sum > 9 else " " + str(cell.down_clue.goal_sum)}\   ', end="")
                    else:
                        print(f' {cell.down_clue.goal_sum if cell.down_clue.goal_sum > 9 else " " + str(cell.down_clue.goal_sum)}\{cell.right_clue.goal_sum if cell.right_clue.goal_sum > 9 else " " + str(cell.right_clue.goal_sum)} ', end="")
                elif cell.cat == EMPTY:
                    print(f'   {cell.val}   ', end="")
            print("|")

        print("\n\n\n\n")

    def build_clues(self):
        clues = []
        for cell in self.cells:
            if cell.cat == HINT:
                if cell.down_clue is not None:
                    clues.append(cell.down_clue)
                if cell.right_clue is not None:
                    clues.append(cell.right_clue)
        return clues

    def setup_board(self):
        board = [[NumberCell((i, j)) for j in range(self.w)] for i in range(self.h)]
        for cell in self.cells:
            board[cell.loc[0]][cell.loc[1]] = cell
        return board

    def get_cell_group(self, clue):
        cell_group = []
        if clue.dir == DOWN:
            for i in range(clue.length):
                cell_group.append(self.board[clue.loc[0] + i + 1][clue.loc[1]])
        elif clue.dir == RIGHT:
            for i in range(clue.length):
                cell_group.append(self.board[clue.loc[0]][clue.loc[1] + i + 1])
        return cell_group

    def assign_clue(self, clue, value_set):
        if clue.dir == DOWN:
            for i in range(clue.length):
                self.board[clue.loc[0] + i + 1][clue.loc[1]].val = value_set.pop(0)
        elif clue.dir == RIGHT:
            for i in range(clue.length):
                self.board[clue.loc[0]][clue.loc[1] + i + 1].val = value_set.pop(0)

    def is_clue_assigned(self, clue):
        return self.count_unassigned_clue(clue) == 0

    def count_unassigned_clue(self, clue):
        cell_group = self.get_cell_group(clue)
        unassigned_count = 0
        for cell in cell_group:
            if cell.val == 0:
                unassigned_count += 1
        return unassigned_count

    def is_complete(self):
        is_complete = True
        for i in range(self.h):
            for j in range(self.w):
                if self.board[i][j].cat == EMPTY and self.board[i][j].val == 0:
                    is_complete = False
        return is_complete

    def is_consistent(self):
        for clue in self.clues:
            cell_group = self.get_cell_group(clue)
            if self.is_clue_assigned(clue):
                current_sum = 0
                values = []
                for cell in cell_group:
                    values.append(cell.val)
                    current_sum += cell.val
                if current_sum != clue.goal_sum or any(values.count(x) > 1 for x in values):
                    return False
        return True


import copy
from operator import itemgetter

class Solver:
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def solve(self):
        solution = self.backtracking(self.puzzle)
        if solution is not None:
            solution.display_board()
            puzzle = solution
        else:
            print("No solution found!")

    def backtracking(self, puzzle):
        return self.recursive_backtracking(copy.deepcopy(puzzle))

    def recursive_backtracking(self, assignment):
        if assignment.is_complete() and assignment.is_consistent():
            print("Puzzle solved :)")
            return assignment
        clue = self.select_unassigned_clue(assignment)
        if clue is not None:
            cell_group = assignment.get_cell_group(clue)
            value_sets = self.generate_value_sets(clue, cell_group, assignment)
            for value_set in value_sets:
                if self.is_consistent(clue, copy.deepcopy(value_set), copy.deepcopy(assignment)):
                    assignment.assign_clue(clue, value_set)
                    assignment.display_board()
                    result = self.recursive_backtracking(copy.deepcopy(assignment))
                    if result is not None:
                        return result

        return None

    def select_unassigned_clue(self, assignment):
        for clue in assignment.clues:
            if not assignment.is_clue_assigned(clue):
                return clue

    def generate_value_sets(self, clue, cell_group, assignment):
        value_sets = []
        assigned_cells = []
        unassigned_cells = []
        allowed_values = copy.deepcopy(NUMBERS)
        for cell in cell_group:
            if cell.val == 0:
                unassigned_cells.append(cell)
            else:
                if cell.val in allowed_values:
                    allowed_values.remove(cell.val)
                assigned_cells.append(cell)
        current_sum = 0
        for cell in assigned_cells:
            current_sum += cell.val
        net_goal_sum = clue.goal_sum - current_sum
        net_cell_count = clue.length - len(assigned_cells)
        unassigned_value_sets = self.generate_sum_combinations(net_goal_sum, net_cell_count, allowed_values)
        for unassigned_value_set in unassigned_value_sets:
            variable_set = copy.deepcopy(cell_group)
            value_set = []
            for cell in variable_set:
                if cell.val == 0:
                    value_set.append(unassigned_value_set.pop(0))
                else:
                    value_set.append(cell.val)
            value_sets.append(value_set)
        return value_sets

    def generate_sum_combinations(self, n, k, allowed_values):
        if k == 1 and n in allowed_values:
            return [[n]]
        combos = []
        for i in allowed_values:
            allowed_values_copy = copy.deepcopy(allowed_values)
            allowed_values_copy.remove(i)
            if n - i > 0:
                combos += [[i] + combo for combo in self.generate_sum_combinations(n - i, k - 1, allowed_values_copy)]
        for combo in combos:
            if any(combo.count(x) > 1 for x in combo):
                combos.remove(combo)
        return combos

    def is_consistent(self, clue, value_set, assignment):
        assignment.assign_clue(clue, value_set)
        assignment.display_board()
        return assignment.is_consistent()


class IntelligentSolver(Solver):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    def select_unassigned_clue(self, assignment):
        clue_list = []
        partial_assigned_list = []
        unassigned_list = []
        for clue in assignment.clues:
            if not assignment.is_clue_assigned(clue):
                unassigned_count = assignment.count_unassigned_clue(clue)
                if unassigned_count == clue.length:
                    unassigned_list.append((clue, unassigned_count))
                else:
                    partial_assigned_list.append((clue, unassigned_count))
        unassigned_list.sort(key=itemgetter(1))
        partial_assigned_list.sort(key=itemgetter(1))
        clue_list = partial_assigned_list + unassigned_list
        return clue_list[0][0]


# main
import copy
import timeit

DOWN = 'down'
RIGHT = 'right'

NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

def read_puzzle(data):
    rows = [row.strip('|').strip() for row in data.strip().split('\n')]

    entries = []

    for row in rows:
        row_entries = [entry.strip() for entry in row.split('|')]
        entries.append(row_entries)

    cells = []
    for i in range(len(entries)):
        for j in range(len(entries[0])):
            if entries[i][j] == '':
                continue
            elif entries[i][j] == 'X':
                cells.append(BlockCell((i, j)))
            elif entries[i][j][:1] == '\\':
                dc, rc = entries[i][j].split('\\')
                rc = int(rc)
                cells.append(ClueCell((i, j), None, Clue(RIGHT, entries[i].count(''), rc)))
            elif entries[i][j][-1:] == '\\':
                dc, rc = entries[i][j].split('\\')
                dc = int(dc)
                cells.append(ClueCell((i, j), Clue(DOWN, entries[:][j].count(''), dc), None))
            else:
                dc, rc = map(int, entries[i][j].split('\\'))
                cells.append(ClueCell((i, j), Clue(DOWN, entries[:][j].count(''), dc), Clue(RIGHT, entries[i].count(''), rc)))

    return len(entries), len(entries[0]), cells

data0 = """
|   X  |  10\  |  3\  |
|  \\7 |      |       |
|  \\6  |      |       |
"""

data1 = """
|  X   | 11\  | 6\   |   X   |  X   |
|  \9  |      |      | 24\   |  X   |
|  \\20 |      |      |       | 4\   |
|  X   |  \\14 |      |       |      |
|  X   |  X   |  \8  |       |      |
"""

data2 = """
|   X   |   X   | 22\   | 12\   |   X   |
|   X   | 15\\12 |       |       |  9\   |
|  \\13  |       |       |       |       |
|  \\29  |       |       |       |       |
|   X   |  \\4   |       |       |   X   |
"""

dataset = [data0, data1, data2]
output = ''

for i in range(len(dataset)):
    h, w, cells = read_puzzle(dataset[i])
    puzzle = Puzzle(h, w, cells)

    # Unintelligent solver:
    unintelligent_solver = Solver(copy.deepcopy(puzzle))
    unintelligent_start = timeit.default_timer()
    unintelligent_solver.solve()
    unintelligent_stop = timeit.default_timer()
    unintelligent_time = unintelligent_stop - unintelligent_start

    # Intelligent solver:
    intelligent_solver = IntelligentSolver(copy.deepcopy(puzzle))
    intelligent_start = timeit.default_timer()
    intelligent_solver.solve()
    intelligent_stop = timeit.default_timer()
    intelligent_time = intelligent_stop - intelligent_start

    output += (f"Unintelligent solver solved puzzle {i + 1} in: {str(unintelligent_time)} sec\n")
    output += (f"Intelligent solver solved puzzle {i + 1} in: {str(intelligent_time)} sec\n\n")

print(output)
