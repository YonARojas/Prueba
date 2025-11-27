from flask import Blueprint, request, jsonify
from app.services.attendance_service import AttendanceService
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/', methods=['GET'])
def get_attendance():
    """Endpoint para obtener registros de asistencia con filtros"""
    try:
        course_id = request.args.get('course_id', type=int)
        student_id = request.args.get('student_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status_filter = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        print(f"📋 Obteniendo asistencias - Filtros: course_id={course_id}, student_id={student_id}, date_from={date_from}, date_to={date_to}, status={status_filter}")
        
        # Convertir fechas
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        pagination = AttendanceService.get_all_attendance(
            course_id=course_id,
            student_id=student_id,
            date_from=date_from,
            date_to=date_to,
            status_filter=status_filter,
            page=page,
            per_page=per_page
        )
        
        print(f"✅ Registros encontrados: {pagination.total}")
        
        # Obtener estadísticas
        stats = AttendanceService.get_attendance_stats(
            course_id=course_id,
            student_id=student_id
        )
        
        print(f"📊 Estadísticas: {stats}")
        
        return jsonify({
            'success': True,
            'data': {
                'attendance': [a.to_dict() for a in pagination.items],
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
        return jsonify({
            'success': False,
            'message': f'Error al obtener asistencias: {str(e)}'
        }), 500

@attendance_bp.route('/<int:attendance_id>', methods=['GET'])
def get_attendance_details(attendance_id):
    """Endpoint para obtener detalles de un registro de asistencia"""
    try:
        attendance = AttendanceService.get_attendance_by_id(attendance_id)
        
        if not attendance:
            return jsonify({
                'success': False,
                'message': 'Registro de asistencia no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': attendance.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles: {str(e)}'
        }), 500

@attendance_bp.route('/create', methods=['POST'])
def create_attendance():
    """Endpoint para crear un nuevo registro de asistencia"""
    try:
        data = request.get_json()
        print(f"📋 Datos recibidos para crear asistencia: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar datos requeridos
        required_fields = ['student_id', 'course_id', 'attendance_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Convertir fecha
        if isinstance(data['attendance_date'], str):
            data['attendance_date'] = datetime.strptime(data['attendance_date'], '%Y-%m-%d').date()
        
        attendance = AttendanceService.create_attendance(data)
        print(f"✅ Asistencia creada exitosamente: {attendance.id}")
        
        return jsonify({
            'success': True,
            'message': 'Asistencia registrada exitosamente',
            'data': attendance.to_dict()
        }), 201
    except Exception as e:
        print(f"❌ Error al crear asistencia: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear asistencia: {str(e)}'
        }), 500

@attendance_bp.route('/create-bulk', methods=['POST'])
def create_bulk_attendance():
    """Endpoint para crear múltiples registros de asistencia"""
    try:
        data = request.get_json()
        print(f"📋 Datos recibidos para crear asistencias masivas")
        
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': 'Se esperaba una lista de registros'
            }), 400
        
        # Convertir fechas
        for record in data:
            if isinstance(record.get('attendance_date'), str):
                record['attendance_date'] = datetime.strptime(record['attendance_date'], '%Y-%m-%d').date()
        
        attendances = AttendanceService.create_bulk_attendance(data)
        print(f"✅ {len(attendances)} asistencias creadas/actualizadas")
        
        return jsonify({
            'success': True,
            'message': f'{len(attendances)} registros procesados exitosamente',
            'data': [a.to_dict() for a in attendances]
        }), 201
    except Exception as e:
        print(f"❌ Error al crear asistencias masivas: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear asistencias: {str(e)}'
        }), 500

@attendance_bp.route('/<int:attendance_id>/update', methods=['PUT'])
def update_attendance(attendance_id):
    """Endpoint para actualizar un registro de asistencia"""
    try:
        data = request.get_json()
        
        attendance = AttendanceService.update_attendance(attendance_id, data)
        
        if not attendance:
            return jsonify({
                'success': False,
                'message': 'Registro de asistencia no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Asistencia actualizada exitosamente',
            'data': attendance.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar asistencia: {str(e)}'
        }), 500

@attendance_bp.route('/<int:attendance_id>/delete', methods=['DELETE'])
def delete_attendance(attendance_id):
    """Endpoint para eliminar un registro de asistencia"""
    try:
        success = AttendanceService.delete_attendance(attendance_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Asistencia eliminada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Registro de asistencia no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar asistencia: {str(e)}'
        }), 500

@attendance_bp.route('/student/<int:student_id>/course/<int:course_id>', methods=['GET'])
def get_student_course_attendance(student_id, course_id):
    """Endpoint para obtener asistencias de un estudiante en un curso"""
    try:
        attendances = AttendanceService.get_student_attendance_by_course(student_id, course_id)
        
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in attendances]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener asistencias: {str(e)}'
        }), 500

@attendance_bp.route('/course/<int:course_id>/date/<string:date>', methods=['GET'])
def get_course_date_attendance(course_id, date):
    """Endpoint para obtener asistencias de un curso en una fecha"""
    try:
        attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        attendances = AttendanceService.get_course_attendance_by_date(course_id, attendance_date)
        
        return jsonify({
            'success': True,
            'data': [a.to_dict() for a in attendances]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener asistencias: {str(e)}'
        }), 500

@attendance_bp.route('/stats', methods=['GET'])
def get_attendance_stats():
    """Endpoint para obtener estadísticas de asistencia"""
    try:
        course_id = request.args.get('course_id', type=int)
        student_id = request.args.get('student_id', type=int)
        
        stats = AttendanceService.get_attendance_stats(
            course_id=course_id,
            student_id=student_id
        )
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500
