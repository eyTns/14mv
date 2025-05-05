from window.const import SPECIAL_CELLS
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
                valid = True
                cells = []
                for dr, dc in direction:
                    new_row, new_col = row + dr, col + dc
                    if not (0 <= new_row < height and 0 <= new_col < width):
                        valid = False
                        break
                    cells.append(applied_grid[new_row][new_col])
                if not valid:
                    continue

                if pattern_condition == "no_all_mines":
                    if all(cell == SPECIAL_CELLS["flag"] for cell in cells):
                        return False
                elif pattern_condition == "max_two_mines":
                    mine_count = sum(
                        1 for cell in cells if cell == SPECIAL_CELLS["flag"]
                    )
                    if mine_count > 2:
                        return False
                elif pattern_condition == "no_all_numbers":
                    if all(cell not in [-1, -2] for cell in cells):
                        return False
                elif pattern_condition == "no_center_mine_only":
                    if cells[0] == SPECIAL_CELLS["flag"]:
                        if all(
                            cell not in [SPECIAL_CELLS["flag"], SPECIAL_CELLS["blank"]]
                            for cell in cells[1:]
                        ):
                            return False
                        flag_count = sum(
                            1 for cell in cells[1:] if cell == SPECIAL_CELLS["flag"]
                        )
                        if flag_count >= 2:
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
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < height and 0 <= new_col < width:
                        pattern_cells.append((new_row, new_col))
                    else:
                        valid = False

                blank_cells = []
                num_blanks = 0
                existing_mines = 0
                existing_numbers = 0

                if pattern_condition == "no_center_mine_only":
                    center_cell = pattern_cells[0]
                    other_cells = pattern_cells[1:]
                else:
                    if not valid:
                        continue

                for r, c in pattern_cells:
                    cell_value = grid[r][c]
                    if cell_value == SPECIAL_CELLS["blank"]:
                        blank_cells.append((r, c))
                        num_blanks += 1
                    elif cell_value == SPECIAL_CELLS["flag"]:
                        existing_mines += 1
                    else:
                        existing_numbers += 1
                blank_cells.sort()

                cases = []
                if not blank_cells:
                    continue
                elif pattern_condition == "no_all_numbers":
                    if existing_mines > 0:
                        continue
                    cases = list(range(1, 2**num_blanks))
                elif pattern_condition == "no_all_mines":
                    if existing_numbers > 0:
                        continue
                    cases = list(range(2**num_blanks - 1))
                elif pattern_condition == "max_two_mines":
                    if existing_mines > 2:
                        continue
                    max_additional_mines = 2 - existing_mines
                    for case in range(2**num_blanks):
                        if bin(case).count("1") <= max_additional_mines:
                            cases.append(case)
                elif pattern_condition == "no_center_mine_only":
                    center_r, center_c = center_cell
                    # print(f"*** {center_cell} ******************")
                    if grid[center_r][center_c] not in [-1, -2]:
                        continue
                    for case in range(2**num_blanks):
                        if center_cell in blank_cells:
                            center_index = blank_cells.index(center_cell)
                            is_center_mine = (case & (1 << center_index)) != 0
                            other_mines_count = existing_mines
                            for i in range(num_blanks):
                                if i != center_index and (case & (1 << i)) != 0:
                                    other_mines_count += 1
                        else:
                            is_center_mine = (
                                grid[center_r][center_c] == SPECIAL_CELLS["flag"]
                            )
                            other_mines_count = existing_mines - int(is_center_mine)
                            other_mines_count += bin(case).count("1")
                        if not is_center_mine:
                            cases.append(case)
                        elif other_mines_count == 1:
                            cases.append(case)
                    # print(is_center_mine, other_mines_count)
                    # print(blank_cells, cases)

                if cases:
                    expanded_regions.append(ExpandedRegion(blank_cells, cases))

    return expanded_regions
