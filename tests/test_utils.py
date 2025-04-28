import warnings

import pytest

from window.image_utils import MSE_of_images, convert_to_numeric
from window.utils import (
    analyze_regions,
    find_double_areas,
    find_single_clickable_cells,
    get_neighboring_cells,
    get_neighboring_cells_with_indices,
)

warnings.filterwarnings("ignore", message="sipPyTypeDict.*")


@pytest.fixture
def sample_best_fit_cells():
    best_fit_cells = [
        [
            "cell_1.png",
            "cell_2.png",
            "cell_3.png",
            "cell_0.png",
            "cell_5.png",
            "cell_6.png",
        ],
        [
            "cell_7.png",
            "cell_8.png",
            "cell_blank.png",
            "cell_flag.png",
            "cell_question.png",
            "cell_1.png",
        ],
        [
            "cell_2.png",
            "cell_3.png",
            "cell_4.png",
            "cell_5.png",
            "cell_6.png",
            "cell_7.png",
        ],
        [
            "cell_8.png",
            "cell_blank.png",
            "cell_flag.png",
            "cell_question.png",
            "cell_1.png",
            "cell_2.png",
        ],
        [
            "cell_3.png",
            "cell_4.png",
            "cell_5.png",
            "cell_6.png",
            "cell_7.png",
            "cell_8.png",
        ],
        [
            "cell_blank.png",
            "cell_flag.png",
            "cell_question.png",
            "cell_1.png",
            "cell_2.png",
            "cell_3.png",
        ],
    ]
    return best_fit_cells


@pytest.fixture
def sample_numeric_grid():
    return [
        [1, 2, 3, 0, 5, 6],
        [7, 8, -1, -2, -3, 1],
        [2, 3, 4, 5, 6, 7],
        [8, -1, -2, -3, 1, 2],
        [3, 4, 5, 6, 7, 8],
        [-1, -2, -3, 1, 2, 3],
    ]


# Test the convert_to_numeric function
def test_convert_to_numeric(sample_best_fit_cells, sample_numeric_grid):
    assert convert_to_numeric(sample_best_fit_cells) == sample_numeric_grid


# Test the get_neighboring_cells function
def test_get_neighboring_cells(sample_numeric_grid):
    neighbors = get_neighboring_cells(2, 3, sample_numeric_grid)
    assert neighbors == [-1, -2, -3, 4, 6, -2, -3, 1]

    neighbors = get_neighboring_cells(2, 5, sample_numeric_grid)
    assert neighbors == [-3, 1, 6, 1, 2]

    neighbors = get_neighboring_cells(0, 0, sample_numeric_grid)
    assert neighbors == [2, 7, 8]


# Test the get_neighboring_cells_with_indices function
def test_get_neighboring_cells_with_indices(sample_numeric_grid):
    neighbors = get_neighboring_cells_with_indices(2, 3, sample_numeric_grid)
    expected_neighbors = [
        (-1, 1, 2),
        (-2, 1, 3),
        (-3, 1, 4),
        (4, 2, 2),
        (6, 2, 4),
        (-2, 3, 2),
        (-3, 3, 3),
        (1, 3, 4),
    ]
    assert neighbors == expected_neighbors

    neighbors = get_neighboring_cells_with_indices(2, 5, sample_numeric_grid)
    expected_neighbors = [(-3, 1, 4), (1, 1, 5), (6, 2, 4), (1, 3, 4), (2, 3, 5)]
    assert neighbors == expected_neighbors

    neighbors = get_neighboring_cells_with_indices(0, 0, sample_numeric_grid)
    expected_neighbors = [(2, 0, 1), (7, 1, 0), (8, 1, 1)]
    assert neighbors == expected_neighbors


def test_minesweeper_hints():
    grid = [
        [-3, 1, 1, 3, -2, 3],
        [-1, 4, -1, -1, -2, -2],
        [-2, -2, -2, 6, -2, -2],
        [-1, -1, -2, 4, -2, 3],
        [-1, -1, 3, 3, 2, 1],
        [-1, -1, 2, -2, 1, 0],
    ]

    number_cells_info = analyze_regions(grid, "V")
    hints = find_double_areas(number_cells_info)
    safe_cells = [(hint[1][0], hint[1][1]) for hint in hints if hint[0] == "safe"]
    mine_cells = [(hint[1][0], hint[1][1]) for hint in hints if hint[0] == "mine"]
    expected_safe_cells = [(3, 1)]

    print(f"생성된 힌트: {hints}")
    print(f"안전한 셀들: {safe_cells}")
    print(f"지뢰 셀들: {mine_cells}")
    assert (3, 1) in safe_cells, "(3,1) 위치가 안전한 셀로 감지되지 않았습니다."
    for cell in expected_safe_cells:
        assert cell in safe_cells, f"{cell} 위치가 안전한 셀로 감지되지 않았습니다."


def test_minesweeper_hints2():
    grid = [
        [-3, 1, 1, 3, -2, 3],
        [-1, 4, -1, -1, -2, -2],
        [-2, -2, -2, 6, -2, -2],
        [-1, -1, -2, 4, -2, 3],
        [-1, -1, 3, 3, 2, 1],
        [-1, -1, 2, -2, 1, 0],
    ]

    number_cells_info = analyze_regions(grid, "V")
    single_cell_hints = find_single_clickable_cells(number_cells_info)
    common_area_hints = find_double_areas(number_cells_info)
    all_hints = single_cell_hints.union(common_area_hints)
    safe_cells = [(hint[1][0], hint[1][1]) for hint in all_hints if hint[0] == "safe"]
    mine_cells = [(hint[1][0], hint[1][1]) for hint in all_hints if hint[0] == "mine"]

    print(f"안전한 셀들: {safe_cells}")
    print(f"지뢰 셀들: {mine_cells}")
    assert (3, 1) in safe_cells, "(3,1) 위치가 안전한 셀로 감지되지 않았습니다."
