from app import db
from datetime import datetime

class EmailNotification(db.Model):
    __tablename__ = 'email_notifications'
    __table_args__ = {'schema': 'DEVELOPER_02'}
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    recipient_name = db.Column(db.String(200))
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    related_table = db.Column(db.String(50))
    related_id = db.Column(db.Integer)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, SENT, FAILED
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'notification_type': self.notification_type,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'error_message': self.error_message
        }
