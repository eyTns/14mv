from window.const import (
    PAGE_COORDINATES,
    SINGLE_RULE_COORDINATES,
    DOUBLE_RULE_COORDINATES,
)


def get_page_coordinates(rule, size=None, difficulty=None):
    if difficulty is None:
        difficulty = ""
    is_combined_rule = len(rule.replace("'", "")) >= 2
    if is_combined_rule:
        key = f"{size}{difficulty}"
        return PAGE_COORDINATES.get(key)
    else:
        difficulty_key = difficulty if difficulty else "."
        return PAGE_COORDINATES.get(difficulty_key)


def get_single_rule_coordinates(rule, size):
    return SINGLE_RULE_COORDINATES.get(f"{rule}{size}")


def get_gallery_coordinates(rule):
    first_rule = ""
    second_rule = ""
    if rule[1] == "'":
        first_rule = rule[:2]
        second_rule = rule[2:]
    else:
        first_rule = rule[0]
        second_rule = rule[1:]
    first_coord = DOUBLE_RULE_COORDINATES.get(first_rule)
    second_coord = DOUBLE_RULE_COORDINATES.get(second_rule)
    coord = dict()
    coord[first_coord[0]] = first_coord[1]
    coord[second_coord[0]] = second_coord[1]
    return (coord["x"], coord["y"], "left")


class PuzzleVariant:
    def __init__(self, rule, size, difficulty=""):
        self.rule = rule
        self.size = size
        self.difficulty = difficulty

    @classmethod
    def from_string(cls, variant_string):
        parts = variant_string.strip().split()
        rule = parts[0]
        size_diff = parts[1]
        difficulty = ""
        if size_diff.endswith("!!"):
            size = int(size_diff[:-2])
            difficulty = "!!"
        elif size_diff.endswith("!"):
            size = int(size_diff[:-1])
            difficulty = "!"
        else:
            size = int(size_diff)
        return cls(rule, size, difficulty)

    def __str__(self):
        return f"{self.rule} {self.size}{self.difficulty}"

    def get_menu_coordinates(self):
        is_combined_rule = len(self.rule.replace("'", "")) >= 2
        page_coord = get_page_coordinates(self.rule, self.size, self.difficulty)
        if is_combined_rule:
            button_coord = get_gallery_coordinates(self.rule)
        else:
            button_coord = get_single_rule_coordinates(self.rule, self.size)
        return [page_coord, button_coord]

    def navigate_to_variant(self, window_title):
        from window.utils import switch_to_other_size, activate_window

        activate_window(window_title)
        page_coord, button_coord = self.get_menu_coordinates()
        switch_to_other_size(window_title, [page_coord, button_coord])
        return True
