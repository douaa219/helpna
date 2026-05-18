from flask import Blueprint, render_template, request, redirect, session, jsonify
import os

from werkzeug.utils import secure_filename

from app.models import (
    db,
    Task,
    User,
    Review,
    Notification,
    Message
)

tasks = Blueprint("tasks", __name__)


@tasks.route("/")
def home():

    return render_template("index.html")


@tasks.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    # CREATE TASK
    if request.method == "POST" and user.role == "client":

        image = request.files["image"]

        filename = ""

        if image:

            filename = secure_filename(image.filename)

            upload_folder = os.path.join(
                "app",
                "static",
                "images"
            )

            image.save(
                os.path.join(upload_folder, filename)
            )

        new_task = Task(
            title=request.form["title"],
            description=request.form["description"],
            location=request.form["location"],
            price=float(request.form["price"]),
            image=filename,
            user_id=user.id
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect("/dashboard")

    # SEARCH
    search = request.args.get("search")
    city = request.args.get("city")

    if user.role == "client":
        tasks_query = Task.query.filter_by(user_id=user.id)
    else:
        tasks_query = Task.query

    if search:
        tasks_query = tasks_query.filter(
            Task.title.ilike(f"%{search}%")
        )

    if city:
        tasks_query = tasks_query.filter(
            Task.location.ilike(f"%{city}%")
        )

    tasks_list = tasks_query.all()

    # NOTIFICATIONS
    notifications = Notification.query.filter_by(
        user_id=user.id,
        is_read=False
    ).all()

    return render_template(
        "dashboard.html",
        user=user,
        tasks=tasks_list,
        notifications=notifications
    )


@tasks.route("/accept/<int:task_id>")
def accept_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if user.role != "worker":
        return redirect("/dashboard")

    task = Task.query.get(task_id)

    if task and task.status == "open":

        task.worker_id = user.id
        task.status = "accepted"

        notification = Notification(
            user_id=task.user_id,
            message=f"Your task '{task.title}' was accepted."
        )

        db.session.add(notification)

        db.session.commit()

    return redirect("/dashboard")


@tasks.route("/review/<int:task_id>", methods=["POST"])
def review_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    task = Task.query.get(task_id)

    if not task or user.role != "client" or task.user_id != user.id:
        return redirect("/dashboard")

    if task.status != "accepted" or not task.worker_id:
        return redirect("/dashboard")

    existing_review = Review.query.filter_by(
        task_id=task.id
    ).first()

    if existing_review:
        return redirect("/dashboard")

    review = Review(
        task_id=task.id,
        client_id=user.id,
        worker_id=task.worker_id,
        rating=int(request.form["rating"]),
        comment=request.form["comment"]
    )

    db.session.add(review)

    notification = Notification(
        user_id=task.worker_id,
        message=f"You received a {review.rating}/5 review."
    )

    db.session.add(notification)

    db.session.commit()

    return redirect("/dashboard")


@tasks.route("/profile/<int:user_id>")
def profile(user_id):

    if "user_id" not in session:
        return redirect("/login")

    profile_user = User.query.get(user_id)

    return render_template(
        "profile.html",
        profile_user=profile_user
    )


@tasks.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        user.phone = request.form["phone"]
        user.city = request.form["city"]
        user.bio = request.form["bio"]

        if user.role == "worker":
            user.category = request.form["category"]

        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "complete_profile.html",
        user=user
    )


@tasks.route("/delete-task/<int:task_id>")
def delete_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    task = Task.query.get(task_id)

    if task and task.user_id == user.id:

        db.session.delete(task)
        db.session.commit()

    return redirect("/dashboard")


@tasks.route("/edit-task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    task = Task.query.get(task_id)

    if not task or task.user_id != user.id:
        return redirect("/dashboard")

    if request.method == "POST":

        task.title = request.form["title"]
        task.description = request.form["description"]
        task.location = request.form["location"]
        task.price = float(request.form["price"])

        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "edit_task.html",
        task=task
    )


@tasks.route("/task/<int:task_id>")
def task_details(task_id):

    task = Task.query.get_or_404(task_id)

    messages = Message.query.filter_by(
        task_id=task.id
    ).all()

    return render_template(
        "task_details.html",
        task=task,
        messages=messages
    )


@tasks.route("/send-message/<int:task_id>", methods=["POST"])
def send_message(task_id):

    if "user_id" not in session:
        return redirect("/login")

    text = request.form["text"]

    message = Message(
        task_id=task_id,
        sender_id=session["user_id"],
        text=text
    )

    db.session.add(message)
    db.session.commit()

    return redirect(f"/task/{task_id}")


@tasks.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if user.email != "admin@helpna.com":
        return redirect("/dashboard")

    users = User.query.all()
    tasks = Task.query.all()

    return render_template(
        "admin.html",
        users=users,
        tasks=tasks
    )


@tasks.route("/api/tasks")
def api_tasks():

    tasks = Task.query.all()

    tasks_data = []

    for task in tasks:

        tasks_data.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "location": task.location,
            "price": task.price,
            "status": task.status,
            "image": task.image
        })

    return jsonify(tasks_data)