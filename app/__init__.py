from flask import Flask
from .models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    print(app.config["SQLALCHEMY_DATABASE_URI"])  # هنا صحيح

    db.init_app(app)

    from .routes.tasks import tasks
    from .routes.auth import auth

    app.register_blueprint(tasks)
    app.register_blueprint(auth)

    return app