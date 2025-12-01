import csv
from io import TextIOWrapper, StringIO, BytesIO

# librerias e importaciones para excel
import io
from flask import request, jsonify, send_file, current_app
from openpyxl import load_workbook
from openpyxl.styles import Alignment
# Importacion del link OneDrive MANTENIEMIENTO desde el archivo config
from config import LinkOneDriveMantenimiento
# Importacion del link OneDrive CALIBRACION desde el archivo config
from config import LinkOneDriveCalibracion

from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_mysqldb import MySQL,MySQLdb
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

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
# Importaciones para el envio de correos en prestamo
from flask_login import current_user
# Importaciones desde el archivo email_service
from email_service import send_email_with_logo
from email_service import send_prestamo_notification_html
# Importaciones desde el archivo email_devolucion
from email_devolucion import send_email_envio_with_logo
from email_devolucion import send_devolucion_notification_html

from extensions import db, csrf, login_manager
from routes import bp

app = Flask(__name__, static_url_path='/inventario-laboratorios/static')
app.config.from_object(config['production'])
app.register_blueprint(bp, url_prefix='/inventario-laboratorios')

# Donde configuro mi clave
app.config['SECRET_KEY'] = 'mysecretkey'
# app.config['UPLOAD_FOLDER'] = 'static/fotos'

# Inicializo las extenciones
csrf.init_app(app)
db.init_app(app)
login_manager.init_app (app)
login_manager.login_view = "inventario.login"

def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

app.register_error_handler(401, status_401)
app.register_error_handler(404, status_404)


if __name__ == '__main__':

    app.run()
