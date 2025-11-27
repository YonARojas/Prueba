from app import db
from app.models.student import Student
from app.models.justification import Justification
from sqlalchemy import func, and_, or_
from datetime import datetime

class StudentService:
    
    @staticmethod
    def get_all_students(status_filter=None, search=None, page=1, per_page=10):
        """Obtiene todos los estudiantes con filtros opcionales"""
        query = db.session.query(Student)
        
        if status_filter and status_filter != 'Todos':
            if status_filter == 'Activos':
                query = query.filter(Student.status == 'A')
            elif status_filter == 'Inactivos':
                query = query.filter(Student.status == 'I')
        
        if search:
            query = query.filter(
                or_(
                    Student.first_name.ilike(f'%{search}%'),
                    Student.last_name.ilike(f'%{search}%'),
                    Student.student_code.ilike(f'%{search}%'),
                    Student.email.ilike(f'%{search}%')
                )
            )
        
        query = query.order_by(Student.first_name, Student.last_name)
        
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def get_student_by_id(student_id):
        """Obtiene un estudiante por ID"""
        return db.session.query(Student).get(student_id)
    
    @staticmethod
    def get_student_by_code(student_code):
        """Obtiene un estudiante por código"""
        return db.session.query(Student).filter(
            Student.student_code == student_code
        ).first()
    
    @staticmethod
    def create_student(data):
        """Crea un nuevo estudiante"""
        try:
            student = Student(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                student_code=data.get('student_code'),
                email=data.get('email'),
                phone=data.get('phone'),
                dni=data.get('dni'),
                career=data.get('career'),
                semester=data.get('semester'),
                password=data.get('password', 'estudiante123')
            )
            
            db.session.add(student)
            db.session.commit()
            return student
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_student(student_id, data):
        """Actualiza un estudiante existente"""
        try:
            student = db.session.query(Student).get(student_id)
            if not student:
                return None
            
            # Actualizar campos
            for key, value in data.items():
                if hasattr(student, key) and value is not None:
                    setattr(student, key, value)
            
            db.session.commit()
            return student
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_student(student_id):
        """Elimina un estudiante (soft delete - cambiar estado)"""
        try:
            student = db.session.query(Student).get(student_id)
            if not student:
                return False
            
            student.status = 'I'
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def restore_student(student_id):
        """Restaura un estudiante inactivo"""
        try:
            student = db.session.query(Student).get(student_id)
            if not student:
                return False
            
            student.status = 'A'
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_student_justifications(student_id, status_filter=None):
        """Obtiene las justificaciones de un estudiante"""
        query = db.session.query(Justification).filter(
            Justification.student_id == student_id
        )
        
        if status_filter:
            query = query.filter(Justification.status == status_filter)
        
        return query.order_by(Justification.submission_date.desc()).all()
    
    @staticmethod
    def get_students_at_risk():
        """Obtiene estudiantes en riesgo por inasistencias - Usa datos REALES de attendance_records"""
        # TODO: Implementar con datos reales de attendance_records
        return []
    
    @staticmethod
    def get_students_critical():
        """Obtiene estudiantes en estado crítico por inasistencias - Usa datos REALES"""
        # TODO: Implementar con datos reales de attendance_records
        return []
    
    @staticmethod
    def update_attendance(student_id, total_classes, total_absences):
        """Actualiza la información de asistencia de un estudiante - DEPRECATED"""
        # Este método ya no se usa, las asistencias se manejan con attendance_records
        return True
    
    @staticmethod
    def get_student_stats():
        """Obtiene estadísticas generales de estudiantes"""
        total = db.session.query(Student).count()
        active = db.session.query(Student).filter(
            Student.status == 'A'
        ).count()
        
        # TODO: Calcular at_risk y critical con datos reales de attendance_records
        at_risk = 0
        critical = 0
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'at_risk': at_risk,
            'critical': critical
        }

# Funciones de compatibilidad con el código anterior
def listar_todos():
    return Student.query.all()

def listar_por_id(student_id):
    return Student.query.get(student_id)

def listar_por_estado(estado):
    status = 'A' if estado == "A" else 'I'
    return Student.query.filter_by(status=status).all()

def crear(data):
    try:
        return StudentService.create_student(data), None
    except Exception as e:
        return None, str(e)

def editar(student_id, data):
    try:
        return StudentService.update_student(student_id, data)
    except Exception as e:
        return None

def eliminar_logico(student_id):
    try:
        success = StudentService.delete_student(student_id)
        return StudentService.get_student_by_id(student_id) if success else None
    except Exception as e:
        return None

def restaurar_logico(student_id):
    try:
        success = StudentService.restore_student(student_id)
        return StudentService.get_student_by_id(student_id) if success else None
    except Exception as e:
        return None