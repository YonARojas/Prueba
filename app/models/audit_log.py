from app import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    __table_args__ = {'schema': 'DEVELOPER_02'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_type = db.Column(db.String(20), nullable=False)  # 'STUDENT' o 'PROFESSOR'
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def log_action(user_id, user_type, action, table_name, record_id=None, old_values=None, new_values=None, ip_address=None):
        """Método helper para registrar acciones fácilmente"""
        audit = AuditLog(
            user_id=user_id,
            user_type=user_type.upper(),
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.session.add(audit)
        return audit
