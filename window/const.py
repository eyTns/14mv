## not fixed
# MAX_CASES = 10000  ## easy puzzles, fast
# MAX_CASES = 30000  ## medium puzzles
# MAX_CASES = 90000  ## hard puzzles (works on most of size 5 puzzles)
MAX_CASES = 650000  ## very hard case (works up to 22 choose 10 = 646646)


TOTAL_MINES = {
    "STANDARD": [10, 14, 20, 26],
    "B": [10, 12, 21, 24],
    "DAH": [8, 10, 14, 20],
}


NEIGHBORS = {
    "STANDARD": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
    "X": [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)],
    "X'": [(-1, 0), (1, 0), (0, -1), (0, 1)],
    "K": [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
}


RULE_Q = {
    "directions": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "pattern_condition": "no_all_numbers",
}

RULE_T = {
    "directions": [
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 0), (1, -1), (2, -2)],
    ],
    "pattern_condition": "no_all_mines",
}

RULE_A = {
    "directions": [
        [(0, 0), (1, 2)],
        [(1, 0), (0, 2)],
        [(0, 0), (2, 1)],
        [(2, 0), (0, 1)],
    ],
    "pattern_condition": "no_all_mines",
}

RULE_H = {
    "directions": [[(0, 0), (0, 1)]],
    "pattern_condition": "no_all_mines",
}

RULE_U = {
    "directions": [[(0, 0), (0, 1)], [(0, 0), (1, 0)]],
    "pattern_condition": "no_all_mines",
}

RULE_D1 = {
    "directions": [
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0)],
    ],
    "pattern_condition": "no_all_mines",
}

RULE_D2 = {
    "directions": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "pattern_condition": "max_two_mines",
}

RULE_D3 = {
    "directions": [[(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]],
    "pattern_condition": "no_center_mine_only",
}


INITIAL_POSITIONS = {
    5: (395, 234),
    6: (370, 209),
    7: (345, 184),
    8: (320, 159),
}

INITIAL_POSITIONS_2 = {
    5: (409, 248),
    6: (386, 225),
    7: (364, 203),
    8: (341, 180),
}

SPECIAL_CELLS = {
    "blank": -1,
    "flag": -2,
    "question": -3,
    "star": -3,
}

CLICK_COORDINATES = {
    "next_level": (564, 484, "left"),
    "skip_button": (856, 75, "left"),
    "confirm_skip": (715, 484, "left"),
    "safe_click": (150, 150, "right"),
    "close_popup": (147, 919, "left"),
}
