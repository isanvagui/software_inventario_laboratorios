from flask import Flask, redirect, url_for
from config import config

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
