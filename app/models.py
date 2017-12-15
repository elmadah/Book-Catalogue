from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import db, login_manager

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class UserBooks(db.Model):
    __tablename__ = 'user_books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=None)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), default=None)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    about = db.Column(db.Text())
    profile_image = db.Column(db.String(200), default="user.svg", nullable=True)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    books = db.relationship('UserBooks',
                             backref='user',
                             foreign_keys=[UserBooks.user_id],
                             lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('Password is not a readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def saved_book(self, user, book_id):
        return self.books.filter_by(
            user_id=user.id, book_id=book_id).first() is not None

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13))
    title = db.Column(db.String(64))
    subtitle = db.Column(db.String(200))
    author = db.Column(db.String(64))
    publisher = db.Column(db.String(160))
    publishedDate = db.Column(db.String(64))
    description = db.Column(db.Text())
    pageCount =db.Column(db.INTEGER())
    categories = db.Column(db.String(64))
    thumbnail = db.Column(db.String(200), default=None, nullable=True)
    averageRating = db.Column(db.INTEGER)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('UserBooks', backref='book', lazy='dynamic')

    def __repr__(self):
        return self.id

def init_db():
    db.create_all()


if __name__ == '__main__':
    init_db()