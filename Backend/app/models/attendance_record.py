from app import db
from datetime import datetime

class AttendanceRecord(db.Model):
    """Modelo para registros de asistencia"""
    __tablename__ = 'attendance_records'
    __table_args__ = {'schema': 'DEVELOPER_01'}
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # PRESENTE, AUSENTE, TARDANZA, JUSTIFICADO
    notes = db.Column(db.String(500))
    recorded_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AttendanceRecord {self.id}: Student {self.student_id} - Course {self.course_id} - {self.status}>'
