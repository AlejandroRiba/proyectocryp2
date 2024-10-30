from datetime import datetime
from models.Database import getDatabase
from models.Usuario import Usuario
from models.Transaccion import Transaccion
from models.DetalleTransaccion import DetalleTransaccion
from models.Producto import Producto
from models.Cliente import Cliente
import datetime
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import cm
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Line
import datetime

# Define la ruta base para el directorio de imágenes
BASE_IMAGE_PATH = os.path.join("static", "images", "products")
LOGO_PATH = os.path.join("static", "images")
PDF_PATH = os.path.join("static","docs","reports")

db = getDatabase()

def get_image_path(filename):
    return os.path.join(BASE_IMAGE_PATH, filename)

def get_pdf_path(filename):
    return os.path.join(PDF_PATH, filename)

def get_logo_path(filename):
    return os.path.join(LOGO_PATH,filename)

meses = ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]

def obtener_nombre_mes(numero_mes):
    numero_mes = int(numero_mes)
    if 1 <= numero_mes <= 12:
        return meses[numero_mes - 1]
    else:
        return "Número de mes no válido"

def procesar_información(empleado_id, year, month):
    try:
        # Obtener los datos del empleado
        empleado = Usuario.query.filter_by(id=empleado_id).first()
        if not empleado:
            print("Empleado no encontrado")
            return None, "Error finding the user"

        # Filtrar transacciones del empleado para el mes y año dados
        transacciones = Transaccion.query.filter(
            Transaccion.empleado_id == empleado_id,
            db.extract('year', Transaccion.fecha) == year,
            db.extract('month', Transaccion.fecha) == month
        ).all()

        if not transacciones:
            print("No hay transacciones para este periodo.")
            return None, "No transactions for this period."

        # Crear lista para almacenar detalles del reporte
        monto_total = 0
        ventas = {
            'headers': {
                'empleado': f"{empleado.id} - {empleado.nombre} {empleado.apellido}",
                'fechareporte': str(datetime.date.today()),
                'mes': f'{obtener_nombre_mes(month)} - {str(year)}',
                'total': '$0',
            }
        }

        # Recorrer las transacciones y sus detalles
        for index, transaccion in enumerate(transacciones):
            detalles = []
            detalles.append(['ID', 'Img', 'Product','Size', 'Quantity', 'Price', 'Total'])
            detalles_transaccion = DetalleTransaccion.query.filter_by(transaccion_id=transaccion.id).all()
            cliente = Cliente.query.get(transaccion.cliente_id) 
            for detalle in detalles_transaccion:
                producto = Producto.query.filter_by(id=detalle.producto_id).first()
                imagen = get_image_path(producto.archivo)
                monto = detalle.cantidad * producto.precio
                detalles.append(
                    [producto.id, Image(imagen, width=1.5*cm, height=1.5*cm), Paragraph(producto.nombre), detalle.talla, detalle.cantidad, f'${producto.precio}', f'${monto}']
                )

            monto_total += transaccion.monto
            venta = {
                'Fecha de Venta': str(transaccion.fecha),
                'data_cliente': [['Client', f'{cliente.nombre} {cliente.apellido}']],
                'data' : detalles,
                'data_price': [['Total', f'${transaccion.monto}']],
            }
            ventas[f'venta_{index}'] = venta
            
            
        # Actualiza el monto total en el encabezado después del bucle
        ventas['headers']['total'] = f'${monto_total}'
        return ventas, None

    except Exception as e:
        return None, "Error generating the report."
    

def generar_pdf_ventas(report_data, pdf_filename):
    pdf_file = os.path.join(PDF_PATH, pdf_filename) #para que se guarde en la ruta dada

    margins = {
        'topMargin': 0.5 * cm,    # Margen superior
        'bottomMargin': 0.5 * cm,  # Margen inferior
        'leftMargin': 1.5 * cm,    # Margen izquierdo
        'rightMargin': 1.5 * cm     # Margen derecho
    }

    document = SimpleDocTemplate(pdf_file, pagesize=letter, **margins)
    document.title = f"Monthly Sales Report - {report_data['headers']['mes']}" 

    elements = []
    styles = getSampleStyleSheet()  # Obtener estilos de muestra
    left_align_title = ParagraphStyle(
        name="LeftAlignedTitle",
        parent=styles["Title"],
        alignment=0
    )

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#85170e')),  # Fila de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fae8d4')), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
        ('WORDWRAP', (1, 1), (-2, -1), 'ON'),
    ])

    style1 = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#525050')),  # Fila de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.honeydew),
        # Líneas externas de la tabla (negras)
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),  # Líneas de la tabla
        ('WORDWRAP', (1, 1), (-2, -1), 'ON'),
    ])

    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0))

    # Agregar el logo
    logo_path = get_logo_path("logo.jpg")  # Cambia esta ruta al logo de tu empresa
    logo = Image(logo_path, width=5 * inch, height=0.5 * inch)
    elements.append(logo)
    elements.append(Spacer(1, 0.5 * cm))  # Espacio entre el logo y el encabezado

    # Agregar encabezados
    header = Paragraph("Monthly Sales Report", left_align_title)
    elements.append(header)
    elements.append(linea)

    # Agregar los datos del encabezado
    encabezados = [
    Paragraph(f"<font color='#d05704'><b>Employee:</b></font> {report_data['headers']['empleado']}", styles['BodyText']),
    Paragraph(f"<font color='#d05704'><b>Report Generation Date:</b></font> {report_data['headers']['fechareporte']}", styles['BodyText']),
    Paragraph(f"<font color='#d05704'><b>Month:</b></font> {report_data['headers']['mes']}", styles['BodyText']),
    Paragraph(f"<font color='#d05704'><b>Total for the Month:</b></font> <b><font color='#0c0553'>{report_data['headers']['total']}</font></b>", styles['BodyText']),
    ]

    for item in encabezados:
        elements.append(item)

    # Recorre las ventas
    for venta_key, data in report_data.items():
        if venta_key.startswith('venta_'):  # Asegurarte de procesar solo las entradas de venta
            # Espacio y título antes de cada tabla
            elements.append(Spacer(1, 0.5 * cm))
            title = Paragraph(f"Sales Table / {data['Fecha de Venta']}", styles['Heading2'])
            elements.append(title)

            # Crear tabla para el subtotal y agregarla a los elementos
            table_tit = Table(data['data_cliente'], colWidths=[2 * cm, 16 * cm])
            table_tit.setStyle(style1)
            elements.append(table_tit)

            # Crear tabla de ventas y agregarla a los elementos
            table = Table(data['data'], colWidths=[2 * cm, 3 * cm, 5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm])
            table.setStyle(style)
            elements.append(table)

            # Crear tabla para el subtotal y agregarla a los elementos
            table_subtotal = Table(data['data_price'], colWidths=[16 * cm, 2 * cm])
            table_subtotal.setStyle(style1)
            elements.append(table_subtotal)

    # Construir el documento
    document.build(elements)
    print(f"PDF '{pdf_file}' generado con éxito.")


def generar_informe_ventas_mensual(empleado_id, year, month):
    ventas, flash_message = procesar_información(empleado_id, year, month)
    if ventas != None:
        pdf_filename = f"monthlyreport_{empleado_id}_{year}-{month}.pdf"
        generar_pdf_ventas(ventas, pdf_filename)
        return True, None
    else: 
        return False, flash_message