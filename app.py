from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
from datetime import datetime, timedelta
import unicodedata

app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Usuarios y contraseñas
USUARIOS = {
    "admin": "diego",
    "user": "1234"
}

CARPETA_CLIENTES = 'clientes'
os.makedirs(CARPETA_CLIENTES, exist_ok=True)

# Lista de productos
productos = [
    {"nombre": "Avena", "imagen": "avena.jpg", "precio": 40},
    {"nombre": "Burritos", "imagen": "burritos.jpeg", "precio": 55},
    {"nombre": "Chilaquiles con Pollo", "imagen": "chilaquiles_pollo.jpg", "precio": 65},
    {"nombre": "Chilaquiles Sencillos", "imagen": "chilaquiles_sencillos.jpg", "precio": 50},
    {"nombre": "Emoladas", "imagen": "emoladas.jpeg", "precio": 60},
    {"nombre": "Enchiladas", "imagen": "enchiladas.jpg", "precio": 60},
    {"nombre": "Hotcake con Huevo", "imagen": "hotcake+huevo.jpeg", "precio": 55},
    {"nombre": "Hotcakes", "imagen": "hotcakes.jpg", "precio": 45},
    {"nombre": "Omelet con Chilaquiles", "imagen": "omelet+chila.jpeg", "precio": 70},
    {"nombre": "Orden de Guisado", "imagen": "ordenguisado.jpg", "precio": 60},
    {"nombre": "Ensalada de Frutas", "imagen": "ensalada_frutas.jpeg", "precio": 50},
    {"nombre": "Ensalada de Atún", "imagen": "ensalada-atun.jpg", "precio": 60},
    {"nombre": "Ensalada de Pollo", "imagen": "ensalada-de-pollo.jpg", "precio": 65},
    {"nombre": "Ensalada Verde", "imagen": "ensalada-verde.jpg", "precio": 55},
    {"nombre": "Sándwich de Atún", "imagen": "sandwich-atun.jpg", "precio": 65},
    {"nombre": "Sándwich de Jamón", "imagen": "sandwich-jamon.jpg", "precio": 55},
    {"nombre": "Sándwich de Panela", "imagen": "sandwich-panela.jpeg", "precio": 60},
    {"nombre": "Sándwich de Pollo", "imagen": "sandwich-pollo.jpeg", "precio": 65},
    {"nombre": "Torta de Chilaquiles", "imagen": "torta-chilaquiles.jpg", "precio": 70},
    {"nombre": "Wrap de Burro", "imagen": "wrap-de-burro.jpg", "precio": 75},
    {"nombre": "Wrap de Chilaquiles", "imagen": "wrap-de-chila.jpg", "precio": 70},
    {"nombre": "Wrap de Pollo", "imagen": "wrap-de-pollo.jpg", "precio": 80},
    {"nombre": "Wrap de Vegetales", "imagen": "wrap-de-vegetales.jpg", "precio": 65},
    {"nombre": "Agua Fresca", "imagen": "bebida-aguas.jpg", "precio": 25},
    {"nombre": "Café Americano", "imagen": "bebida-cafe.jpg", "precio": 30},
    {"nombre": "Capuchino", "imagen": "bebida-capuchino.jpeg", "precio": 40},
    {"nombre": "Licuado de Frutas", "imagen": "bebida-licuados.jpg", "precio": 50},
    {"nombre": "Té Caliente", "imagen": "bebida-te.jpeg", "precio": 35},
    {"nombre": "Quesadilla de Guiso", "imagen": "adicional-quesadilla-guiso.jpg", "precio": 30},
    {"nombre": "Taco Sencillo", "imagen": "adicional-taco.jpg", "precio": 25},
    {"nombre": "Tostada de Guiso", "imagen": "adicional-tostada-guiso.jpg", "precio": 35},
    {"nombre": "Tostada de Queso", "imagen": "adicional-tostada-queso.jpg", "precio": 35},
]

def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

def obtener_pedidos_listos():
    pedidos_listos = []
    ahora = datetime.now()
    for filename in os.listdir(CARPETA_CLIENTES):
        if filename.endswith('.json'):
            ruta = os.path.join(CARPETA_CLIENTES, filename)
            with open(ruta) as f:
                pedido = json.load(f)
            if pedido.get('entregado'):
                hora_listo = datetime.strptime(pedido['hora_listo'], "%Y-%m-%d %H:%M:%S") if 'hora_listo' in pedido else None
                if hora_listo and (ahora - hora_listo).total_seconds() > 60:
                    # Eliminar solo el campo hora_listo para que el mensaje desaparezca
                    pedido.pop('hora_listo', None)
                    with open(ruta, 'w') as f:
                        json.dump(pedido, f, indent=4)
                else:
                    pedidos_listos.append(pedido['nombre'])
    return pedidos_listos

@app.route('/login', methods=['GET', 'POST'])
def login():
    pedidos_listos = obtener_pedidos_listos()
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login'))
    return render_template('login.html', productos=productos, pedidos_listos=pedidos_listos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.before_request
def verificar_sesion():
    rutas_libres = ['login', 'static', 'index']
    if request.endpoint not in rutas_libres and 'usuario' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    pedidos_listos = obtener_pedidos_listos()
    return render_template('index.html', productos=productos, pedidos_listos=pedidos_listos)

@app.route('/iniciar_pedido', methods=['GET', 'POST'])
def iniciar_pedido():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        session['nombre'] = nombre
        session['pedido'] = []
        session['nota'] = ""
        return redirect(url_for('menu'))
    return render_template('iniciar_pedido.html')

@app.route('/menu')
@app.route('/menu/<categoria>')
def menu(categoria=None):
    if categoria == 'ensaladas':
        productos_filtrados = [p for p in productos if normalizar(p['nombre']).startswith('ensalada')]
        titulo = "Ensaladas"
    elif categoria == 'sandwich':
        productos_filtrados = [p for p in productos if 'sandwich' in normalizar(p['nombre']) or 'torta' in normalizar(p['nombre'])]
        titulo = "Sandwich"
    elif categoria == 'wraps':
        productos_filtrados = [p for p in productos if 'wrap' in normalizar(p['nombre'])]
        titulo = "Wraps"
    elif categoria == 'bebidas':
        productos_filtrados = [p for p in productos if 'bebida' in normalizar(p['imagen']) or 'cafe' in normalizar(p['nombre']) or 'te' in normalizar(p['nombre']) or 'licuado' in normalizar(p['nombre'])]
        titulo = "Bebidas"
    elif categoria == 'adicionales':
        productos_filtrados = [p for p in productos if 'adicional' in normalizar(p['imagen']) or 'quesadilla' in normalizar(p['nombre']) or 'tostada' in normalizar(p['nombre']) or 'taco' in normalizar(p['nombre'])]
        titulo = "Adicionales"
    else:
        productos_filtrados = productos
        titulo = "Menú General"
    return render_template('menu.html', productos=productos_filtrados, categoria=titulo)

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = session.get('nombre')
    if not nombre:
        return redirect(url_for('iniciar_pedido'))

    producto = request.form.get('producto')
    precio = float(request.form.get('precio'))

    pedido = session.get('pedido', [])
    pedido.append({'producto': producto, 'precio': precio})
    session['pedido'] = pedido

    return redirect(request.referrer or url_for('menu'))

@app.route('/resumen', methods=['GET', 'POST'])
def resumen():
    if request.method == 'POST':
        nota = request.form.get('nota', '')
        session['nota'] = nota
        return redirect(url_for('resumen'))

    pedido = session.get('pedido', [])
    nota = session.get('nota', '')
    total = sum(p['precio'] for p in pedido)
    return render_template('resumen.html', pedido=pedido, total=total, nota=nota)

@app.route('/eliminar_producto/<int:indice>', methods=['POST'])
def eliminar_producto(indice):
    pedido = session.get('pedido', [])
    if 0 <= indice < len(pedido):
        pedido.pop(indice)
        session['pedido'] = pedido
    return redirect(url_for('resumen'))

@app.route('/confirmar_pedido')
def confirmar_pedido():
    nombre = session.get('nombre')
    pedido = session.get('pedido', [])
    nota = session.get('nota', '')

    if not nombre or not pedido:
        return redirect(url_for('iniciar_pedido'))

    ahora = datetime.now()
    codigo = ahora.strftime("%Y-%m-%d_%H-%M-%S")

    datos_pedido = {
        'codigo': codigo,
        'nombre': nombre,
        'pedido': pedido,
        'nota': nota,
        'total': sum(p['precio'] for p in pedido),
        'hora': ahora.strftime("%Y-%m-%d %H:%M:%S"),
        'entregado': False
    }

    with open(os.path.join(CARPETA_CLIENTES, f"{codigo}.json"), 'w') as f:
        json.dump(datos_pedido, f, indent=4)

    session.pop('nombre', None)
    session.pop('pedido', None)
    session.pop('nota', None)

    return render_template('pedido_guardado.html', datos=datos_pedido)

@app.route('/pedidos')
def ver_pedidos():
    pedidos = []
    for filename in sorted(os.listdir(CARPETA_CLIENTES)):
        if filename.endswith('.json'):
            with open(os.path.join(CARPETA_CLIENTES, filename)) as f:
                pedidos.append(json.load(f))
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/marcar_listo/<codigo>', methods=['POST'])
def marcar_listo(codigo):
    archivo = os.path.join(CARPETA_CLIENTES, f"{codigo}.json")
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
        datos['entregado'] = True
        datos['hora_listo'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(archivo, 'w') as f:
            json.dump(datos, f, indent=4)
    return redirect(url_for('ver_pedidos'))

@app.route('/desmarcar_listo/<codigo>', methods=['POST'])
def desmarcar_listo(codigo):
    archivo = os.path.join(CARPETA_CLIENTES, f"{codigo}.json")
    if os.path.exists(archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
        datos['entregado'] = False
        datos.pop('hora_listo', None)
        with open(archivo, 'w') as f:
            json.dump(datos, f, indent=4)
    return redirect(url_for('ver_pedidos'))

@app.route('/eliminar_todos', methods=['POST'])
def eliminar_todos():
    for filename in os.listdir(CARPETA_CLIENTES):
        if filename.endswith('.json'):
            os.remove(os.path.join(CARPETA_CLIENTES, filename))
    return redirect(url_for('ver_pedidos'))

@app.route('/contabilidad')
def contabilidad():
    resumen = {}
    total_ventas = 0
    total_pedidos = 0

    for filename in os.listdir(CARPETA_CLIENTES):
        if filename.endswith('.json'):
            with open(os.path.join(CARPETA_CLIENTES, filename)) as f:
                pedido = json.load(f)
                total_pedidos += 1
                total_ventas += pedido['total']

                for item in pedido['pedido']:
                    nombre = item['producto']
                    precio = item['precio']
                    if nombre not in resumen:
                        resumen[nombre] = {'cantidad': 0, 'total': 0}
                    resumen[nombre]['cantidad'] += 1
                    resumen[nombre]['total'] += precio

    return render_template('contabilidad.html', resumen=resumen, total_ventas=total_ventas, total_pedidos=total_pedidos)

@app.route('/eliminar_contabilidad', methods=['POST'])
def eliminar_contabilidad():
    for filename in os.listdir(CARPETA_CLIENTES):
        if filename.endswith('.json'):
            os.remove(os.path.join(CARPETA_CLIENTES, filename))
    flash("Contabilidad del día eliminada.")
    return redirect(url_for('contabilidad'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
