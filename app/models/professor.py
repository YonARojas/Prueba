from app import db
from datetime import datetime

class Professor(db.Model):
    __tablename__ = 'professors'
    __table_args__ = {'schema': 'DEVELOPER_01'}
    
    id = db.Column(db.Integer, primary_key=True)
    professor_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dni = db.Column(db.String(8), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='PROFESOR', nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Professor {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'professor_code': self.professor_code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'dni': self.dni,
            'phone': self.phone,
            'specialization': self.specialization,
            'department': self.department,
            'role': self.role,
            'status': 'active' if self.status == 'A' else 'inactive',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
