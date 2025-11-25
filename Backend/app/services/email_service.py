"""
Servicio para envío de emails
Maneja todas las notificaciones por correo electrónico del sistema
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from app import db
import os

class EmailService:
    
    # Configuración SMTP (usar variables de entorno en producción)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', 'sistema@vallegrandecañete.edu.pe')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'sistema@vallegrandecañete.edu.pe')
    FROM_NAME = 'Sistema de Justificaciones - Valle Grande de Cañete'
    
    @staticmethod
    def send_email(to_email, to_name, subject, body_html, notification_type='GENERAL', related_table=None, related_id=None):
        """
        Envía un email y registra en la base de datos
        
        Args:
            to_email: Email del destinatario
            to_name: Nombre del destinatario
            subject: Asunto del email
            body_html: Cuerpo del email en HTML
            notification_type: Tipo de notificación
            related_table: Tabla relacionada (opcional)
            related_id: ID del registro relacionado (opcional)
            
        Returns:
            bool: True si se envió correctamente, False si falló
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{EmailService.FROM_NAME} <{EmailService.FROM_EMAIL}>"
            msg['To'] = f"{to_name} <{to_email}>"
            
            # Agregar cuerpo HTML
            html_part = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                if EmailService.SMTP_PASSWORD:
                    server.login(EmailService.SMTP_USER, EmailService.SMTP_PASSWORD)
                server.send_message(msg)
            
            # Registrar en base de datos
            EmailService._log_email(
                to_email, to_name, subject, body_html,
                notification_type, related_table, related_id,
                'SENT', None
            )
            
            print(f"✅ Email enviado a {to_email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error al enviar email a {to_email}: {error_msg}")
            
            # Registrar error en base de datos
            EmailService._log_email(
                to_email, to_name, subject, body_html,
                notification_type, related_table, related_id,
                'FAILED', error_msg
            )
            
            return False
    
    @staticmethod
    def _log_email(to_email, to_name, subject, body, notification_type, related_table, related_id, status, error_msg):
        """Registra el email en la base de datos"""
        try:
            from app.models.email_notification import EmailNotification
            
            notification = EmailNotification(
                recipient_email=to_email,
                recipient_name=to_name,
                subject=subject,
                body=body,
                notification_type=notification_type,
                related_table=related_table,
                related_id=related_id,
                status=status,
                sent_at=datetime.utcnow() if status == 'SENT' else None,
                error_message=error_msg
            )
            
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            print(f"⚠️ Error al registrar email en BD: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def send_justification_submitted(student, professor, justification, course):
        """
        Envía email al profesor cuando un estudiante envía una justificación
        """
        subject = f"Nueva Justificación - {student.full_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Nueva Solicitud de Justificación</h2>
                
                <p>Estimado/a <strong>{professor.full_name}</strong>,</p>
                
                <p>El estudiante <strong>{student.full_name}</strong> ha enviado una nueva solicitud de justificación:</p>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Estudiante:</strong> {student.full_name} ({student.student_code})</p>
                    <p><strong>Curso:</strong> {course.course_name}</p>
                    <p><strong>Fecha de inasistencia:</strong> {justification.absence_date.strftime('%d/%m/%Y')}</p>
                    <p><strong>Motivo:</strong> {justification.reason_type}</p>
                    <p><strong>Descripción:</strong> {justification.reason_description}</p>
                </div>
                
                <p>Por favor, revise y procese esta solicitud en el sistema.</p>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    Este es un mensaje automático del Sistema de Justificaciones.<br>
                    Valle Grande de Cañete
                </p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            professor.email,
            professor.full_name,
            subject,
            body_html,
            'JUSTIFICATION_SUBMITTED',
            'justifications',
            justification.id
        )
    
    @staticmethod
    def send_justification_processed(student, justification, course, admin_response, approved):
        """
        Envía email al estudiante cuando su justificación es procesada
        """
        status_text = "APROBADA" if approved else "RECHAZADA"
        color = "#10b981" if approved else "#ef4444"
        
        subject = f"Justificación {status_text} - {course.course_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {color};">Justificación {status_text}</h2>
                
                <p>Estimado/a <strong>{student.full_name}</strong>,</p>
                
                <p>Su solicitud de justificación ha sido <strong style="color: {color};">{status_text}</strong>:</p>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Curso:</strong> {course.course_name}</p>
                    <p><strong>Fecha de inasistencia:</strong> {justification.absence_date.strftime('%d/%m/%Y')}</p>
                    <p><strong>Motivo:</strong> {justification.reason_type}</p>
                </div>
                
                <div style="background: {'#d1fae5' if approved else '#fee2e2'}; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Respuesta del profesor:</strong></p>
                    <p>{admin_response}</p>
                </div>
                
                <p>Puede ver más detalles en el sistema.</p>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    Este es un mensaje automático del Sistema de Justificaciones.<br>
                    Valle Grande de Cañete
                </p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            student.email,
            student.full_name,
            subject,
            body_html,
            'JUSTIFICATION_PROCESSED',
            'justifications',
            justification.id
        )
    
    @staticmethod
    def send_attendance_alert(student, attendance_stats):
        """
        Envía alerta al estudiante cuando tiene 30% o más de inasistencias
        """
        subject = "⚠️ ALERTA: Alto Porcentaje de Inasistencias"
        
        absence_percentage = attendance_stats['absence_percentage']
        risk_level = attendance_stats['risk_level']
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #fee2e2; padding: 20px; border-left: 4px solid #ef4444; border-radius: 8px;">
                    <h2 style="color: #dc2626; margin-top: 0;">⚠️ ALERTA DE INASISTENCIAS</h2>
                </div>
                
                <p>Estimado/a <strong>{student.full_name}</strong>,</p>
                
                <p>Le informamos que su porcentaje de inasistencias ha alcanzado un nivel <strong style="color: #dc2626;">{risk_level}</strong>:</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <h1 style="color: #dc2626; font-size: 48px; margin: 0;">{absence_percentage}%</h1>
                    <p style="margin: 5px 0; color: #666;">de inasistencias</p>
                </div>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>⚠️ IMPORTANTE:</strong></p>
                    <ul>
                        <li>Total de clases: {attendance_stats['total_classes']}</li>
                        <li>Inasistencias: {attendance_stats['absent']}</li>
                        <li>Justificadas: {attendance_stats['justified']}</li>
                    </ul>
                </div>
                
                <p><strong>Recomendaciones:</strong></p>
                <ul>
                    <li>Asista regularmente a clases</li>
                    <li>Justifique sus inasistencias cuando sea necesario</li>
                    <li>Contacte a su profesor si tiene dificultades</li>
                </ul>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    Este es un mensaje automático del Sistema de Justificaciones.<br>
                    Valle Grande de Cañete
                </p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            student.email,
            student.full_name,
            subject,
            body_html,
            'ATTENDANCE_ALERT',
            'students',
            student.id
        )
    
    @staticmethod
    def send_custom_message(student, attendance_stats, subject, custom_message):
        """
        Envía un mensaje personalizado del profesor al estudiante
        """
        absence_percentage = attendance_stats['absence_percentage']
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 2px solid #3b82f6; border-radius: 12px;">
                <div style="background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: white; margin: 0; text-align: center;">📧 Mensaje del Profesor</h2>
                </div>
                
                <p style="font-size: 16px;">Estimado/a <strong>{student.full_name}</strong>,</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                    <p style="margin: 0; white-space: pre-wrap; font-size: 15px; line-height: 1.8;">{custom_message}</p>
                </div>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0 0 10px 0;"><strong>📊 Tus Estadísticas de Asistencia:</strong></p>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Total de clases: <strong>{attendance_stats['total_classes']}</strong></li>
                        <li>Presentes: <strong>{attendance_stats['present']}</strong></li>
                        <li>Inasistencias: <strong style="color: #dc2626;">{attendance_stats['absent']}</strong></li>
                        <li>Porcentaje de inasistencias: <strong style="color: #dc2626; font-size: 18px;">{absence_percentage}%</strong></li>
                    </ul>
                </div>
                
                <div style="background: #e0f2fe; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #0369a1;">
                        💡 <strong>Recuerda:</strong> Puedes justificar tus inasistencias a través del sistema. 
                        Si tienes alguna duda o necesitas ayuda, no dudes en contactarnos.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                    <p style="color: #6b7280; font-size: 12px; margin: 5px 0;">
                        Sistema de Gestión de Justificaciones<br>
                        <strong>Instituto Valle Grande de Cañete</strong><br>
                        Este mensaje fue enviado por tu profesor
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            student.email,
            student.full_name,
            subject,
            body_html,
            'CUSTOM_MESSAGE',
            'students',
            student.id
        )
