from flask import Flask, render_template_string, request, jsonify, send_from_directory, session, send_file
from flask_cors import CORS
import json
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_variedades_osmari' 
CORS(app, supports_credentials=True)

# Contraseña del administrador 
ADMIN_PASSWORD = "admin1234"

# Datos de Pago Móvil para Variedades Osmari (Banco de Venezuela)
DATOS_PAGO = {
    "banco": "0102 - Banco de Venezuela",
    "cedula": "V-17758545",
    "telefono": "04220082464",
    "whatsapp": "584220082464"
}

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'productos.json'
EXCEL_FILE = 'ventas.csv'

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_productos(productos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# HTML DEL PANEL DE ADMINISTRACIÓN FUTURISTA (VARIEDADES OSMARI)
# ---------------------------------------------------------
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VARIEDADES OSMARI // Panel de Control</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg-deep: #05070b;
            --bg-card: rgba(13, 20, 35, 0.85);
            --neon-cyan: #00f0ff;
            --neon-green: #00ff66;
            --neon-pink: #ff007f;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --border-glow: rgba(0, 240, 255, 0.3);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        
        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(255, 0, 127, 0.05) 0%, transparent 40%);
            min-height: 100vh;
            padding: 30px 15px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .login-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glow);
            padding: 40px 30px;
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(0, 240, 255, 0.15);
            width: 100%;
            max-width: 420px;
            text-align: center;
        }

        .login-card h2 {
            color: var(--neon-cyan);
            font-size: 1.4rem;
            letter-spacing: 2px;
            margin-bottom: 10px;
            text-transform: uppercase;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        }

        .login-card p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 25px; }

        .login-card input {
            width: 100%;
            padding: 12px 15px;
            margin-bottom: 18px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s;
        }

        .login-card input:focus {
            border-color: var(--neon-cyan);
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
        }

        .btn-login {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.3), rgba(0, 240, 255, 0.1));
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-login:hover {
            background: var(--neon-cyan);
            color: var(--bg-deep);
            box-shadow: 0 0 20px var(--neon-cyan);
        }

        .error-msg {
            color: var(--neon-pink);
            font-size: 0.85rem;
            margin-top: 15px;
            display: none;
            text-shadow: 0 0 8px rgba(255, 0, 127, 0.4);
        }

        .admin-container {
            display: none;
            width: 100%;
            max-width: 1000px;
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glow);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 0 35px rgba(0, 0, 0, 0.8);
        }

        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 15px;
        }

        .admin-header h1 {
            color: var(--neon-cyan);
            font-size: 1.5rem;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
        }

        h3 { color: var(--text-main); font-size: 1.1rem; margin-bottom: 15px; letter-spacing: 1px; }

        .form-grid {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }

        input, select, button {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.95rem;
            outline: none;
        }

        select option { background: #0f172a; color: white; }

        input:focus, select:focus {
            border-color: var(--neon-cyan);
            box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
        }

        .btn-add {
            background: linear-gradient(135deg, rgba(0, 255, 102, 0.2), rgba(0, 255, 102, 0.05));
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-add:hover {
            background: var(--neon-green);
            color: #000;
            box-shadow: 0 0 15px var(--neon-green);
        }

        .btn-delete {
            background: rgba(255, 0, 127, 0.15);
            border: 1px solid var(--neon-pink);
            color: var(--neon-pink);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-delete:hover {
            background: var(--neon-pink);
            color: white;
            box-shadow: 0 0 10px var(--neon-pink);
        }

        .btn-logout {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-logout:hover { border-color: var(--neon-pink); color: var(--neon-pink); }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); vertical-align: middle; }
        th { color: var(--neon-cyan); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }

        .img-preview { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid var(--border-glow); }

        @media (max-width: 768px) {
            .form-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div class="login-card" id="login-section">
        <h2><i class="fa-solid fa-shield-halved"></i> ACCESO CENTRAL</h2>
        <p>Autenticación requerida - Variedades Osmari</p>
        <form id="login-form">
            <input type="password" id="admin-pass" placeholder="Clave de Administrador" required>
            <button type="submit" class="btn-login">INGRESAR AL SISTEMA</button>
            <div class="error-msg" id="error-msg">⚠️ Clave incorrecta. Acceso denegado.</div>
        </form>
    </div>

    <div class="admin-container" id="admin-section">
        <div class="admin-header">
            <h1>⚡ VARIEDADES OSMARI // INVENTARIO</h1>
            <button class="btn-logout" onclick="logout()"><i class="fa-solid fa-power-off"></i> Salir</button>
        </div>

        <div style="margin-bottom: 25px; background: rgba(0, 240, 255, 0.05); border: 1px solid var(--border-glow); padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin-bottom: 5px; color: var(--neon-cyan);"><i class="fa-solid fa-file-excel"></i> Control de Ventas</h3>
                <p style="color: var(--text-muted); font-size: 0.85rem;">Descarga el registro de pedidos en formato compatible con Excel (CSV).</p>
            </div>
            <button class="btn-add" onclick="downloadReport()" style="padding: 10px 20px;">
                <i class="fa-solid fa-download"></i> DESCARGAR REPORTE
            </button>
        </div>

        <h3>REGISTRAR NUEVO ITEM</h3>
        <form id="product-form" style="margin-top: 15px;">
            <div class="form-grid">
                <input type="text" id="nombre" placeholder="Nombre (ej: Camisa Ovejita / Queso Paisa)" required>
                <input type="number" step="0.01" id="precio" placeholder="Precio ($)" required>
                <!-- SELECTOR CON TODAS LAS NUEVAS CATEGORÍAS -->
                <select id="categoria">
                    <option value="ropa">Ropa y Moda</option>
                    <option value="lenceria">Lencería</option>
                    <option value="cremas">Cuidado Personal / Cremas</option>
                    <option value="charcuteria">Charcutería</option>
                    <option value="quesos">Quesos</option>
                    <option value="viveres">Víveres</option>
                    <option value="hogar">Hogar / Varios</option>
                </select>
                <select id="unidad">
                    <option value="Unidad">Por Unidad</option>
                    <option value="Kg">Por Kg</option>
                    <option value="Pack">Por Pack</option>
                </select>
            </div>
            
            <div class="form-grid" style="grid-template-columns: 3fr 1fr;">
                <input type="file" id="imagen" accept="image/*">
                <button type="submit" class="btn-add">+ AGREGAR ITEM</button>
            </div>
        </form>

        <hr style="margin: 25px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">

        <h3>PRODUCTOS REGISTRADOS</h3>
        <table>
            <thead>
                <tr>
                    <th>Visual</th>
                    <th>Producto</th>
                    <th>Categoría</th>
                    <th>Precio</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody id="inventory-table"></tbody>
        </table>
    </div>

    <script>
        const API_URL = `${window.location.origin}/api/productos`;

        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('admin-pass').value;

            try {
                const res = await fetch(`${window.location.origin}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });

                const data = await res.json();
                if (data.success) {
                    document.getElementById('login-section').style.display = 'none';
                    document.getElementById('admin-section').style.display = 'block';
                    fetchProducts();
                } else {
                    document.getElementById('error-msg').style.display = 'block';
                }
            } catch (err) {
                console.error("Error en autenticación:", err);
            }
        });

        async function logout() {
            await fetch(`${window.location.origin}/api/logout`, { method: 'POST' });
            location.reload();
        }

        function downloadReport() {
            window.location.href = `${window.location.origin}/api/descargar-ventas`;
        }

        async function fetchProducts() {
            try {
                const res = await fetch(API_URL);
                const productos = await res.json();
                renderTable(productos);
            } catch (err) {
                console.error("Error al obtener datos:", err);
            }
        }

        function renderTable(productos) {
            const tbody = document.getElementById('inventory-table');
            tbody.innerHTML = '';
            
            productos.forEach(p => {
                const imgSrc = p.imagen ? `${window.location.origin}/uploads/${p.imagen}` : 'https://via.placeholder.com/45?text=NA';
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><img src="${imgSrc}" class="img-preview" alt="Foto"></td>
                    <td><strong>${p.nombre}</strong> <span style="color:var(--text-muted); font-size:0.85rem;">(${p.unidad})</span></td>
                    <td style="color:var(--neon-cyan);">${p.categoria.toUpperCase()}</td>
                    <td style="color:var(--neon-green); font-weight:bold;">$${p.precio.toFixed(2)}</td>
                    <td><button class="btn-delete" onclick="deleteProduct(${p.id})">ELIMINAR</button></td>
                `;
                tbody.appendChild(row);
            });
        }

        document.getElementById('product-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('nombre', document.getElementById('nombre').value);
            formData.append('precio', document.getElementById('precio').value);
            formData.append('categoria', document.getElementById('categoria').value);
            formData.append('unidad', document.getElementById('unidad').value);
            
            const fileInput = document.getElementById('imagen');
            if (fileInput.files[0]) {
                formData.append('imagen', fileInput.files[0]);
            }

            const res = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });

            if(res.status === 401) {
                alert("Sesión expirada.");
                location.reload();
                return;
            }

            document.getElementById('product-form').reset();
            fetchProducts();
        });

        async function deleteProduct(id) {
            if(confirm("¿Confirmar eliminación del registro?")) {
                const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
                if(res.status === 401) {
                    alert("No autorizado.");
                    location.reload();
                    return;
                }
                fetchProducts();
            }
        }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# RUTAS DE FLASK
# ---------------------------------------------------------

@app.route('/')
def cliente_page():
    productos = cargar_productos()
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read(), productos=productos, pago=DATOS_PAGO)

@app.route('/admin')
def admin_page():
    return render_template_string(ADMIN_HTML)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/login', methods=['POST'])
def data_login():
    data = request.get_json()
    if data and data.get('password') == ADMIN_PASSWORD:
        session['admin_logged'] = True
        return jsonify({"success": True, "mensaje": "Acceso concedido"})
    return jsonify({"success": False, "mensaje": "Contraseña incorrecta"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('admin_logged', None)
    return jsonify({"success": True})

@app.route('/api/registrar-pago', methods=['POST'])
def registrar_pago():
    try:
        data = request.get_json()
        nombre = data.get('cliente', '')
        direccion = data.get('direccion', '')
        metodo = data.get('metodo', '')
        referencia = data.get('referencia', '')
        monto = data.get('monto', 0.0)
        detalles = data.get('detalles', '')
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        file_exists = os.path.exists(EXCEL_FILE)

        with open(EXCEL_FILE, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            if not file_exists:
                writer.writerow(['Fecha y Hora', 'Cliente', 'Direccion', 'Metodo de Pago', 'N° Referencia', 'Total ($)', 'Detalle Orden'])
            writer.writerow([fecha, nombre, direccion, metodo, referencia, monto, detalles])

        return jsonify({"success": True, "mensaje": "Venta registrada con éxito"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/descargar-ventas', methods=['GET'])
def descargar_ventas():
    if not session.get('admin_logged'):
        return jsonify({"error": "No autorizado."}), 401
    
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True, download_name='ventas_variedades_osmari.csv')
    else:
        return "Aún no hay registros de ventas guardados en el sistema.", 404

@app.route('/api/productos', methods=['GET'])
def get_productos():
    return jsonify(cargar_productos())

@app.route('/api/productos', methods=['POST'])
def add_producto():
    if not session.get('admin_logged'):
        return jsonify({"error": "No autorizado."}), 401

    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')
    unidad = request.form.get('unidad', 'Unidad')

    imagen_filename = ''
    if 'imagen' in request.files:
        archivo = request.files['imagen']
        if archivo.filename != '':
            filename = secure_filename(archivo.filename)
            productos = cargar_productos()
            nuevo_id = max([p['id'] for p in productos], default=0) + 1
            filename = f"prod_{nuevo_id}_{filename}"
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_filename = filename

    productos = cargar_productos()
    nuevo_id = max([p['id'] for p in productos], default=0) + 1

    nuevo_producto = {
        "id": nuevo_id,
        "nombre": nombre,
        "precio": float(precio),
        "categoria": categoria,
        "unidad": unidad,
        "imagen": imagen_filename
    }

    productos.append(nuevo_producto)
    guardar_productos(productos)
    return jsonify({"mensaje": "Producto guardado con éxito", "producto": nuevo_producto}), 201

@app.route('/api/productos/<int:prod_id>', methods=['DELETE'])
def delete_producto(prod_id):
    if not session.get('admin_logged'):
        return jsonify({"error": "No autorizado."}), 401

    productos = cargar_productos()
    for p in productos:
        if p['id'] == prod_id and p.get('imagen'):
            ruta_img = os.path.join(app.config['UPLOAD_FOLDER'], p['imagen'])
            if os.path.exists(ruta_img):
                os.remove(ruta_img)

    productos = [p for p in productos if p['id'] != prod_id]
    guardar_productos(productos)
    return jsonify({"mensaje": "Producto eliminado exitosamente"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
