"""
Servicio para cálculos estadísticos y de asistencia
Calcula porcentajes REALES de asistencia e identifica estudiantes en riesgo
"""
from app import db
from app.models.student import Student
from app.models.attendance_record import AttendanceRecord
from app.models.justification import Justification
from sqlalchemy import func, and_

class StatisticsService:
    
    @staticmethod
    def calculate_student_attendance(student_id, course_id=None):
        """
        Calcula el porcentaje de asistencia REAL de un estudiante
        
        Args:
            student_id: ID del estudiante
            course_id: ID del curso (opcional, si no se especifica calcula para todos)
            
        Returns:
            dict con estadísticas de asistencia
        """
        query = db.session.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id
        )
        
        if course_id:
            query = query.filter(AttendanceRecord.course_id == course_id)
        
        # Total de registros
        total_classes = query.count()
        
        if total_classes == 0:
            return {
                'total_classes': 0,
                'present': 0,
                'absent': 0,
                'justified': 0,
                'late': 0,
                'attendance_percentage': 100.0,
                'absence_percentage': 0.0,
                'risk_level': 'NORMAL'
            }
        
        # Contar por estado
        present = query.filter(AttendanceRecord.status == 'PRESENTE').count()
        absent = query.filter(AttendanceRecord.status == 'AUSENTE').count()
        justified = query.filter(AttendanceRecord.status == 'JUSTIFICADO').count()
        late = query.filter(AttendanceRecord.status == 'TARDANZA').count()
        
        # Calcular porcentajes
        attendance_percentage = round((present / total_classes) * 100, 2)
        absence_percentage = round((absent / total_classes) * 100, 2)
        
        # Determinar nivel de riesgo
        risk_level = StatisticsService._determine_risk_level(absence_percentage)
        
        return {
            'total_classes': total_classes,
            'present': present,
            'absent': absent,
            'justified': justified,
            'late': late,
            'attendance_percentage': attendance_percentage,
            'absence_percentage': absence_percentage,
            'risk_level': risk_level
        }
    
    @staticmethod
    def _determine_risk_level(absence_percentage):
        """Determina el nivel de riesgo según el porcentaje de inasistencias"""
        if absence_percentage >= 30:
            return 'CRITICO'  # ROJO
        elif absence_percentage >= 25:
            return 'EN_RIESGO'  # NARANJA
        elif absence_percentage >= 20:
            return 'ATENCION'  # AMARILLO
        else:
            return 'NORMAL'  # VERDE
    
    @staticmethod
    def get_students_at_risk():
        """
        Obtiene lista de estudiantes en riesgo (≥25% inasistencias)
        
        Returns:
            list de estudiantes con sus estadísticas
        """
        students = db.session.query(Student).filter(Student.status == 'A').all()
        at_risk_students = []
        
        for student in students:
            stats = StatisticsService.calculate_student_attendance(student.id)
            
            if stats['absence_percentage'] >= 25:
                student_data = student.to_dict()
                student_data['attendance_stats'] = stats
                at_risk_students.append(student_data)
        
        # Ordenar por porcentaje de inasistencias (mayor a menor)
        at_risk_students.sort(
            key=lambda x: x['attendance_stats']['absence_percentage'],
            reverse=True
        )
        
        return at_risk_students
    
    @staticmethod
    def get_critical_students():
        """
        Obtiene lista de estudiantes en estado CRÍTICO (≥30% inasistencias)
        
        Returns:
            list de estudiantes críticos
        """
        students = db.session.query(Student).filter(Student.status == 'A').all()
        critical_students = []
        
        for student in students:
            stats = StatisticsService.calculate_student_attendance(student.id)
            
            if stats['absence_percentage'] >= 30:
                student_data = student.to_dict()
                student_data['attendance_stats'] = stats
                critical_students.append(student_data)
        
        return critical_students
    
    @staticmethod
    def get_justification_stats(student_id):
        """
        Obtiene estadísticas de justificaciones de un estudiante
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            dict con estadísticas de justificaciones
        """
        total = db.session.query(Justification).filter(
            Justification.student_id == student_id
        ).count()
        
        pending = db.session.query(Justification).filter(
            and_(
                Justification.student_id == student_id,
                Justification.status == 'PENDIENTE'
            )
        ).count()
        
        approved = db.session.query(Justification).filter(
            and_(
                Justification.student_id == student_id,
                Justification.status == 'APROBADA'
            )
        ).count()
        
        rejected = db.session.query(Justification).filter(
            and_(
                Justification.student_id == student_id,
                Justification.status == 'RECHAZADA'
            )
        ).count()
        
        approval_rate = round((approved / total * 100), 1) if total > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'approval_rate': approval_rate
        }
    
    @staticmethod
    def get_dashboard_stats():
        """
        Obtiene estadísticas generales para el dashboard del profesor
        
        Returns:
            dict con estadísticas generales
        """
        # Total de estudiantes
        total_students = db.session.query(Student).filter(
            Student.status == 'A'
        ).count()
        
        # Estudiantes en riesgo
        at_risk = len(StatisticsService.get_students_at_risk())
        
        # Estudiantes críticos
        critical = len(StatisticsService.get_critical_students())
        
        # Justificaciones pendientes
        pending_justifications = db.session.query(Justification).filter(
            Justification.status == 'PENDIENTE'
        ).count()
        
        # Total de justificaciones
        total_justifications = db.session.query(Justification).count()
        
        # Justificaciones aprobadas
        approved_justifications = db.session.query(Justification).filter(
            Justification.status == 'APROBADA'
        ).count()
        
        # Justificaciones rechazadas
        rejected_justifications = db.session.query(Justification).filter(
            Justification.status == 'RECHAZADA'
        ).count()
        
        return {
            'total_students': total_students,
            'students_at_risk': at_risk,
            'students_critical': critical,
            'pending_justifications': pending_justifications,
            'total_justifications': total_justifications,
            'approved_justifications': approved_justifications,
            'rejected_justifications': rejected_justifications
        }
