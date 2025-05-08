## not fixed
# MAX_CASES = 10000  ## easy puzzles, fast
# MAX_CASES = 30000  ## medium puzzles
# MAX_CASES = 90000  ## hard puzzles
# MAX_CASES = 300000  ## harder puzzles
# MAX_CASES = 650000  ## very hard case (works up to 22 choose 10 = 646646)
MAX_CASES = 1100000  ## very hard case (works up to 25 choose 17 = 1081575)


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
    "outsider_condition": "invalid",
}

RULE_T = {
    "directions": [
        [(0, 0), (0, 1), (0, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 0), (1, -1), (2, -2)],
    ],
    "pattern_condition": "no_all_mines",
    "outsider_condition": "invalid",
}

RULE_A = {
    "directions": [
        [(0, 0), (1, 2)],
        [(1, 0), (0, 2)],
        [(0, 0), (2, 1)],
        [(2, 0), (0, 1)],
    ],
    "pattern_condition": "no_all_mines",
    "outsider_condition": "invalid",
}

RULE_H = {
    "directions": [[(0, 0), (0, 1)]],
    "pattern_condition": "no_all_mines",
    "outsider_condition": "invalid",
}

RULE_U = {
    "directions": [[(0, 0), (0, 1)], [(0, 0), (1, 0)]],
    "pattern_condition": "no_all_mines",
    "outsider_condition": "invalid",
}


RULE_D1 = {
    "directions": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "pattern_condition": "max_two_mines",
    "outsider_condition": "number",
}

RULE_D2 = {
    "directions": [[(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]],
    "pattern_condition": "cross_D",
    "outsider_condition": "number",
}

# RULE_B = {
#     "name": "B",
#     "directions": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
#     "pattern_condition": "max_two_mines",
#     "outsider_condition": "number",
# }


def get_rule_B(size):
    directions = [
        [(i, 0) for i in range(size)],
        [(0, j) for j in range(size)],
    ]
    if size in [5, 6]:
        pattern_condition = "exact_two_mines"
    elif size in [7, 8]:
        pattern_condition = "exact_three_mines"
    return {
        "name": "B",
        "directions": directions,
        "pattern_condition": pattern_condition,
        "outsider_condition": "invalid",
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


BASIC_RULES = "VQCTODSBMLWNXPE"

PAGE_COORDINATES = {
    ".": (920, 160, "left"),
    "!": (920, 200, "left"),
    "!!": (960, 200, "left"),
    "?": (920, 280, "left"),
    "?!": (960, 280, "left"),
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
    ## left side
    "Q5": (480, 160, "left"),
    "Q6": (440, 160, "left"),
    "Q7": (400, 160, "left"),
    "Q8": (360, 160, "left"),
    "C5": (480, 200, "left"),
    "C6": (440, 200, "left"),
    "C7": (400, 200, "left"),
    "C8": (360, 200, "left"),
    "T5": (480, 240, "left"),
    "T6": (440, 240, "left"),
    "T7": (400, 240, "left"),
    "T8": (360, 240, "left"),
    "O5": (480, 280, "left"),
    "O6": (440, 280, "left"),
    "O7": (400, 280, "left"),
    "O8": (360, 280, "left"),
    "D5": (480, 320, "left"),
    "D6": (440, 320, "left"),
    "D7": (400, 320, "left"),
    "D8": (360, 320, "left"),
    "S5": (480, 360, "left"),
    "S6": (440, 360, "left"),
    "S7": (400, 360, "left"),
    "S8": (360, 360, "left"),
    "B5": (480, 400, "left"),
    "B6": (440, 400, "left"),
    "B7": (400, 400, "left"),
    "B8": (360, 400, "left"),
    ## right side
    "M5": (560, 160, "left"),
    "M6": (600, 160, "left"),
    "M7": (640, 160, "left"),
    "M8": (680, 160, "left"),
    "L5": (560, 200, "left"),
    "L6": (600, 200, "left"),
    "L7": (640, 200, "left"),
    "L8": (680, 200, "left"),
    "W5": (560, 240, "left"),
    "W6": (600, 240, "left"),
    "W7": (640, 240, "left"),
    "W8": (680, 240, "left"),
    "N5": (560, 280, "left"),
    "N6": (600, 280, "left"),
    "N7": (640, 280, "left"),
    "N8": (680, 280, "left"),
    "X5": (560, 320, "left"),
    "X6": (600, 320, "left"),
    "X7": (640, 320, "left"),
    "X8": (680, 320, "left"),
    "P5": (560, 360, "left"),
    "P6": (600, 360, "left"),
    "P7": (640, 360, "left"),
    "P8": (680, 360, "left"),
    "E5": (560, 400, "left"),
    "E6": (600, 400, "left"),
    "E7": (640, 400, "left"),
    "E8": (680, 400, "left"),
    ## other side
    "X'5": (440, 120, "left"),
    "X'6": (480, 120, "left"),
    "X'7": (520, 120, "left"),
    "X'8": (560, 120, "left"),
    "K5": (440, 160, "left"),
    "K6": (480, 160, "left"),
    "K7": (520, 160, "left"),
    "K8": (560, 160, "left"),
    "W'5": (440, 200, "left"),
    "W'6": (480, 200, "left"),
    "W'7": (520, 200, "left"),
    "W'8": (560, 200, "left"),
    "T'5": (440, 240, "left"),
    "T'6": (480, 240, "left"),
    "T'7": (520, 240, "left"),
    "T'8": (560, 240, "left"),
    "D'5": (440, 280, "left"),
    "D'6": (480, 280, "left"),
    "D'7": (520, 280, "left"),
    "D'8": (560, 280, "left"),
    "A5": (440, 320, "left"),
    "A6": (480, 320, "left"),
    "A7": (520, 320, "left"),
    "A8": (560, 320, "left"),
    "H5": (440, 360, "left"),
    "H6": (480, 360, "left"),
    "H7": (520, 360, "left"),
    "H8": (560, 360, "left"),
    "E'5": (440, 400, "left"),
    "E'6": (480, 400, "left"),
    "E'7": (520, 400, "left"),
    "E'8": (560, 400, "left"),
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
