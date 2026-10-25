from flask import Flask, render_template, send_from_directory, jsonify, send_file
import os
import json
import csv
import io

app = Flask(__name__)

# Ruta del archivo JSON de productos
PRODUCTOS_FILE = os.path.join(app.root_path, 'static', 'productos.json')

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Ruta para la página principal (Catálogo y Tienda)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el panel de administración
@app.route('/admin')
def admin():
    return render_template('admin.html')

# API opcional para obtener la lista de productos desde el servidor
@app.route('/api/productos', methods=['GET'])
def api_get_productos():
    productos = cargar_productos()
    return jsonify(productos)

# Ruta para descargar el reporte de inventario en archivo CSV
@app.route('/descargar_reporte')
def descargar_reporte():
    productos = cargar_productos()
    
    # Crear un archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir los encabezados de las columnas
    writer.writerow(['ID', 'Nombre', 'Precio ($)', 'Categoría', 'Unidad', 'Imagen'])
    
    # Escribir los datos de cada producto
    for p in productos:
        writer.writerow([
            p.get('id'),
            p.get('nombre'),
            p.get('precio'),
            p.get('categoria'),
            p.get('unidad'),
            p.get('imagen')
        ])
        
    output.seek(0)
    
    # Enviar el archivo como descarga automática al navegador
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='reporte_inventario_variedades_osmari.csv'
    )

# Ruta para asegurar que las imágenes carguen sin problemas desde la carpeta uploads
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)

if __name__ == '__main__':
    app.run(debug=True)
