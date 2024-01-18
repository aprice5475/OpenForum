import base64
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required, login_user, logout_user

from ..forms import ContactForm, RegistrationForm, AboutForm, TopicForm, CommentForm

from ..models import User, Topic, Comment
from ..utils import current_time
from .. import bcrypt, mail
from flask_mail import Message

forum = Blueprint("forum", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """


def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


""" ************ View functions ************ """


@forum.route("/", methods=["GET", "POST"])
def index():
    form = None
    if current_user and current_user.is_authenticated:
        form = TopicForm()
        if request.method == "POST":
            if form.validate_on_submit():
                t = Topic.objects(topic=form.topic.data).first()

                if t is None:
                    newTopic = Topic(
                        topic=form.topic.data,
                        author=current_user,
                        content=form.description.data,
                        date=current_time(),
                    )
                    newTopic.save()
                    return redirect(request.path)

    # view topics
    topics = Topic.objects()
    topicLst = []
    for t in topics:
        topicLst.append(t)
    return render_template("index.html", topicLst=topicLst, form=form)


@forum.route("/topics/<topic>", methods=["GET", "POST"])
def topic_detail(topic):
    form = None
    topicObj = Topic.objects(topic=topic).first()
    if topicObj is None:
        return render_template("404.html")

    if current_user and current_user.is_authenticated:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(
                commenter=current_user,
                content=form.comment.data,
                date=current_time(),
                topic=topic,
            )
            comment.save()
            # email topic author
            if topicObj.author.email:
                msg_body = current_user.username + 'replied "' + form.comment.data + '"'
                msg = Message(
                    body=msg_body,
                    subject="From GameHub - New reply to " + topic,
                    recipients=[topicObj.author.email],
                )
                mail.send(msg)

            return redirect(request.path)
    comments = Comment.objects(topic=topic)
    return render_template(
        "topic_detail.html", form=form, topicObj=topicObj, comments=comments
    )
