from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import pandas as pd

from app.database import get_db
from app.crud import export_crud
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/export",
    tags=["export"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/class/{class_id}/csv")
def export_class_as_csv(class_id: int, db: Session = Depends(get_db)):
    df = export_crud.generate_class_report_df(db, class_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Class not found or has no students")

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=class_{class_id}_report.csv"}
    )

@router.get("/class/{class_id}/xlsx")
def export_class_as_xlsx(class_id: int, db: Session = Depends(get_db)):
    df = export_crud.generate_class_report_df(db, class_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Class not found or has no students")

    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    
    stream.seek(0)
    
    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=class_{class_id}_report.xlsx"}
    )


@router.get("/student/{student_id}/pdf")
def export_student_as_pdf(student_id: int, db: Session = Depends(get_db)):
    pdf_buffer = export_crud.generate_student_pdf_report(db, student_id)
    if pdf_buffer is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # --- THIS IS THE FIX: We read the bytes from the buffer before sending ---
    return Response(
        content=pdf_buffer.getvalue(),
        media_type='application/pdf',
        headers={"Content-Disposition": f"attachment; filename=student_{student_id}_report.pdf"}
    )