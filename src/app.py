import csv
from io import TextIOWrapper, StringIO
import io

from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_mysqldb import MySQL,MySQLdb
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from datetime import datetime, timedelta


# Para subir archivos tipo foto al servidor
import os
import shutil
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
@login_required
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
# @login_required
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
                flash("Contraseña incorrecta...")
                return render_template('auth/login.html')
        else:
            flash("Usuario no encontrado...")
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
    cur = db.connection.cursor()

    # Obtener la fecha actual
    fecha_actual = datetime.now().date()

    # Consultar la cantidad de equipos según el vencimiento del mantenimiento
    cur.execute("""
        SELECT 
            SUM(DATEDIFF(vencimiento_mantenimiento, %s) < 0) AS vencidas,
            SUM(DATEDIFF(vencimiento_mantenimiento, %s) BETWEEN 0 AND 30) AS proximas,
            SUM(DATEDIFF(vencimiento_mantenimiento, %s) BETWEEN 31 AND 90) AS entre_31_y_90,
            SUM(DATEDIFF(vencimiento_mantenimiento, %s) > 90) AS mas_90_dias
        FROM indexssalud WHERE enable = 1 and de_baja = 0
    """, (fecha_actual, fecha_actual, fecha_actual, fecha_actual))

    # Obtener los resultados
    resultados_mantenimiento = cur.fetchone()
    vencidas_mantenimiento = resultados_mantenimiento[0]
    proximas_mantenimiento = resultados_mantenimiento[1]
    entre_31_y_90_mantenimiento = resultados_mantenimiento[2]
    mas_90_dias_mantenimiento = resultados_mantenimiento[3]

    print(resultados_mantenimiento)
   

    # Consultar la cantidad de equipos según el vencimiento de la calibración
    cur.execute("""
        SELECT 
            SUM(DATEDIFF(vencimiento_calibracion, %s) < 0) AS vencidas,
            SUM(DATEDIFF(vencimiento_calibracion, %s) BETWEEN 0 AND 30) AS proximas,
            SUM(DATEDIFF(vencimiento_calibracion, %s) BETWEEN 31 AND 90) AS entre_31_y_90,
            SUM(DATEDIFF(vencimiento_calibracion, %s) > 90) AS mas_90_dias
        FROM indexssalud
        WHERE enable = 1 and de_baja = 0
    """, (fecha_actual, fecha_actual, fecha_actual, fecha_actual))

    # Obtener los resultados del vencimiento de calibración
    resultados_calibracion = cur.fetchone()
    vencidas_calibracion = resultados_calibracion[0]
    proximas_calibracion = resultados_calibracion[1]
    entre_31_y_90_calibracion = resultados_calibracion[2]
    mas_90_dias_calibracion = resultados_calibracion[3]

    return render_template('home.html', vencidas_mantenimiento=vencidas_mantenimiento, 
                                        proximas_mantenimiento=proximas_mantenimiento, 
                                        entre_31_y_90_mantenimiento=entre_31_y_90_mantenimiento, 
                                        mas_90_dias_mantenimiento=mas_90_dias_mantenimiento,
                                        vencidas_calibracion=vencidas_calibracion, 
                                        proximas_calibracion=proximas_calibracion, 
                                        entre_31_y_90_calibracion=entre_31_y_90_calibracion, 
                                        mas_90_dias_calibracion=mas_90_dias_calibracion)


# ---------------------------INICIA MODULO DE GASTRONOMIA-----------------------------
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

        flash('Producto agregado satisfactoriamente', 'success')
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

# --------------------------------------------- DATOS PROVEEDOR SALUD --------------------------------
@app.route('/datosProveedorSalud/<id>')
def datosProveedorSalud(id):
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur = db.connection.cursor()
    cur.execute('SELECT * FROM datosproveedorsalud WHERE id = %s', [id])
    proveedor = cur.fetchall()
    print (proveedor)
    return render_template('datosProveedorSalud.html', datosproveedorsalud=proveedor)

# FUNCIÓN ACTUALIZAR DATOS PROVEEDOR
@app.route('/update_datos_proveedor_salud/<id>', methods = ['POST'])
def ACTUALIZAR_DATOS_PROVEEDOR_SALUD(id):
    if request.method =='POST':
        telefono_empresa = request.form ['telefono_empresa']
        nombre_empresa = request.form ['nombre_empresa']
        nombre_contacto = request.form ['nombre_contacto']
        correo = request.form ['correo']
        cargo_contacto = request.form ['cargo_contacto']
        ciudad = request.form ['ciudad']
        cur = db.connection.cursor() 
        cur.execute(""" UPDATE datosproveedorsalud SET telefono_empresa = %s, nombre_empresa = %s, nombre_contacto = %s, correo = %s, cargo_contacto = %s, ciudad = %s WHERE id = %s """, 
                                                      (telefono_empresa, nombre_empresa, nombre_contacto, correo, cargo_contacto, ciudad, id))
        db.connection.commit()
    flash('Datos actualizados satisfactorimanete', 'success')
    return redirect(url_for('datosProveedorSalud', id = id))
    # return redirect(url_for('datosProveedorSalud')) 

# ESTA FUNCIÓN ME LLEVA A OTRA VISTA PARA AGREGAR LOS NUEVOS PROVEEDORES
@app.route('/agregarNuevoProveedor')
def agregarNuevoProveedor():
    return render_template('agregarNuevoProveedor.html')

@app.route('/add_datos_proveedor_salud', methods=['POST'])
def AGREGAR_DATOS_PROVEEDOR_SALUD():
    if request.method =='POST':
        telefono_empresa = request.form ['telefono_empresa']
        nombre_empresa = request.form ['nombre_empresa']
        nombre_contacto = request.form ['nombre_contacto']
        correo = request.form ['correo']
        cargo_contacto = request.form ['cargo_contacto']
        ciudad = request.form ['ciudad']

         # Valida que todos los campos estén diligenciados
        if not telefono_empresa or not nombre_empresa or not nombre_contacto or not ciudad:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('agregarNuevoProveedor'))
        
        cur = db.connection.cursor() 
        cur.execute('INSERT INTO datosproveedorsalud (telefono_empresa, nombre_empresa, nombre_contacto, correo, cargo_contacto, ciudad) VALUES (%s, %s, %s, %s, %s, %s)', 
                                                     (telefono_empresa, nombre_empresa, nombre_contacto, correo, cargo_contacto, ciudad))
        db.connection.commit()
    flash ('Datos agregados satisfactoriamente', 'success')
    return redirect(url_for('agregarNuevoProveedor')) 

# --------------------------- INICIA MODULO DE SALUD-----------------------------
@app.route('/indexSalud')
@login_required
def indexSalud():
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur = db.connection.cursor()
    cur.execute('SELECT * FROM indexssalud where enable=1 AND de_baja=0') #A raiz del enable=1 no se deben eliminar en la DB
    data = cur.fetchall()

    cur.execute('SELECT id, nombre_empresa FROM datosproveedorsalud')
    proveedores = cur.fetchall()

    cur.execute('SELECT id, estado_equipo FROM estados_equipos')
    estadoEquipos = cur.fetchall()

    cur.execute('SELECT id, ubicacion_original FROM ubicacion_equipos')
    ubicacionEquipos = cur.fetchall()
    # print(ubicacionEquipos)
    return render_template('indexSalud.html', indexssalud=data, proveedores=proveedores, estadoEquipos=estadoEquipos, ubicacionEquipos=ubicacionEquipos)

@app.route('/add_productoSalud', methods=['POST'])
def AGREGAR_PRODUCTO_SALUD():
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        # Validación de cod_articulo
        try:
            cod_articulo = int(cod_articulo)
        except ValueError:
            flash('Por favor ingresar solo números en el código del articulo', 'error')
            return redirect(url_for('indexSalud'))

        # Consulta para verificar si el cod_articulo ya existe en la base de datos
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM indexssalud WHERE cod_articulo = %s", (cod_articulo,))
        existing_articulo = cur.fetchone()

        if existing_articulo:
            flash(f'El código de artículo {cod_articulo} ya existe', 'error')
            return redirect(url_for('indexSalud'))

        # Obtener hora actual del equipo
        hora_actual = datetime.now()

        # PARA EL CHECKBOX Y SEMAFORO DE MANTENIMIENTO
        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

        # checkbox_mantenimiento = 'Inactivo' # Valor predeterminado

        if fecha_mantenimiento and vencimiento_mantenimiento:
            fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d')
            vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y-%m-%d')

            if hora_actual > vencimiento_mantenimiento:
                color = 'purple'  # Vencido
                # checkbox_mantenimiento = 'Inactivo'
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=30):
                color = 'red'  # Falta menos de un mes
                # checkbox_mantenimiento = 'Inactivo'
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=90):
                color = 'yellow'  # Falta menos de tres meses
                # checkbox_mantenimiento = 'Activo'
            else:
                color = 'green'  # Vigente
                # checkbox_mantenimiento = 'Activo'
        else:
            flash('Debe ingresar las fechas de inicio y vencimiento de mantenimiento.', 'error')
            return redirect(url_for('indexSalud'))

        # PARA EL CHECKBOX DE CALIBRACIÓN
        fecha_calibracion = request.form ['fecha_calibracion']
        vencimiento_calibracion = request.form ['vencimiento_calibracion']

        # checkbox_calibracion = 'Inactivo' # Valor predeterminado

        if fecha_calibracion and vencimiento_calibracion:
            fecha_calibracion = datetime.strptime(fecha_calibracion, '%Y-%m-%d')
            vencimiento_calibracion = datetime.strptime(vencimiento_calibracion, '%Y-%m-%d')
            # if vencimiento_calibracion <= hora_actual + timedelta(days=30):
            #     checkbox_calibracion = 'Inactivo'
            # else:
            #     checkbox_calibracion = 'Activo'
        # else:
        #     flash('Debe ingresar las fechas de inicio y vencimiento de calibración.', 'error')
            return redirect(url_for('indexSalud'))

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
            flash('Por favor seleccione el archivo')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath_to_db = os.path.join(app.config['UPLOAD_FOLDER'].split('/')[-1], filename) #Esta ruta guarda la imagen en la BD 
            filepath_to_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filepath_to_db = filepath_to_db.replace("\\", "/")
            file.save(filepath_to_save)
        especificaciones_instalacion = request.form ['especificaciones_instalacion']
        cuidados_basicos = request.form ['cuidados_basicos']
        periodicidad_calibracion = request.form ['periodicidad_calibracion']
        marca_equipo_salud = request.form ['marca_equipo_salud']
        modelo_equipo_salud = request.form ['modelo_equipo_salud']
        serial_equipo_salud = request.form ['serial_equipo_salud']

        # cur = db.connection.cursor()
        if estado_equipo == "DE BAJA":
            # Guardar en la tabla de equipos de baja
            cur.execute(
                "INSERT INTO equipossalud_debaja (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, color, imagen, especificaciones_instalacion, cuidados_basicos, periodicidad_calibracion,  marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    cod_articulo,
                    nombre_equipo,
                    fecha_mantenimiento,
                    vencimiento_mantenimiento,
                    fecha_calibracion,
                    vencimiento_calibracion,
                    fecha_ingreso,
                    periodicidad,
                    estado_equipo,
                    ubicacion_original,
                    garantia,
                    criticos,
                    proveedor_responsable,
                    color,
                    # checkbox_mantenimiento,
                    # checkbox_calibracion,
                    filepath_to_db,
                    especificaciones_instalacion,
                    cuidados_basicos,
                    periodicidad_calibracion,
                    marca_equipo_salud,
                    modelo_equipo_salud,
                    serial_equipo_salud
                ),
            )
        else:   
            cur.execute(
                "INSERT INTO indexssalud (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, color, imagen, especificaciones_instalacion, cuidados_basicos, periodicidad_calibracion, marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud) VALUES (  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    cod_articulo,
                    nombre_equipo,
                    fecha_mantenimiento,
                    vencimiento_mantenimiento,
                    fecha_calibracion,
                    vencimiento_calibracion,
                    fecha_ingreso,
                    periodicidad,
                    estado_equipo,
                    ubicacion_original,
                    garantia,
                    criticos,
                    proveedor_responsable,
                    color,
                    # checkbox_mantenimiento,
                    # checkbox_calibracion,
                    filepath_to_db,
                    especificaciones_instalacion,
                    cuidados_basicos,
                    periodicidad_calibracion,
                    marca_equipo_salud,
                    modelo_equipo_salud,
                    serial_equipo_salud
                    
                ),
            )
        db.connection.commit()
        # print(estado_equipo)

        # Solo inserta en el historial si hubo cambios en las fechas de matenimiento y calibración
        cur.execute("""INSERT INTO historial_fechas (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion) VALUES ( %s, %s, %s, %s, %s, %s, %s)""", 
                                                    (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion))
        db.connection.commit()

        flash ('Equipo agregado satisfactoriamente', 'success')
        return redirect(url_for('indexSalud')) 

# ---------------------------INICIA INSERT MASIVO DE EQUIPOS CSV DE SALUD-----------------------------
@app.route('/insert_csv', methods=['POST'])
def insert_csv():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash('No selecciono ningun archivo')
            return redirect(url_for('indexSalud'))

        # Decodifica la fila
        file = TextIOWrapper(file, encoding='latin-1')
        csv_reader = csv.reader(file)

        # Salta el encabezado
        next(csv_reader)

        # Procesa las filas
        cur = db.connection.cursor()

        # Definir la carpeta de destino para las imágenes 
        fotos_folder = os.path.join(os.getcwd(), 'src', 'static', 'fotos')
        
        for row in csv_reader:
            cod_articulo = row[0]
            nombre_equipo = row[1] 
            fecha_mantenimiento = row[2]
            vencimiento_mantenimiento = row[3] 
            fecha_calibracion = row[4] if row[4] else None
            vencimiento_calibracion = row[5] if row[5] else None
            fecha_ingreso = row[6] 
            periodicidad = row[7] 
            periodicidad_calibracion = row[8]
            estado_equipo = row[9] 
            ubicacion_original = row[10] 
            garantia = row[11] 
            criticos = row[12] 
            proveedor_responsable = row[13] 
            imagen = row[14]
            especificaciones_instalacion = row[15] 
            cuidados_basicos = row[16] 
            marca_equipo_salud = row[17]
            modelo_equipo_salud = row[18]
            serial_equipo_salud = row[19]

            # Validación de cod_articulo
            try:
                cod_articulo = int(cod_articulo)
            except ValueError:
                flash('Por favor ingresar solo números en el código del articulo', 'error')
                return redirect(url_for('indexSalud'))
            
            # Consulta para verificar si el cod_articulo ya existe en la base de datos
            cur = db.connection.cursor()
            cur.execute("SELECT * FROM indexssalud WHERE cod_articulo = %s", (cod_articulo,))
            existing_articulo = cur.fetchone()

            if existing_articulo:
                flash(f'El código de artículo {cod_articulo} ya existe', 'error')
                return redirect(url_for('indexSalud'))
            
            # Obtener la ruta de la imagen desde Descargas
            imagen_descargas_path = os.path.join(os.path.expanduser('~'), 'C:/Users/1058912992/Pictures', imagen)
            # Verificar si el archivo existe en Descargas
            if not os.path.isfile(imagen_descargas_path):
                flash(f'La imagen {imagen} no se encontró en la carpeta de descargas.', 'error')
                return redirect(url_for('indexSalud'))

            # Mover la imagen a la carpeta de fotos en el proyecto
            nombre_imagen_seguro = secure_filename(imagen)
            imagen_destino_path = os.path.join(fotos_folder, nombre_imagen_seguro)

            try:
                shutil.copy(imagen_descargas_path, imagen_destino_path)
            except Exception as e:
                flash(f'Error al mover la imagen {imagen}: {e}', 'error')
                return redirect(url_for('indexSalud'))

            # Definir la ruta relativa para guardar en la base de datos
            ruta_imagen_db = f'fotos/{nombre_imagen_seguro}'

            # Obtener hora actual del equipo
            hora_actual = datetime.now()
            # Analiza las fechas en formato YYYY/MM/DD
            if fecha_mantenimiento:
                fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y/%m/%d')
            if vencimiento_mantenimiento:
                vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y/%m/%d')

                # PARA EL CHECKBOX Y SEMAFORO DE MANTENIMIENTO
                if hora_actual > vencimiento_mantenimiento:
                    color = 'purple'  # Vencido
                    # checkbox_mantenimiento = 'Inactivo'
                elif vencimiento_mantenimiento <= hora_actual + timedelta(days=30):
                    color = 'red'  # Falta menos de un mes
                    # checkbox_mantenimiento = 'Inactivo'
                elif vencimiento_mantenimiento <= hora_actual + timedelta(days=90):
                    color = 'yellow'  # Falta menos de tres meses
                    # checkbox_mantenimiento = 'Activo'
                else:
                    color = 'green'  # Vigente
                    # checkbox_mantenimiento = 'Activo'
            else:
                flash('Debe ingresar las fechas de inicio y vencimiento de mantenimiento.', 'error')
                return redirect(url_for('indexSalud'))
            
            # if fecha_calibracion:
            #     fecha_calibracion = datetime.strptime(fecha_calibracion, '%Y/%m/%d') if fecha_calibracion else None
            # if vencimiento_calibracion:
            #     vencimiento_calibracion = datetime.strptime(vencimiento_calibracion, '%Y/%m/%d') if vencimiento_calibracion else None

            # PARA EL CHECKBOX Y SEMAFORO DE CALIBRACIÓN
            # checkbox_calibracion = 'Inactivo' # Valor predeterminado
            # if fecha_calibracion and vencimiento_calibracion:

                # if vencimiento_calibracion <= hora_actual + timedelta(days=30):
                #     checkbox_calibracion = 'Inactivo'
                # else:
                #     checkbox_calibracion = 'Activo'
            # else:
                # flash('Debe ingresar las fechas de inicio y vencimiento de calibración.', 'error')
                # return redirect(url_for('indexSalud'))

            if estado_equipo == 'DE BAJA':

                # Insertar en la tabla equipossalud_debaja
                cur.execute("INSERT INTO equipossalud_debaja (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, imagen, especificaciones_instalacion, cuidados_basicos, periodicidad_calibracion, marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        cod_articulo,
                        nombre_equipo,
                        fecha_mantenimiento,
                        vencimiento_mantenimiento,
                        fecha_calibracion,
                        vencimiento_calibracion,
                        fecha_ingreso,
                        periodicidad,
                        estado_equipo,
                        ubicacion_original,
                        garantia,
                        criticos,
                        proveedor_responsable,
                        ruta_imagen_db,
                        especificaciones_instalacion, 
                        cuidados_basicos,
                        periodicidad_calibracion,
                        marca_equipo_salud,
                        modelo_equipo_salud,
                        serial_equipo_salud,
                        color,
                        # checkbox_mantenimiento,
                        # checkbox_calibracion,
                    ),
                )
            else:

                # Insertar en la tabla indexssalud
                cur.execute("INSERT INTO indexssalud (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, imagen, especificaciones_instalacion, cuidados_basicos, periodicidad_calibracion, marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        cod_articulo,
                        nombre_equipo,
                        fecha_mantenimiento,
                        vencimiento_mantenimiento,
                        fecha_calibracion,  
                        vencimiento_calibracion,  
                        fecha_ingreso,
                        periodicidad,
                        estado_equipo,
                        ubicacion_original,
                        garantia,
                        criticos,
                        proveedor_responsable,
                        ruta_imagen_db,
                        especificaciones_instalacion, 
                        cuidados_basicos,
                        periodicidad_calibracion,
                        marca_equipo_salud,
                        modelo_equipo_salud,
                        serial_equipo_salud,
                        color,
                        # checkbox_mantenimiento,
                        # checkbox_calibracion,
                    ),
                )

            # Solo inserta en el historial si hubo cambios en las fechas de matenimiento y calibración
            cur.execute("""INSERT INTO historial_fechas (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion) VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                                                        (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion))
            db.connection.commit()

        db.connection.commit()
        flash('Datos insertados exitosamente', 'success')
        return redirect(url_for('indexSalud'))
# ---------------------------FINALIZA INSERT MASIVA CSV DE SALUD-----------------------------

# ---------------------------INICIA ACTUALIZACIÓN MASIVA DE FECHAS DE MANTENIMIENTO, CALIBRACIÓN Y PERIODICIDAD EQUIPOS CSV DE SALUD-----------------------------
@app.route('/updateDate_csv', methods=['POST'])
def updateDate_csv():
    if request.method == 'POST':
        file = request.files['file']

        if not file:
            flash('No selecciono ningun archivo')
            return redirect(url_for('indexSalud'))
        
        # Decodifica la fila
        file = TextIOWrapper(file, encoding='latin-1')
        csv_reader = csv.reader(file)
        
        # Salta el encabezado
        next(csv_reader)
        
        # Leer cada fila y actualizar las fechas
        for row in csv_reader:
            cod_articulo = row[0]
            fecha_mantenimiento = datetime.strptime(row[1], '%Y/%m/%d')
            vencimiento_mantenimiento = datetime.strptime(row[2], '%Y/%m/%d')
            fecha_calibracion = datetime.strptime(row[3], '%Y/%m/%d') if row[3] else None
            vencimiento_calibracion = datetime.strptime(row[4], '%Y/%m/%d') if row[4] else None
            periodicidad = row[5]
            periodicidad_calibracion = row[6] if row[6] else 0

            # Verificar si el cod_articulo existe en la tabla indexssalud y obtiene las fechas actuales antes de actualizar
            cur = db.connection.cursor()
            cur.execute('SELECT fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion FROM indexssalud WHERE cod_articulo = %s', [cod_articulo])
            producto = cur.fetchone()

            if not producto:
                # Si el cod_articulo no existe
                flash(f'El artículo con código {cod_articulo} no existe', 'error')
                continue  # Saltar a la siguiente fila del archivo

            # Extraer las fechas actuales
            fecha_mantenimiento_actual = producto[0]
            vencimiento_mantenimiento_actual = producto[1]
            fecha_calibracion_actual = producto[2]
            vencimiento_calibracion_actual = producto[3]

            # Verificar si alguna de las fechas ingresadas es diferente de las almacenadas
            if (fecha_mantenimiento.date() != fecha_mantenimiento_actual or 
                vencimiento_mantenimiento.date() != vencimiento_mantenimiento_actual or 
                fecha_calibracion != fecha_calibracion_actual or 
                vencimiento_calibracion != vencimiento_calibracion_actual):

                # Actualizar las fechas en la tabla indexssalud
                cur = db.connection.cursor()
                cur.execute("""UPDATE indexssalud SET fecha_mantenimiento = %s, vencimiento_mantenimiento = %s, fecha_calibracion = %s, vencimiento_calibracion = %s, periodicidad = %s, periodicidad_calibracion = %s WHERE cod_articulo = %s""",
                                                     (fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion, cod_articulo))
                db.connection.commit()
        
                # Solo inserta en el historial si hubo cambios en las fechas de matenimiento y calibración
                cur.execute("""INSERT INTO historial_fechas (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion) VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                                                            (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion))
                db.connection.commit()

                # Obtener hora actual del equipo
                hora_actual = datetime.now()
                
                # PARA EL CHECKBOX DE CALIBRACIÓN
                # checkbox_mantenimiento = 'Inactivo' # Valor predeterminado

                
                if hora_actual > vencimiento_mantenimiento:
                    color = 'purple'  # Vencido
                    # checkbox_mantenimiento = 'Inactivo'
                elif vencimiento_mantenimiento <= hora_actual + timedelta(days=30):
                    color = 'red'  # Falta menos de un mes
                    # checkbox_mantenimiento = 'Inactivo'
                elif vencimiento_mantenimiento <= hora_actual + timedelta(days=90):
                    color = 'yellow'  # Falta menos de tres meses
                    # checkbox_mantenimiento = 'Activo'
                else:
                    color = 'green'  # Vigente
                    # checkbox_mantenimiento = 'Activo' 
                
                # PARA EL CHECKBOX DE CALIBRACIÓN
                # checkbox_calibracion = 'Inactivo' # Valor predeterminado

                
                # if vencimiento_calibracion <= hora_actual + timedelta(days=30):
                #     checkbox_calibracion = 'Inactivo'
                # else:
                #     checkbox_calibracion = 'Activo'

                # Actualizar el color y los checkboxes en la tabla indexssalud
                cur.execute(""" UPDATE indexssalud SET color = %s WHERE cod_articulo = %s""", 
                                                      (color, cod_articulo))
                db.connection.commit()

            else:
                flash(f'Las fechas para el artículo {cod_articulo} no han cambiado', 'info')

        flash('Fechas actualizadas con éxito', 'success')
        return redirect(url_for('indexSalud'))
# ---------------------------FINALIZA ACTUALIZACIÓN MASIVA DE FECHAS CSV DE SALUD-----------------------------

# ---------------------------INICIA EXPORTACIÓN DE CSV DE EQUIPOS DE SALUD-----------------------------
@app.route('/exportCsvsalud')
def exportCsv():
    # Obtener los datos de la tabla indexssalud
    cur = db.connection.cursor()
    cur.execute('SELECT cod_articulo, nombre_equipo, periodicidad, fecha_mantenimiento, vencimiento_mantenimiento, periodicidad_calibracion, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, checkbox_mantenimiento, checkbox_calibracion, especificaciones_instalacion, cuidados_basicos, marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud FROM indexssalud WHERE enable = 1')
    registros = cur.fetchall()

    # Crear un archivo CSV en memoria
    si = StringIO()
    writer = csv.writer(si)

    # Escribir los encabezados de las columnas
    writer.writerow(['Código articulo', 'Nombre Equipo', 'Periodicidad Mantenimiento', 'Inicio Mantenimiento', 'Vencimiento Mantenimiento', 'Periodicidad Calibración', 'Inicio Calibración', 'Vencimiento Calibración', 'Fecha Ingreso', 
                      'Estado Equipo', 'Ubicación Original', 'Garantía', 'Críticos', 'Proveedor Responsable', 'Check Mantenimiento', 'Check Calibración', 'Especificaciones Instalación', 'Cuidados Básicos', ' Marca Equipo', 'Modelo Equipo', 'Serial Equipo'])

    # Escribir los registros de la tabla
    for registro in registros:
        writer.writerow(registro)

    # Preparar el archivo CSV para su descarga
    salida = Response(si.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    salida.headers['Content-Disposition'] = 'attachment; filename=equiposSalud.csv'

    return salida
# ---------------------------FINALIZA EXPORTACIÓN DE CSV DE EQUIPOS DE SALUD-----------------------------

# ---------------------------INICIA EXPORTACIÓN DE CSV DE EQUIPOS DE BAJA DE SALUD-----------------------------
@app.route('/exportCsvSaludDeBaja')
def exportCsvDeBaja():
    # Obtener los datos de la tabla indexssalud
    cur = db.connection.cursor()
    cur.execute('SELECT cod_articulo, nombre_equipo, periodicidad, fecha_mantenimiento, vencimiento_mantenimiento, periodicidad_calibracion, fecha_calibracion, vencimiento_calibracion, fecha_ingreso, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, checkbox_mantenimiento, checkbox_calibracion, especificaciones_instalacion, cuidados_basicos, marca_equipo_salud, modelo_equipo_salud, serial_equipo_salud FROM equipossalud_debaja')
    registros = cur.fetchall()

    # Crear un archivo CSV en memoria
    si = StringIO()
    writer = csv.writer(si)

    # Escribir los encabezados de las columnas
    writer.writerow(['Código articulo', 'Nombre Equipo', 'Periodicidad Mantenimiento', 'Inicio Mantenimiento', 'Vencimiento Mantenimiento', 'Periodicidad Calibración', 'Inicio Calibración', 'Vencimiento Calibración', 'Fecha Ingreso', 
                     'Estado Equipo', 'Ubicación Original', 'Garantía', 'Críticos', 'Proveedor Responsable', 'Check Mantenimiento', 'Check Calibración', 'Especificaciones Instalación', 'Cuidados Básicos', ' Marca Equipo', 'Modelo Equipo', 'Serial Equipo'])

    # Escribir los registros de la tabla
    for registro in registros:
        writer.writerow(registro)

    # Preparar el archivo CSV para su descarga
    salida = Response(si.getvalue().encode('utf-8-sig'), mimetype='text/csv')
    salida.headers['Content-Disposition'] = 'attachment; filename=equiposSaludDeBaja.csv'

    return salida
# ---------------------------FINALIZA EXPORTACIÓN DE CSV DE EQUIPOS DE EQUIPOS DE BAJA DE SALUD-----------------------------

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

        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        # Obtener hora actual del equipo
        hora_actual = datetime.now()

        # PARA EL CHECKBOX Y SEMAFORO DE MANTENIMIENTO
        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

        if fecha_mantenimiento and vencimiento_mantenimiento:
            fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d')
            vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y-%m-%d')

            if hora_actual > vencimiento_mantenimiento:
                color = 'purple'  # Vencido
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=30):
                color = 'red'  # Falta menos de un mes
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=90):
                color = 'yellow'  # Falta menos de tres meses
            else:
                color = 'green'  # Vigente
        else:
            flash('Debe ingresar las fechas de inicio y vencimiento de mantenimiento.', 'error')
            return redirect(url_for('indexSalud'))

        # PARA EL CHECKBOX DE CALIBRACIÓN
        fecha_calibracion = request.form ['fecha_calibracion']
        vencimiento_calibracion = request.form ['vencimiento_calibracion']

        # if fecha_calibracion and vencimiento_calibracion:
        #     fecha_calibracion = datetime.strptime(fecha_calibracion, '%Y/%m/%d')
        #     vencimiento_calibracion = datetime.strptime(vencimiento_calibracion, '%Y/%m/%d')

        # else:
        #     flash('Debe ingresar las fechas de inicio y vencimiento de calibración.', 'error')
        #     return redirect(url_for('indexSalud'))

        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']
        estado_equipo = request.form ['estado_equipo']
        ubicacion_original = request.form ['ubicacion_original']
        garantia = request.form ['garantia']
        criticos = request.form ['criticos']
        proveedor_responsable = request.form ['proveedor_responsable']
        # especificaiones_instalacion = request.form ['especificaiones_instalacion']
        periodicidad_calibracion = request.form ['periodicidad_calibracion']

        cur = db.connection.cursor()

        # Obtener la ruta de la imagen desde la tabla indexssalud
        cur.execute('SELECT imagen FROM indexssalud WHERE cod_articulo = %s', (cod_articulo,))
        imagen_result = cur.fetchone()
        filepath_to_db = imagen_result[0] if imagen_result else None

        if nuevo_estado == 'DE BAJA':
            # Actualizar el estado y marcar como dado de baja en indexssalud
            cur.execute(
                """UPDATE indexssalud 
                   SET estado_equipo = %s, enable = 0 and de_baja = 1 
                   WHERE cod_articulo = %s""", 
                (nuevo_estado, cod_articulo)
            )

            # Verificar si el equipo ya está en equipossalud_debaja
            cur.execute('SELECT * FROM equipossalud_debaja WHERE cod_articulo = %s', (cod_articulo,))
            equipo_existente = cur.fetchone()

            # Insertar el equipo en equipossalud_debaja si no existe
            if not equipo_existente:
                cur.execute(
                    """INSERT INTO equipossalud_debaja 
                    (cod_articulo, nombre_equipo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, fecha_ingreso,
                    periodicidad, estado_equipo, ubicacion_original, garantia, criticos, proveedor_responsable, color, imagen, periodicidad_calibracion) 
                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        cod_articulo,
                        nombre_equipo,
                        fecha_mantenimiento,
                        vencimiento_mantenimiento,
                        fecha_calibracion,
                        vencimiento_calibracion,
                        fecha_ingreso,
                        periodicidad,
                        nuevo_estado,  # Estado del equipo
                        ubicacion_original,
                        garantia,
                        criticos,
                        proveedor_responsable,
                        color,
                        filepath_to_db,
                        # especificaiones_instalacion,
                        periodicidad_calibracion
                    ),
                )
        
        else:
            # Actualiza el estado si no está dado de baja
            cur.execute('UPDATE indexssalud SET estado_equipo = %s WHERE cod_articulo = %s', (nuevo_estado, cod_articulo))

        db.connection.commit()
        flash('Estado del equipo actualizado correctamente', 'success')
        return redirect(url_for('indexSalud'))


# ESTA FUNCIÓN ME LLEVA A OTRA VISTA TRAYENDO LOS PARAMETROS DE AGREGAR PARA DESPUES PODER ACTUALIZAR EN LA SIGUIENTE FUNCIÓN. LAS DOS SE COMPLEMENTAN
@app.route('/edit_productoSalud/<id>/<vista>', methods=['GET'])
@login_required
def GET_PRODUCTO_SALUD(id, vista):
    cur = db.connection.cursor()

    # Verificar de qué vista proviene la solicitud para seleccionar la tabla correcta
    if vista == 'indexSalud':
        cur.execute('SELECT * FROM indexssalud WHERE id = %s', [id])
    elif vista == 'equiposDeBajaSalud':
        cur.execute('SELECT * FROM equipossalud_debaja WHERE id = %s', [id])

    data = cur.fetchall()

    if data:
        cod_articulo = data[0][1]
    print(cod_articulo)    
    # Obtener el historial de fechas del equipo
    cur.execute("""SELECT * FROM historial_fechas WHERE cod_articulo = %s ORDER BY fecha_mantenimiento DESC""", [cod_articulo])
    fechas = cur.fetchall()
    # print (fechas)
    return render_template('editar_producto_indexSalud.html', producto = data[0], historial = cod_articulo)


# FUNCIÓN ACTUALIZAR EDITAR/VER HOJA DE VIDA
@app.route('/actualizarSalud/<id>', methods = ['POST'])
def ACTUALIZAR_PRODUCTO_SALUD(id):
    if request.method =='POST':
        cod_articulo = request.form ['cod_articulo']
        nombre_equipo = request.form ['nombre_equipo']

        # Obtener hora actual del equipo
        hora_actual = datetime.now()

        fecha_mantenimiento = request.form ['fecha_mantenimiento']
        vencimiento_mantenimiento = request.form ['vencimiento_mantenimiento']

        # checkbox_mantenimiento = 'Inactivo' # Valor predeterminado

        if fecha_mantenimiento and vencimiento_mantenimiento:
            fecha_mantenimiento = datetime.strptime(fecha_mantenimiento, '%Y-%m-%d')
            vencimiento_mantenimiento = datetime.strptime(vencimiento_mantenimiento, '%Y-%m-%d')

            if hora_actual > vencimiento_mantenimiento:
                color = 'purple'  # Vencido
                # checkbox_mantenimiento = 'Inactivo'
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=30):
                color = 'red'  # Falta menos de un mes
                # checkbox_mantenimiento = 'Inactivo'
            elif vencimiento_mantenimiento <= hora_actual + timedelta(days=90):
                color = 'yellow'  # Falta menos de tres meses
                # checkbox_mantenimiento = 'Activo'
            else:
                color = 'green'  # Vigente
                # checkbox_mantenimiento = 'Activo'
        else:
            flash('Debe ingresar las fechas de inicio y vencimiento de mantenimiento.', 'error')
            return redirect(url_for('indexSalud'))

        fecha_calibracion = request.form ['fecha_calibracion']
        vencimiento_calibracion = request.form ['vencimiento_calibracion']
        fecha_ingreso = request.form ['fecha_ingreso']
        periodicidad = request.form ['periodicidad']
        periodicidad_calibracion = request.form ['periodicidad_calibracion']
        # estado_equipo = request.form ['estado_equipo']
        # ubicacion_original = request.form ['ubicacion_original']
        garantia = request.form ['garantia']
        # criticos = request.form ['criticos']
        # proveedor_responsable = request.form ['proveedor_responsable']

        especificaciones_instalacion = request.form ['especificaciones_instalacion']
        cuidados_basicos = request.form ['cuidados_basicos']
        
        cur = db.connection.cursor() 

        # Obtener las fechas actuales antes de actualizar
        cur.execute('SELECT fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion FROM indexssalud WHERE id = %s', [id])
        fechas_actuales = cur.fetchone()

        fecha_mantenimiento_actual = fechas_actuales[0]
        vencimiento_mantenimiento_actual = fechas_actuales[1]
        fecha_calibracion_actual = fechas_actuales[2]
        vencimiento_calibracion_actual = fechas_actuales[3]

        cur.execute(
            """ UPDATE indexssalud SET cod_articulo = %s, nombre_equipo = %s, fecha_mantenimiento = %s, vencimiento_mantenimiento = %s, fecha_calibracion = %s, vencimiento_calibracion = %s, fecha_ingreso = %s, periodicidad = %s, garantia = %s, color = %s, especificaciones_instalacion = %s, cuidados_basicos = %s, periodicidad_calibracion = %s WHERE id = %s""",
            (
                cod_articulo,
                nombre_equipo,
                fecha_mantenimiento,
                vencimiento_mantenimiento,
                fecha_calibracion,
                vencimiento_calibracion,
                fecha_ingreso,
                periodicidad,
                garantia,
                color,
                especificaciones_instalacion,
                cuidados_basicos,
                periodicidad_calibracion,
                id,
            ),
        )
        db.connection.commit()

        # Verificar si alguna de las fechas ingresadas es diferente de las almacenadas
        if (fecha_mantenimiento.date() != fecha_mantenimiento_actual or 
            vencimiento_mantenimiento.date() != vencimiento_mantenimiento_actual or 
            fecha_calibracion != fecha_calibracion_actual or 
            vencimiento_calibracion != vencimiento_calibracion_actual):

            # Solo inserta en el historial si hubo cambios en las fechas de matenimiento y calibración
            cur.execute("""INSERT INTO historial_fechas (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion) VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                                                        (cod_articulo, fecha_mantenimiento, vencimiento_mantenimiento, fecha_calibracion, vencimiento_calibracion, periodicidad, periodicidad_calibracion))
            db.connection.commit()

        flash('Producto actualizado satisfactorimanete', 'success')
        return redirect(url_for('indexSalud')) 

# HISTORIAL FECHAS MANTENIMIENTO Y CALIBRACIÓN
@app.route('/historialFechas/<cod_articulo>')
def historialFechas(cod_articulo):
    # print(cod_articulo)
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""SELECT * FROM historial_fechas WHERE cod_articulo = %s ORDER BY fecha_mantenimiento DESC""", [cod_articulo])
    historial = cur.fetchall()
    print(historial)
    return render_template('historialFechas.html', historial=historial)

# ==========================INICIA FUNCIÓN EQUIPOS DADOS DE BAJA=====================
@app.route('/equiposDeBajaSalud')
def equiposDeBajaSalud():
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT id, estado_equipo FROM estados_equipos')
    estadoEquipos = cur.fetchall()
    
    cur.execute('SELECT * FROM equipossalud_debaja')
    equipos_de_baja = cur.fetchall()
    return render_template('equiposDeBajaSalud.html', equipos_de_baja=equipos_de_baja, estadoEquipos=estadoEquipos)
# ==========================FINALIZA FUNCIÓN EQUIPOS DADOS DE BAJA=====================


# FUNCIÓN ELIMINAR
@app.route('/delete_productoSalud/<string:id>')
def ELIMINAR_CONTACTO_SALUD(id):
    cur = db.connection.cursor()
    # cur.execute('DELETE FROM indexssalud WHERE id = {0}'.format(id))
    cur.execute('UPDATE indexssalud SET enable=0 WHERE id = {0}'.format(id)) #Esta linea de codigo en la vista elimina el producto pero no de la DB, la cual realiza es una actualización
    db.connection.commit()
    flash('Producto eliminado satisfactoriamente', 'success')
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
    # app.run(host='0.0.0.0',port=8080)
    app.run()
