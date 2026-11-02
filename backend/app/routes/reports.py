from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Session as AttendanceSession, Class, Student, Attendance, Teacher
from ..services.report_service import generate_attendance_excel, generate_attendance_csv
from ..utils.security import decode_access_token

router = APIRouter(prefix="/reports", tags=["Reports"])
security_optional = HTTPBearer(auto_error=False)

def get_current_teacher_flexible(
    token_query: Optional[str] = Query(None, alias="token"),
    auth_cred: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Teacher:
    """
    Allows authentication via either:
    1. HTTP Header: Authorization: Bearer <token>
    2. Query Parameter: ?token=<token> (for direct browser file downloads/links)
    """
    token = None
    if auth_cred and auth_cred.credentials:
        token = auth_cred.credentials
    elif token_query:
        token = token_query

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Provide Bearer header or ?token= query parameter."
        )

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )

    teacher = db.query(Teacher).filter(Teacher.email == payload.get("sub")).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher account not found")
    return teacher

@router.get("/session/{session_id}/excel")
def download_session_excel(
    session_id: int,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher_flexible)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    cls = db.query(Class).filter(Class.id == session.class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=403, detail="Access denied")

    records = []
    for att in session.attendance_records:
        student = db.query(Student).filter(Student.usn == att.usn).first()
        records.append({
            "usn": att.usn,
            "name": student.name if student else "N/A",
            "status": att.status,
            "confidence": att.confidence,
            "method": att.method
        })

    # Compute Cumulative Attendance Summary for the class across all sessions
    all_sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id == cls.id).all()
    # Filter sessions that have at least 1 record
    valid_sessions = [s for s in all_sessions if len(s.attendance_records) > 0]
    valid_session_ids = [s.id for s in valid_sessions]
    total_sessions_count = len(valid_session_ids)

    cumulative_summary = []
    if total_sessions_count > 0:
        section_students = db.query(Student).filter(Student.section == cls.section).all()
        for s in section_students:
            present_count = db.query(Attendance).filter(
                Attendance.session_id.in_(valid_session_ids),
                Attendance.usn == s.usn,
                Attendance.status == "PRESENT"
            ).count()
            pct = round((present_count / total_sessions_count) * 100, 1)
            cumulative_summary.append({
                "USN": s.usn,
                "Student Name": s.name,
                "Attended Sessions": present_count,
                "Total Sessions": total_sessions_count,
                "Attendance %": f"{pct}%",
                "Eligibility Status": "Eligible (>= 75%)" if pct >= 75.0 else "Shortage Warning (< 75%)"
            })

    class_info = {"subject": cls.subject, "section": cls.section}
    excel_bytes = generate_attendance_excel(class_info, session.date, records, cumulative_summary=cumulative_summary)

    filename = f"Attendance_{cls.subject}_{cls.section}_{session.date.strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/session/{session_id}/csv")
def download_session_csv(
    session_id: int,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher_flexible)
):
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    cls = db.query(Class).filter(Class.id == session.class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=403, detail="Access denied")

    records = []
    for att in session.attendance_records:
        student = db.query(Student).filter(Student.usn == att.usn).first()
        records.append({
            "USN": att.usn,
            "Name": student.name if student else "N/A",
            "Subject": cls.subject,
            "Section": cls.section,
            "Date": session.date.strftime('%Y-%m-%d %H:%M'),
            "Status": att.status,
            "Method": att.method,
            "Confidence": round(att.confidence, 4)
        })

    csv_data = generate_attendance_csv(records)
    filename = f"Attendance_{cls.subject}_{cls.section}_{session.date.strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
