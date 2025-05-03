from typing import Iterator

from pydantic import BaseModel
from itertools import groupby


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


class WRegion(BaseModel):
    center: tuple[int, int]
    mines_component: list[int]
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]


class LRegion(BaseModel):
    center: tuple[int, int]
    number: int
    pre_filled_mines: list[tuple[int, int]]
    pre_filled_numbers: list[tuple[int, int]]


class ExpandedRegion(BaseModel):
    blank_cells: list[tuple[int, int]]
    cases: list[int]

    def __init__(self, blank_cells: list[tuple[int, int]], cases: list[int]):
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
    def from_wregion(cls, wregion: WRegion) -> "ExpandedRegion":
        center_x, center_y = wregion.center
        surrounding_cells = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                surrounding_cells.append((center_x + dx, center_y + dy))

        blank_cells = [
            cell
            for cell in surrounding_cells
            if cell not in wregion.pre_filled_mines
            and cell not in wregion.pre_filled_numbers
        ]
        blank_cells.sort()

        valid_cases = []
        for case_bits in range(1 << len(blank_cells)):
            current_mines = set(wregion.pre_filled_mines)
            for i, cell in enumerate(blank_cells):
                if case_bits & (1 << i):
                    current_mines.add(cell)
            if get_mines_component(surrounding_cells, current_mines) == sorted(
                wregion.mines_component
            ):
                valid_cases.append(case_bits)

        return cls(blank_cells=blank_cells, cases=valid_cases)

    @classmethod
    def from_lregion(cls, lregion: LRegion) -> "ExpandedRegion":
        center_x, center_y = lregion.center
        surrounding_cells = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                surrounding_cells.append((center_x + dx, center_y + dy))
        blank_cells = [
            cell
            for cell in surrounding_cells
            if cell not in lregion.pre_filled_mines
            and cell not in lregion.pre_filled_numbers
        ]
        blank_cells.sort()
        valid_cases = []
        for case_bits in range(1 << len(blank_cells)):
            mine_count = len(lregion.pre_filled_mines)
            for i, cell in enumerate(blank_cells):
                if case_bits & (1 << i):
                    mine_count += 1
            if lregion.number in [mine_count + 1, mine_count - 1]:
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
