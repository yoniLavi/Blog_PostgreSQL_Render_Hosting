from statistics import median, mean

from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy import text

from config import Config
from models import User, BlogPost, db

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = "login"

with app.app_context():
    db.init_app(app)
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allow_edit(post):
    return post.author == current_user


@app.route("/")
def index():
    return render_template("index.html", posts=BlogPost.query.all())


@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_action():
    user = User(username=request.form["username"], password=request.form["password"])
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_action():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(f"No such user '{username}'")
        return redirect(url_for("login_page"))
    if password != user.password:
        flash(f"Invalid password for the user '{username}'")
        return redirect(url_for("login_page"))

    login_user(user)
    return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
@login_required
def logout_page():
    return render_template("logout.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout_action():
    logout_user()
    return redirect(url_for("index"))


@app.route("/create", methods=["GET"])
@login_required
def create_post_page():
    return render_template("create.html")


@app.route("/create", methods=["POST"])
@login_required
def create_post_action():
    post = BlogPost(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user,
    )
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/post/<int:post_id>")
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template("post.html", post=post, allow_edit=allow_edit(post))


@app.route("/edit/<int:post_id>", methods=["GET"])
@login_required
def edit_page(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if not allow_edit(post):
        flash(f"Only this post's author ({post.author}) is allowed to edit it")
        return redirect(url_for("post", post_id=post.id))
    return render_template("edit.html", post=post)


@app.route("/edit/<int:post_id>", methods=["POST"])
@login_required
def edit_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if not allow_edit(post):
        flash(f"Only this post's author ({post.author}) is allowed to edit it")
        return redirect(url_for("post", post_id=post.id))
    post.title = request.form["title"]
    post.content = request.form["content"]
    db.session.commit()
    return redirect(url_for("post", post_id=post.id))


@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_action(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if not allow_edit(post):
        flash(f"Only this post's author ({post.author}) is allowed to delete it")
        return redirect(url_for("post", post_id=post.id))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/stats")
def stats():
    title_lengths = BlogPost.get_title_lengths()

    return render_template(
        "stats.html",
        average_length=mean(title_lengths),
        max_length=max(title_lengths),
        min_length=min(title_lengths),
        total_length=sum(title_lengths),
        median_length=median(title_lengths),
    )


if __name__ == "__main__":
    app.run(debug=True)
