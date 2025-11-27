from app import db
from datetime import datetime

class CourseEnrollment(db.Model):
    """Modelo para inscripciones de estudiantes a cursos"""
    __tablename__ = 'course_enrollments'
    __table_args__ = {'schema': 'DEVELOPER_01'}
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(10), default='A')  # A=Activo, I=Inactivo, R=Retirado
    
    # Relaciones sin foreign keys (tablas en esquemas diferentes)
    # student = db.relationship('Student', backref='enrollments', foreign_keys=[student_id])
    # course = db.relationship('Course', backref='enrollments', foreign_keys=[course_id])
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<CourseEnrollment {self.id}: Student {self.student_id} - Course {self.course_id}>'
