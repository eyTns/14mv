from window.const import RULE_Q, RULE_T, RULE_U, SPECIAL_CELLS
from window.region import ExpandedRegion, Region

####################################


def is_valid_case_for_rule(
    applied_grid: list[list[int]],
    rule: dict,
) -> bool:
    height = len(applied_grid)
    width = len(applied_grid[0])
    rule_directions = rule["directions"]
    pattern_condition = rule["pattern_condition"]
    for row in range(height):
        for col in range(width):
            for direction in rule_directions:

                if pattern_condition == "no_all_mines":
                    valid = True
                    all_mines = True
                    for dr, dc in direction:
                        new_row, new_col = row + dr, col + dc
                        if not (0 <= new_row < height and 0 <= new_col < width):
                            valid = False
                            break
                        cell = applied_grid[new_row][new_col]
                        if cell != SPECIAL_CELLS["flag"]:
                            all_mines = False
                    if not valid:
                        continue
                    if all_mines:
                        return False

                elif pattern_condition == "no_all_numbers":
                    valid = True
                    all_numbers = True
                    for dr, dc in direction:
                        new_row, new_col = row + dr, col + dc
                        if not (0 <= new_row < height and 0 <= new_col < width):
                            valid = False
                            break
                        cell = applied_grid[new_row][new_col]
                        if cell in [-1, -2]:
                            all_numbers = False
                    if not valid:
                        continue
                    if all_numbers:
                        return False

    return True


def filter_cases_by_rule(
    expanded_region: ExpandedRegion,
    grid: list[list[int]],
    rule: dict,
) -> ExpandedRegion:
    blank_cells = expanded_region.blank_cells
    cases = expanded_region.cases
    filtered_cases = []
    for case in cases:
        applied_grid = [row[:] for row in grid]
        for idx, cell in enumerate(blank_cells):
            row, col = cell
            if case & (1 << idx):
                applied_grid[row][col] = SPECIAL_CELLS["flag"]
            else:
                applied_grid[row][col] = SPECIAL_CELLS["star"]
        if is_valid_case_for_rule(applied_grid, rule):
            filtered_cases.append(case)

    return ExpandedRegion(blank_cells=blank_cells, cases=filtered_cases)


################################


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


################################


def get_expanded_regions_by_rule(grid, rule) -> list[ExpandedRegion]:
    height = len(grid)
    width = len(grid[0])
    directions = rule["directions"]
    pattern_condition = rule["pattern_condition"]
    expanded_regions = []

    for row in range(height):
        for col in range(width):
            for direction in directions:
                pattern_cells = []
                valid = True
                for dr, dc in direction:
                    new_row = row + dr
                    new_col = col + dc
                    if not (0 <= new_row < height and 0 <= new_col < width):
                        valid = False
                        break
                    pattern_cells.append((new_row, new_col))
                if not valid:
                    continue
                blank_cells = []
                condition_met = False
                for r, c in pattern_cells:
                    cell_value = grid[r][c]
                    if cell_value == SPECIAL_CELLS["blank"]:
                        blank_cells.append((r, c))
                    elif pattern_condition == "no_all_numbers":
                        if cell_value == SPECIAL_CELLS["flag"]:
                            condition_met = True
                            break
                    elif pattern_condition == "no_all_mines":
                        if cell_value not in [-1, -2]:
                            condition_met = True
                            break
                if condition_met or not blank_cells:
                    continue

                num_blanks = len(blank_cells)
                cases = []
                if pattern_condition == "no_all_numbers":
                    cases = list(range(1, 2**num_blanks))
                elif pattern_condition == "no_all_mines":
                    cases = list(range(2**num_blanks - 1))
                if cases:
                    expanded_regions.append(ExpandedRegion(blank_cells, cases))
    return expanded_regions


# def get_quad_expanded_regions(grid) -> list:
#     """Rule Q: 모든 쿼드에는 지뢰가 1개 이상 있다"""
#     return get_expanded_regions_by_rule(grid, RULE_Q)


# def get_triplet_expanded_regions(grid) -> list:
#     """Rule T: 모든 연속된 3개의 셀에는 숫자가 1개 이상 있다"""
#     return get_expanded_regions_by_rule(grid, RULE_T)


# def get_single_expanded_regions(grid) -> list:
#     """Rule U: 모든 연속된 2개의 셀에는 숫자가 1개 이상 있다"""
#     return get_expanded_regions_by_rule(grid, RULE_U)
