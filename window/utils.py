import time
from itertools import combinations
from math import comb

import pyautogui
import pygetwindow as gw

from window.const import (
    CLICK_COORDINATES,
    INITIAL_POSITIONS,
    INITIAL_POSITIONS_2,
    NEIGHBORS,
    RULE_Q,
    RULE_T,
    RULE_U,
    RULE_A,
    # RULE_B,
    get_rule_B,
    RULE_H,
    RULE_D1,
    RULE_D2,
    SPECIAL_CELLS,
    TOTAL_MINES,
    MAX_CASES,
)
from window.image_utils import PuzzleStatus, capture_window_screenshot, completed_check
from window.region import (
    ExpandedRegion,
    Region,
    RuleRegion,
)
from window.rules import (
    is_valid_case_for_rule,
    filter_cases_by_rule,
    get_expanded_regions_by_rule,
)
from window.hint_utils import (
    find_double_areas,
    find_quadruple_inequalities,
    find_single_clickable_cells,
    find_triple_inclusions,
    find_triple_inequalities,
    find_two_pairs_inequalities,
    find_flag_adjacent_cells,
    find_remaining_cells_from_quad,
    find_single_cell_from_triplet,
)


def get_neighboring_cells(row, col, grid):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = row + dr, col + dc
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r != row or c != col):
                neighbors.append(grid[r][c])
    return neighbors


def get_neighboring_cells_with_indices(row, col, grid):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = row + dr, col + dc
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r != row or c != col):
                neighbors.append((grid[r][c], r, c))
    return neighbors


def get_total_mines(rule, cell_size):
    if rule[0] == "B":
        return TOTAL_MINES["B"][cell_size - 5]
    elif rule[0] in "DAHU":
        return TOTAL_MINES["DAHU"][cell_size - 5]
    else:
        return TOTAL_MINES["STANDARD"][cell_size - 5]


def get_neighbors(rule):
    for key in ["V", "X", "X'", "K"]:
        if rule.endswith(key):
            return NEIGHBORS[key]
    else:
        return NEIGHBORS["STANDARD"]


def get_rule_regions(grid, rule) -> list[Region]:
    # ["V", "X", "X'", "K", "B"]
    regions = []

    if rule in ["V", "X", "X'", "K"]:
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] >= 0:
                    mines_needed = grid[r][c]
                    neighboring_blanks = set()
                    for dr, dc in NEIGHBORS[rule]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                            if grid[nr][nc] == -1:
                                neighboring_blanks.add((nr, nc))
                            elif grid[nr][nc] == -2:
                                mines_needed -= 1
                    if neighboring_blanks:
                        regions.append(
                            Region(
                                mines_needed=mines_needed,
                                blank_cells=neighboring_blanks,
                            )
                        )
        return regions
    elif rule == "B":
        mine_value = get_total_mines(rule, len(grid)) // len(grid)
        for row in range(len(grid)):
            mines_needed = mine_value
            blanks = set()
            for col in range(len(grid[0])):
                if grid[row][col] == -2:
                    mines_needed -= 1
                elif grid[row][col] == -1:
                    blanks.add((row, col))
            if blanks:
                regions.append(
                    Region(
                        mines_needed=mines_needed,
                        blank_cells=blanks,
                    )
                )
        for col in range(len(grid[0])):
            mines_needed = mine_value
            blanks = set()
            for row in range(len(grid)):
                if grid[row][col] == -2:
                    mines_needed -= 1
                elif grid[row][col] == -1:
                    blanks.add((row, col))
            if blanks:
                regions.append(
                    Region(
                        mines_needed=mines_needed,
                        blank_cells=blanks,
                    )
                )
        return regions


def get_grid_region(grid, rule) -> Region:
    mines_needed = get_total_mines(rule, len(grid))
    blanks = set()
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == -2:
                mines_needed -= 1
            elif grid[r][c] == -1:
                blanks.add((r, c))
    return Region(
        mines_needed=mines_needed,
        blank_cells=blanks,
    )


def get_all_rule_regions(grid, rule) -> list[Region]:
    regions = []
    regionable_single = ["Q", "C", "T", "O", "D", "S", "T'", "D'", "A", "H"]
    if rule in regionable_single:
        regions.extend(get_rule_regions(grid, "V"))
    else:
        if rule == "V":
            regions.extend(get_rule_regions(grid, "V"))
        elif rule == "B":
            regions.extend(get_rule_regions(grid, "V"))
            regions.extend(get_rule_regions(grid, "B"))
        else:
            if rule.startswith("B"):
                regions.extend(get_rule_regions(grid, "B"))
            if rule.endswith("X"):
                regions.extend(get_rule_regions(grid, "X"))
            elif rule.endswith("X'"):
                regions.extend(get_rule_regions(grid, "X'"))
            elif rule.endswith("K"):
                regions.extend(get_rule_regions(grid, "K"))
    return regions


def analyze_exregions_by_rule(grid, rule) -> list:
    regions = []
    rows, cols = len(grid), len(grid[0])

    if rule in ["W", "W'", "L", "P", "M", "N"]:
        region_type = RuleRegion

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] >= 0:
                center = (r, c)
                cell_value = grid[r][c]
                pre_filled_mines = []
                pre_filled_numbers = []
                has_blank = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if not (0 <= nr < rows) or not (0 <= nc < cols):
                            pre_filled_numbers.append((nr, nc))
                            continue
                        neighbor_value = grid[nr][nc]
                        if neighbor_value == SPECIAL_CELLS["flag"]:
                            pre_filled_mines.append((nr, nc))
                        elif (
                            neighbor_value >= 0
                            or neighbor_value == SPECIAL_CELLS["question"]
                            or neighbor_value == SPECIAL_CELLS["star"]
                        ):
                            pre_filled_numbers.append((nr, nc))
                        elif neighbor_value == SPECIAL_CELLS["blank"]:
                            has_blank = True

                if has_blank:
                    region = region_type(
                        center=center,
                        number=cell_value,
                        pre_filled_mines=pre_filled_mines,
                        pre_filled_numbers=pre_filled_numbers,
                    )
                    regions.append(region)
    return regions


def analyze_exregions_by_right_side_rules(grid, rule) -> list:
    exregions = []
    rules_to_check = []
    if "M" in rule:
        rules_to_check.append("M")
    if "L" in rule:
        rules_to_check.append("L")
    if "W" in rule and "W'" not in rule:
        rules_to_check.append("W")
    if "N" in rule:
        rules_to_check.append("N")
    if "P" in rule:
        rules_to_check.append("P")
    if "W'" in rule:
        rules_to_check.append("W'")
    for rule in rules_to_check:
        for exregion in analyze_exregions_by_rule(grid, rule):
            exregions.append(ExpandedRegion.from_rule_region(exregion, rule))
    return exregions


def find_all_area_hints(regions, grid, rule):
    hints = set()
    if rule == "UW":
        hints.update(find_flag_adjacent_cells(grid))
    if "Q" in rule:
        hints.update(find_remaining_cells_from_quad(grid))
    if "T" in rule:
        hints.update(find_single_cell_from_triplet(grid))
    hints.update(find_single_clickable_cells(regions))
    hints.update(find_double_areas(regions))
    hints.update(find_triple_inclusions(regions[:200]))
    hints.update(find_triple_inequalities(regions[:200]))
    hints.update(find_quadruple_inequalities(regions[:60]))
    hints.update(find_two_pairs_inequalities(regions[:60]))
    return hints


def diff_regions(regions: list[Region]):
    while True:
        more_regions = []
        for ri, rj in combinations((regions), 2):
            if ri.total_blanks == rj.total_blanks:
                continue
            elif ri.total_blanks > rj.total_blanks:
                ri, rj = rj, ri
            if ri.blank_cells < rj.blank_cells:
                rk = rj - ri
                if not rk in regions and not rk in more_regions:
                    more_regions.append(rk)
                    if len(regions) + len(more_regions) >= 1000:
                        return regions + more_regions
        if more_regions:
            regions.extend(more_regions)
        else:
            return regions


def expand_regions(regions: list[Region], grid, rule) -> list[ExpandedRegion]:
    expanded_regions = []
    for region in regions:
        blank_cells = list(region.blank_cells)
        combinations_count = comb(len(blank_cells), region.mines_needed)
        if combinations_count > MAX_CASES:
            continue

        valid_mine_combinations = []
        for mines in combinations(blank_cells, region.mines_needed):
            numbers = [cell for cell in blank_cells if cell not in mines]
            applied_grid = [row[:] for row in grid]
            for row, col in mines:
                applied_grid[row][col] = SPECIAL_CELLS["flag"]
            for row, col in numbers:
                applied_grid[row][col] = SPECIAL_CELLS["star"]
            if "Q" in rule:
                if not is_valid_case_for_rule(applied_grid, RULE_Q):
                    continue
            if "T" in rule:
                if not is_valid_case_for_rule(applied_grid, RULE_T):
                    continue
            if "D" in rule and "D'" not in rule:
                # if not is_valid_case_for_rule(applied_grid, RULE_D1):
                #     continue
                # if not is_valid_case_for_rule(applied_grid, RULE_D1):
                #     continue
                if not is_valid_case_for_rule(applied_grid, RULE_D2):
                    continue
            if "B" in rule:
                if not is_valid_case_for_rule(applied_grid, get_rule_B(len(grid))):
                    continue
            if "A" in rule:
                if not is_valid_case_for_rule(applied_grid, RULE_A):
                    continue
            if "H" in rule:
                if not is_valid_case_for_rule(applied_grid, RULE_H):
                    continue
            if "U" in rule:
                if not is_valid_case_for_rule(applied_grid, RULE_U):
                    continue
            valid_mine_combinations.append(mines)
        if len(valid_mine_combinations) > MAX_CASES:
            continue

        expanded_region = ExpandedRegion.from_mine_combinations(
            blank_cells, valid_mine_combinations
        )
        expanded_regions.append(expanded_region)

    return expanded_regions


def extract_hints(
    region: ExpandedRegion,
) -> tuple[set[tuple[str, tuple[int, int]]], ExpandedRegion]:
    if not region:
        return set(), None
    hints = set()
    uncertain_cells = []
    uncertain_cell_indices = []
    total_cases = len(region.cases)
    bit_masks = [1 << i for i in range(len(region.blank_cells))]
    mine_counts = [0] * len(region.blank_cells)
    for case in region.cases:
        for i, mask in enumerate(bit_masks):
            if case & mask:
                mine_counts[i] += 1
    for i, (cell, count) in enumerate(zip(region.blank_cells, mine_counts)):
        if count == total_cases:
            hints.add(("mine", cell))
        elif count == 0:
            hints.add(("safe", cell))
        else:
            uncertain_cells.append(cell)
            uncertain_cell_indices.append(i)
    if not hints:
        return set(), region
    if uncertain_cells:
        mask = sum(1 << i for i in uncertain_cell_indices)
        seen_patterns = set()
        new_cases = []
        for case in region.cases:
            pattern = case & mask
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                new_case = 0
                for new_idx, old_idx in enumerate(uncertain_cell_indices):
                    if case & (1 << old_idx):
                        new_case |= 1 << new_idx
                new_cases.append(new_case)
        return hints, ExpandedRegion(blank_cells=uncertain_cells, cases=new_cases)

    return hints, None


def merge_expanded_regions(r1: ExpandedRegion, r2: ExpandedRegion) -> ExpandedRegion:
    all_cells = list(set(r1.blank_cells) | set(r2.blank_cells))
    all_cells.sort()
    r1_cell_indices = {}
    r2_cell_indices = {}
    for i, cell in enumerate(r1.blank_cells):
        r1_cell_indices[cell] = i
    for i, cell in enumerate(r2.blank_cells):
        r2_cell_indices[cell] = i

    new_cases = []
    for case1 in r1.cases:
        for case2 in r2.cases:
            valid = True
            new_case = 0
            for new_idx, cell in enumerate(all_cells):
                mine1 = None
                mine2 = None
                if cell in r1_cell_indices:
                    idx1 = r1_cell_indices[cell]
                    mine1 = bool(case1 & (1 << idx1))
                if cell in r2_cell_indices:
                    idx2 = r2_cell_indices[cell]
                    mine2 = bool(case2 & (1 << idx2))
                if mine1 is not None and mine2 is not None and mine1 != mine2:
                    valid = False
                    break
                if mine1 or mine2:
                    new_case |= 1 << new_idx
            if valid:
                new_cases.append(new_case)
    if not new_cases:
        return None

    return ExpandedRegion(blank_cells=all_cells, cases=new_cases)


def apply_filter_for_all_rules(
    region: ExpandedRegion, grid: list[list[int]], rule: str
) -> ExpandedRegion:
    if "Q" in rule:
        region = filter_cases_by_rule(region, grid, RULE_Q)
    if "T" in rule:
        region = filter_cases_by_rule(region, grid, RULE_T)
    if "D" in rule:
        # region = filter_cases_by_rule(region, grid, RULE_D1)
        # region = filter_cases_by_rule(region, grid, RULE_D1)
        region = filter_cases_by_rule(region, grid, RULE_D2)
    if "B" in rule:
        region = filter_cases_by_rule(region, grid, get_rule_B(len(grid)))
    if "A" in rule:
        r1 = region
        region = filter_cases_by_rule(region, grid, RULE_A)
    if "H" in rule:
        region = filter_cases_by_rule(region, grid, RULE_H)
    if "U" in rule:
        region = filter_cases_by_rule(region, grid, RULE_U)
    return region


def get_expanded_regions_by_left_side_rules(grid, rule):
    exregions = []
    if "Q" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_Q))
    if "T" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_T))
    if "D" in rule and "D'" not in rule:
        # exregions.extend(get_expanded_regions_by_rule(grid, RULE_D1))
        # exregions.extend(get_expanded_regions_by_rule(grid, RULE_D1))
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_D2))
    if "B" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, get_rule_B(len(grid))))
    if "A" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_A))
    if "H" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_H))
    if "U" in rule:
        exregions.extend(get_expanded_regions_by_rule(grid, RULE_U))
    return exregions


def solve_with_expanded_regions(
    exregions: list[ExpandedRegion], grid: list[list[int]], rule: str
) -> set[tuple[str, tuple[int, int]]]:
    logging_this = False

    hints = set()

    reduced_regions = []
    for exregion in exregions:
        if logging_this:
            print(exregion)
        exregion = apply_filter_for_all_rules(exregion, grid, rule)
        new_hints, reduced = extract_hints(exregion)
        if new_hints:
            hints.update(new_hints)
        if (
            reduced
            and reduced not in reduced_regions
            and 2 ** len(reduced.blank_cells) > reduced.case_count
        ):
            reduced_regions.append(reduced)
        if logging_this:
            print(reduced, "\n")
    exregions = reduced_regions

    start_time = time.time()
    while len(exregions) > 1:
        if logging_this:
            print(f"{len(exregions)} Regions", end=" / ")
        exregions.sort(key=lambda r: r.case_count)
        r1 = exregions.pop(0)
        # print(r1.case_count, exregions[-1].case_count, end=" / ")
        # print(r1)

        subset_region = 0
        min_cases = float("inf")
        best_reduced = None
        best_partner_idx = None
        for i in range(len(exregions)):
            r2 = exregions[i]
            r1_cells = set(r1.blank_cells)
            r2_cells = set(r2.blank_cells)
            is_subset = r1_cells.issubset(r2_cells)
            if r1.case_count * r2.case_count > MAX_CASES and not is_subset:
                continue

            merged = merge_expanded_regions(r1, r2)
            merged = apply_filter_for_all_rules(merged, grid, rule)
            new_hints, reduced = extract_hints(merged)
            if new_hints:
                hints.update(new_hints)
            if time.time() - start_time > 0.5 and hints:
                break
                # return hints
            if is_subset:
                subset_region += 1
                if reduced:
                    exregions[i] = reduced
                else:
                    break
            elif not is_subset and reduced and 1 < len(reduced.cases) <= MAX_CASES:
                if len(reduced.cases) < min_cases:
                    min_cases = len(reduced.cases)
                    best_reduced = reduced
                    best_partner_idx = i
        if subset_region > 0:
            if logging_this:
                # print(f"r1 is subset of {subset_region} regions - {r1}")
                print(f"r1 is subset of {subset_region} regions")
                # print(exregions[i])
            continue
        if time.time() - start_time > 0.5 and hints:
            return hints
        if best_partner_idx is not None:
            exregions.pop(best_partner_idx)
            if best_reduced and len(best_reduced.cases) <= MAX_CASES:
                exregions.append(best_reduced)
            if logging_this:
                print(f"Merging: {len(r1.cases)} -> {min_cases}")
        if time.time() - start_time < 0.5 and hints:
            for i in range(len(exregions)):
                new_exregion = apply_hints_to_exregion(exregions[i], hints)
                if new_exregion != exregions[i]:
                    if logging_this:
                        print(
                            f"Hint applied: {exregions[i].case_count} -> {new_exregion.case_count}"
                        )
                    exregions[i] = new_exregion

    if exregions:
        final_hints, _ = extract_hints(exregions[0])
        hints.update(final_hints)

    return hints


def apply_hints_to_exregion(
    exregion: ExpandedRegion, hints: set[tuple[str, tuple[int, int]]]
) -> ExpandedRegion | None:
    """주어진 힌트들을 exregion에 적용하여 cases를 필터링"""
    filtered_cases = []

    for case in exregion.cases:
        valid = True
        for hint_type, cell in hints:
            if cell in exregion.blank_cells:
                idx = exregion.blank_cells.index(cell)
                has_mine = bool(case & (1 << idx))
                if (hint_type == "mine" and not has_mine) or (
                    hint_type == "safe" and has_mine
                ):
                    valid = False
                    break
        if valid:
            filtered_cases.append(case)

    if not filtered_cases:
        print("이런 경우는 없을듯?")
        return None

    return ExpandedRegion(blank_cells=exregion.blank_cells, cases=filtered_cases)


def apply_hints(grid: list[list[int]], hints):
    for hint_type, (r, c) in hints:
        if hint_type == "safe":
            grid[r][c] = -3
        elif hint_type == "mine":
            grid[r][c] = -2
    return grid


def location_to_cell_coordinates(window_title, location, size):
    row, col = location

    if window_title == "Minesweeper Variants":
        initial_x, initial_y = INITIAL_POSITIONS[size]
        x_increment, y_increment = 50, 50
    elif window_title == "Minesweeper Variants 2":
        initial_x, initial_y = INITIAL_POSITIONS_2[size]
        x_increment, y_increment = 45, 45

    x1 = initial_x + col * x_increment
    y1 = initial_y + row * y_increment
    x2 = x1 + x_increment // 2
    y2 = y1 + y_increment // 2
    return (x2, y2)


def activate_window(window_title):
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    return True


def click_positions(window_title, clicks):
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()
        original_x, original_y = pyautogui.position()
        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.PAUSE = 0.0001
        # pyautogui.PAUSE = 0.3

        base_x = target_window.left
        base_y = target_window.top
        clicks.append(CLICK_COORDINATES["safe_click"])
        pyautogui.moveTo(base_x + 150, base_y + 150)
        for relative_x, relative_y, button_type in clicks:
            absolute_x = base_x + relative_x
            absolute_y = base_y + relative_y
            pyautogui.moveTo(absolute_x, absolute_y)
            pyautogui.click(button=button_type)

        pyautogui.moveTo(original_x, original_y)
        pyautogui.FAILSAFE = True

        return True

    except Exception as e:
        print(f"Error clicking positions: {e}")
        return False


def click_hints(window_title, hints, size):
    clicks = []
    for hint in hints:
        location = hint[1]
        relative_x, relative_y = location_to_cell_coordinates(
            window_title, location, size
        )
        button_type = "left" if hint[0] == "safe" else "right"
        clicks.append((relative_x, relative_y, button_type))
    return click_positions(window_title, clicks)


def click_hints_twice(window_title, hints, size):
    left_clicks = []
    right_clicks = []
    for hint in hints:
        location = hint[1]
        relative_x, relative_y = location_to_cell_coordinates(
            window_title, location, size
        )
        if hint[0] == "safe":
            left_clicks.append((relative_x, relative_y, "left"))
        else:
            right_clicks.append((relative_x, relative_y, "right"))
    clicks = left_clicks + right_clicks + left_clicks
    return click_positions(window_title, clicks)


def input_spacebar(window_title):
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    pyautogui.press("space")


def next_level_check(window_title, save_path):
    capture_window_screenshot(window_title)
    status = completed_check(save_path)
    if status == PuzzleStatus.FINISH:
        input_spacebar(window_title)
        click_positions(window_title, [CLICK_COORDINATES["next_level"]])
        time.sleep(0.3)
    elif status == PuzzleStatus.NEXT:
        click_positions(window_title, [CLICK_COORDINATES["next_level"]])
        time.sleep(0.3)
    elif status == PuzzleStatus.STAR_BROKEN:
        skip_level(window_title)
        time.sleep(0.3)
    elif status == PuzzleStatus.WRONG_POPUP:
        click_positions(window_title, [CLICK_COORDINATES["close_popup"]])
        time.sleep(0.3)
    elif status == PuzzleStatus.ALREADY_SOLVED:
        click_positions(window_title, [CLICK_COORDINATES["skip_button"]])
        time.sleep(0.3)
    return status


def skip_level(window_title):
    skip1 = CLICK_COORDINATES["skip_button"]
    skip2 = CLICK_COORDINATES["confirm_skip"]
    click_positions(window_title, [skip1, skip2])


def process_hints(window_title, hints, size, save_path):
    # print(f"{len(hints)} hints found")
    # click_hints(self.window_title, hints, self.cell_size)
    click_hints_twice(window_title, hints, size)
    next_level_check(window_title, save_path)


def switch_to_other_size(window_title, click):
    time.sleep(0.5)
    click_positions(window_title, [(985, 75, "left")])
    time.sleep(0.5)
    click_positions(window_title, [(750, 494, "left")])
    time.sleep(0.5)
    if isinstance(click, tuple):
        click_positions(window_title, [click])
    elif isinstance(click, list):
        click_positions(window_title, click)
    else:
        raise TypeError("clicks should be tuple or list of tuples")
    time.sleep(0.5)
    click_positions(window_title, [(864, 484, "left")])
    time.sleep(0.5)
