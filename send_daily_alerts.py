"""
Script para enviar alertas diarias de asistencia
Ejecutar manualmente o programar con cron/task scheduler
"""
from app import create_app, db
from app.models.student import Student
from app.services.statistics_service import StatisticsService
from app.services.email_service import EmailService
from datetime import datetime

def send_daily_attendance_alerts():
    """Envía alertas diarias a estudiantes con inasistencias críticas"""
    app = create_app()
    
    with app.app_context():
        print('\n' + '='*60)
        print(f'🔔 ENVÍO DE ALERTAS DE INASISTENCIA')
        print(f'📅 Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        print('='*60 + '\n')
        
        print('🔍 Buscando estudiantes con alertas de inasistencia...\n')
        
        # Obtener todos los estudiantes activos
        students = Student.query.filter_by(status='A').all()
        print(f'📊 Total de estudiantes activos: {len(students)}\n')
        
        critical_students = []
        risk_students = []
        
        for student in students:
            # Calcular estadísticas
            stats = StatisticsService.calculate_student_attendance(student.id)
            
            # Clasificar por nivel de riesgo
            if stats['absence_percentage'] >= 30:
                critical_students.append((student, stats))
            elif stats['absence_percentage'] >= 25:
                risk_students.append((student, stats))
        
        print(f'❌ Estudiantes CRÍTICOS (≥30% inasistencias): {len(critical_students)}')
        print(f'🟠 Estudiantes EN RIESGO (25-29% inasistencias): {len(risk_students)}\n')
        
        # Enviar alertas solo a estudiantes críticos
        alerts_sent = 0
        alerts_failed = 0
        
        if len(critical_students) > 0:
            print('📧 Enviando alertas a estudiantes críticos...\n')
            
            for student, stats in critical_students:
                print(f'   → {student.full_name} ({student.student_code})')
                print(f'     Email: {student.email}')
                print(f'     Inasistencias: {stats["absence_percentage"]}%')
                
                if EmailService.send_attendance_alert(student, stats):
                    alerts_sent += 1
                    print(f'     ✅ Alerta enviada exitosamente\n')
                else:
                    alerts_failed += 1
                    print(f'     ❌ Error al enviar alerta\n')
        else:
            print('ℹ️ No hay estudiantes críticos para enviar alertas\n')
        
        # Resumen
        print('='*60)
        print('📊 RESUMEN DEL ENVÍO')
        print('='*60)
        print(f'✅ Alertas enviadas exitosamente: {alerts_sent}')
        print(f'❌ Alertas fallidas: {alerts_failed}')
        print(f'📧 Total de emails enviados: {alerts_sent}')
        print('='*60 + '\n')

if __name__ == '__main__':
    try:
        send_daily_attendance_alerts()
    except Exception as e:
        print(f'\n❌ ERROR CRÍTICO: {str(e)}\n')
        import traceback
        traceback.print_exc()
