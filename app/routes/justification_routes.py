from flask import Blueprint, request, jsonify
from app import db
from app.models.justification import Justification
from app.services.justification_service import JustificationService
from app.services.student_service import StudentService
from datetime import datetime
import os

justification_bp = Blueprint('justifications', __name__)

@justification_bp.route('/stats', methods=['GET'])
def get_justification_stats():
    """Endpoint para obtener estadísticas de justificaciones"""
    try:
        total = db.session.query(Justification).count()
        pending = db.session.query(Justification).filter(Justification.status == 'PENDIENTE').count()
        approved = db.session.query(Justification).filter(Justification.status == 'APROBADA').count()
        rejected = db.session.query(Justification).filter(Justification.status == 'RECHAZADA').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'pending': pending,
                'approved': approved,
                'rejected': rejected
            }
        })
    except Exception as e:
        print(f"❌ Error en /stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Endpoint para obtener datos del dashboard administrativo"""
    try:
        stats = JustificationService.get_dashboard_stats()
        recent_requests = JustificationService.get_recent_requests(limit=5)
        
        # Convertir a diccionarios
        recent_requests_data = [req.to_dict() for req in recent_requests]
        
        return jsonify({
            'success': True,
            'data': {
                'stats': stats,
                'recent_requests': recent_requests_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos del dashboard: {str(e)}'
        }), 500

@justification_bp.route('/', methods=['GET'])
def get_justifications():
    """Endpoint para obtener justificaciones con filtros"""
    try:
        status = request.args.get('status', 'Todas')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        pagination = JustificationService.get_requests_by_status(
            status=status if status != 'Todas' else None,
            search=search if search else None,
            page=page,
            per_page=per_page
        )
        
        # Obtener estadísticas para los contadores
        stats = JustificationService.get_dashboard_stats()
        
        # Enriquecer justificaciones con datos del estudiante
        justifications_data = []
        for j in pagination.items:
            j_dict = j.to_dict()
            # Obtener datos del estudiante
            student = StudentService.get_student_by_id(j.student_id)
            if student:
                j_dict['student_email'] = student.email
                j_dict['student_phone'] = student.phone
                j_dict['student_career'] = student.career
                j_dict['student_semester'] = student.semester
            justifications_data.append(j_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'justifications': justifications_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'stats': {
                    'total': stats['total_requests'],
                    'pending': stats['pending_requests'],
                    'approved': stats['approved_requests'],
                    'rejected': stats['rejected_requests']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener justificaciones: {str(e)}'
        }), 500

@justification_bp.route('/all', methods=['GET'])
def get_all_justifications():
    """Endpoint para obtener todas las justificaciones (para dashboard)"""
    try:
        justifications = JustificationService.get_all_requests()
        
        # Enriquecer con datos del estudiante
        justifications_data = []
        for j in justifications:
            j_dict = j.to_dict()
            # Obtener datos del estudiante
            student = StudentService.get_student_by_id(j.student_id)
            if student:
                j_dict['student_name'] = student.full_name
                j_dict['student_code'] = student.student_code
                j_dict['student_email'] = student.email
                j_dict['student_phone'] = student.phone
                j_dict['student_career'] = student.career
                j_dict['student_semester'] = student.semester
            # Obtener nombre del curso
            from app.models.course import Course
            course = db.session.query(Course).get(j.course_id)
            if course:
                j_dict['course_name'] = course.course_name
            # Asegurar que los campos de attachment estén presentes
            print(f"📎 Justificación {j.id} - Archivo: {j.attachment_filename}")
            justifications_data.append(j_dict)
        
        return jsonify({
            'success': True,
            'data': justifications_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener justificaciones: {str(e)}'
        }), 500

@justification_bp.route('/<int:justification_id>', methods=['GET'])
def get_justification_details(justification_id):
    """Endpoint para obtener detalles de una justificación específica"""
    try:
        justification = JustificationService.get_request_by_id(justification_id)
        
        if not justification:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': justification.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles: {str(e)}'
        }), 500

@justification_bp.route('/<int:justification_id>/approve', methods=['POST'])
def approve_justification(justification_id):
    """Endpoint para aprobar una justificación"""
    try:
        data = request.json or {}
        admin_id = data.get('professor_id') or data.get('admin_id', 1)
        admin_response = data.get('admin_response', '')
        
        success = JustificationService.approve_request(justification_id, admin_id, admin_response)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Justificación aprobada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
    except Exception as e:
        print(f"❌ Error al aprobar: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al aprobar justificación: {str(e)}'
        }), 500

@justification_bp.route('/<int:justification_id>/reject', methods=['POST'])
def reject_justification(justification_id):
    """Endpoint para rechazar una justificación"""
    try:
        data = request.json or {}
        admin_id = data.get('professor_id') or data.get('admin_id', 1)
        admin_response = data.get('admin_response', '')
        
        success = JustificationService.reject_request(justification_id, admin_id, admin_response)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Justificación rechazada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
    except Exception as e:
        print(f"❌ Error al rechazar: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al rechazar justificación: {str(e)}'
        }), 500

# RUTA DESHABILITADA - Usar justification_student_routes.py en su lugar
# @justification_bp.route('/create', methods=['POST'])
# def create_justification():
#     """Endpoint para crear una nueva justificación"""
#     try:
#         data = request.get_json()
#         
#         # Validar datos requeridos
#         required_fields = ['student_id', 'absence_date', 'course_subject', 'reason', 'detailed_description']
#         for field in required_fields:
#             if not data.get(field):
#                 return jsonify({
#                     'success': False,
#                     'message': f'Campo requerido: {field}'
#                 }), 400
#         
#         # Convertir fecha
#         absence_date = datetime.strptime(data['absence_date'], '%Y-%m-%d').date()
#         
#         # Crear justificación
#         justification = JustificationService.create_request(
#             student_id=data['student_id'],
#             absence_date=absence_date,
#             course_subject=data['course_subject'],
#             reason=data['reason'],
#             detailed_description=data['detailed_description']
#         )
#         
#         return jsonify({
#             'success': True,
#             'message': 'Justificación creada exitosamente',
#             'data': justification.to_dict()
#         }), 201
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error al crear justificación: {str(e)}'
#         }), 500

@justification_bp.route('/reports/monthly-trends', methods=['GET'])
def get_monthly_trends():
    """Endpoint para obtener tendencias mensuales"""
    try:
        trends = JustificationService.get_monthly_trends()
        return jsonify({
            'success': True,
            'data': trends
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener tendencias: {str(e)}'
        }), 500

@justification_bp.route('/reports/reason-distribution', methods=['GET'])
def get_reason_distribution():
    """Endpoint para obtener distribución de motivos"""
    try:
        distribution = JustificationService.get_reason_distribution()
        return jsonify({
            'success': True,
            'data': distribution
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener distribución: {str(e)}'
        }), 500

@justification_bp.route('/reports/analytics', methods=['GET'])
def get_analytics():
    """Endpoint para obtener análisis completo"""
    try:
        stats = JustificationService.get_dashboard_stats()
        approval_rate = JustificationService.get_approval_rate()
        avg_response_time = JustificationService.get_average_response_time()
        monthly_trends = JustificationService.get_monthly_trends()
        reason_distribution = JustificationService.get_reason_distribution()
        
        # Determinar motivo principal
        main_reason = reason_distribution[0] if reason_distribution else {'reason': 'N/A', 'percentage': 0}
        
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
                'monthly_trends': monthly_trends,
                'reason_distribution': reason_distribution,
                'students_requiring_attention': [
                    s.to_dict() for s in JustificationService.get_students_requiring_attention()
                ]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener análisis: {str(e)}'
        }), 500