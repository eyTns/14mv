from typing import Iterator

from pydantic import BaseModel


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


class ExpandedRegion(BaseModel):
    blank_cells: list[tuple[int, int]]
    cases: list[int]

    def __init__(self, blank_cells: list[tuple[int, int]], cases: list[int]):
        super().__init__(blank_cells=blank_cells, cases=cases)

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
        for mine_set in mine_combinations:
            case = 0
            for i, cell in enumerate(blank_cells):
                if cell in mine_set:
                    case |= 1 << i
            cases.append(case)
        return cls(blank_cells=blank_cells, cases=cases)
