from flask import (Flask, request, render_template,
                   redirect, url_for)
import json
import os

app = Flask(__name__)
ARCHIVO = 'productos.json'


def cargar_productos():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def guardar_productos(productos):
    with open(ARCHIVO, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)


def nuevo_id(productos):
    if not productos:
        return 1
    return max(p['id'] for p in productos) + 1


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registrar', methods=['POST'])
def registrar():
    productos = cargar_productos()

    try:
        precio   = float(request.form.get('precio', 0))
        cantidad = int(request.form.get('cantidad', 0))
    except (TypeError, ValueError):
        return "Datos inválidos", 400

    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return "El nombre es obligatorio", 400

    nuevo = {
        'id':       nuevo_id(productos),
        'nombre':   nombre,
        'precio':   precio,
        'cantidad': cantidad,
        'total':    precio * cantidad
    }
    productos.append(nuevo)
    guardar_productos(productos)
    return render_template('resultado.html',
                           accion='registrado', producto=nuevo)


@app.route('/productos')
def listar():
    productos        = cargar_productos()
    total_productos  = len(productos)
    valor_inventario = sum(p['total'] for p in productos)
    promedio_precio  = (sum(p['precio'] for p in productos) / total_productos
                        if total_productos else 0)
    return render_template(
        'lista.html',
        productos=productos,
        total_productos=total_productos,
        valor_inventario=valor_inventario,
        promedio_precio=promedio_precio
    )


@app.route('/producto/<int:id>')
def detalle(id):
    productos = cargar_productos()
    producto  = next((p for p in productos if p['id'] == id), None)
    if producto is None:
        return "Producto no encontrado", 404
    return render_template('detalle.html', producto=producto)


@app.route('/editar/<int:id>')
def editar(id):
    productos = cargar_productos()
    producto  = next((p for p in productos if p['id'] == id), None)
    if producto is None:
        return "Producto no encontrado", 404
    return render_template('editar.html', producto=producto)


@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    productos = cargar_productos()
    encontrado = False

    for p in productos:
        if p['id'] == id:
            try:
                p['precio']   = float(request.form.get('precio', 0))
                p['cantidad'] = int(request.form.get('cantidad', 0))
            except (TypeError, ValueError):
                return "Datos inválidos", 400

            p['nombre'] = request.form.get('nombre', '').strip()
            p['total']  = p['precio'] * p['cantidad']
            encontrado  = True
            break

    if not encontrado:
        return "Producto no encontrado", 404

    guardar_productos(productos)
    producto = next(p for p in productos if p['id'] == id)
    return render_template('resultado.html',
                          accion='actualizado', producto=producto)


@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    productos = cargar_productos()
    productos = [p for p in productos if p['id'] != id]
    guardar_productos(productos)
    return redirect(url_for('listar'))


if __name__ == '__main__':
    app.run(debug=True)
