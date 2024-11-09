from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()
swagger = Swagger()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SWAGGER'] = {
        'title': 'Flask CRUD API',
        'uiversion': 3,
        'version': '1.0',
        'description': 'A simple Flask CRUD API with JWT authentication',
        'specs_route': '/docs/',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
            }
        },
        'security': [{'Bearer': []}]
    }

    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Import routes after db initialization
    from app.routes.user import user_api
    app.register_blueprint(user_api, url_prefix='/api/user')

    from app.routes.image import image_api
    app.register_blueprint(image_api, url_prefix='/api/image')

    from app.routes.tabular import tabular_api
    app.register_blueprint(tabular_api, url_prefix='/api/tabular')

    from app.routes.text import text_api
    app.register_blueprint(text_api, url_prefix='/api/text')
    return app