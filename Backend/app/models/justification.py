from app import db
from datetime import datetime

class Justification(db.Model):
    __tablename__ = 'justifications'
    __table_args__ = {'schema': 'DEVELOPER_02'}
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    absence_date = db.Column(db.Date, nullable=False)
    reason_type = db.Column(db.String(50), nullable=False)
    reason_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='PENDIENTE', nullable=False)
    admin_response = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    review_date = db.Column(db.DateTime, nullable=True)
    # Campos de attachment
    attachment_filename = db.Column(db.String(255), nullable=True)
    attachment_path = db.Column(db.String(500), nullable=True)
    attachment_size = db.Column(db.Integer, nullable=True)
    attachment_type = db.Column(db.String(100), nullable=True)
    
    # Relaciones (sin foreign keys por estar en esquemas diferentes)
    # student = db.relationship('Student', backref=db.backref('justifications', lazy=True))
    # course = db.relationship('Course', backref=db.backref('justifications', lazy=True))
    # professor = db.relationship('Professor', backref=db.backref('processed_justifications', lazy=True))
    
    def __repr__(self):
        return f'<Justification {self.id}: Student {self.student_id} - {self.reason_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'absence_date': self.absence_date.isoformat() if self.absence_date else None,
            'reason_type': self.reason_type,
            'reason_description': self.reason_description,
            'status': self.status,
            'admin_response': self.admin_response,
            'reviewed_by': self.reviewed_by,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            # Campos de attachment
            'attachment_filename': self.attachment_filename,
            'attachment_path': self.attachment_path,
            'attachment_size': self.attachment_size,
            'attachment_type': self.attachment_type,
            'has_attachment': self.attachment_filename is not None
        }

class JustificationAttachment(db.Model):
    __tablename__ = 'justification_attachments'
    __table_args__ = {'schema': 'DEVELOPER_02'}
    
    id = db.Column(db.Integer, primary_key=True)
    justification_id = db.Column(db.Integer, db.ForeignKey('DEVELOPER_02.justifications.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<JustificationAttachment {self.id}: {self.original_filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'justification_id': self.justification_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }