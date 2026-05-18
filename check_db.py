from app import create_app
from app.models import db, User, Task
import os

app = create_app()

with app.app_context():
    print("DATABASE PATH:", db.engine.url)

    db.drop_all()
    db.create_all()

    print("TABLES:", db.metadata.tables.keys())
    print("DONE")