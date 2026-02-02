from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io


from app.database import get_db
from app.crud import export_crud
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/export",
    tags=["export"],
    dependencies=[Depends(get_current_user)]
)

import csv
import xlsxwriter

@router.get("/class/{class_id}/csv")
def export_class_as_csv(class_id: int, db: Session = Depends(get_db)):
    result = export_crud.generate_class_report_data(db, class_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Class not found or has no students")
    
    data, columns = result

    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)
    
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=class_{class_id}_report.csv"}
    )

@router.get("/class/{class_id}/xlsx")
def export_class_as_xlsx(class_id: int, db: Session = Depends(get_db)):
    result = export_crud.generate_class_report_data(db, class_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Class not found or has no students")
        
    data, columns = result

    stream = io.BytesIO()
    workbook = xlsxwriter.Workbook(stream, {'in_memory': True})
    worksheet = workbook.add_worksheet('Students')
    
    # Write Header
    for col_num, col_name in enumerate(columns):
        worksheet.write(0, col_num, col_name)
        
    # Write Data
    for row_num, row_data in enumerate(data, start=1):
        for col_num, col_name in enumerate(columns):
            worksheet.write(row_num, col_num, row_data.get(col_name, ""))
            
    workbook.close()
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