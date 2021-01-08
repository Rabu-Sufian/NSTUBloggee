from nstublog import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

############## Db Models ###################
class User(db.Model, UserMixin):
    '''
    User
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    users_type = db.Column(db.String(10), nullable=False)
    liked = db.relationship('Like', foreign_keys='Like.user_id', backref='user', lazy='dynamic')
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.users_type}')"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id) 


    def like_post(self, post):
        if not self.has_liked_post(post):
            like = Like(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            Like.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return Like.query.filter(
            Like.user_id == self.id,
            Like.post_id == post.id).count() > 0        


class Post(db.Model):
    __searchable__ = ['title', 'body']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    image = db.Column(db.String(150), nullable=False, default='no-image.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)
    author = db.relationship('User',
        backref=db.backref('posts', lazy=True,  primaryjoin="User.id == Post.user_id"))#post table, duita table er sathe relation tai primary join
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
        nullable=False)
    category = db.relationship('Category',
        backref=db.backref('posts', lazy=True))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow) 
          

    def __repr__(self):
        return '<Post %r>' % self.title
    
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    count = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '{}'.format(self.name)
   
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    post = db.relationship('Post', backref=db.backref('posts',lazy=True, passive_deletes=True))
    date_pub = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)      

    def __repr__(self):
        return '{}'.format(self.name)


class Like(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))


   