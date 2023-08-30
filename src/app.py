from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config

from datetime import datetime, timedelta


# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)
login_manager_app = LoginManager(app)
app.secret_key='mysecretkey'

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


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
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')
#---------------------------INICIA MODULO DE GASTRONOMIA-----------------------------
@app.route('/indexGastronomia')
def indexGastronomia():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM productos')
    data = cur.fetchall()
    # print(data)
    return render_template('indexGastronomia.html', productos = data)

@app.route('/add_producto', methods=['POST'])
def AGREGAR_PRODUCTO():
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        descripcion = request.form ['descripcion']
        un_medida = request.form ['un_medida']
        clasificacion = request.form ['clasificacion']
        cur = db.connection.cursor() 
        cur.execute('INSERT INTO productos (cod_articulo, descripcion, un_medida, clasificacion) VALUES (%s, %s, %s, %s)', (cod_articulo, descripcion, un_medida, clasificacion))
        db.connection.commit()
        flash ('Contacto agregado satisfactoriamente')
        return redirect(url_for('indexGastronomia')) 

# ESTA FUNCIÓN ME LLEVA A OTRA VENTANA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN
@app.route('/edit_producto/<id>')
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
        flash('Producto actualizado satisfactorimanete')
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
        cur.execute('INSERT INTO labtoriouno (codigo_articulo, ingrediente, unidad_medida, cantidad_preparacion) VALUES (%s, %s, %s, %s)', (codigo_articulo, ingrediente, unidad_medida, cantidad_preparacion))
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
def indexSalud():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM indexssalud')
    data = cur.fetchall()
    # print(data)
    return render_template('indexSalud.html', indexssalud = data)

@app.route('/add_productoSalud', methods=['POST'])
def AGREGAR_PRODUCTO_SALUD():
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

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
        
 
        fecha_calibracion = request.form ['fecha_calibracion']
        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']

        estado_equipo = request.form ['estado_equipo']
        
        ubicacion_original = request.form ['ubicacion_original']
        garantia = request.form ['garantia']
        criticos = request.form ['criticos']
        proveedor_responsable = request.form ['proveedor_responsable']

        cur = db.connection.cursor() 
        cur.execute('INSERT INTO indexssalud (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                             (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, color))
        db.connection.commit()
        print(estado_equipo)
        flash ('Producto agregado satisfactoriamente')
        return redirect(url_for('indexSalud')) 
    
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

# ESTA FUNCIÓN ME LLEVA A OTRA VENTANA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN
@app.route('/edit_productoSalud/<id>')
def GET_PRODUCTO_SALUD(id):
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM indexssalud WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('editar_producto_indexSalud.html', producto = data[0])

# FUNCIÓN ACTUALIZAR
@app.route('/actualizarSalud/<id>', methods = ['POST'])
def ACTUALIZAR_PRODUCTO_SALUD(id):
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        #--------------------------- estas dos lineas permiten mostrar la fecha de vencimiento apartir de la fecha_mantenimiento -----------------------------
        # fecha_mantenimiento = datetime.strptime(request.form['fecha_mantenimiento'], '%Y-%m-%d')
        # vencimiento_mantenimiento = fecha_mantenimiento + timedelta(days=365)

        fecha_calibracion = request.form ['fecha_calibracion']
        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']
        estado_equipo = request.form ['estado_equipo']
        ubicacion_original = request.form ['ubicacion_original']
        garantia = request.form ['garantia']
        criticos = request.form ['criticos']
        proveedor_responsable = request.form ['proveedor_responsable']
        cur = db.connection.cursor() 
        cur.execute(""" UPDATE indexssalud SET cod_articulo = %s, nombre_equipo = %s, fecha_mantenimiento = %s, fecha_calibracion = %s, fecha_ingreso = %s, periodicidad = %s, estado_equipo = %s, ubicacion_original = %s, garantia = %s, criticos = %s, proveedor_responsable = %s WHERE id = %s """, 
                                               (cod_articulo, nombre_equipo, fecha_mantenimiento, fecha_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, id))
        db.connection.commit()
        flash('Producto actualizado satisfactorimanete')
        return redirect(url_for('indexSalud'))

# FUNCIÓN ELIMINAR
@app.route('/delete_productoSalud/<string:id>')
def ELIMINAR_CONTACTO_SALUD(id):
    cur = db.connection.cursor()
    cur.execute('DELETE FROM indexssalud WHERE id = {0}'.format(id))
    db.connection.commit()
    flash('Producto eliminado satisfactoriamente')
    return redirect(url_for('indexSalud'))

@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"


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
