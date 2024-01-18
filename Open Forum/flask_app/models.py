from flask_login import UserMixin
from datetime import datetime
from .utils import current_time
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True, minLength=1, maxLength=40)
    password = db.StringField(required=True)
    email = db.EmailField()
    about = db.StringField()
    profile_pic = db.ImageField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Topic(db.Document):
    author = db.ReferenceField("User", required=True)
    topic = db.StringField(required=True, maxLength=100)
    content = db.StringField(required=True, minLength=3, maxLength=400)
    date = db.StringField(required=True)


class Comment(db.Document):
    commenter = db.ReferenceField("User", required=True)
    content = db.StringField(required=True, minLength=5, maxLength=200)
    date = db.StringField(required=True)
    topic = db.StringField(required=True)
