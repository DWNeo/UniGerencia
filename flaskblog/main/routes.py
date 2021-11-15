from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import current_user, login_required
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():  
    if not current_user.is_authenticated:
        flash('É necessário realizar login para utilizar o aplicativo.', 'info')
        return redirect(url_for('users.login'))
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=1000)

    return render_template('home.html', posts=posts, form=form)


@main.route("/about")
def about():
    return render_template('about.html', title='Sobre o Aplicativo')
