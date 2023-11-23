# config.py
class Config:
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    JWT_SECRET_KEY = 'aisecretpasswordstg'


class ProductionConfig(Config):
    DEBUG = False
    JWT_SECRET_KEY = 'aisecretpasswordprod'
