from typing import Iterator

from pydantic import BaseModel
from itertools import groupby

from window.const import RULE_Q, RULE_T, SPECIAL_CELLS


class Region(BaseModel):
    mines_needed: int
    blank_cells: set[tuple[int, int]]

    @property
    def total_blanks(self) -> int:
        return len(self.blank_cells)

    @property
    def numbers_needed(self) -> int:
        return self.total_blanks - self.mines_needed

    def __eq__(self, other: "Region") -> bool:
        return self.blank_cells == other.blank_cells

    def __sub__(self, other: "Region") -> "Region":
        return Region(
            mines_needed=self.mines_needed - other.mines_needed,
            blank_cells=self.blank_cells - other.blank_cells,
        )


class RuleRegion(BaseModel):
    center: tuple[int, int]
    number: int
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]


class LeftSideRegion(BaseModel):
    rule: str
    area_cells: list[tuple[int, int]]
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]

    @classmethod
    def from_left_side_rule(cls, grid, rule, row, col):
        if rule == "Q":
            rule_dict = RULE_Q
        elif rule == "T":
            rule_dict = RULE_T

        directions = rule_dict["directions"][0]  ## 틀렸음
        area_cells = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
                if rule_dict["outsider_condition"] == "invalid":
                    return None
            area_cells.append((new_row, new_col))
        pre_filled_mines = []
        pre_filled_numbers = []
        for r, c in area_cells:
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                cell_value = grid[r][c]
                if cell_value == SPECIAL_CELLS["flag"]:
                    pre_filled_mines.append((r, c))
                elif cell_value not in [-1, -2]:
                    pre_filled_numbers.append((r, c))

        if (
            rule_dict["pattern_condition"] == "no_all_numbers"
            and len(pre_filled_numbers) == 4
        ):
            return None

        return cls(
            rule=rule,
            area_cells=area_cells,
            pre_filled_mines=pre_filled_mines,
            pre_filled_numbers=pre_filled_numbers,
        )


class RightSideRegion(BaseModel):
    rule: str
    center: tuple[int, int]
    number: int
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]


class GridRegion(BaseModel):
    mines_needed: int
    numbers_needed: int
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]


class ExpandedRegion(BaseModel):
    blank_cells: list[tuple[int, int]]
    cases: list[int]

    def __init__(self, blank_cells: list[tuple[int, int]], cases: list[int]):
        # blank_cells.sort() ## cases의 값이 바뀌므로 금지. 중복 제거를 위해 미리 정렬된 상태로 들어와야 함
        cases.sort()
        super().__init__(blank_cells=blank_cells, cases=cases)

    def __eq__(self, other: "ExpandedRegion") -> bool:
        return all(
            [
                set(self.blank_cells) == set(other.blank_cells),
                set(self.cases) == set(other.cases),
            ]
        )

    @property
    def case_count(self) -> int:
        return len(self.cases)

    def get_case(self, case_index: int) -> Iterator[tuple[tuple[int, int], bool]]:
        case = self.cases[case_index]
        for i, cell in enumerate(self.blank_cells):
            has_mine = bool(case & (1 << i))
            yield cell, has_mine

    def _get_surrounding_cells(center: tuple[int, int]) -> list[tuple[int, int]]:
        center_x, center_y = center
        return [
            (center_x + dx, center_y + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]

    @classmethod
    def _prepare_blank_cells(
        cls,
        center: tuple[int, int],
        pre_filled_mines: list[tuple[int, int]],
        pre_filled_numbers: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        surrounding_cells = cls._get_surrounding_cells(center)
        mines_set = set(pre_filled_mines)
        numbers_set = set(pre_filled_numbers)
        blank_cells = sorted(
            [
                cell
                for cell in surrounding_cells
                if cell not in mines_set and cell not in numbers_set
            ]
        )
        return blank_cells, surrounding_cells

    @classmethod
    def from_mine_combinations(
        cls,
        blank_cells: list[tuple[int, int]],
        mine_combinations: list[set[tuple[int, int]]],
    ) -> "ExpandedRegion":
        cases = []
        blank_cells.sort()
        for mine_set in mine_combinations:
            case = 0
            for i, cell in enumerate(blank_cells):
                if cell in mine_set:
                    case |= 1 << i
            cases.append(case)
        return cls(blank_cells=blank_cells, cases=cases)

    @classmethod
    def from_rule_region(cls, region, rule) -> "ExpandedRegion":
        if rule == "M":
            return cls.from_mregion(region)
        elif rule == "L":
            return cls.from_lregion(region)
        elif rule == "W":
            return cls.from_wregion(region)
        elif rule == "N":
            return cls.from_nregion(region)
        elif rule == "P":
            return cls.from_pregion(region)
        elif rule == "W'":
            return cls.from_wprimeregion(region)
        else:
            raise ValueError(f"Invalid rule: {rule}")

    @classmethod
    def from_wregion(cls, wregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, surrounding_cells = cls._prepare_blank_cells(
            wregion.center, wregion.pre_filled_mines, wregion.pre_filled_numbers
        )
        valid_cases = []
        pre_filled_mines_set = set(wregion.pre_filled_mines)
        if wregion.number == 0:
            mines_component = []
        else:
            mines_component = [int(digit) for digit in str(wregion.number)]

        for case_bits in range(1 << len(blank_cells)):
            current_mines = pre_filled_mines_set.copy()
            current_mines.update(
                blank_cells[i] for i in range(len(blank_cells)) if case_bits & (1 << i)
            )
            if get_mines_component(surrounding_cells, current_mines) == sorted(
                mines_component
            ):
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_wprimeregion(cls, wprimeregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, surrounding_cells = cls._prepare_blank_cells(
            wprimeregion.center,
            wprimeregion.pre_filled_mines,
            wprimeregion.pre_filled_numbers,
        )
        valid_cases = []
        pre_filled_mines_set = set(wprimeregion.pre_filled_mines)
        target_number = wprimeregion.number

        for case_bits in range(1 << len(blank_cells)):
            current_mines = pre_filled_mines_set.copy()
            current_mines.update(
                blank_cells[i] for i in range(len(blank_cells)) if case_bits & (1 << i)
            )
            mines_component = get_mines_component(surrounding_cells, current_mines)
            if mines_component and max(mines_component) == target_number:
                valid_cases.append(case_bits)
            if not mines_component and target_number == 0:
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_lregion(cls, lregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, _ = cls._prepare_blank_cells(
            lregion.center, lregion.pre_filled_mines, lregion.pre_filled_numbers
        )
        valid_cases = []
        pre_filled_mines_count = len(lregion.pre_filled_mines)
        target_numbers = {lregion.number - 1, lregion.number + 1}

        for case_bits in range(1 << len(blank_cells)):
            mine_count = pre_filled_mines_count + bin(case_bits).count("1")
            if mine_count in target_numbers:
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_pregion(cls, pregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, surrounding_cells = cls._prepare_blank_cells(
            pregion.center, pregion.pre_filled_mines, pregion.pre_filled_numbers
        )
        valid_cases = []
        pre_filled_mines_set = set(pregion.pre_filled_mines)
        target_number = pregion.number

        for case_bits in range(1 << len(blank_cells)):
            current_mines = pre_filled_mines_set.copy()
            current_mines.update(
                blank_cells[i] for i in range(len(blank_cells)) if case_bits & (1 << i)
            )
            if (
                len(get_mines_component(surrounding_cells, current_mines))
                == target_number
            ):
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_mregion(cls, mregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, surrounding_cells = cls._prepare_blank_cells(
            mregion.center, mregion.pre_filled_mines, mregion.pre_filled_numbers
        )
        valid_cases = []
        pre_filled_mines_set = set(mregion.pre_filled_mines)
        target_number = mregion.number

        def get_effective_mines(mines):
            effective_count = 0
            for mine in mines:
                r, c = mine
                if (r + c) % 2 == 1:  ## colored
                    effective_count += 2
                else:
                    effective_count += 1
            return effective_count

        for case_bits in range(1 << len(blank_cells)):
            current_mines = pre_filled_mines_set.copy()
            current_mines.update(
                blank_cells[i] for i in range(len(blank_cells)) if case_bits & (1 << i)
            )
            if get_effective_mines(current_mines) == target_number:
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_nregion(cls, nregion: RuleRegion) -> "ExpandedRegion":
        blank_cells, surrounding_cells = cls._prepare_blank_cells(
            nregion.center, nregion.pre_filled_mines, nregion.pre_filled_numbers
        )
        valid_cases = []
        pre_filled_mines_set = set(nregion.pre_filled_mines)
        target_number = nregion.number

        def get_effective_mines(mines):
            effective_count = 0
            for mine in mines:
                r, c = mine
                if (r + c) % 2 == 1:  ## colored
                    effective_count += 1
                else:
                    effective_count -= 1
            return effective_count

        for case_bits in range(1 << len(blank_cells)):
            current_mines = pre_filled_mines_set.copy()
            current_mines.update(
                blank_cells[i] for i in range(len(blank_cells)) if case_bits & (1 << i)
            )
            if abs(get_effective_mines(current_mines)) == target_number:
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)


def get_mines_component(surrounding_cells, mines):
    surrounding_cells.sort()
    circular_order = [0, 1, 2, 4, 7, 6, 5, 3]
    ordered_cells = [surrounding_cells[i] for i in circular_order]
    mine_pattern = [cell in mines for cell in ordered_cells]
    if all(mine_pattern):
        return [len(mine_pattern)]
    if not any(mine_pattern):
        return []
    while not (mine_pattern[0] == True and mine_pattern[-1] == False):
        mine_pattern = mine_pattern[1:] + [mine_pattern[0]]

    components = [len(list(group)) for key, group in groupby(mine_pattern) if key]
    return sorted(components)
