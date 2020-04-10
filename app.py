from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
import models  # nopep8
migrate = Migrate(app, db)
import routes  # nopep8


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
