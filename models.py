from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

# define User Class inherits from db.Model
class User(db.Model):
    # setup model 
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False) 

    # classmethod for register
    @classmethod
    def register(cls, username, pwd):
        """Register user with hashed password & return user"""
        # turn password into a hash with bcrypt (returns a bytestring)
        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string to store in database
        hashed_utf8 = hashed.decode('utf8')
        # return instance of user with username and hashed pwd 
        return cls(username=username, password=hashed_utf8) 

    # classmethod for authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & pwd is correct
        Return user if valid; else return False 
        """
        u = User.query.filter_by(username=username).first() 
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance 
            return u
        else: 
            return False 

# Tweet Model
class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # setup ForeignKey constraint to make sure actual user ID exists from User Model 
    # relationship SQLAlchemy 
    user = db.relationship('User', backref="tweets")