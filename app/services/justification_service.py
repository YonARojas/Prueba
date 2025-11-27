from app import db
from app.models.justification import Justification, JustificationAttachment
from app.models.student import Student
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from collections import defaultdict
import os

class JustificationService:
    
    @staticmethod
    def get_dashboard_stats():
        """Obtiene estadísticas para el dashboard administrativo"""
        total_requests = db.session.query(Justification).count()
        pending_requests = db.session.query(Justification).filter(
            Justification.status == 'PENDIENTE'
        ).count()
        approved_requests = db.session.query(Justification).filter(
            Justification.status == 'APROBADA'
        ).count()
        rejected_requests = db.session.query(Justification).filter(
            Justification.status == 'RECHAZADA'
        ).count()
        
        # Estadísticas de estudiantes
        total_students = db.session.query(Student).count()
        active_students = db.session.query(Student).filter(
            Student.status == 'A'
        ).count()
        
        # Estudiantes en riesgo (25-29% inasistencias)
        at_risk_students = db.session.query(Student).filter(
            and_(
                Student.total_classes > 0,
                (Student.total_absences * 100.0 / Student.total_classes) >= 25,
                (Student.total_absences * 100.0 / Student.total_classes) < 30
            )
        ).count()
        
        # Estudiantes en estado crítico (30%+ inasistencias)
        critical_students = db.session.query(Student).filter(
            and_(
                Student.total_classes > 0,
                (Student.total_absences * 100.0 / Student.total_classes) >= 30
            )
        ).count()
        
        return {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
            'total_students': total_students,
            'active_students': active_students,
            'at_risk_students': at_risk_students,
            'critical_students': critical_students
        }
    
    @staticmethod
    def get_recent_requests(limit=10):
        """Obtiene las solicitudes más recientes"""
        return db.session.query(Justification)\
            .join(Student)\
            .order_by(Justification.submission_date.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_all_requests():
        """Obtiene todas las justificaciones ordenadas por fecha"""
        return db.session.query(Justification)\
            .order_by(Justification.submission_date.desc())\
            .all()
    
    @staticmethod
    def get_requests_by_status(status=None, search=None, page=1, per_page=10):
        """Obtiene solicitudes filtradas por estado y búsqueda"""
        query = db.session.query(Justification).join(Student)
        
        if status and status != 'Todas':
            query = query.filter(Justification.status == status)
        
        if search:
            query = query.filter(
                or_(
                    Student.first_name.ilike(f'%{search}%'),
                    Student.last_name.ilike(f'%{search}%'),
                    Student.student_code.ilike(f'%{search}%')
                )
            )
        
        query = query.order_by(Justification.submission_date.desc())
        
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_request_by_id(request_id):
        """Obtiene una solicitud por ID"""
        return db.session.query(Justification)\
            .join(Student)\
            .filter(Justification.id == request_id)\
            .first()
    
    @staticmethod
    def approve_request(request_id, admin_id, admin_response=None):
        """Aprueba una solicitud"""
        justification = db.session.query(Justification).get(request_id)
        if justification:
            justification.status = 'APROBADA'
            justification.review_date = datetime.utcnow()
            justification.reviewed_by = admin_id
            if admin_response:
                justification.admin_response = admin_response
            db.session.commit()
            
            # Enviar email al estudiante
            try:
                from app.services.email_service import EmailService
                from app.models.student import Student
                from app.models.course import Course
                student = db.session.query(Student).get(justification.student_id)
                course = db.session.query(Course).get(justification.course_id)
                if student and student.email:
                    print(f"📧 Enviando email de aprobación a: {student.email}")
                    EmailService.send_justification_approved(student, justification, course, admin_response)
                    print(f"✅ Email de aprobación enviado")
            except Exception as e:
                print(f"⚠️ Error al enviar email: {e}")
            
            return True
        return False
    
    @staticmethod
    def reject_request(request_id, admin_id, admin_response=None):
        """Rechaza una solicitud"""
        justification = db.session.query(Justification).get(request_id)
        if justification:
            justification.status = 'RECHAZADA'
            justification.review_date = datetime.utcnow()
            justification.reviewed_by = admin_id
            if admin_response:
                justification.admin_response = admin_response
            db.session.commit()
            
            # Enviar email al estudiante
            try:
                from app.services.email_service import EmailService
                from app.models.student import Student
                from app.models.course import Course
                student = db.session.query(Student).get(justification.student_id)
                course = db.session.query(Course).get(justification.course_id)
                if student and student.email:
                    print(f"📧 Enviando email de rechazo a: {student.email}")
                    EmailService.send_justification_rejected(student, justification, course, admin_response)
                    print(f"✅ Email de rechazo enviado")
            except Exception as e:
                print(f"⚠️ Error al enviar email: {e}")
            
            return True
        return False
    
    @staticmethod
    def create_request(student_id, absence_date, course_subject, reason, detailed_description, files=None):
        """Crea una nueva solicitud de justificación"""
        try:
            justification = Justification(
                student_id=student_id,
                absence_date=absence_date,
                course_subject=course_subject,
                reason=reason,
                detailed_description=detailed_description
            )
            
            db.session.add(justification)
            db.session.flush()  # Para obtener el ID
            
            # Procesar archivos adjuntos si existen
            if files:
                for file in files:
                    if file and file.filename:
                        # Aquí iría la lógica para guardar el archivo
                        # Por ahora solo creamos el registro
                        attachment = JustificationAttachment(
                            justification_id=justification.id,
                            filename=file.filename,
                            original_filename=file.filename,
                            file_path=f"/uploads/{justification.id}/{file.filename}",
                            file_size=0,  # Se calcularía al guardar
                            mime_type=file.content_type or 'application/octet-stream'
                        )
                        db.session.add(attachment)
            
            db.session.commit()
            return justification
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_monthly_trends():
        """Obtiene tendencias mensuales de solicitudes"""
        # Últimos 6 meses
        six_months_ago = datetime.now() - timedelta(days=180)
        
        results = db.session.query(
            func.extract('year', Justification.submission_date).label('year'),
            func.extract('month', Justification.submission_date).label('month'),
            func.count(Justification.id).label('count')
        ).filter(
            Justification.submission_date >= six_months_ago
        ).group_by(
            func.extract('year', Justification.submission_date),
            func.extract('month', Justification.submission_date)
        ).order_by('year', 'month').all()
        
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        monthly_data = []
        for result in results:
            month_name = months[int(result.month) - 1]
            monthly_data.append({
                'month': month_name,
                'count': result.count
            })
        
        return monthly_data
    
    @staticmethod
    def get_reason_distribution():
        """Obtiene distribución de motivos de justificación"""
        results = db.session.query(
            Justification.reason,
            func.count(Justification.id).label('count')
        ).group_by(Justification.reason).order_by(func.count(Justification.id).desc()).all()
        
        total = sum(result.count for result in results)
        
        distribution = []
        for result in results:
            percentage = round((result.count / total * 100), 1) if total > 0 else 0
            distribution.append({
                'reason': result.reason,
                'count': result.count,
                'percentage': percentage
            })
        
        return distribution
    
    @staticmethod
    def get_approval_rate():
        """Calcula la tasa de aprobación general"""
        total = db.session.query(Justification).filter(
            Justification.status.in_(['APROBADA', 'RECHAZADA'])
        ).count()
        
        approved = db.session.query(Justification).filter(
            Justification.status == 'APROBADA'
        ).count()
        
        return round((approved / total * 100), 1) if total > 0 else 0
    
    @staticmethod
    def get_average_response_time():
        """Calcula el tiempo promedio de respuesta"""
        results = db.session.query(
            func.avg(
                func.extract('epoch', Justification.processed_date - Justification.submission_date) / 86400
            ).label('avg_days')
        ).filter(
            Justification.processed_date.isnot(None)
        ).first()
        
        return round(results.avg_days, 1) if results.avg_days else 0
    
    @staticmethod
    def get_students_requiring_attention():
        """Obtiene estudiantes que requieren atención por inasistencias"""
        return db.session.query(Student).filter(
            and_(
                Student.total_classes > 0,
                (Student.total_absences * 100.0 / Student.total_classes) >= 25
            )
        ).order_by(
            (Student.total_absences * 100.0 / Student.total_classes).desc()
        ).all()