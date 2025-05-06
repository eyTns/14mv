## not fixed
# MAX_CASES = 10000  ## easy puzzles, fast
# MAX_CASES = 30000  ## medium puzzles
# MAX_CASES = 90000  ## hard puzzles
MAX_CASES = 160000  ## harder puzzles
# MAX_CASES = 300000  ## harder puzzles
# MAX_CASES = 650000  ## very hard case (works up to 22 choose 10 = 646646)
# MAX_CASES = 1100000  ## very hard case (works up to 25 choose 17 = 1081575)


TOTAL_MINES = {
    "STANDARD": [10, 14, 20, 26],
    "B": [10, 12, 21, 24],
    "DAHU": [8, 10, 14, 20],
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


PAGE_COORDINATES = {
    ".": (920, 160, "left"),
    "!": (920, 200, "left"),
    "!!": (960, 200, "left"),
    "5": (920, 320, "left"),
    "6": (920, 360, "left"),
    "7": (920, 400, "left"),
    "8": (920, 440, "left"),
    "5!": (960, 320, "left"),
    "6!": (960, 360, "left"),
    "7!": (960, 400, "left"),
    "8!": (960, 440, "left"),
    "5!!": (1000, 320, "left"),
    "6!!": (1000, 360, "left"),
    "7!!": (1000, 400, "left"),
    "8!!": (1000, 440, "left"),
}

SINGLE_RULE_COORDINATES = {
    "Q5": (480, 160, "left"),
    "Q6": (440, 160, "left"),
    "Q7": (400, 160, "left"),
    "Q8": (360, 160, "left"),
    "T5": (480, 240, "left"),
    "T6": (440, 240, "left"),
    "T7": (400, 240, "left"),
    "T8": (360, 240, "left"),
    "P5": (560, 360, "left"),
    "P6": (600, 360, "left"),
    "P7": (640, 360, "left"),
    "P8": (680, 360, "left"),
    ## add more
}

DOUBLE_RULE_COORDINATES = {
    "Q": ("y", 120),
    "C": ("y", 160),
    "T": ("y", 200),
    "O": ("y", 240),
    "D": ("y", 280),
    "S": ("y", 320),
    "B": ("y", 360),
    "T'": ("y", 400),
    "D'": ("y", 440),
    "A": ("y", 480),
    "M": ("x", 240),
    "L": ("x", 280),
    "W": ("x", 320),
    "N": ("x", 360),
    "X": ("x", 400),
    "P": ("x", 440),
    "E": ("x", 480),
    "X'": ("x", 520),
    "K": ("x", 560),
    "W'": ("x", 600),
    "E'": ("x", 640),
    "#": ("x", 720),
    "#'": ("x", 760),
}
