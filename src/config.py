#-------------CONFIGURACION BASE DE DATOS-----------------------
class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'
    # SECRET_KEY = ''


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'flaskinventario'


config = {
    'development': DevelopmentConfig
}
