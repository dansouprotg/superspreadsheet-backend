from sqlalchemy.orm import Session
from . import student_crud, class_crud, analytics_crud

import io
from datetime import datetime

# ReportLab Imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


# --- CSV and XLSX Generation (Refactored to remove Pandas) ---

def generate_class_report_data(db: Session, class_id: int):
    db_class = class_crud.get_class(db, class_id=class_id)
    if not db_class:
        return None

    ordered_columns = ["Student Name", "Listening", "Reading", "Speaking", "Writing"]
    data = []
    
    for student in db_class.students:
        student_data = {"Student Name": student.name}
        # Get skill status values
        skills_map = {skill.name: skill.current_status.value for skill in student.skills}
        
        # Ensure all columns exist (default to empty string if missing)
        row = {}
        row["Student Name"] = student.name
        for col in ordered_columns[1:]: # Skip Student Name
            row[col] = skills_map.get(col, "")
            
        data.append(row)

    return data, ordered_columns

# --- NEW Professional PDF Generation using reportlab ---

def generate_student_pdf_report(db: Session, student_id: int):
    student = student_crud.get_student_by_id(db, student_id=student_id)
    if not student:
        return None

    analytics = analytics_crud.get_student_analytics(db, student_id=student_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=1*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=18))
    styles.add(ParagraphStyle(name='SectionTitle', parent=styles['h2'], fontSize=14, spaceBefore=20, spaceAfter=10))
    styles.add(ParagraphStyle(name='SmallGrey', parent=styles['Normal'], textColor=colors.dimgrey))

    story = []

    # --- Header ---
    story.append(Paragraph("Student Progress Report", styles['ReportTitle']))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['SmallGrey']))
    story.append(Spacer(1, 0.25*inch))

    # --- Student Info ---
    info_data = [
        [Paragraph("<b>Student:</b>", styles['Normal']), Paragraph(student.name, styles['Normal'])],
        [Paragraph("<b>Class:</b>", styles['Normal']), Paragraph(student.enrolled_class.name, styles['Normal'])],
        [Paragraph("<b>Enrollment Date:</b>", styles['Normal']), Paragraph(student.enrollment_date.strftime('%Y-%m-%d'), styles['Normal'])],
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, None])
    info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 0.25*inch))

    # --- Analytics Summary Section ---
    story.append(Paragraph("Current Status Overview", styles['SectionTitle']))

    # Create Bar Chart
    drawing = Drawing(400, 200)
    chart_data = [(
        analytics['red']['count'],
        analytics['yellow']['count'],
        analytics['green']['count'],
        analytics['gold']['count'],
    )]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = chart_data
    bc.groupSpacing = 10
    bc.barSpacing = 2
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 4 # There are 4 skills total
    bc.valueAxis.valueStep = 1
    bc.categoryAxis.labels.boxAnchor = 'n'
    bc.categoryAxis.labels.textAnchor = 'middle'
    bc.categoryAxis.categoryNames = ['Red', 'Yellow', 'Green', 'Gold']
    bc.bars[0].fillColor = colors.HexColor('#dc3545')
    bc.bars[1].fillColor = colors.HexColor('#ffc107')
    bc.bars[2].fillColor = colors.HexColor('#198754')
    bc.bars[3].fillColor = colors.HexColor('#ffb700')
    drawing.add(bc)
    story.append(drawing)
    story.append(Spacer(1, 0.25*inch))

    # --- Progress Timeline Section ---
    story.append(Paragraph("Progress Timeline (Most Recent First)", styles['SectionTitle']))
    
    if student.milestones:
        sorted_milestones = sorted(student.milestones, key=lambda m: m.timestamp, reverse=True)
        
        timeline_data = [
            [Paragraph("<b>Date</b>", styles['Normal']), Paragraph("<b>Skill</b>", styles['Normal']), Paragraph("<b>Change</b>", styles['Normal']), Paragraph("<b>Notes & Narrative</b>", styles['Normal'])]
        ]
        
        for milestone in sorted_milestones:
            date_str = milestone.timestamp.strftime('%Y-%m-%d %H:%M')
            skill_str = milestone.skill_name
            change_str = f"{milestone.previous_status.value if milestone.previous_status else 'None'} → {milestone.new_status.value}"
            
            notes = []
            if milestone.narrative:
                notes.append(Paragraph(f"<i>{milestone.narrative}</i>", styles['Italic']))
            if milestone.comment:
                notes.append(Paragraph(f"<b>Teacher:</b> {milestone.comment}", styles['Normal']))
            
            timeline_data.append([date_str, skill_str, change_str, notes])

        timeline_table = Table(timeline_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, None])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(timeline_table)
    else:
        story.append(Paragraph("No milestones recorded.", styles['Normal']))

    doc.build(story)
    
    buffer.seek(0)
    return buffer