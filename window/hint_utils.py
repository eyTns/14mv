from itertools import combinations
from window.region import Region
from window.const import SPECIAL_CELLS


def find_single_clickable_cells(regions_info: list[Region]):
    hints = set()

    for region in regions_info:
        mines_needed = region.mines_needed
        if region.mines_needed == 0 and len(region.blank_cells) > 0:
            for blank_r, blank_c in region.blank_cells:
                hints.add(("safe", (blank_r, blank_c)))
        elif mines_needed == len(region.blank_cells) > 0:
            for blank_r, blank_c in region.blank_cells:
                hints.add(("mine", (blank_r, blank_c)))

    return hints


def deduce_double_inequalities(r1: Region, r2: Region):
    hints = set()

    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r1on = r1b - r2b
    r1m = r1.mines_needed
    r2m = r2.mines_needed

    if r1m - r2m >= len(r1on):
        for blank_r, blank_c in r2b - r1b:
            hints.add(("safe", (blank_r, blank_c)))
        for blank_r, blank_c in r1b - r2b:
            hints.add(("mine", (blank_r, blank_c)))

    return hints


def find_double_areas(regions_info: list[Region]):
    hints = set()
    for r1, r2 in combinations(regions_info, 2):
        hints.update(deduce_double_inequalities(r1, r2))
        hints.update(deduce_double_inequalities(r2, r1))
    return hints


def find_triple_inclusions(regions_info: list[Region]):
    hints = set()

    for r1, r2, r3 in combinations(regions_info, 3):
        if not (r1.blank_cells & r2.blank_cells):
            r12 = Region(
                mines_needed=r1.mines_needed + r2.mines_needed,
                blank_cells=r1.blank_cells | r2.blank_cells,
            )
            hints.update(deduce_double_inequalities(r12, r3))
            hints.update(deduce_double_inequalities(r3, r12))
        if not (r2.blank_cells & r3.blank_cells):
            r23 = Region(
                mines_needed=r2.mines_needed + r3.mines_needed,
                blank_cells=r2.blank_cells | r3.blank_cells,
            )
            hints.update(deduce_double_inequalities(r23, r1))
            hints.update(deduce_double_inequalities(r1, r23))
        if not (r3.blank_cells & r1.blank_cells):
            r31 = Region(
                mines_needed=r3.mines_needed + r1.mines_needed,
                blank_cells=r3.blank_cells | r1.blank_cells,
            )
            hints.update(deduce_double_inequalities(r31, r2))
            hints.update(deduce_double_inequalities(r2, r31))
    return hints


def deduce_triple_inequalities(r1: Region, r2: Region, r3: Region):
    hints = set()
    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r3b = r3.blank_cells
    r1on = r1b - r2b - r3b
    r1m = r1.mines_needed
    r2m = r2.mines_needed
    r3m = r3.mines_needed
    r1n = r1.numbers_needed
    r2n = r2.numbers_needed
    r3n = r3.numbers_needed
    if r1m - r2m - r3m + 1 >= len(r1on):
        safe_cells = (r2b & r3b) - r1b
        if safe_cells:
            for blank_r, blank_c in safe_cells:
                hints.add(("safe", (blank_r, blank_c)))
    if r1n - r2n - r3n + 1 >= len(r1on):
        mine_cells = (r2b & r3b) - r1b
        if mine_cells:
            for blank_r, blank_c in mine_cells:
                hints.add(("mine", (blank_r, blank_c)))
    return hints


def find_triple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3 in combinations(regions_info, 3):
        hints.update(deduce_triple_inequalities(r1, r2, r3))
        hints.update(deduce_triple_inequalities(r2, r3, r1))
        hints.update(deduce_triple_inequalities(r3, r1, r2))
        if deep and hints:
            print(f"Triple hints: {hints}")
            return hints
    return hints


def deduce_quadruple_inequalities(r1: Region, r2: Region, r3: Region, r4: Region):
    hints = set()

    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r3b = r3.blank_cells
    r4b = r4.blank_cells
    r1on = r1b - r2b - r3b - r4b
    r1m = r1.mines_needed
    r2m = r2.mines_needed
    r3m = r3.mines_needed
    r4m = r4.mines_needed
    r1n = r1.numbers_needed
    r2n = r2.numbers_needed
    r3n = r3.numbers_needed
    r4n = r4.numbers_needed

    if r1m - r2m - r3m - r4m + 1 >= len(r1on):
        safe23 = r2b & r3b
        safe34 = r3b & r4b
        safe42 = r4b & r2b
        safe_cells = (safe23 | safe34 | safe42) - r1b
        if safe_cells:
            for blank_r, blank_c in safe_cells:
                hints.add(("safe", (blank_r, blank_c)))

    if r1n - r2n - r3n - r4n + 1 >= len(r1on):
        mine23 = r2b & r3b
        mine34 = r3b & r4b
        mine42 = r4b & r2b
        mine_cells = (mine23 | mine34 | mine42) - r1b
        if mine_cells:
            for blank_r, blank_c in mine_cells:
                hints.add(("mine", (blank_r, blank_c)))

    return hints


def find_quadruple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3, r4 in combinations(regions_info, 4):
        hints.update(deduce_quadruple_inequalities(r1, r2, r3, r4))
        hints.update(deduce_quadruple_inequalities(r2, r3, r4, r1))
        hints.update(deduce_quadruple_inequalities(r3, r4, r1, r2))
        hints.update(deduce_quadruple_inequalities(r4, r1, r2, r3))
        if deep and hints:
            print(f"Quadruple hints: {hints}")
            return hints
    return hints


def find_two_pairs_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3, r4 in combinations(regions_info, 4):
        r1b = r1.blank_cells
        r2b = r2.blank_cells
        r3b = r3.blank_cells
        r4b = r4.blank_cells
        if r1b & r2b == r3b & r4b:
            r12 = Region(
                mines_needed=r1.mines_needed + r2.mines_needed,
                blank_cells=r1.blank_cells | r2.blank_cells,
            )
            r34 = Region(
                mines_needed=r3.mines_needed + r4.mines_needed,
                blank_cells=r3.blank_cells | r4.blank_cells,
            )
            hints.update(deduce_double_inequalities(r12, r34))
            hints.update(deduce_double_inequalities(r34, r12))
        if r1b & r3b == r2b & r4b:
            r13 = Region(
                mines_needed=r1.mines_needed + r3.mines_needed,
                blank_cells=r1.blank_cells | r3.blank_cells,
            )
            r24 = Region(
                mines_needed=r2.mines_needed + r4.mines_needed,
                blank_cells=r2.blank_cells | r4.blank_cells,
            )
            hints.update(deduce_double_inequalities(r13, r24))
            hints.update(deduce_double_inequalities(r24, r13))
        if r1b & r4b == r2b & r3b:
            r14 = Region(
                mines_needed=r1.mines_needed + r4.mines_needed,
                blank_cells=r1.blank_cells | r4.blank_cells,
            )
            r23 = Region(
                mines_needed=r2.mines_needed + r3.mines_needed,
                blank_cells=r2.blank_cells | r3.blank_cells,
            )
            hints.update(deduce_double_inequalities(r14, r23))
            hints.update(deduce_double_inequalities(r23, r14))
        if deep and hints:
            print(f"Two Pair hints: {hints}")
            return hints
    return hints


def find_flag_adjacent_cells(grid):
    """Rule U: 지뢰에 이웃한 셀은 숫자이다"""
    height = len(grid)
    width = len(grid[0])
    hints = set()

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for row in range(height):
        for col in range(width):
            if grid[row][col] == SPECIAL_CELLS["blank"]:
                for dx, dy in directions:
                    new_row, new_col = row + dx, col + dy
                    if 0 <= new_row < height and 0 <= new_col < width:
                        if grid[new_row][new_col] == SPECIAL_CELLS["flag"]:
                            hints.add(("safe", (row, col)))
                            break
    return hints


def find_remaining_cells_from_quad(grid):
    """Rule Q: 2*2 중 3개의 셀이 숫자이고 나머지가 빈칸이면 그건 지뢰다"""
    height = len(grid)
    width = len(grid[0])
    hints = set()
    for row in range(height - 1):
        for col in range(width - 1):
            cells = [(row, col), (row, col + 1), (row + 1, col), (row + 1, col + 1)]
            blank_count = 0
            blank_pos = None
            for r, c in cells:
                if grid[r][c] == SPECIAL_CELLS["blank"]:
                    blank_count += 1
                    blank_pos = (r, c)
                elif grid[r][c] == SPECIAL_CELLS["flag"]:
                    blank_count = -1
                    break
            if blank_count == 1:
                hints.add(("mine", blank_pos))
    return hints


def find_single_cell_from_triplet(grid):
    """Rule T: 가로, 세로, 대각선으로 연속한 3개의 셀 중 2개가 지뢰이고 나머지가 빈칸이면 그건 숫자다"""
    height = len(grid)
    width = len(grid[0])
    hints = set()
    directions = [
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]
    for row in range(height):
        for col in range(width):
            for direction in directions:
                cells = []
                valid = True
                flag_count = 0
                blank_pos = None
                for dr, dc in direction:
                    new_row, new_col = row + dr, col + dc
                    if not (0 <= new_row < height and 0 <= new_col < width):
                        valid = False
                        break

                    cell_value = grid[new_row][new_col]
                    cells.append((new_row, new_col, cell_value))
                    if cell_value == SPECIAL_CELLS["flag"]:
                        flag_count += 1
                    elif cell_value == SPECIAL_CELLS["blank"]:
                        if blank_pos is None:
                            blank_pos = (new_row, new_col)
                        else:
                            valid = False
                            break

                if valid and flag_count == 2 and blank_pos is not None:
                    hints.add(("safe", blank_pos))
    return hints
