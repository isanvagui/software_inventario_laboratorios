from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL,MySQLdb
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from datetime import datetime, timedelta

# Para subir archivos tipo foto al servidor
import os
from werkzeug.utils import secure_filename

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User
# Para el modulo json que se esta utilizan para el checked
from flask import Flask, render_template, request, jsonify 

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)
app.secret_key='mysecretkey'
app.config['UPLOAD_FOLDER'] = 'src/static/fotos'

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.after_request
def evita_cache(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.expires = 0
    response.pragma = 'no-cache'
    return response

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/logout')
# @login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')


#---------------------------INICIA MODULO DE GASTRONOMIA-----------------------------
@app.route('/indexGastronomia')
@login_required
def indexGastronomia():
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur = db.connection.cursor()
    cur.execute('SELECT * FROM productos')
    data = cur.fetchall()
    print(data)
    return render_template('indexGastronomia.html', productos = data)

@app.route('/add_producto', methods=['POST'])
def AGREGAR_PRODUCTO():
    if request.method =='POST':
        cod_articulo = request.form['cod_articulo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        fecha = datetime.strptime(fecha, '%Y-%m-%d')
        concepto = request.form['concepto']
        cantidad_producto = float(request.form['cantidad_producto'])
        un_medida = request.form['un_medida']
        # stock_productos = request.form['stock_productos']
        clasificacion = request.form['clasificacion']
        entrada = float(request.form['entrada']) if request.form['concepto'] == "Entrada" else 0.0
        salida = float(request.form['salida']) if request.form['concepto'] == "Salida" else 0.0

        cur = db.connection.cursor()
        
        cantidad_calculada = cantidad_producto * (entrada - salida)     

        # Inserta el registro
        cur.execute('INSERT INTO productos (cod_articulo, descripcion, fecha, cantidad_producto, concepto, un_medida, clasificacion, entrada, salida, cantidad_calculada) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                           (cod_articulo, descripcion, fecha, cantidad_producto, concepto, un_medida, clasificacion, entrada, salida, cantidad_calculada))
        db.connection.commit()

        # Actualizar el saldo de todos los registros con el mismo cod_articulo
        cur.execute('SELECT * FROM productos WHERE cod_articulo = %s', (cod_articulo,))
        data = cur.fetchall()
        saldo = 0
        stock_productos = 0
        for producto in data:
            saldo += float(producto[12])  # Calcula el saldo    
            stock_productos += float(producto[5]) * (1 if producto[4] == "Entrada" else -1) # Update the "stock_productos" based on the "concepto"
            cur.execute('UPDATE productos SET saldo = %s, stock_productos = %s WHERE id = %s', (saldo, stock_productos,producto[0]))
        db.connection.commit()

        flash('Producto agregado satisfactoriamente')
        return redirect(url_for('indexGastronomia'))

# ESTA FUNCIÓN ME LLEVA A OTRA VENTANA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN
@app.route('/edit_producto/<id>')
@login_required
def GET_PRODUCTO(id):
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM productos WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('edit-producto.html', producto = data[0])

# FUNCIÓN ACTUALIZAR
@app.route('/update/<id>', methods = ['POST'])
def ACTUALIZAR_PRODUCTO(id):
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        descripcion = request.form ['descripcion']
        un_medida = request.form ['un_medida']
        clasificacion = request.form ['clasificacion']
        cur = db.connection.cursor() 
        cur.execute(""" UPDATE productos SET cod_articulo = %s, descripcion = %s, un_medida = %s, clasificacion = %s WHERE id = %s """, (cod_articulo, un_medida, descripcion, clasificacion, id))
        db.connection.commit()
        flash('Producto actualizado satisfactoriamente')
        return redirect(url_for('indexGastronomia'))

# FUNCIÓN ELIMINAR
@app.route('/delete_producto/<string:id>')
def ELIMINAR_CONTACTO(id):
    cur = db.connection.cursor()
    cur.execute('DELETE FROM productos WHERE id = {0}'.format(id))
    db.connection.commit()
    flash('Producto eliminado satisfactoriamente')
    return redirect(url_for('indexGastronomia'))

#--------------------------------------------- LABORATORIO UNO GASTRONOMIA --------------------------------
@app.route('/labtorioUno')
def labtorioUno():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM labtoriouno')
    data = cur.fetchall()
    # print(data)
    return render_template('labtorioUno.html', labtoriouno = data)

@app.route('/add_producto_laboratorioUno', methods=['POST'])
def AGREGAR_PRODUCTO_LABTORIOUNO():
    if request.method =='POST':
        codigo_articulo = request.form ['codigo_articulo']
        ingrediente = request.form ['ingrediente']
        unidad_medida = request.form ['unidad_medida']
        cantidad_preparacion = request.form ['cantidad_preparacion']
        cur = db.connection.cursor() 
        cur.execute('INSERT INTO labtoriouno (codigo_articulo, ingrediente, unidad_medida, cantidad_preparacion) VALUES (%s, %s, %s, %s)', 
                                             (codigo_articulo, ingrediente, unidad_medida, cantidad_preparacion))
        db.connection.commit()
        flash ('Contacto agregado satisfactoriamente')
        return redirect(url_for('labtorioUno')) 

# ESTA FUNCIÓN ME LLEVA A OTRA VENTANA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN
@app.route('/editar_producto_labtoriouno/<id>')
def EDITAR_PRODUCTO(id):
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM labtoriouno WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('editar_producto_labtoriouno.html', producto = data[0])

# FUNCIÓN ACTUALIZAR
@app.route('/actualizar_laboratoriouno/<id>', methods = ['POST'])
def ACTUALIZAR_PRODUCTO_LABORATORIUNO(id):
    if request.method =='POST':
        codigo_articulo = request.form ['codigo_articulo']
        ingrediente = request.form ['ingrediente']
        unidad_medida = request.form ['unidad_medida']
        cantidad_preparacion = request.form ['cantidad_preparacion']
        cur = db.connection.cursor() 
        cur.execute(""" UPDATE labtoriouno SET codigo_articulo = %s, ingrediente = %s, unidad_medida = %s, cantidad_preparacion = %s WHERE id = %s """, (codigo_articulo, unidad_medida, ingrediente, cantidad_preparacion, id))
        db.connection.commit()
        flash('Producto actualizado satisfactorimanete')
        return redirect(url_for('labtorioUno'))

# FUNCIÓN ELIMINAR
@app.route('/delete_producto_laboratorioUno/<string:id>')
def ELIMINAR_PRODUCTO_LABORATORIOUNO(id):
    cur = db.connection.cursor()
    cur.execute('DELETE FROM labtoriouno WHERE id = {0}'.format(id))
    db.connection.commit()
    flash('Producto eliminado satisfactoriamente')
    return redirect(url_for('labtorioUno'))

#--------------------------- INICIA MODULO DE SALUD-----------------------------
@app.route('/indexSalud')
@login_required
def indexSalud():
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur = db.connection.cursor()
    cur.execute('SELECT * FROM indexssalud where enable=1') #A raiz del enable=1 no se deben eliminar en la DB
    data = cur.fetchall()
    print(data)
    return render_template('indexSalud.html', indexssalud = data)

@app.route('/add_productoSalud', methods=['POST'])
def AGREGAR_PRODUCTO_SALUD():
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

        if fecha_mantenimiento and vencimiento_mantenimiento:
            fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d')
            vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y-%m-%d')

            diferencia_dias = (vencimiento_mantenimiento - fecha_mantenimiento).days

            if diferencia_dias < 0:
                color = 'red'  # Vencido
            elif diferencia_dias <= 30:
                color = 'yellow'  # Próximo a vencer
            else:
                color = 'green'  # Vigente
            # print(diferencia_dias)
        else:
            # Manejar el caso donde no se proporciona una fecha
            flash('Debe ingresar las fechas de mantenimiento y vencimiento.', 'error')
            return redirect(url_for('indexSalud'))
        
 
        fecha_calibracion = request.form ['fecha_calibracion']
        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']

        estado_equipo = request.form ['estado_equipo']
        
        ubicacion_original = request.form ['ubicacion_original']
        garantia = request.form ['garantia']
        criticos = request.form ['criticos']
        proveedor_responsable = request.form ['proveedor_responsable']

        # Manejo de la imagen
        if 'imagen_producto' not in request.files:
            flash('No existe archivo')
            return redirect(request.url)
        file = request.files['imagen_producto']
        if file.filename == '':
            flash('Por favor selecciona el archivo')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath_to_db = os.path.join(app.config['UPLOAD_FOLDER'].split('/')[-1], filename) #Esta ruta guarda la imagen en la BD 
            filepath_to_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filepath_to_db = filepath_to_db.replace("\\", "/")
            file.save(filepath_to_save)

        cur = db.connection.cursor() 
        cur.execute('INSERT INTO indexssalud (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, imagen, color) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                             (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, filepath_to_db, color))
        db.connection.commit()
        # print(estado_equipo)
        flash ('Producto agregado satisfactoriamente')
        return redirect(url_for('indexSalud')) 
    
# ================================CHECKBOX PROGRAMACIÓN MANTENIMIENTO===============================
@app.route('/checkbox_programacionMantenimiento', methods=['POST'])
def checkbox_programacionMantenimiento():

    if request.method == 'POST':
            data = request.get_json()
            producto_id = data['productoId']
            nuevo_estado = data['nuevoEstado']
            name = data['name']
       
            cur = db.connection.cursor()
            if name == "fecha_mantenimiento":
                cur.execute('UPDATE indexssalud SET checkbox_mantenimiento = %s WHERE id = %s', (nuevo_estado, producto_id))
            
            elif name == "fecha_calibracion":
                cur.execute('UPDATE indexssalud SET checkbox_calibracion = %s WHERE id = %s', (nuevo_estado, producto_id))
            db.connection.commit()
            # print("hola",data)
            # return redirect(url_for('indexSalud'))
            return jsonify({'message': 'Estado actualizado correctamente'})

    return jsonify({'error': 'Método no permitido'}), 405
# ======================================================================================================

# ================================CHECKBOX PROGRAMACIÓN FECHA DE CALIBRACIÓN===============================
# @app.route('/checkbox_programacionCalibracion', methods=['POST'])
# def checkbox_programacionCalibracion():
#     if request.method == 'POST':
#             data = request.get_json()
#             producto_id = data['productoId']
#             nuevo_estado = data['nuevoEstado']

#             cur = db.connection.cursor()
#             cur.execute('UPDATE indexssalud SET checkbox_calibracion = %s WHERE id = %s', (nuevo_estado, producto_id))
#             db.connection.commit()

#             return redirect(url_for('indexSalud'))

#     return jsonify({'error': 'Método no permitido'}), 405
# =====================================================================================================
    
# ACTUALIZA EL ESTADO DEL EQUIPO DESDE EL DESPLEGABLE QUE SE ENCUENTRA EN LA MISMA TABLA INDEXSALUD
@app.route('/update_estado_equipo', methods=['POST'])
def update_estado_equipo():
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        nuevo_estado = request.form['nuevo_estado_equipo']

        cur = db.connection.cursor()
        cur.execute('UPDATE indexssalud SET estado_equipo = %s WHERE id = %s', (nuevo_estado, producto_id))
        db.connection.commit()

        flash('Estado del equipo actualizado correctamente')
        return redirect(url_for('indexSalud'))

# ESTA FUNCIÓN ME LLEVA A OTRA VISTA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN 
@app.route('/edit_productoSalud/<id>')
@login_required
def GET_PRODUCTO_SALUD(id):
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM indexssalud WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('editar_producto_indexSalud.html', producto = data[0])

# FUNCIÓN ACTUALIZAR EDITAR/VER HOJA DE VIDA
@app.route('/actualizarSalud/<id>', methods = ['POST'])
def ACTUALIZAR_PRODUCTO_SALUD(id):
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

        if fecha_mantenimiento and vencimiento_mantenimiento:
            fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d')
            vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y-%m-%d')

            diferencia_dias = (vencimiento_mantenimiento - fecha_mantenimiento).days

            if diferencia_dias < 0:
                color = 'red'  # Vencido
            elif diferencia_dias <= 30:
                color = 'yellow'  # Próximo a vencer
            else:
                color = 'green'  # Vigente
            print(diferencia_dias)
        else:
            # Manejar el caso donde no se proporciona una fecha
            flash('Debe ingresar las fechas de mantenimiento y vencimiento.', 'error')
            return redirect(url_for('indexSalud'))
 
        fecha_calibracion = request.form ['fecha_calibracion']
        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']

        # estado_equipo = request.form ['estado_equipo']
        
        # ubicacion_original = request.form ['ubicacion_original']
        # garantia = request.form ['garantia']
        # criticos = request.form ['criticos']
        # proveedor_responsable = request.form ['proveedor_responsable']

        cur = db.connection.cursor() 
        cur.execute(""" UPDATE indexssalud SET cod_articulo = %s, nombre_equipo = %s, fecha_mantenimiento = %s, vencimiento_mantenimiento = %s, fecha_calibracion = %s, fecha_ingreso = %s, periodicidad = %s, color = %s WHERE id = %s""",
                                              (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, color, id))
        db.connection.commit()
        # print(estado_equipo)
        flash('Producto actualizado satisfactorimanete')
        return redirect(url_for('indexSalud')) 

# FUNCIÓN ELIMINAR
@app.route('/delete_productoSalud/<string:id>')
def ELIMINAR_CONTACTO_SALUD(id):
    cur = db.connection.cursor()
    # cur.execute('DELETE FROM indexssalud WHERE id = {0}'.format(id))
    cur.execute('UPDATE indexssalud SET enable=0 WHERE id = {0}'.format(id)) #Esta linea de codigo en la vista elimina el producto pero no de la DB, la cual realiza es una actualización
    db.connection.commit()
    flash('Producto eliminado satisfactoriamente')
    return redirect(url_for('indexSalud'))


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
