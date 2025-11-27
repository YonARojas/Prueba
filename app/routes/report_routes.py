"""
Rutas para generación de reportes PDF y Excel
"""
from flask import Blueprint, send_file, jsonify
from app.services.report_service import ReportService
from app.routes.auth_routes import token_required
from datetime import datetime

report_bp = Blueprint('reports', __name__)

@report_bp.route('/students/pdf', methods=['GET'])
@token_required
def get_students_pdf(current_user):
    """Genera PDF con todos los estudiantes"""
    try:
        buffer = ReportService.generate_students_pdf()
        
        if not buffer:
            return jsonify({'error': 'No se pudo generar el reporte'}), 500
        
        filename = f'estudiantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/students/<int:student_id>/pdf', methods=['GET'])
@token_required
def get_student_pdf(current_user, student_id):
    """Genera PDF individual de un estudiante"""
    try:
        buffer = ReportService.generate_student_pdf(student_id)
        
        if not buffer:
            return jsonify({'error': 'Estudiante no encontrado'}), 404
        
        filename = f'estudiante_{student_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/students/excel', methods=['GET'])
@token_required
def get_students_excel(current_user):
    """Genera Excel con todos los estudiantes"""
    try:
        buffer = ReportService.generate_students_excel()
        
        if not buffer:
            return jsonify({'error': 'No se pudo generar el reporte'}), 500
        
        filename = f'estudiantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/professors/pdf', methods=['GET'])
@token_required
def get_professors_pdf(current_user):
    """Genera PDF con todos los profesores"""
    try:
        buffer = ReportService.generate_professors_pdf()
        
        if not buffer:
            return jsonify({'error': 'No se pudo generar el reporte'}), 500
        
        filename = f'profesores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
