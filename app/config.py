from datetime import timedelta
import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_path, "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'loRX-E9-7uCwAnjO0ytAvuNRHWLiGHI3H9INu_PjoMo'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)