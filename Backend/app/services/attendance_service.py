from app.models.attendance_record import AttendanceRecord
from app.models.student import Student
from app.models.course import Course
from app.models.professor import Professor
from app.models.audit_log import AuditLog
from app import db
from datetime import datetime, date
from flask import request

class AttendanceService:
    """Servicio para gestión de registros de asistencia"""
    
    @staticmethod
    def get_all_attendance(course_id=None, student_id=None, date_from=None, date_to=None, status_filter=None, page=1, per_page=50):
        """Obtener registros de asistencia con filtros"""
        query = AttendanceRecord.query
        
        # Filtro por curso
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        # Filtro por estudiante
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        # Filtro por rango de fechas
        if date_from:
            query = query.filter(AttendanceRecord.attendance_date >= date_from)
        if date_to:
            query = query.filter(AttendanceRecord.attendance_date <= date_to)
        
        # Filtro por estado
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Ordenar por fecha descendente
        query = query.order_by(AttendanceRecord.attendance_date.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_attendance_by_id(attendance_id):
        """Obtener registro de asistencia por ID"""
        return AttendanceRecord.query.get(attendance_id)
    
    @staticmethod
    def create_attendance(data):
        """Crear nuevo registro de asistencia"""
        attendance = AttendanceRecord(
            student_id=data['student_id'],
            course_id=data['course_id'],
            attendance_date=data['attendance_date'],
            status=data.get('status', 'AUSENTE'),
            notes=data.get('notes'),
            recorded_by=data.get('recorded_by')
        )
        
        db.session.add(attendance)
        db.session.flush()
        
        # Actualizar contadores del estudiante si es ausencia
        if attendance.status == 'AUSENTE':
            student = Student.query.get(data['student_id'])
            if student:
                student.total_absences = (student.total_absences or 0) + 1
                student.unjustified_absences = (student.unjustified_absences or 0) + 1
        
        # Registrar en audit_logs
        if data.get('recorded_by'):
            professor = Professor.query.get(data['recorded_by'])
            course = Course.query.get(data['course_id'])
            if professor and course:
                AuditLog.log_action(
                    user_email=professor.email,
                    user_type='professor',
                    action_type='RECORD_ATTENDANCE',
                    table_name='attendance_records',
                    record_id=attendance.id,
                    description=f'Registró asistencia para {course.course_name} - Estado: {attendance.status}',
                    ip_address=request.remote_addr if request else None
                )
        
        db.session.commit()
        return attendance
    
    @staticmethod
    def create_bulk_attendance(data_list):
        """Crear múltiples registros de asistencia"""
        created_records = []
        
        for data in data_list:
            # Verificar si ya existe un registro para ese estudiante, curso y fecha
            existing = AttendanceRecord.query.filter_by(
                student_id=data['student_id'],
                course_id=data['course_id'],
                attendance_date=data['attendance_date']
            ).first()
            
            if existing:
                # Actualizar el existente
                existing.status = data.get('status', existing.status)
                existing.notes = data.get('notes', existing.notes)
                existing.recorded_by = data.get('recorded_by', existing.recorded_by)
                created_records.append(existing)
            else:
                # Crear nuevo
                attendance = AttendanceRecord(
                    student_id=data['student_id'],
                    course_id=data['course_id'],
                    attendance_date=data['attendance_date'],
                    status=data.get('status', 'AUSENTE'),
                    notes=data.get('notes'),
                    recorded_by=data.get('recorded_by')
                )
                db.session.add(attendance)
                created_records.append(attendance)
                
                # Actualizar contadores del estudiante
                if attendance.status == 'AUSENTE':
                    student = Student.query.get(data['student_id'])
                    if student:
                        student.total_absences = (student.total_absences or 0) + 1
                        student.unjustified_absences = (student.unjustified_absences or 0) + 1
        
        db.session.commit()
        return created_records
    
    @staticmethod
    def update_attendance(attendance_id, data):
        """Actualizar registro de asistencia"""
        attendance = AttendanceRecord.query.get(attendance_id)
        if not attendance:
            return None
        
        old_status = attendance.status
        
        # Actualizar campos
        if 'status' in data:
            attendance.status = data['status']
        if 'notes' in data:
            attendance.notes = data['notes']
        if 'justification_id' in data:
            attendance.justification_id = data['justification_id']
        
        # Actualizar contadores del estudiante si cambió el estado
        if old_status != attendance.status:
            student = Student.query.get(attendance.student_id)
            if student:
                # Revertir el conteo anterior
                if old_status == 'AUSENTE':
                    student.total_absences = max(0, (student.total_absences or 0) - 1)
                    student.unjustified_absences = max(0, (student.unjustified_absences or 0) - 1)
                
                # Aplicar el nuevo conteo
                if attendance.status == 'AUSENTE':
                    student.total_absences = (student.total_absences or 0) + 1
                    student.unjustified_absences = (student.unjustified_absences or 0) + 1
                elif attendance.status == 'JUSTIFICADO':
                    student.justified_absences = (student.justified_absences or 0) + 1
        
        db.session.commit()
        return attendance
    
    @staticmethod
    def delete_attendance(attendance_id):
        """Eliminar registro de asistencia"""
        attendance = AttendanceRecord.query.get(attendance_id)
        if not attendance:
            return False
        
        # Actualizar contadores del estudiante
        if attendance.status == 'AUSENTE':
            student = Student.query.get(attendance.student_id)
            if student:
                student.total_absences = max(0, (student.total_absences or 0) - 1)
                student.unjustified_absences = max(0, (student.unjustified_absences or 0) - 1)
        
        db.session.delete(attendance)
        db.session.commit()
        return True
    
    @staticmethod
    def get_attendance_stats(course_id=None, student_id=None):
        """Obtener estadísticas de asistencia"""
        query = AttendanceRecord.query
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        total = query.count()
        present = query.filter_by(status='PRESENTE').count()
        absent = query.filter_by(status='AUSENTE').count()
        late = query.filter_by(status='TARDANZA').count()
        justified = query.filter_by(status='JUSTIFICADO').count()
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'justified': justified,
            'attendance_rate': round((present / total * 100), 2) if total > 0 else 0
        }
    
    @staticmethod
    def get_student_attendance_by_course(student_id, course_id):
        """Obtener asistencias de un estudiante en un curso específico"""
        return AttendanceRecord.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).order_by(AttendanceRecord.attendance_date.desc()).all()
    
    @staticmethod
    def get_course_attendance_by_date(course_id, attendance_date):
        """Obtener todas las asistencias de un curso en una fecha específica"""
        return AttendanceRecord.query.filter_by(
            course_id=course_id,
            attendance_date=attendance_date
        ).all()
