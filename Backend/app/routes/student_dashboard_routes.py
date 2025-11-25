from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.models.justification import Justification
from app.models.course import Course
from sqlalchemy import func

student_dashboard_bp = Blueprint('student_dashboard', __name__)

@student_dashboard_bp.route('/<int:student_id>/dashboard', methods=['GET'])
def get_student_dashboard(student_id):
    """Dashboard del estudiante con estadísticas"""
    try:
        student = db.session.query(Student).get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Estadísticas de justificaciones
        total_justifications = db.session.query(Justification).filter(
            Justification.student_id == student_id
        ).count()
        
        pending_justifications = db.session.query(Justification).filter(
            Justification.student_id == student_id,
            Justification.status == 'PENDIENTE'
        ).count()
        
        approved_justifications = db.session.query(Justification).filter(
            Justification.student_id == student_id,
            Justification.status == 'APROBADA'
        ).count()
        
        rejected_justifications = db.session.query(Justification).filter(
            Justification.student_id == student_id,
            Justification.status == 'RECHAZADA'
        ).count()
        
        # Obtener estadísticas de asistencia desde la base de datos
        try:
            from app.models.attendance_record import AttendanceRecord
            total_classes = db.session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id
            ).count()
            
            present = db.session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.status == 'PRESENTE'
            ).count()
            
            absent = db.session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.status == 'AUSENTE'
            ).count()
            
            justified = db.session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.status == 'JUSTIFICADO'
            ).count()
            
            if total_classes > 0:
                attendance_percentage = round(((present + justified) / total_classes) * 100, 1)
            else:
                attendance_percentage = 100
        except Exception as stats_error:
            print(f"Error al calcular estadísticas: {stats_error}")
            attendance_percentage = 100
            total_classes = 0
            present = 0
            absent = 0
            justified = 0
        
        # Justificaciones recientes
        recent_justifications = db.session.query(Justification).filter(
            Justification.student_id == student_id
        ).order_by(Justification.submission_date.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'student': student.to_dict(include_stats=False),
                'stats': {
                    'total_justifications': total_justifications,
                    'pending': pending_justifications,
                    'approved': approved_justifications,
                    'rejected': rejected_justifications,
                    'attendance_percentage': attendance_percentage,
                    'total_classes': total_classes,
                    'present': present,
                    'absent': absent,
                    'justified': justified
                },
                'recent_justifications': [j.to_dict() for j in recent_justifications]
            }
        })
        
    except Exception as e:
        print(f"Error en dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@student_dashboard_bp.route('/<int:student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    """Obtener cursos del estudiante"""
    try:
        # Aquí deberías hacer un JOIN con course_enrollments
        # Por ahora, devolvemos todos los cursos
        courses = db.session.query(Course).filter(Course.status == 'A').all()
        
        return jsonify({
            'success': True,
            'data': [course.to_dict() for course in courses]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@student_dashboard_bp.route('/<int:student_id>/attendance', methods=['GET'])
def get_student_attendance(student_id):
    """Obtener asistencia del estudiante por curso"""
    try:
        from app.models.attendance_record import AttendanceRecord
        
        # Obtener todos los registros de asistencia del estudiante agrupados por curso
        from sqlalchemy import case
        
        attendance_by_course = db.session.query(
            Course.course_name,
            func.count(AttendanceRecord.id).label('total'),
            func.sum(case((AttendanceRecord.status == 'PRESENTE', 1), else_=0)).label('present'),
            func.sum(case((AttendanceRecord.status == 'AUSENTE', 1), else_=0)).label('absent'),
            func.sum(case((AttendanceRecord.status == 'JUSTIFICADO', 1), else_=0)).label('justified')
        ).join(
            AttendanceRecord, Course.id == AttendanceRecord.course_id
        ).filter(
            AttendanceRecord.student_id == student_id
        ).group_by(
            Course.course_name
        ).all()
        
        # Formatear los datos
        attendance_data = []
        for row in attendance_by_course:
            total = row.total or 0
            present = row.present or 0
            justified = row.justified or 0
            absent = row.absent or 0
            
            if total > 0:
                percentage = round(((present + justified) / total) * 100, 1)
            else:
                percentage = 0
            
            attendance_data.append({
                'course': row.course_name,
                'total': total,
                'present': present,
                'absent': absent,
                'justified': justified,
                'percentage': percentage
            })
        
        return jsonify({
            'success': True,
            'data': attendance_data
        })
        
    except Exception as e:
        print(f"Error en attendance: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
