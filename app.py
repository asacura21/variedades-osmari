from flask import Flask, render_template, send_from_directory, jsonify, send_file, request, redirect, url_for, session
import os
import json
import csv
import io

app = Flask(__name__)
app.secret_key = 'osmari_secure_key_2026'  # Clave secreta para mantener la sesión segura

# Ruta del archivo JSON de productos
PRODUCTOS_FILE = os.path.join(app.root_path, 'static', 'productos.json')

# CLAVE DE ADMINISTRADOR (Puedes cambiarla aquí cuando quieras)
ADMIN_PASSWORD = "admin1234"  # <--- Cambia esto por la clave secreta que prefieras

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Ruta para la página principal (Catálogo y Tienda)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para iniciar sesión en el Admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged'] = True
            return redirect(url_for('admin'))
        else:
            error = "Clave incorrecta. Inténtalo de nuevo."
    return render_template('login.html', error=error)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('admin_logged', None)
    return redirect(url_for('login'))

# Ruta para el panel de administración (Protegida con clave)
@app.route('/admin')
def admin():
    if not session.get('admin_logged'):
        return redirect(url_for('login'))
    return render_template('admin.html')

# API opcional para obtener la lista de productos desde el servidor
@app.route('/api/productos', methods=['GET'])
def api_get_productos():
    productos = cargar_productos()
    return jsonify(productos)

# Ruta para descargar el reporte de inventario en archivo CSV (Protegida también)
@app.route('/descargar_reporte')
def descargar_reporte():
    if not session.get('admin_logged'):
        return redirect(url_for('login'))
        
    productos = cargar_productos()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Nombre', 'Precio ($)', 'Categoría', 'Unidad', 'Imagen'])
    
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
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='reporte_inventario_variedades_osmari.csv'
    )

# Ruta para asegurar que las imágenes carguen sin problemas
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)

if __name__ == '__main__':
    app.run(debug=True)
