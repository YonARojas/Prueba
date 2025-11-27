from flask import Blueprint, request, jsonify
from app.services.justification_service import JustificationService
from app.services.student_service import StudentService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin', methods=['GET'])
def get_admin_dashboard():
    """Endpoint principal para el dashboard administrativo"""
    try:
        # Obtener estadísticas de justificaciones
        justification_stats = JustificationService.get_dashboard_stats()
        
        # Obtener estadísticas de estudiantes
        student_stats = StudentService.get_student_stats()
        
        # Obtener solicitudes recientes
        recent_requests = JustificationService.get_recent_requests(limit=10)
        
        # Obtener estudiantes que requieren atención
        students_requiring_attention = JustificationService.get_students_requiring_attention()[:5]
        
        return jsonify({
            'success': True,
            'data': {
                'metrics': {
                    'justifications': {
                        'total': justification_stats['total_requests'],
                        'pending': justification_stats['pending_requests'],
                        'approved': justification_stats['approved_requests'],
                        'rejected': justification_stats['rejected_requests']
                    },
                    'students': {
                        'total': student_stats['total'],
                        'active': student_stats['active'],
                        'at_risk': student_stats['at_risk'],
                        'critical': student_stats['critical']
                    }
                },
                'recent_requests': [req.to_dict() for req in recent_requests],
                'students_requiring_attention': [s.to_dict() for s in students_requiring_attention]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos del dashboard: {str(e)}'
        }), 500

@dashboard_bp.route('/reports', methods=['GET'])
def get_reports_dashboard():
    """Endpoint para el dashboard de reportes y análisis"""
    try:
        # Obtener métricas principales
        stats = JustificationService.get_dashboard_stats()
        approval_rate = JustificationService.get_approval_rate()
        avg_response_time = JustificationService.get_average_response_time()
        
        # Obtener tendencias mensuales
        monthly_trends = JustificationService.get_monthly_trends()
        
        # Obtener distribución de motivos
        reason_distribution = JustificationService.get_reason_distribution()
        
        # Determinar motivo principal
        main_reason = reason_distribution[0] if reason_distribution else {
            'reason': 'N/A', 
            'percentage': 0
        }
        
        # Obtener solicitudes recientes con estadísticas
        recent_requests = JustificationService.get_recent_requests(limit=10)
        
        # Calcular estadísticas de solicitudes recientes
        recent_requests_data = []
        for req in recent_requests:
            student = req.student
            if student:
                justification_stats = student.get_justification_stats()
                req_data = req.to_dict()
                req_data['student_justification_stats'] = justification_stats
                recent_requests_data.append(req_data)
        
        return jsonify({
            'success': True,
            'data': {
                'metrics': {
                    'total_requests': stats['total_requests'],
                    'approval_rate': approval_rate,
                    'avg_response_time': avg_response_time,
                    'main_reason': main_reason['reason'],
                    'main_reason_percentage': main_reason['percentage']
                },
                'charts': {
                    'monthly_trends': monthly_trends,
                    'reason_distribution': reason_distribution
                },
                'recent_requests': recent_requests_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos de reportes: {str(e)}'
        }), 500

@dashboard_bp.route('/students-management', methods=['GET'])
def get_students_management_dashboard():
    """Endpoint para el dashboard de gestión de estudiantes"""
    try:
        # Obtener estadísticas de estudiantes
        student_stats = StudentService.get_student_stats()
        
        # Obtener estudiantes que requieren atención
        students_requiring_attention = JustificationService.get_students_requiring_attention()
        
        # Obtener algunos estudiantes recientes para mostrar
        recent_students = StudentService.get_all_students(
            status_filter=None, 
            search=None, 
            page=1, 
            per_page=6
        )
        
        return jsonify({
            'success': True,
            'data': {
                'stats': student_stats,
                'students_requiring_attention': [s.to_dict() for s in students_requiring_attention],
                'recent_students': [s.to_dict() for s in recent_students.items]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos de gestión de estudiantes: {str(e)}'
        }), 500

@dashboard_bp.route('/courses', methods=['GET'])
def get_courses():
    """Endpoint para obtener todos los cursos"""
    try:
        from app.models.course import Course
        courses = Course.query.filter_by(status='A').all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in courses]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener cursos: {str(e)}'
        }), 500

@dashboard_bp.route('/courses/<int:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    """Endpoint para obtener estudiantes de un curso específico"""
    try:
        from app.models.course_enrollment import CourseEnrollment
        from app.models.student import Student
        
        # Obtener inscripciones activas del curso
        enrollments = CourseEnrollment.query.filter_by(
            course_id=course_id,
            status='A'
        ).all()
        
        # Obtener estudiantes
        students = []
        for enrollment in enrollments:
            student = Student.query.get(enrollment.student_id)
            if student and student.status == 'A':
                students.append(student.to_dict())
        
        return jsonify({
            'success': True,
            'data': students
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estudiantes del curso: {str(e)}'
        }), 500
