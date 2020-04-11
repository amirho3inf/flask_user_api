from flask import Flask
from config import Config
from importlib import import_module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt_manager = JWTManager(app)
import_module('models')
migrate = Migrate(app, db)
import_module('routes')


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
