from flask import Blueprint, request, jsonify
from app.services.student_service import StudentService
from datetime import datetime

student_bp = Blueprint('students', __name__)

@student_bp.route('/', methods=['GET'])
def get_students():
    """Endpoint para obtener estudiantes con filtros"""
    try:
        status_filter = request.args.get('status', 'todos')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))  # Aumentar para mostrar más estudiantes
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        print(f"📋 Filtros recibidos: status={status_filter}, include_inactive={include_inactive}, search={search}")
        
        # Mapear filtros del frontend al backend
        backend_status_filter = None
        if status_filter == 'activo':
            backend_status_filter = 'Activos'
        elif status_filter == 'inactivo':
            backend_status_filter = 'Inactivos'
        elif status_filter == 'todos':
            backend_status_filter = None  # Mostrar todos
        else:
            backend_status_filter = status_filter
        
        pagination = StudentService.get_all_students(
            status_filter=backend_status_filter,
            search=search if search else None,
            page=page,
            per_page=per_page
        )
        
        print(f"✅ Estudiantes encontrados: {pagination.total}")
        
        # Obtener estadísticas
        stats = StudentService.get_student_stats()
        
        # Verificar si se solicitan estadísticas
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        
        # Convertir estudiantes a dict
        students_data = []
        for student in pagination.items:
            student_dict = student.to_dict(include_stats=include_stats)
            students_data.append(student_dict)
        
        if include_stats and students_data:
            print(f"📊 Ejemplo de estadísticas del primer estudiante: {students_data[0].get('attendance_percentage', 'N/A')}%")
        
        return jsonify({
            'success': True,
            'data': {
                'students': students_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'stats': stats
            }
        })
    except Exception as e:
        print(f"❌ Error al obtener estudiantes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener estudiantes: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
def get_student_details(student_id):
    """Endpoint para obtener detalles completos de un estudiante"""
    try:
        student = StudentService.get_student_by_id(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener justificaciones recientes del estudiante
        recent_justifications = StudentService.get_student_justifications(
            student_id, status_filter=None
        )[:5]  # Últimas 5
        
        student_data = student.to_dict()
        student_data['recent_justifications'] = [j.to_dict() for j in recent_justifications]
        
        return jsonify({
            'success': True,
            'data': student_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles del estudiante: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>/justifications', methods=['GET'])
def get_student_justifications(student_id):
    """Endpoint para obtener todas las justificaciones de un estudiante"""
    try:
        status_filter = request.args.get('status')
        justifications = StudentService.get_student_justifications(
            student_id, status_filter
        )
        
        return jsonify({
            'success': True,
            'data': [j.to_dict() for j in justifications]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener justificaciones: {str(e)}'
        }), 500

@student_bp.route('/create', methods=['POST'])
def create_student():
    """Endpoint para crear un nuevo estudiante"""
    try:
        data = request.get_json()
        print(f"📋 Datos recibidos para crear estudiante: {data}")
        
        # Validar que se recibieron datos
        if not data:
            print("❌ No se recibieron datos JSON")
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar datos requeridos
        required_fields = ['first_name', 'last_name', 'student_code', 'email', 'career', 'semester']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ Campo faltante: {field}")
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que el código de estudiante no exista
        existing_student = StudentService.get_student_by_code(data['student_code'])
        if existing_student:
            return jsonify({
                'success': False,
                'message': 'El código de estudiante ya existe'
            }), 400
        
        # Convertir fecha de nacimiento si existe
        if data.get('birth_date'):
            try:
                print(f"🗓️ Convirtiendo fecha: {data['birth_date']}")
                data['birth_date'] = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                print(f"✅ Fecha convertida: {data['birth_date']}")
            except Exception as date_error:
                print(f"❌ Error al convertir fecha: {date_error}")
                return jsonify({
                    'success': False,
                    'message': f'Formato de fecha inválido: {str(date_error)}'
                }), 400
        
        # Crear estudiante
        print(f"✅ Creando estudiante con datos: {data}")
        student = StudentService.create_student(data)
        print(f"✅ Estudiante creado exitosamente: {student.id}")
        
        return jsonify({
            'success': True,
            'message': 'Estudiante creado exitosamente',
            'data': student.to_dict()
        }), 201
    except Exception as e:
        print(f"❌ Error al crear estudiante: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear estudiante: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>/update', methods=['PUT'])
def update_student(student_id):
    """Endpoint para actualizar un estudiante"""
    try:
        data = request.get_json()
        
        # Convertir fecha de nacimiento si existe
        if data.get('birth_date'):
            data['birth_date'] = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        student = StudentService.update_student(student_id, data)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Estudiante actualizado exitosamente',
            'data': student.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar estudiante: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>/delete', methods=['PATCH'])
def delete_student(student_id):
    """Endpoint para eliminar (desactivar) un estudiante"""
    try:
        print(f"🗑️ Recibida petición de eliminación para estudiante ID: {student_id}")
        success = StudentService.delete_student(student_id)
        print(f"✅ Resultado de eliminación: {success}")
        
        if success:
            print(f"✅ Estudiante {student_id} marcado como inactivo exitosamente")
            return jsonify({
                'success': True,
                'message': 'Estudiante desactivado exitosamente'
            })
        else:
            print(f"❌ Estudiante {student_id} no encontrado")
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
    except Exception as e:
        print(f"❌ Error al desactivar estudiante {student_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al desactivar estudiante: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>/restore', methods=['PATCH'])
def restore_student(student_id):
    """Endpoint para restaurar un estudiante inactivo"""
    try:
        success = StudentService.restore_student(student_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Estudiante restaurado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al restaurar estudiante: {str(e)}'
        }), 500

@student_bp.route('/<int:student_id>/attendance', methods=['PUT'])
def update_attendance(student_id):
    """Endpoint para actualizar información de asistencia"""
    try:
        data = request.get_json()
        
        total_classes = data.get('total_classes')
        total_absences = data.get('total_absences')
        
        if total_classes is None or total_absences is None:
            return jsonify({
                'success': False,
                'message': 'Se requieren total_classes y total_absences'
            }), 400
        
        success = StudentService.update_attendance(
            student_id, total_classes, total_absences
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Asistencia actualizada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar asistencia: {str(e)}'
        }), 500

@student_bp.route('/at-risk', methods=['GET'])
def get_students_at_risk():
    """Endpoint para obtener estudiantes en riesgo"""
    try:
        students = StudentService.get_students_at_risk()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in students]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estudiantes en riesgo: {str(e)}'
        }), 500

@student_bp.route('/critical', methods=['GET'])
def get_students_critical():
    """Endpoint para obtener estudiantes en estado crítico"""
    try:
        students = StudentService.get_students_critical()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in students]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estudiantes críticos: {str(e)}'
        }), 500

@student_bp.route('/attendance-report', methods=['GET'])
def get_attendance_report():
    """Endpoint para generar reporte de asistencia"""
    try:
        # Estudiantes en riesgo (25-29%)
        at_risk_students = StudentService.get_students_at_risk()
        
        # Estudiantes críticos (30%+)
        critical_students = StudentService.get_students_critical()
        
        return jsonify({
            'success': True,
            'data': {
                'at_risk': {
                    'count': len(at_risk_students),
                    'students': [s.to_dict() for s in at_risk_students]
                },
                'critical': {
                    'count': len(critical_students),
                    'students': [s.to_dict() for s in critical_students]
                },
                'generated_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500


@student_bp.route('/stats', methods=['GET'])
def get_students_stats():
    """Endpoint para obtener estadísticas de estudiantes"""
    try:
        stats = StudentService.get_student_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500
