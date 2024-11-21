import os
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for

from models.Reporte import obtener_reportes_por_empleado
from models.Usuario import obtener_empleados, obtener_usuario_por_id
from pyFunctions import mainfunc
from pyFunctions.reportepdf import generar_informe_ventas_mensual, obtener_archivo_por_id_y_fecha, obtener_empleado_id_de_nombre_archivo, verificar_firma
from init import REPORTS_DIR

reports_blueprint = Blueprint('reports', __name__)

# Ruta para consultar los informes
@reports_blueprint.route('/consulta_informes', methods=['GET'])
def consulta_informes():
    username = session['username']
    employee = obtener_usuario_por_id(username)

    if employee.cargo == 'Employee':
        reportes = obtener_reportes_por_empleado(employee.id)
        files = []
        for reporte in reportes:
            file = obtener_archivo_por_id_y_fecha(REPORTS_DIR, employee.id, reporte.fecha.year, reporte.fecha.month)
            if file:
                files.append(file)
        return render_template('consulta_informes.html', status=username, files=files)

    else:
        employees = obtener_empleados()
        all_files = {}

        for employee in employees:
            reportes = obtener_reportes_por_empleado(employee.id)
            employee_files = []
            for reporte in reportes:
                file = obtener_archivo_por_id_y_fecha(REPORTS_DIR, employee.id, reporte.fecha.year, reporte.fecha.month)
                if file:
                    employee_files.append(file)
            if employee_files:
                all_files[employee.nombre] = employee_files
        return render_template('consulta_informes_admin.html', status=username, all_files=all_files)
    
@reports_blueprint.route('/verificar_firma_de_archivo/<filename>', methods=['POST'])
def verificar_firma_de_archivo(filename):
    es_valida = verificar_firma(filename, obtener_empleado_id_de_nombre_archivo(filename))

    if es_valida:
        flash('La firma es válida.', 'success')
    else:
        flash('La firma no es válida.', 'danger')

    return redirect('/consulta_informes')
    
@reports_blueprint.route('/download_report/<filename>')
def download_report(filename):
    # Verifica que el archivo exista en la carpeta `reports` antes de enviarlo
    if filename in os.listdir(REPORTS_DIR):
        return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
    else:
        abort(404)  # Devuelve un error 404 si el archivo no existe

# Ruta para generar un informe
@reports_blueprint.route('/generar_informe', methods=['GET', 'POST'])
def generar_informe():
    if request.method == 'POST':
        access = mainfunc.auth(session['username'], request.form['password'], None)
        if access:
            year = int(request.form['year'])
            month = int(request.form['month'])
            private_key = session['private_key']
            report, flash_message = generar_informe_ventas_mensual(session['username'], year, month, private_key)
            if report:
                return jsonify({"success": True, "message": "Welcome.", "destino": '/consulta_informes'}), 200
            else:
                return jsonify({"success": False, "message": flash_message, "destino":None}), 204
        else:
            return jsonify({"success": False, "message": "Incorrect password. Try again.", "destino":None}), 401
    else:
        username = session['username']
        return render_template('generar_informe.html', status=username)
   