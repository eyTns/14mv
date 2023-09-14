import pytest
from PyQt5.QtWidgets import QApplication, QMainWindow
from window.window import MyWindow
from window import utils
from window.utils import convert_to_numeric, get_neighboring_cells, get_neighboring_cells_with_indices
import os
import sys

@pytest.fixture
def sample_best_fit_cells():
    best_fit_cells = [
        ['cell_1.png', 'cell_2.png', 'cell_3.png', 'cell_0.png', 'cell_5.png', 'cell_6.png'],
        ['cell_7.png', 'cell_8.png', 'cell_blank.png', 'cell_flag.png', 'cell_question.png', 'cell_1.png'],
        ['cell_2.png', 'cell_3.png', 'cell_4.png', 'cell_5.png', 'cell_6.png', 'cell_7.png'],
        ['cell_8.png', 'cell_blank.png', 'cell_flag.png', 'cell_question.png', 'cell_1.png', 'cell_2.png'],
        ['cell_3.png', 'cell_4.png', 'cell_5.png', 'cell_6.png', 'cell_7.png', 'cell_8.png'],
        ['cell_blank.png', 'cell_flag.png', 'cell_question.png', 'cell_1.png', 'cell_2.png', 'cell_3.png']
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
        [-1, -2, -3, 1, 2, 3]
    ]


# Test the convert_to_numeric function
def test_convert_to_numeric(sample_best_fit_cells, sample_numeric_grid):
    assert convert_to_numeric(sample_best_fit_cells) == sample_numeric_grid


# Test the get_neighboring_cells function
def test_get_neighboring_cells(sample_numeric_grid):
    # Test case 1: Middle of the grid
    neighbors = get_neighboring_cells(2, 3, sample_numeric_grid)
    assert neighbors == [-1, -2, -3, 4, 6, -2, -3, 1]

    # Test case 2: Edge of the grid
    neighbors = get_neighboring_cells(2, 5, sample_numeric_grid)
    assert neighbors == [-3, 1, 6, 1, 2]

    # Test case 3: Corner of the grid
    neighbors = get_neighboring_cells(0, 0, sample_numeric_grid)
    assert neighbors == [2, 7, 8]


# Test the get_neighboring_cells_with_indices function
def test_get_neighboring_cells_with_indices(sample_numeric_grid):
    # Test case 1: Middle of the grid
    neighbors = get_neighboring_cells_with_indices(2, 3, sample_numeric_grid)
    expected_neighbors = [(-1, 1, 2), (-2, 1, 3), (-3, 1, 4), (4, 2, 2), (6, 2, 4), (-2, 3, 2), (-3, 3, 3), (1, 3, 4)]
    assert neighbors == expected_neighbors

    # Test case 2: Edge of the grid
    neighbors = get_neighboring_cells_with_indices(2, 5, sample_numeric_grid)
    expected_neighbors = [(-3, 1, 4), (1, 1, 5), (6, 2, 4), (1, 3, 4), (2, 3, 5)]
    assert neighbors == expected_neighbors

    # Test case 3: Corner of the grid
    neighbors = get_neighboring_cells_with_indices(0, 0, sample_numeric_grid)
    expected_neighbors = [(2, 0, 1), (7, 1, 0), (8, 1, 1)]
    assert neighbors == expected_neighbors