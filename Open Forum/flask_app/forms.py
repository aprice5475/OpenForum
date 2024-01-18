from ast import Pass
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, RadioField
from wtforms.widgets import TextArea
from .utils import datetime
from wtforms.validators import (
    InputRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from flask_mail import Mail

from .models import User


class ReviewForm(FlaskForm):
    rating = RadioField(
        "How would you rate the app experience?",
        choices=["Amazing", "Ok", "Idk"],
        validators=[InputRequired()],
    )
    content = StringField(
        "Additional thoughts or concerns?",
        validators=[Length(max=150)],
        widget=TextArea(),
    )
    submit = SubmitField("Share feedback")


class ContactForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    submit = SubmitField("Sign Up for Notifications")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError("Username is taken")


class CommentForm(FlaskForm):
    comment = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=1, max=150)]
    )
    submit = SubmitField("Reply")


class AboutForm(FlaskForm):
    about = StringField(
        "About Me", validators=[InputRequired(), Length(max=200)], widget=TextArea()
    )
    picture = FileField("Profile Photo", validators=[FileAllowed(["png", "jpg"])])
    submit = SubmitField("Update Profile")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class TopicForm(FlaskForm):
    topic = StringField("New Topic", validators=[InputRequired(), Length(max=100)])
    description = TextAreaField(
        "Description", validators=[InputRequired(), Length(min=3, max=400)]
    )
    submit = SubmitField("Post")
