from color_engine import delta_e_2000


def assign_shade_groups(rolls, tolerance=1.2):
    """
    Leader-based relative grouping using ΔE2000

    rolls: list of dicts
           [{"roll_no":..., "lab":..., ...}, ...]

    tolerance:
        1.0 – 1.3  → A
        1.3 – 2.0  → B
        2.0 - 2.5  → C
        > 2.5      → D
    """

    groups = []

    for roll in rolls:
        assigned = False

        for idx, group in enumerate(groups):
            leader_lab = group["leader_lab"]
            de = delta_e_2000(roll["lab"], leader_lab)

            if de <= tolerance:
                roll["shade_group"] = chr(ord("A") + idx)
                roll["delta_e"] = round(de, 2)
                group["members"].append(roll)
                assigned = True
                break

        # ---------- CREATE NEW SHADE ----------
        if not assigned:
            roll["shade_group"] = chr(ord("A") + len(groups))
            roll["delta_e"] = 0.0

            groups.append({
                "leader_lab": roll["lab"],
                "members": [roll]
            })

    return rolls
