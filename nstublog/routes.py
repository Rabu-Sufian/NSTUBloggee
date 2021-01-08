import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort, current_app
from nstublog import app, db, bcrypt, mail, search
from nstublog.models import User, Post, Category, Comment, Like
from nstublog.forms import (TeacherRegistrationForm, StudentRegistrationForm, LoginForm, UpdateAccountForm, 
                            PostForm, AddCommentForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

#Create_index 
""" search.create_index()
search.create_index(Post)

#Update_index
search.create_index(update=True)
search.create_index(Post, update=True)

#Delete_index
search.create_index(delete=True)
search.create_index(Post, delete=True)  """
 
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.join(User).filter_by(users_type='student').all()
    postss = Post.query.join(User).filter_by(users_type='teacher').all()
    categories = Category.query.all()
    count_list = []
    for c in categories:
        cout = Post.query.join(Category).filter_by(id=c.id).count() 
        count_list.append(cout) 
    """ query = db.session.query(Category.name, db.func.count(Post.category_id)).outerjoin(Post, Category.id == Post.category_id).group_by(Category.name).all()  
    result = dict(query)  """
    return render_template('home.html', posts=posts, postss=postss, categories_count_list=zip(categories, count_list)) 

@app.route('/search/', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword')
    posts = Post.query.msearch(keyword,fields=['title', 'body']).all()
    return render_template('search.html', posts=posts) 

@app.route('/register')
def register():
    return render_template('register.html', title='Register')

@app.route('/student_registration', methods=['GET', 'POST']) 
def student_registration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, users_type='student')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('student.html', title='Register', form=form)


@app.route('/teacher_registration', methods=['GET', 'POST']) 
def teacher_registration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, users_type='teacher')
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('teacher.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:    
            flash('Login Unsuccessful. Please check email and password', 'error')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


############# save picture #############

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email  
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Profile', image_file=image_file, form=form)


####################save photo for posts ######################
def save_photo(photo):
    rand_hex = secrets.token_urlsafe(10)
    _, file_extention = os.path.splitext(photo.filename)
    file_name = rand_hex + file_extention
    file_path = os.path.join(current_app.root_path, 'static/images', file_name)
    photo.save(file_path)
    return file_name

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture = save_photo(form.picture.data)
            post = Post(title=form.title.data, body=form.content.data, image=picture, author=current_user, category=form.category.data)    
            db.session.add(post)
            db.session.commit()
        else:
            post = Post(title=form.title.data, body=form.content.data, author=current_user, category=form.category.data)
            db.session.add(post)
            db.session.commit()        
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='Add Post', form=form)

@app.route('/blog/teacher')
def teacher_blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(User).filter_by(users_type='teacher').order_by(Post.pub_date.desc()).paginate(page=page, per_page=4)
    categories = Category.query.all()
    return render_template("teacher_posts.html", posts=posts, categories=categories)

@app.route('/blog/student')
def student_blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(User).filter_by(users_type='student').order_by(Post.pub_date.desc()).paginate(page=page, per_page=4)
    categories = Category.query.all()
    return render_template("student_posts.html", posts=posts, categories=categories)

@app.route("/blog/teacher/category/<int:id>")
def get_teachcategory(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=id).join(User).filter_by(users_type='teacher').order_by(Post.pub_date.desc()).paginate(page=page, per_page=4)
    return render_template('teacher_category.html', title='Teacher Blog Category', posts=posts, category=category)

@app.route("/blog/student/category/<int:id>")
def get_studcategory(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=id).join(User).filter_by(users_type='student').order_by(Post.pub_date.desc()).paginate(page=page, per_page=4)
    return render_template('student_category.html', title='Student Blog Category', posts=posts, category=category)

@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id) 
    posts = Post.query.all()     
    form = AddCommentForm()
    comments = Comment.query.filter_by(post_id=post.id).all()
    if form.validate_on_submit():
        comment = Comment(name=form.name.data, email=form.email.data, message=form.message.data, post_id=post.id)    
        db.session.add(comment)
        post.comments = post.comments + 1
        db.session.commit()
        flash('Your Comment has been posted!', 'success')  
        return redirect(request.url)
    return render_template('post.html', title=post.title, post=post, form=form, comments=comments, posts=posts)


@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/post/<int:post_id>/<action>')
def page_turn(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404() 
    pid = post.id
    count = Post.query.count()
    if action == 'next':    
        while (count > 0):
            pid = pid + 1 
            if Post.query.get(pid) is not None:
                return redirect(url_for('post', post_id=pid))
                break     
            else:
                count = count - 1    
    if action == 'previous':
        while (count > 0):
            pid = pid - 1 
            if Post.query.get(pid) is not None:
                return redirect(url_for('post', post_id=pid))
                break     
            else:
                count = count - 1 

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_photo(form.picture.data)
            post.image = picture_file
        post.title = form.title.data
        post.body = form.content.data
        post.category = form.category.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.category.data = post.category
        form.content.data = post.body
    return render_template('new_post.html', title='Update Post',
                           form=form)   


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/category/<int:id>")
def get_category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=id).order_by(Post.pub_date.desc()).paginate(page=page, per_page=4)
    return render_template('category.html', title='Category', posts=posts, category=category)


############### Sent Mail ###################
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='rabiasufian75@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    
    '''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm() 
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))   
    return render_template('reset_request.html', title='Reset Password', form=form)    


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)    


################## ############ ERRORS ######## #########################

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500 