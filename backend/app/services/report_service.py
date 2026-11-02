import io
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_attendance_excel(
    class_info: Dict[str, Any],
    session_date: datetime.datetime,
    records: List[Dict[str, Any]],
    cumulative_summary: Optional[List[Dict[str, Any]]] = None
) -> bytes:
    """
    Generates a beautifully formatted college-ready Excel workbook with:
    1. Session Attendance Sheet
    2. Cumulative Attendance & Eligibility Sheet (<75% flagged in red)
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Session Details DataFrame
        session_rows = []
        for r in records:
            method_raw = str(r.get("method", "AUTO")).upper()
            if "MANUAL" in method_raw:
                method_label = "Teacher Manual Override"
            elif "REVIEW" in method_raw:
                method_label = "Teacher Verified (AI Queue)"
            elif r.get("status") == "ABSENT":
                method_label = "Unmatched / Absent"
            else:
                method_label = "AI Facial Recognition"

            session_rows.append({
                "USN": r["usn"],
                "Student Name": r.get("name", "N/A"),
                "Status": r["status"],
                "Confidence": f"{round(r.get('confidence', 1.0) * 100, 1)}%" if r.get("status") == "PRESENT" else "0.0%",
                "Verification Method": method_label
            })

        df_session = pd.DataFrame(session_rows)
        df_session.to_excel(writer, sheet_name="Session Attendance", index=False, startrow=3)

        wb = writer.book
        ws_session = writer.sheets["Session Attendance"]

        # Title Block
        ws_session["A1"] = f"Classroom Attendance - {class_info.get('subject')} (Section: {class_info.get('section')})"
        ws_session["A1"].font = Font(name="Calibri", size=14, bold=True, color="1F497D")
        ws_session["A2"] = f"Date: {session_date.strftime('%Y-%m-%d %H:%M')} | Total Students: {len(records)}"
        ws_session["A2"].font = Font(name="Calibri", size=10, italic=True)

        # Style header row (Row 4)
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        for col_idx in range(1, len(df_session.columns) + 1):
            cell = ws_session.cell(row=4, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Style data rows and highlight PRESENT (green) vs ABSENT (red)
        green_fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
        red_fill = PatternFill(start_color="FCE5CD", end_color="FCE5CD", fill_type="solid")

        for row_idx in range(5, len(session_rows) + 5):
            status_cell = ws_session.cell(row=row_idx, column=3)
            if status_cell.value == "PRESENT":
                status_cell.fill = green_fill
                status_cell.font = Font(bold=True, color="274E13")
            else:
                status_cell.fill = red_fill
                status_cell.font = Font(bold=True, color="783F04")

        # Adjust column widths
        for col in ws_session.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_session.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # 2. Cumulative Summary Sheet
        if cumulative_summary:
            df_cum = pd.DataFrame(cumulative_summary)
            df_cum.to_excel(writer, sheet_name="Cumulative Summary", index=False, startrow=3)
            ws_cum = writer.sheets["Cumulative Summary"]

            ws_cum["A1"] = f"Cumulative Attendance Record - {class_info.get('subject')}"
            ws_cum["A1"].font = Font(name="Calibri", size=14, bold=True, color="1F497D")

            for col_idx in range(1, len(df_cum.columns) + 1):
                cell = ws_cum.cell(row=4, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Flag < 75% in red
            shortage_fill = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
            for row_idx in range(5, len(cumulative_summary) + 5):
                pct_cell = ws_cum.cell(row=row_idx, column=df_cum.columns.get_loc("Attendance %") + 1)
                try:
                    pct_val = float(str(pct_cell.value).replace("%", ""))
                    if pct_val < 75.0:
                        pct_cell.fill = shortage_fill
                        pct_cell.font = Font(bold=True, color="990000")
                except Exception:
                    pass

            for col in ws_cum.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws_cum.column_dimensions[col_letter].width = max(max_len + 4, 12)

    output.seek(0)
    return output.getvalue()

def generate_attendance_csv(records: List[Dict[str, Any]]) -> str:
    """Generates a standard CSV string for ERP/portal ingest."""
    df = pd.DataFrame(records)
    return df.to_csv(index=False)
