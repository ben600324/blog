from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint , jsonify)
from flask_login import current_user, login_required
from flaskblog import db, ma, auth, bcrypt
from flaskblog.models import Post, PostSchema, User
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

# REST api

# Init schema
post_schema = PostSchema(strict=True)
posts_schema = PostSchema(many=True, strict=True)

#Create a Post
@posts.route("/post/add/apiV1", methods=['POST'])
def add_posts():
    user = User.query.filter_by(username=request.authorization.username).first()
    if user and bcrypt.check_password_hash(user.password, request.authorization.password):
        api_post = Post(title=request.json['title'], content=request.json['content'], user_id= user.id)
        db.session.add(api_post)
        db.session.commit()

        return post_schema.jsonify(api_post)
    else:
        return 'Unauthorized Access'

@posts.route("/posts/get/apiV1", methods=['GET'])
def get_posts():
    
    all_posts = Post.query.all()
    result = posts_schema.dump(all_posts)
    return jsonify(result.data)