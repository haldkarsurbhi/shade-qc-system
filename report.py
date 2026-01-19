import os
from datetime import datetime
import pandas as pd

from data_store import get_all_rolls


def generate_excel_report(report_path, buyer, contract):
    """
    Generates Excel report with:
    - Buyer & Contract at top (once)
    - Roll-wise shade data below
    """

    rolls = get_all_rolls()

    if not rolls:
        return

    # ---------------- TABLE DATA ----------------
    table_data = []
    for r in rolls:
        table_data.append({
            "Roll No": r["roll_no"],
            "Delta E": r["delta_e"],
            "Shade Group": r["shade_group"],
            "Image Name": os.path.basename(r["image_path"])
        })

    df = pd.DataFrame(table_data)

    # ---------------- WRITE EXCEL ----------------
    with pd.ExcelWriter(report_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Shade Report")
        writer.sheets["Shade Report"] = worksheet

        # Formats
        title_fmt = workbook.add_format({
            "bold": True, "font_size": 14
        })
        header_fmt = workbook.add_format({
            "bold": True, "border": 1
        })
        cell_fmt = workbook.add_format({
            "border": 1
        })

        # ---------------- HEADER INFO ----------------
        worksheet.write("A1", "Shade Grouping QC Report", title_fmt)

        worksheet.write("A3", "Buyer Name:")
        worksheet.write("B3", buyer)

        worksheet.write("A4", "Contract No:")
        worksheet.write("B4", contract)

        worksheet.write("A5", "Report Date:")
        worksheet.write("B5", datetime.now().strftime("%d-%m-%Y %H:%M"))

        # ---------------- TABLE START ----------------
        start_row = 7

        for col, column_name in enumerate(df.columns):
            worksheet.write(start_row, col, column_name, header_fmt)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                worksheet.write(start_row + 1 + row_idx, col_idx, value, cell_fmt)

        # ---------------- COLUMN WIDTH ----------------
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 25)
