from app.models.student import Student
from app.models.professor import Professor
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.attendance_record import AttendanceRecord
from app.models.justification import Justification
from app.models.audit_log import AuditLog

__all__ = [
    'Student',
    'Professor', 
    'Course',
    'CourseEnrollment',
    'AttendanceRecord',
    'Justification',
    'AuditLog'
]