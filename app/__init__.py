from flask import Flask
from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    # Initialize the app with MongoDB
    mongo.init_app(app)

    # Import and initialize routes
    from app.routes import init_routes
    init_routes(app)

    return app
