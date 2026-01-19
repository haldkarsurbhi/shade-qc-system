from grouping import assign_shade_groups

# ---------- GLOBAL STORAGE ----------
ROLL_DATA = []


def add_roll(roll_no, image_path, lab):
    ROLL_DATA.append({
        "roll_no": roll_no,
        "image_path": image_path,
        "lab": lab,
        "shade_group": "-",
        "delta_e": None
    })


def get_all_rolls():
    return ROLL_DATA


def perform_grouping(tolerance=1.5):
    global ROLL_DATA
    ROLL_DATA = assign_shade_groups(ROLL_DATA, tolerance)
    return ROLL_DATA
