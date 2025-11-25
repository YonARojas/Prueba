from flask import Blueprint, request, jsonify
from app import db
from app.models.justification import Justification
from app.models.student import Student
from app.models.course import Course
from app.models.audit_log import AuditLog
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

justification_student_bp = Blueprint('justification_student', __name__)

UPLOAD_FOLDER = 'uploads/justifications'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@justification_student_bp.route('/create', methods=['POST'])
def create_justification():
    """Crear nueva justificación (estudiante)"""
    try:
        print("🔵 Iniciando creación de justificación...")
        # Obtener datos del formulario
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        absence_date = request.form.get('absence_date')
        reason_type = request.form.get('reason_type')
        reason_description = request.form.get('reason_description')
        print(f"📝 Datos recibidos: student_id={student_id}, course_id={course_id}, absence_date={absence_date}")
        
        # Validar campos requeridos
        if not all([student_id, course_id, absence_date, reason_type, reason_description]):
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            }), 400
        
        # Validar que la fecha no sea mayor a 7 días atrás
        absence_date_obj = datetime.strptime(absence_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_diff = (today - absence_date_obj).days
        
        if days_diff > 7:
            return jsonify({
                'success': False,
                'message': 'Solo puedes justificar inasistencias de hasta 7 días atrás'
            }), 400
        
        if days_diff < 0:
            return jsonify({
                'success': False,
                'message': 'No puedes justificar inasistencias futuras'
            }), 400
        
        # Verificar que el estudiante existe
        print(f"🔍 Buscando estudiante con ID: {student_id}")
        student = db.session.query(Student).get(student_id)
        print(f"✅ Estudiante encontrado: {student}")
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Verificar que el curso existe
        print(f"🔍 Buscando curso con ID: {course_id}")
        course = db.session.query(Course).get(course_id)
        print(f"✅ Curso encontrado: {course}")
        if not course:
            return jsonify({
                'success': False,
                'message': 'Curso no encontrado'
            }), 404
        
        # Manejar archivo adjunto
        attachment_filename = None
        attachment_path = None
        attachment_type = None
        attachment_size = None
        
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                print(f"📎 Archivo recibido: {file.filename}")
                
                # Validar extensión
                if allowed_file(file.filename):
                    # Crear directorio si no existe
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    
                    # Generar nombre único
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{student_id}_{timestamp}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    
                    # Guardar archivo
                    file.save(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    print(f"✅ Archivo guardado: {file_path} ({file_size} bytes)")
                    
                    # Guardar info para la BD
                    attachment_filename = unique_filename
                    attachment_path = f'/uploads/justifications/{unique_filename}'
                    attachment_type = file.content_type
                    attachment_size = file_size
                else:
                    print(f"⚠️ Archivo rechazado: extensión no permitida")
        
        # Crear la justificación
        print("📝 Creando objeto Justification...")
        justification = Justification(
            student_id=student_id,
            course_id=course_id,
            absence_date=absence_date_obj,
            reason_type=reason_type,
            reason_description=reason_description,
            status='PENDIENTE',
            attachment_filename=attachment_filename,
            attachment_path=attachment_path,
            attachment_type=attachment_type,
            attachment_size=attachment_size
        )
        
        print("💾 Agregando a la sesión...")
        db.session.add(justification)
        print("🔄 Haciendo flush...")
        db.session.flush()  # Para obtener el ID
        print(f"✅ Justification creada con ID: {justification.id}")
        if attachment_filename:
            print(f"📎 Con archivo adjunto: {attachment_filename}")
        
        # Registrar en audit_logs
        AuditLog.log_action(
            user_id=student.id,
            user_type='STUDENT',
            action='CREATE_JUSTIFICATION',
            table_name='justifications',
            record_id=justification.id,
            new_values=f'Creó justificación para {course.course_name} - {reason_type}',
            ip_address=request.remote_addr
        )
        
        db.session.commit()
        
        # Enviar email al profesor del curso
        try:
            from app.services.email_service import EmailService
            from app.models.professor import Professor
            professor = db.session.query(Professor).get(course.professor_id)
            if professor and professor.email:
                print(f"📧 Enviando email a profesor: {professor.email}")
                EmailService.send_justification_submitted(
                    student, professor, justification, course
                )
                print(f"✅ Email enviado exitosamente")
            else:
                print(f"⚠️ Profesor no tiene email configurado")
        except Exception as email_error:
            print(f"⚠️ Error al enviar email al profesor: {email_error}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True,
            'message': 'Justificación creada exitosamente',
            'data': justification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error al crear justificación:")
        print(error_trace)
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_student_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_justifications(student_id):
    """Obtener todas las justificaciones de un estudiante"""
    try:
        status_filter = request.args.get('status')
        
        query = db.session.query(Justification).filter(
            Justification.student_id == student_id
        )
        
        if status_filter and status_filter != 'TODAS':
            query = query.filter(Justification.status == status_filter)
        
        justifications = query.order_by(Justification.submission_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [j.to_dict() for j in justifications]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_student_bp.route('/<int:justification_id>', methods=['GET'])
def get_justification_detail(justification_id):
    """Obtener detalle de una justificación"""
    try:
        justification = db.session.query(Justification).get(justification_id)
        
        if not justification:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': justification.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
