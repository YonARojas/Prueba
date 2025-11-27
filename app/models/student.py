from app import db
from datetime import datetime
from enum import Enum

class StudentStatus(Enum):
    ACTIVO = "A"
    INACTIVO = "I"

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {'schema': 'DEVELOPER_01'}
    
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dni = db.Column(db.String(8), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    career = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def absence_percentage(self):
        """Calcula el porcentaje de ausencias desde la base de datos"""
        stats = self.get_attendance_stats()
        return stats.get('absence_percentage', 0)
    
    @property
    def attendance_percentage(self):
        """Calcula el porcentaje de asistencia desde la base de datos"""
        stats = self.get_attendance_stats()
        return stats.get('attendance_percentage', 0)
    
    @property
    def risk_level(self):
        """Determina el nivel de riesgo basado en ausencias reales"""
        stats = self.get_attendance_stats()
        return stats.get('risk_level', 'NORMAL')
    
    def get_attendance_stats(self):
        """Obtiene estadísticas de asistencia REALES del estudiante"""
        from app.services.statistics_service import StatisticsService
        return StatisticsService.calculate_student_attendance(self.id)
    
    def get_justification_stats(self):
        """Obtiene estadísticas de justificaciones REALES del estudiante"""
        from app.services.statistics_service import StatisticsService
        return StatisticsService.get_justification_stats(self.id)
    
    def __repr__(self):
        return f'<Student {self.full_name}>'
    
    def to_dict(self, include_stats=False):
        """Convierte el estudiante a diccionario con estadísticas REALES"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'student_code': self.student_code,
            'email': self.email,
            'phone': self.phone,
            'dni': self.dni,
            'career': self.career,
            'semester': self.semester,
            'status': 'active' if self.status == 'A' else 'inactive',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_stats:
            try:
                attendance_stats = self.get_attendance_stats()
                justification_stats = self.get_justification_stats()
                
                data.update({
                    'attendance_stats': attendance_stats,
                    'justification_stats': justification_stats,
                    'attendance_percentage': attendance_stats.get('attendance_percentage', 100.0),
                    'absence_percentage': attendance_stats.get('absence_percentage', 0.0),
                    'risk_level': attendance_stats.get('risk_level', 'NORMAL')
                })
            except Exception as e:
                print(f"⚠️ Error al obtener estadísticas para estudiante {self.id}: {e}")
                # Valores por defecto si falla (100% porque no hay datos)
                data.update({
                    'attendance_stats': {
                        'total_classes': 0,
                        'present': 0,
                        'absent': 0,
                        'justified': 0,
                        'late': 0,
                        'attendance_percentage': 100.0,
                        'absence_percentage': 0.0,
                        'risk_level': 'NORMAL'
                    },
                    'justification_stats': {
                        'total': 0,
                        'pending': 0,
                        'approved': 0,
                        'rejected': 0
                    },
                    'attendance_percentage': 100.0,
                    'absence_percentage': 0.0,
                    'risk_level': 'NORMAL'
                })
        
        return data
