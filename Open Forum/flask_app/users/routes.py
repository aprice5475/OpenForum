import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
from .. import bcrypt, mail
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, ContactForm, AboutForm, ReviewForm
from ..models import Comment, User
from flask_mail import Message

users = Blueprint("users", __name__)

""" ************ User Management views ************ """


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        redirect(url_for("forum.index"))

    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
                "utf-8"
            )
            user = User(username=form.username.data, password=hashed_password)
            user.save()
            return redirect(url_for("users.login"))
    return render_template("register.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for("forum.index"))

    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.objects(username=form.username.data).first()

            if user is not None and bcrypt.check_password_hash(
                user.password, form.password.data
            ):
                login_user(user)
                return redirect(url_for("users.account"))
            else:
                flash("Failed to login!")
    return render_template("login.html", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("forum.index"))


@users.route("/review", methods=["GET", "POST"])
@login_required
def review():
    reviewForm = ReviewForm()
    if request.method == "POST":
        if reviewForm.validate_on_submit():
            msg_body = reviewForm.rating.data + "\n"
            msg_body += "Additional Thoughts: " + reviewForm.content.data
            msg = Message(
                body=msg_body,
                subject="New Feedback for GameHub",
                recipients=["pythonflask388j@gmail.com"],
            )
            mail.send(msg)
        return redirect(url_for("forum.index"))
    return render_template("review.html", form=reviewForm)


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    contactForm = ContactForm()
    aboutForm = AboutForm()
    if request.method == "POST":
        if contactForm.validate_on_submit():
            current_user.modify(email=contactForm.email.data)
            current_user.save()
            msg = Message(
                body="Thanks for signing up for email notifications!",
                subject="Flask Contact Sign Up",
                recipients=[contactForm.email.data],
            )
            mail.send(msg)
            return redirect(url_for("users.account"))
        if aboutForm.about.data and aboutForm.validate_on_submit():
            current_user.modify(about=aboutForm.about.data)
            current_user.save()
            return redirect(url_for("users.account"))
        if aboutForm.picture.data and aboutForm.validate():
            image = aboutForm.picture.data
            filename = secure_filename(image.filename)
            content_type = f"images/{filename[-3:]}"

            if current_user.profile_pic.get() is None:
                current_user.profile_pic.put(image.stream, content_type=content_type)
            else:
                current_user.profile_pic.replace(
                    image.stream, content_type=content_type
                )
            current_user.save()
            return redirect(url_for("users.account"))
    profile_pic_base64 = None
    if current_user.profile_pic.get() is not None:
        profile_pic_base64 = get_b64_img(current_user.username)
    return render_template(
        "account.html",
        username=current_user.username,
        image=profile_pic_base64,
        aboutForm=aboutForm,
        contactForm=contactForm,
        about=current_user.about,
    )


@users.route("/user/<username>", methods=["GET", "POST"])
def user_detail(username):
    error = None
    about = None
    user = User.objects(username=username).first()
    picBase64 = None
    comments = []
    if user is None:
        error = f"{username} doesn't exist"
    elif user.profile_pic is not None:
        picBytes = BytesIO(user.profile_pic.read())
        picBase64 = base64.b64encode(picBytes.getvalue()).decode()
        comments = list(Comment.objects(commenter=current_user))
        about = user.about
    return render_template(
        "user_detail.html",
        image=picBase64,
        error=error,
        username=username,
        comments=comments,
        about=about,
    )


def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
