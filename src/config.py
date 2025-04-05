#-------------CONFIGURACION BASE DE DATOS-----------------------
class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'
    # SECRET_KEY = ''

#para puebas
class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'flaskinventario'

#para producción
class ProductionConfig(Config):
    DEBUG = True
    MYSQL_HOST = '10.3.1.110'
    MYSQL_PORT = 3306
    MYSQL_USER = 'dbgestionlab'
    MYSQL_PASSWORD = 'Medellin2025*'
    MYSQL_DB = 'flaskinventario'

    print('ok')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
