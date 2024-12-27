from base64 import b64encode
from datetime import date, datetime
import re

from PyPDF2 import PdfReader, PdfWriter
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
from reportlab.platypus import Frame, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Line
from reportlab.pdfgen import canvas
from pyFunctions.cryptoUtils import sign_message_ECDSA, verify_signature_ECDSA
from models.Reporte import crear_reporte

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,  load_pem_private_key, load_pem_public_key
)
from cryptography.exceptions import InvalidSignature
from base64 import b64encode, b64decode

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
    
def verificar_espacio(elements, contenido, page_height, top_margin, bottom_margin, current_y):
    """
    Verifica si hay espacio suficiente en la página para agregar contenido.

    :param elements: Lista de elementos a renderizar en el PDF.
    :param contenido: Altura total requerida por el nuevo contenido.
    :param page_height: Altura total de la página.
    :param top_margin: Margen superior.
    :param bottom_margin: Margen inferior.
    :param current_y: Posición actual en la página.
    :return: Nueva posición `current_y`.
    """
    espacio_disponible = page_height - top_margin - bottom_margin - current_y
    if contenido > espacio_disponible:
        # Si no hay suficiente espacio, agregar salto de página
        elements.append(PageBreak())
        current_y = top_margin  # Reiniciar posición para la nueva página
    return current_y

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
                    [producto.id, Image(imagen, width=1*cm, height=1*cm), Paragraph(producto.nombre), detalle.talla, detalle.cantidad, f'${producto.precio}', f'${monto}']
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
    page_height = letter[1]  # Altura de la página
    top_margin = 0.5 * cm  # Margen superior
    bottom_margin = 0.5 * cm  # Margen inferior
    current_y = top_margin  # Posición inicial en la página (comienza en el margen superior)

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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1D2D44')),  # Fila de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#f1e5c6')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1e5c6')), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
        ('WORDWRAP', (1, 1), (-2, -1), 'ON'),
    ])

    style1 = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#657891')),  # Fila de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#01060e')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#01060e')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1e5c6')),
        # Líneas externas de la tabla (negras)
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),  # Líneas de la tabla
        ('WORDWRAP', (1, 1), (-2, -1), 'ON'),
    ])

    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0))

    # Agregar el logo
    logo_path = get_logo_path("logo.jpg")  # Cambia esta ruta al logo de tu empresa
    logo = Image(logo_path, width=4 * inch, height=0.4 * inch)
    elements.append(logo)
    elements.append(Spacer(1, 0.5 * cm))  # Espacio entre el logo y el encabezado
    current_y += 0.4 * inch  # Espacio para el encabezado

    # Agregar encabezados
    header = Paragraph("Monthly Sales Report", left_align_title)
    elements.append(header)
    elements.append(linea)
    current_y += 2 * cm  # Espacio para el encabezado

    # Agregar los datos del encabezado
    encabezados = [
    Paragraph(f"<font color='#9b3205'><b>Employee:</b></font> {report_data['headers']['empleado']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Report Generation Date:</b></font> {report_data['headers']['fechareporte']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Month:</b></font> {report_data['headers']['mes']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Total for the Month:</b></font> <b><font color='#031b4e'>{report_data['headers']['total']}</font></b>", styles['BodyText']),
    ]

    for item in encabezados:
        elements.append(item)
        current_y += 0.6 * cm  # Espacio para el encabezado

    # Recorre las ventas
    for venta_key, data in report_data.items():
        if venta_key.startswith('venta_'):  # Asegurarte de procesar solo las entradas de venta
            # Espacio y título antes de cada tabla
            # Calcular altura total requerida para este bloque
            altura_titulo = 1.5 * cm  # Altura estimada del título
            altura_tabla_cliente = len(data['data_cliente']) * 0.6 * cm  # Altura de la tabla de cliente
            altura_tabla_ventas = len(data['data']) * 1 * cm  # Altura de la tabla de ventas
            altura_tabla_subtotal = len(data['data_price']) * 0.6 * cm  # Altura de la tabla de subtotal
            altura_bloque = altura_titulo + altura_tabla_cliente + altura_tabla_ventas + altura_tabla_subtotal + 1.5 * cm  # Altura total del bloque

            # Verificar espacio disponible y saltar de página si no cabe
            current_y = verificar_espacio(elements, altura_bloque, page_height, top_margin, bottom_margin, current_y)
            elements.append(Spacer(1, 0.5 * cm))
            title = Paragraph(f"Sales Table / {data['Fecha de Venta']}", styles['Heading2'])
            elements.append(title)
            current_y += altura_titulo

            # Crear tabla para el cliente y agregarla a los elementos
            table_tit = Table(data['data_cliente'], colWidths=[2 * cm, 16 * cm])
            table_tit.setStyle(style1)
            elements.append(table_tit)
            current_y += altura_tabla_cliente

            # Crear tabla de ventas y agregarla a los elementos
            table = Table(data['data'], colWidths=[2 * cm, 3 * cm, 5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm])
            table.setStyle(style)
            elements.append(table)
            current_y += altura_tabla_ventas

            # Crear tabla para el subtotal y agregarla a los elementos
            table_subtotal = Table(data['data_price'], colWidths=[16 * cm, 2 * cm])
            table_subtotal.setStyle(style1)
            elements.append(table_subtotal)
            current_y += altura_tabla_subtotal

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
    # with open(pdf_file, "rb") as f:
    #    contenido = f.read().split(b'\n')
    #    pdf_content = b'\n'.join(contenido[:-1])  # Combinar todo menos la última línea (la firma)
    #    firma = contenido[-1] #firma por separado

    usuario = obtener_usuario_por_id(empleado_id)
    public_key = usuario.publickey

    verificado = verify_pdf(pdf_file, public_key)
    return verificado
    

def generar_informe_ventas_mensual(empleado_id, year, month, private_key):
    ventas, flash_message = procesar_información(empleado_id, year, month)
    if ventas is None:
        return False, flash_message
    pdf_filename = f"monthlyreport_{empleado_id}_{year}-{month:02d}.pdf"
    generar_pdf_ventas(ventas, pdf_filename)
    pdf_file = os.path.join(PDF_PATH, pdf_filename)
    sign_pdf(pdf_file, pdf_file, private_key, ventas)
        
    # Crear fecha con base en el año y mes proporcionados
    fecha_reporte = date(year, month, 1)
        
    crear_reporte(empleado_id, fecha_reporte)
    return True, None
    
def obtener_archivo_por_id_y_fecha(directorio, id_empleado, año, mes):
    print(f'Busqueda de archivos para {id_empleado}')
    patron_fecha = f"{año}-{mes:02d}"  # Formatear el mes con dos dígitos
    print(f'Patron fecha {patron_fecha}')
    for archivo in os.listdir(directorio):
        if (
            archivo.startswith(f"monthlyreport_{id_empleado}_") and
            patron_fecha in archivo and
            archivo.endswith(".pdf")
        ):
            print(f'archivo encontrado en directorio -- {archivo}')
            return archivo  # Devuelve el archivo en cuanto se encuentra
    return None  # Si no se encuentra ningún archivo, devuelve None

def obtener_empleado_id_de_nombre_archivo(filename):
    # Suponiendo que el formato del nombre del archivo es 'monthlyreport_<ID>_<año>-<mes>'
    match = re.match(r'monthlyreport_(\d+)_(\d{4})-(\d{2})', filename)
    if match:
        return match.group(1)  # Devuelve el ID del empleado
    return None

def sign_pdf(input_pdf_path, output_pdf_path, private_key_base64, report_data):
    # Decodificar la clave privada desde la cadena base64
    private_key_bytes = b64decode(private_key_base64)
    
    # Cargar la clave privada desde los bytes decodificados
    private_key = load_pem_private_key(private_key_bytes, password=None)

    # Leer el contenido del PDF original
    reader = PdfReader(input_pdf_path)
    pdf_data = b"".join([page.extract_text().encode() for page in reader.pages])

    # Calcular el hash del contenido
    digest = hashes.Hash(hashes.SHA256())
    digest.update(pdf_data)
    pdf_hash = digest.finalize()

    # Generar la firma con la clave privada
    signature = private_key.sign(pdf_hash, ec.ECDSA(hashes.SHA256()))
    signature_base64 = b64encode(signature).decode()

    # Crear un PDF con la firma visible usando ReportLab
    visible_signature_pdf = "firma_visible_temp.pdf"
    generar_pagina_firma(signature_base64, report_data, visible_signature_pdf)


    # Combinar el PDF original con la firma visible
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    signature_reader = PdfReader(visible_signature_pdf)
    writer.add_page(signature_reader.pages[0])

    # Agregar la firma a los metadatos
    writer.add_metadata({"/ECDSASignature": signature_base64})

    # Guardar el PDF firmado
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    # Eliminar el archivo temporal de la firma visible
    if os.path.exists(visible_signature_pdf):
        os.remove(visible_signature_pdf)
        print(f"Archivo temporal '{visible_signature_pdf}' eliminado.")

    print(f"PDF firmado guardado en {output_pdf_path}")

def generar_pagina_firma(signature_base64, report_data, output_pdf_path):
    """
    Genera una página de firma visible con un estilo similar al encabezado del reporte.
    """
    # Configuración del PDF
    pdf_file = output_pdf_path
    margins = {
        'topMargin': 0.5 * cm,    # Margen superior
        'bottomMargin': 0.5 * cm,  # Margen inferior
        'leftMargin': 1.5 * cm,    # Margen izquierdo
        'rightMargin': 1.5 * cm     # Margen derecho
    }

    document = SimpleDocTemplate(pdf_file, pagesize=letter, **margins)
    elements = []
    styles = getSampleStyleSheet()

    # Estilo del título
    left_align_title = ParagraphStyle(
        name="LeftAlignedTitle",
        parent=styles["Title"],
        alignment=0
    )

    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0))

    # Agregar el logo
    logo_path = get_logo_path("logo.jpg")  # Cambia esta ruta al logo de tu empresa
    logo = Image(logo_path, width=4 * inch, height=0.4 * inch)
    elements.append(logo)
    elements.append(Spacer(1, 0.5 * cm))  # Espacio entre el logo y el encabezado

    # Agregar encabezados
    header = Paragraph("Monthly Sales Report", left_align_title)
    elements.append(header)
    elements.append(linea)

    # Agregar los datos del encabezado
    encabezados = [
    Paragraph(f"<font color='#9b3205'><b>Employee:</b></font> {report_data['headers']['empleado']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Report Generation Date:</b></font> {report_data['headers']['fechareporte']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Month:</b></font> {report_data['headers']['mes']}", styles['BodyText']),
    Paragraph(f"<font color='#9b3205'><b>Total for the Month:</b></font> <b><font color='#031b4e'>{report_data['headers']['total']}</font></b>", styles['BodyText']),
    ]

    for item in encabezados:
        elements.append(item)

    elements.append(Spacer(1, 1.2 * cm))

    # Agregar una línea horizontal antes de la firma
    linea = Drawing(500, 1)
    linea.add(Line(0, 0, 500, 0))

    # Agregar la firma
    leyenda_seguridad_texto = """
    This document has been digitally signed with ECDSA by the author. The verification of this signature ensures the authenticity of the sales data and guarantees non-repudiation, meaning the author cannot deny the validity of the signature or the transaction.
    """
    leyenda_seguridad = Paragraph(leyenda_seguridad_texto, styles['BodyText'])
    elements.append(leyenda_seguridad)
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(linea)
    elements.append(Spacer(1, 0.3 * cm))
    firma_titulo = Paragraph("<b>Digital Signature:</b>", styles['BodyText'])
    elements.append(firma_titulo)
    firma_parrafos = [
        Paragraph(signature_base64[:80], styles['BodyText']),
        Paragraph(signature_base64[80:160], styles['BodyText']),
        Paragraph(signature_base64[160:], styles['BodyText']),
    ]
    for parrafo in firma_parrafos:
        elements.append(parrafo)

    # Generar PDF
    document.build(elements)
    print(f"Página de firma visible generada en {output_pdf_path}")


def verify_pdf(pdf_path, public_key_base64):
    # Leer el PDF firmado
    reader = PdfReader(pdf_path)

    # Extraer la firma de los metadatos
    metadata = reader.metadata
    signature_base64 = metadata.get("/ECDSASignature")
    if not signature_base64:
        raise ValueError("No se encontró la firma en los metadatos del PDF.")
    signature_bytes = b64decode(signature_base64)

    # Extraer el contenido del PDF para calcular el hash
    pdf_data = b"".join([page.extract_text().encode() for page in reader.pages[:-1]])  # Excluir la página de firma visible
    digest = hashes.Hash(hashes.SHA256())
    digest.update(pdf_data)
    pdf_hash = digest.finalize()

    # Decodificar la cadena base64 de la clave pública
    public_key_bytes = b64decode(public_key_base64)

    # Cargar la clave pública desde los bytes decodificados
    public_key = load_pem_public_key(public_key_bytes)

    # Verificar la firma con la clave pública
    try:
        public_key.verify(signature_bytes, pdf_hash, ec.ECDSA(hashes.SHA256()))
        print("La firma es válida.")
        return True
    except InvalidSignature:
        print("La firma no es válida.")
        return False