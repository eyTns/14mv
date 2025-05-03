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
    RULE_H,
    SPECIAL_CELLS,
    TOTAL_MINES,
    MAX_EXPAND_CASES,
    MAX_MERGE_CASES,
)
from window.image_utils import PuzzleStatus, capture_window_screenshot, completed_check
from window.region import ExpandedRegion, Region, WRegion, LRegion, PRegion
from window.rules import is_valid_case_for_rule, filter_cases_by_rule


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
    if rule in TOTAL_MINES:
        return TOTAL_MINES[rule][cell_size - 5]
    else:
        return None


def get_cell_region(grid, rule, row, col) -> Region:
    """
    주어진 셀의 이웃한 빈 칸들을 찾습니다.

    Args:
        grid (list): 게임 그리드
        rule (str): "V", "X" 등 - 이웃을 찾는 규칙
            V: 주변 8방향의 1칸
            X: 상하좌우 방향으로 1-2칸
        row (int): 현재 셀의 행 번호
        col (int): 현재 셀의 열 번호

    Returns:
        Region:
    """
    mines_needed = grid[row][col]
    neighboring_blanks = set()

    if rule in NEIGHBORS.keys():
        neighbors = NEIGHBORS[rule]
    else:
        raise ValueError(f"Invalid rule. Available rules: {NEIGHBORS.keys()}")

    for dr, dc in neighbors:
        r = row + dr
        c = col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] == -1:
                neighboring_blanks.add((r, c))
            elif grid[r][c] == -2:
                mines_needed -= 1

    if neighboring_blanks:
        return Region(
            mines_needed=mines_needed,
            blank_cells=neighboring_blanks,
        )
    else:
        return None


def get_grid_region(grid, rule) -> Region:
    mine_value = get_total_mines(rule, len(grid))
    mines_needed = mine_value
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


def get_row_column_region(grid, rule, row, col) -> Region:
    mine_value = get_total_mines(rule, len(grid)) // len(grid)
    blanks = set()

    cells_to_check = []
    if row is not None:
        mine_value *= row[1] - row[0] + 1
        cells_to_check = [
            (r, c) for r in range(row[0], row[1] + 1) for c in range(len(grid[0]))
        ]
    elif col is not None:
        mine_value *= col[1] - col[0] + 1
        cells_to_check = [
            (r, c) for c in range(col[0], col[1] + 1) for r in range(len(grid))
        ]
    mines_needed = mine_value

    for r, c in cells_to_check:
        if grid[r][c] == -2:
            mines_needed -= 1
        elif grid[r][c] == -1:
            blanks.add((r, c))

    return Region(
        mines_needed=mines_needed,
        blank_cells=blanks,
    )


def analyze_regions(grid, rule, grid_region=True) -> list[Region]:
    regions = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] >= 0:
                regions.append(get_cell_region(grid, rule, r, c))

    if grid_region:
        regions.append(get_grid_region(grid, rule))

    if "B" in rule:
        for start in range(len(grid)):
            regions.append(get_row_column_region(grid, rule, (start, start), None))
            regions.append(get_row_column_region(grid, rule, None, (start, start)))

    return [r for r in regions if r]


def analyze_wregions(grid, rule) -> list[WRegion]:
    wregions = []
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] >= 0:
                center = (r, c)
                if grid[r][c] == 0:
                    mines_component = []
                else:
                    mines_component = [int(digit) for digit in str(grid[r][c])]
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
                        cell_value = grid[nr][nc]
                        if cell_value == SPECIAL_CELLS["flag"]:
                            pre_filled_mines.append((nr, nc))
                        elif (
                            cell_value >= 0
                            or cell_value == SPECIAL_CELLS["question"]
                            or cell_value == SPECIAL_CELLS["star"]
                        ):
                            pre_filled_numbers.append((nr, nc))
                        elif cell_value == SPECIAL_CELLS["blank"]:
                            has_blank = True
                if has_blank:
                    wregion = WRegion(
                        center=center,
                        mines_component=mines_component,
                        pre_filled_mines=pre_filled_mines,
                        pre_filled_numbers=pre_filled_numbers,
                    )
                    wregions.append(wregion)

    return wregions


def analyze_lregions(grid, rule) -> list[LRegion]:
    lregions = []
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] >= 0:
                center = (r, c)
                number = grid[r][c]
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
                        cell_value = grid[nr][nc]
                        if cell_value == SPECIAL_CELLS["flag"]:
                            pre_filled_mines.append((nr, nc))
                        elif (
                            cell_value >= 0
                            or cell_value == SPECIAL_CELLS["question"]
                            or cell_value == SPECIAL_CELLS["star"]
                        ):
                            pre_filled_numbers.append((nr, nc))
                        elif cell_value == SPECIAL_CELLS["blank"]:
                            has_blank = True
                if has_blank:
                    lregion = LRegion(
                        center=center,
                        number=number,
                        pre_filled_mines=pre_filled_mines,
                        pre_filled_numbers=pre_filled_numbers,
                    )
                    lregions.append(lregion)
    return lregions


def analyze_pregions(grid, rule) -> list[PRegion]:
    return analyze_lregions(grid, rule)


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
        if combinations_count > MAX_EXPAND_CASES:
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
        if len(valid_mine_combinations) > MAX_MERGE_CASES:
            continue

        expanded_region = ExpandedRegion.from_mine_combinations(
            blank_cells, valid_mine_combinations
        )
        expanded_regions.append(expanded_region)

    return expanded_regions


def extract_hints(
    region: ExpandedRegion,
) -> tuple[set[tuple[str, tuple[int, int]]], ExpandedRegion]:
    """
    ExpandedRegion에서 확실한 힌트들을 추출하고, 남은 불확실한 셀들의 ExpandedRegion을 반환

    Returns:
        tuple[set[hints], ExpandedRegion]:
            - hints: ("mine" or "safe", (row, col)) 형태의 힌트들
            - 불확실한 셀들만 남은 새로운 ExpandedRegion
    """
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
    """
    두 ExpandedRegion을 병합하여 새로운 ExpandedRegion 생성
    충돌하는 셀(같은 위치에 다른 지뢰 상태)이 있는 조합은 제외

    Returns:
        ExpandedRegion: 병합된 새로운 region
    """
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


def solve_with_expanded_regions(
    exregions: list[ExpandedRegion], grid: list[list[int]], rule: str
) -> list[tuple[str, tuple[int, int]]]:
    hints = set()

    reduced_regions = []
    for region in exregions:
        if "Q" in rule:
            region = filter_cases_by_rule(region, grid, RULE_Q)
        if "T" in rule:
            region = filter_cases_by_rule(region, grid, RULE_T)
        if "A" in rule:
            region = filter_cases_by_rule(region, grid, RULE_A)
        if "H" in rule:
            region = filter_cases_by_rule(region, grid, RULE_H)
        if "U" in rule:
            region = filter_cases_by_rule(region, grid, RULE_U)
        new_hints, reduced = extract_hints(region)
        if new_hints:
            hints.update(new_hints)
        if reduced:
            reduced_regions.append(reduced)

    exregions = reduced_regions

    start_time = time.time()

    while len(exregions) > 1:
        print(f"{len(exregions)}", end=" / ")
        # print(f"{len(exregions)} / ")

        exregions.sort(key=lambda r: len(r.cases))
        r1 = exregions.pop(0)
        # print(r1, end=" / ")

        # 부분집합 관계인 영역들 처리
        subset_region = 0
        for i in range(len(exregions)):
            r2 = exregions[i]
            if set(r1.blank_cells).issubset(set(r2.blank_cells)):
                merged = merge_expanded_regions(r1, r2)
                if merged is None:
                    continue
                if "Q" in rule:
                    merged = filter_cases_by_rule(merged, grid, RULE_Q)
                if "T" in rule:
                    merged = filter_cases_by_rule(merged, grid, RULE_T)
                if "A" in rule:
                    merged = filter_cases_by_rule(merged, grid, RULE_A)
                if "H" in rule:
                    merged = filter_cases_by_rule(merged, grid, RULE_H)
                if "U" in rule:
                    merged = filter_cases_by_rule(merged, grid, RULE_U)
                if merged is None:
                    continue
                new_hints, reduced = extract_hints(merged)
                if new_hints:
                    hints.update(new_hints)
                if reduced:
                    subset_region += 1
                    exregions[i] = reduced

        if subset_region >= 2:
            # 전체가 아닌 영역끼리 합친 경우
            print(f"subset case exist for r1 - {r1}")
            continue

        min_cases = float("inf")
        best_reduced = None
        best_partner_idx = None

        # 영역 병합
        for i in range(len(exregions)):
            r2 = exregions[i]
            if not set(r1.blank_cells) & set(r2.blank_cells):
                continue
            if r1.case_count * r2.case_count > MAX_EXPAND_CASES:
                continue
            merged = merge_expanded_regions(r1, r2)
            if "Q" in rule:
                merged = filter_cases_by_rule(merged, grid, RULE_Q)
            if "T" in rule:
                merged = filter_cases_by_rule(merged, grid, RULE_T)
            if "A" in rule:
                merged = filter_cases_by_rule(merged, grid, RULE_A)
            if "H" in rule:
                merged = filter_cases_by_rule(merged, grid, RULE_H)
            if "U" in rule:
                merged = filter_cases_by_rule(merged, grid, RULE_U)
            if merged is None:
                continue
            new_hints, reduced = extract_hints(merged)
            if new_hints:
                hints.update(new_hints)
            if time.time() - start_time > 0.5 and hints:
                return hints
            if reduced and 1 < len(reduced.cases) <= MAX_MERGE_CASES:
                if len(reduced.cases) < min_cases:
                    min_cases = len(reduced.cases)
                    best_reduced = reduced
                    best_partner_idx = i
        if time.time() - start_time > 0.5 and hints:
            return hints
        if best_partner_idx is not None:
            exregions.pop(best_partner_idx)
            if best_reduced and 1 < len(best_reduced.cases) <= MAX_MERGE_CASES:
                exregions.append(best_reduced)
        print(f"{len(r1.cases)} -> {min_cases}")

    if exregions:
        final_hints, _ = extract_hints(exregions[0])
        hints.update(final_hints)

    return hints


def apply_hints_to_region(
    region: ExpandedRegion, hints: set[tuple[str, tuple[int, int]]]
) -> ExpandedRegion | None:
    """
    주어진 힌트들을 region에 적용하여 cases를 필터링
    """
    filtered_cases = []

    for case in region.cases:
        valid = True
        for hint_type, cell in hints:
            if cell in region.blank_cells:
                idx = region.blank_cells.index(cell)
                has_mine = bool(case & (1 << idx))
                if (hint_type == "mine" and not has_mine) or (
                    hint_type == "safe" and has_mine
                ):
                    valid = False
                    break
        if valid:
            filtered_cases.append(case)

    if not filtered_cases:
        return None

    return ExpandedRegion(blank_cells=region.blank_cells, cases=filtered_cases)


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
    time.sleep(0.2)
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
        time.sleep(0.05)
    elif status == PuzzleStatus.NEXT:
        click_positions(window_title, [CLICK_COORDINATES["next_level"]])
    elif status == PuzzleStatus.STAR_BROKEN:
        skip_level(window_title)


def skip_level(window_title):
    skip1 = CLICK_COORDINATES["skip_button"]
    skip2 = CLICK_COORDINATES["confirm_skip"]
    click_positions(window_title, [skip1, skip2])
