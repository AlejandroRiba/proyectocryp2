from datetime import date, datetime
import re
from models.Database import getDatabase
from models.Usuario import Usuario, obtener_usuario_por_id
from models.Transaccion import Transaccion
from models.DetalleTransaccion import DetalleTransaccion
from models.Producto import Producto
from models.Cliente import Cliente
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import cm
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Line
from reportlab.pdfgen import canvas
from pyFunctions.cryptoUtils import sign_message_ECDSA, verify_signature_ECDSA
from models.Reporte import crear_reporte

# Define la ruta base para el directorio de imágenes
BASE_IMAGE_PATH = os.path.join("static", "images", "products")
LOGO_PATH = os.path.join("static", "images")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define la ruta completa a la carpeta `reports`
PDF_PATH = os.path.join(BASE_DIR, 'reports')

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
            return None, "No transactions for this period."

        # Crear lista para almacenar detalles del reporte
        monto_total = 0
        fecha_y_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ventas = {
            'headers': {
                'empleado': f"{empleado.id} - {empleado.nombre} {empleado.apellido}",
                'fechareporte': str(fecha_y_hora),
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
        print(e)
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
    document.author = report_data['headers']['empleado']

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


def agregar_firma(pdf_file, private_key):
    # Leer el contenido del PDF
    with open(pdf_file, "rb") as f:
        contenido = f.read()

    firma = sign_message_ECDSA(private_key, contenido)

    # Si no hay firma, agregarla
    with open(pdf_file, "wb") as f: 
        f.write(contenido)
        f.write(b'\n')  # Indicador de que hay una firma
        f.write(firma)

    print("Firma añadida con éxito.")

def verificar_firma(pdf_filename, empleado_id):
    # Leer la clave pública desde el archivo
    pdf_file = os.path.join(PDF_PATH, pdf_filename)
    # Leer el contenido del PDF
    with open(pdf_file, "rb") as f:
        contenido = f.read().split(b'\n')
        pdf_content = b'\n'.join(contenido[:-1])  # Combinar todo menos la última línea (la firma)
        firma = contenido[-1] #firma por separado

    usuario = obtener_usuario_por_id(empleado_id)
    public_key = usuario.publickey

    verificado = verify_signature_ECDSA(public_key, pdf_content, firma)
    return verificado
    

def generar_informe_ventas_mensual(empleado_id, year, month, private_key):
    ventas, flash_message = procesar_información(empleado_id, year, month)
    if ventas is None:
        return False, flash_message
    pdf_filename = f"monthlyreport_{empleado_id}_{year}-{month:02d}.pdf"
    generar_pdf_ventas(ventas, pdf_filename)
    pdf_file = os.path.join(PDF_PATH, pdf_filename)
    agregar_firma(pdf_file, private_key)
        
    # Crear fecha con base en el año y mes proporcionados
    fecha_reporte = date(year, month, 1)
        
    crear_reporte(empleado_id, fecha_reporte)
    return True, None
    
def obtener_archivo_por_id_y_fecha(directorio, id_empleado, año, mes):
    patron_fecha = f"{año}-{mes:02d}"  # Formatear el mes con dos dígitos
    for archivo in os.listdir(directorio):
        if (
            archivo.startswith(f"monthlyreport_{id_empleado}_") and
            patron_fecha in archivo and
            archivo.endswith(".pdf")
        ):
            return archivo  # Devuelve el archivo en cuanto se encuentra
    return None  # Si no se encuentra ningún archivo, devuelve None

def obtener_empleado_id_de_nombre_archivo(filename):
    # Suponiendo que el formato del nombre del archivo es 'monthlyreport_<ID>_<año>-<mes>'
    match = re.match(r'monthlyreport_(\d+)_(\d{4})-(\d{2})', filename)
    if match:
        return match.group(1)  # Devuelve el ID del empleado
    return None