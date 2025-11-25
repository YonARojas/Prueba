from app.models.professor import Professor
from app import db
from werkzeug.security import generate_password_hash

class ProfessorService:
    """Servicio para gestión de profesores"""
    
    @staticmethod
    def get_all_professors(status_filter=None, search=None, page=1, per_page=50):
        """Obtener todos los profesores con filtros y paginación"""
        query = Professor.query
        
        # Filtro por estado
        if status_filter == 'Activos':
            query = query.filter_by(status='A')
        elif status_filter == 'Inactivos':
            query = query.filter_by(status='I')
        
        # Búsqueda por nombre, código o email
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Professor.first_name.ilike(search_pattern),
                    Professor.last_name.ilike(search_pattern),
                    Professor.professor_code.ilike(search_pattern),
                    Professor.email.ilike(search_pattern),
                    Professor.department.ilike(search_pattern)
                )
            )
        
        # Ordenar por apellido
        query = query.order_by(Professor.last_name, Professor.first_name)
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_professor_by_id(professor_id):
        """Obtener profesor por ID"""
        return Professor.query.get(professor_id)
    
    @staticmethod
    def get_professor_by_code(professor_code):
        """Obtener profesor por código"""
        return Professor.query.filter_by(professor_code=professor_code).first()
    
    @staticmethod
    def get_professor_by_email(email):
        """Obtener profesor por email"""
        return Professor.query.filter_by(email=email).first()
    
    @staticmethod
    def create_professor(data):
        """Crear nuevo profesor"""
        professor = Professor(
            first_name=data['first_name'],
            last_name=data['last_name'],
            professor_code=data['professor_code'],
            email=data['email'],
            password=data.get('password', 'profesor123'),  # Password por defecto
            phone=data.get('phone'),
            dni=data.get('dni'),
            specialization=data.get('specialization'),
            department=data.get('department'),
            role=data.get('role', 'PROFESOR'),
            status='A'
        )
        
        db.session.add(professor)
        db.session.commit()
        return professor
    
    @staticmethod
    def update_professor(professor_id, data):
        """Actualizar profesor"""
        professor = Professor.query.get(professor_id)
        if not professor:
            return None
        
        # Actualizar campos
        if 'first_name' in data:
            professor.first_name = data['first_name']
        if 'last_name' in data:
            professor.last_name = data['last_name']
        if 'email' in data:
            professor.email = data['email']
        if 'phone' in data:
            professor.phone = data['phone']
        if 'dni' in data:
            professor.dni = data['dni']
        if 'specialization' in data:
            professor.specialization = data['specialization']
        if 'department' in data:
            professor.department = data['department']
        if 'role' in data:
            professor.role = data['role']
        if 'password' in data and data['password']:
            professor.password = data['password']
        
        db.session.commit()
        return professor
    
    @staticmethod
    def delete_professor(professor_id):
        """Desactivar profesor (soft delete)"""
        professor = Professor.query.get(professor_id)
        if not professor:
            return False
        
        professor.status = 'I'
        db.session.commit()
        return True
    
    @staticmethod
    def restore_professor(professor_id):
        """Restaurar profesor inactivo"""
        professor = Professor.query.get(professor_id)
        if not professor:
            return False
        
        professor.status = 'A'
        db.session.commit()
        return True
    
    @staticmethod
    def get_professor_stats():
        """Obtener estadísticas de profesores"""
        total = Professor.query.count()
        active = Professor.query.filter_by(status='A').count()
        inactive = Professor.query.filter_by(status='I').count()
        
        # Contar por rol
        coordinators = Professor.query.filter_by(role='COORDINADOR', status='A').count()
        admins = Professor.query.filter_by(role='ADMIN', status='A').count()
        regular = Professor.query.filter_by(role='PROFESOR', status='A').count()
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'by_role': {
                'coordinators': coordinators,
                'admins': admins,
                'regular': regular
            }
        }
    
    @staticmethod
    def get_professor_courses(professor_id):
        """Obtener cursos asignados a un profesor"""
        from app.models.course import Course
        return Course.query.filter_by(professor_id=professor_id, status='A').all()
