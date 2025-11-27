from flask import Blueprint, request, jsonify
from app.services.professor_service import ProfessorService
from datetime import datetime

professor_bp = Blueprint('professors', __name__)

@professor_bp.route('/', methods=['GET'])
def get_professors():
    """Endpoint para obtener profesores con filtros"""
    try:
        status_filter = request.args.get('status', 'todos')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        print(f"📋 Filtros recibidos: status={status_filter}, search={search}")
        
        # Mapear filtros
        backend_status_filter = None
        if status_filter == 'activo':
            backend_status_filter = 'Activos'
        elif status_filter == 'inactivo':
            backend_status_filter = 'Inactivos'
        
        pagination = ProfessorService.get_all_professors(
            status_filter=backend_status_filter,
            search=search if search else None,
            page=page,
            per_page=per_page
        )
        
        print(f"✅ Profesores encontrados: {pagination.total}")
        
        # Obtener estadísticas
        stats = ProfessorService.get_professor_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'professors': [p.to_dict() for p in pagination.items],
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
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener profesores: {str(e)}'
        }), 500

@professor_bp.route('/<int:professor_id>', methods=['GET'])
def get_professor_details(professor_id):
    """Endpoint para obtener detalles completos de un profesor"""
    try:
        professor = ProfessorService.get_professor_by_id(professor_id)
        
        if not professor:
            return jsonify({
                'success': False,
                'message': 'Profesor no encontrado'
            }), 404
        
        # Obtener cursos del profesor
        courses = ProfessorService.get_professor_courses(professor_id)
        
        professor_data = professor.to_dict()
        professor_data['courses'] = [c.to_dict() for c in courses]
        
        return jsonify({
            'success': True,
            'data': professor_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles del profesor: {str(e)}'
        }), 500

@professor_bp.route('/create', methods=['POST'])
def create_professor():
    """Endpoint para crear un nuevo profesor"""
    try:
        data = request.get_json()
        print(f"📋 Datos recibidos para crear profesor: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se recibieron datos'
            }), 400
        
        # Validar datos requeridos
        required_fields = ['first_name', 'last_name', 'professor_code', 'email', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que el código no exista
        existing = ProfessorService.get_professor_by_code(data['professor_code'])
        if existing:
            return jsonify({
                'success': False,
                'message': 'El código de profesor ya existe'
            }), 400
        
        # Verificar que el email no exista
        existing_email = ProfessorService.get_professor_by_email(data['email'])
        if existing_email:
            return jsonify({
                'success': False,
                'message': 'El email ya está registrado'
            }), 400
        
        professor = ProfessorService.create_professor(data)
        print(f"✅ Profesor creado exitosamente: {professor.id}")
        
        return jsonify({
            'success': True,
            'message': 'Profesor creado exitosamente',
            'data': professor.to_dict()
        }), 201
    except Exception as e:
        print(f"❌ Error al crear profesor: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al crear profesor: {str(e)}'
        }), 500

@professor_bp.route('/<int:professor_id>/update', methods=['PUT'])
def update_professor(professor_id):
    """Endpoint para actualizar un profesor"""
    try:
        data = request.get_json()
        
        professor = ProfessorService.update_professor(professor_id, data)
        
        if not professor:
            return jsonify({
                'success': False,
                'message': 'Profesor no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Profesor actualizado exitosamente',
            'data': professor.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar profesor: {str(e)}'
        }), 500

@professor_bp.route('/<int:professor_id>/delete', methods=['PATCH'])
def delete_professor(professor_id):
    """Endpoint para eliminar (desactivar) un profesor"""
    try:
        print(f"🗑️ Recibida petición de eliminación para profesor ID: {professor_id}")
        success = ProfessorService.delete_professor(professor_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Profesor desactivado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Profesor no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al desactivar profesor: {str(e)}'
        }), 500

@professor_bp.route('/<int:professor_id>/restore', methods=['PATCH'])
def restore_professor(professor_id):
    """Endpoint para restaurar un profesor inactivo"""
    try:
        success = ProfessorService.restore_professor(professor_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Profesor restaurado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Profesor no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al restaurar profesor: {str(e)}'
        }), 500
