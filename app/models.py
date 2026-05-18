from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    bio = db.Column(db.Text)
    category = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    price = db.Column(db.Float)
    image = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    status = db.Column(db.String(20), default="open")

    worker = db.relationship("User", foreign_keys=[worker_id])
    review = db.relationship("Review", backref="task", uselist=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id')
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    text = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )