from app import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    __table_args__ = {'schema': 'DEVELOPER_02'}
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    professor_id = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String(200))
    status = db.Column(db.String(1), default='A', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'credits': self.credits,
            'semester': self.semester,
            'professor_id': self.professor_id,
            'schedule': self.schedule,
            'status': 'active' if self.status == 'A' else 'inactive',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
