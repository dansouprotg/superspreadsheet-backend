from flask import Blueprint, jsonify, Response, send_file
from app.database import SessionLocal
from app.crud import export_crud
import io
import csv
import xlsxwriter

export_bp = Blueprint('export', __name__)

@export_bp.route("/api/export/class/<int:class_id>/csv", methods=["GET"])
def export_class_as_csv(class_id):
    db = SessionLocal()
    try:
        result = export_crud.generate_class_report_data(db, class_id)
        if result is None:
             return jsonify({"detail": "Class not found or has no students"}), 404
        
        data, columns = result

        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        
        # Convert StringIO to BytesIO for send_file if needed/preferred, or use Response directly
        output = io.BytesIO(stream.getvalue().encode('utf-8'))
        
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"class_{class_id}_report.csv"
        )
    finally:
        db.close()

@export_bp.route("/api/export/class/<int:class_id>/xlsx", methods=["GET"])
def export_class_as_xlsx(class_id):
    db = SessionLocal()
    try:
        result = export_crud.generate_class_report_data(db, class_id)
        if result is None:
             return jsonify({"detail": "Class not found or has no students"}), 404
            
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
        
        return send_file(
            stream,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"class_{class_id}_report.xlsx"
        )
    finally:
        db.close()


@export_bp.route("/api/export/student/<int:student_id>/pdf", methods=["GET"])
def export_student_as_pdf(student_id):
    db = SessionLocal()
    try:
        pdf_buffer = export_crud.generate_student_pdf_report(db, student_id)
        if pdf_buffer is None:
             return jsonify({"detail": "Student not found"}), 404

        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"student_{student_id}_report.pdf"
        )
    finally:
        db.close()
