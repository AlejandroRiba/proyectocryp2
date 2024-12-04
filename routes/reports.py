import os
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for

from models.Reporte import obtener_reportes_por_empleado, obtener_reporte_por_fecha_y_empleado
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
    
    # Obtener filtros
    id_empleado = request.args.get('id_empleado', '')
    mes = request.args.get('mes', '')
    año = request.args.get('año', '')

    if employee.cargo == 'Employee':
        reportes = obtener_reportes_por_empleado(employee.id)
        files = []

        for reporte in reportes:
            if (not año or reporte.fecha.year == int(año)) and \
               (not mes or reporte.fecha.month == int(mes)):
                file = obtener_archivo_por_id_y_fecha(REPORTS_DIR, employee.id, reporte.fecha.year, reporte.fecha.month)
                if file:
                    files.append(file)

        return render_template(
            'consulta_informes.html',
            status=username,
            files=files,
            filtros={'id_empleado': id_empleado, 'mes': mes, 'año': año}
        )
    else:
        employees = obtener_empleados()
        all_files = {}

        for employee in employees:
            reportes = obtener_reportes_por_empleado(employee.id)
            employee_files = []

            for reporte in reportes:
                if (not año or reporte.fecha.year == int(año)) and \
                   (not mes or reporte.fecha.month == int(mes)):
                    file = obtener_archivo_por_id_y_fecha(REPORTS_DIR, employee.id, reporte.fecha.year, reporte.fecha.month)
                    if file:
                        employee_files.append(file)
            if employee_files:
                all_files[employee.nombre] = employee_files

        print(all_files)
        return render_template(
            'consulta_informes_admin.html',
            status=username,
            all_files=all_files,
            filtros={'id_empleado': id_empleado, 'mes': mes, 'año': año}
        )

    
@reports_blueprint.route('/verificar_firma_de_archivo/<filename>', methods=['POST'])
def verificar_firma_de_archivo(filename):
    es_valida = verificar_firma(filename, obtener_empleado_id_de_nombre_archivo(filename))
    print(es_valida)
    if es_valida:
        flash('La firma es válida.', 'success')
    else:
        flash('La firma no es válida.', 'danger')

    return redirect('/consulta_informes')
    
@reports_blueprint.route('/download_report/<filename>')
def download_report(filename):
    # Verifica que el archivo exista en la carpeta `reports` antes de enviarlo}
    if filename in os.listdir(REPORTS_DIR):
        return send_from_directory(REPORTS_DIR, filename, as_attachment=True)
    else:
        abort(404)  # Devuelve un error 404 si el archivo no existe

# Ruta para generar un informe
@reports_blueprint.route('/generar_informe', methods=['GET', 'POST'])
def generar_informe():
    if request.method == 'GET':
        username = session['username']
        return render_template('generar_informe.html', status=username)
    if request.method == 'POST':
        access = mainfunc.auth(session['username'], request.form['password'], None)
        if not access:
            return jsonify({"success": False, "message": "Incorrect password. Try again.", "destino":None}), 401
        
        year = int(request.form['year'])
        month = int(request.form['month'])

        #Corrección: verificar si existe un reporte del mismo mes y año creado previamente
        existeReporte = obtener_reporte_por_fecha_y_empleado(empleado_id = session['username'], mes = month, anio = year)
        if existeReporte:
            return jsonify({"success": False, "message": "There is already a report for this month and year created.", "destino": None}), 401

        private_key = session['private_key']
        report, flash_message = generar_informe_ventas_mensual(session['username'], year, month, private_key)
        print(flash_message)
        print(report)
        if report:
            return jsonify({"success": True, "message": "Welcome.", "destino": '/consulta_informes'}), 200
        else:
            return jsonify({"success": False, "message": flash_message, "destino":None}), 401
            
        
   
@reports_blueprint.route('/reports', methods=['GET'])
def listar_reportes():
    directorio_reportes = REPORTS_DIR
    id_empleado = request.args.get('id_empleado')
    mes = request.args.get('mes')
    año = request.args.get('año')

    # Listar archivos
    reportes = os.listdir(directorio_reportes)
    archivos_filtrados = []

    for reporte in reportes:
        partes = reporte.split('_')  # Ejemplo: "monthlyreport_123_2024-11.pdf"
        if len(partes) != 3:
            continue

        _, empleado_id, fecha = partes
        empleado_id = empleado_id
        fecha_año, fecha_mes = fecha.split('.')[0].split('-')

        if (not id_empleado or empleado_id == id_empleado) and \
           (not mes or fecha_mes == mes) and \
           (not año or fecha_año == año):
            archivos_filtrados.append(reporte)

    return jsonify(archivos_filtrados)