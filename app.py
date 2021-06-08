from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Tweet
from forms import UserForm, TweetForm
# exceptions for creating duplicate username
from sqlalchemy.exc import IntegrityError
# Heroku Deployment
import os 

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://auth_demo"
# If we are in production, make sure we DO NOT use the debug mode
if os.environ.get('ENV') == 'production':
    # Heroku gives us an environment variable called DATABASE_URL when we add a postgres database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://auth_demo'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgres://auth_demo').replace("://", "ql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
# Heroku Deployment (secretkey)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'hellosecret1') 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# create db 
connect_db(app)
db.create_all() 

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return render_template('index.html')

# tweets route -> add functionality to add tweets from a specific user
@app.route('/tweets', methods=["GET", "POST"]) 
def show_tweets():
    # add logic to look into session
    if "user_id" not in session:
        flash('Please login first!', 'danger')
        return redirect('/')
    # create new instance for TweetForm
    form = TweetForm()
    # get all Tweets (could be sorted later on?) 
    all_tweets = Tweet.query.all() 
    # validate form 
    if form.validate_on_submit():
        # just get text
        text = form.text.data 
        # set user_id on tweet; reference user_id session 
        new_tweet = Tweet(text=text, user_id=session['user_id'])
        db.session.add(new_tweet)
        db.session.commit() 
        flash('Tweet Posted!', 'success')
        return redirect('/tweets')

    return render_template('tweets.html', form=form, tweets=all_tweets)

# register route (same route will handle both methods)
@app.route('/register', methods=["GET", "POST"]) 
def register_user():
    # initialize userForm
    form = UserForm() 
    if form.validate_on_submit():
        # get username from form
        username = form.username.data
        password = form.password.data
        # error handling later where username could be duplicated and we want to prevent that
        new_user = User.register(username, password)
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)
        # add session  
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', 'success')
        return redirect('/tweets')

    return render_template('register.html', form=form)

# login route (could use different login/registration form) 
@app.route('/login', methods=["GET", "POST"]) 
def login_user():
    form = UserForm()
    # login logic 
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # call authenticate (on classmethod authenticate)
        user = User.authenticate(username, password)
        if user:
            # add session
            flash(f'Welcome back, {user.username}', 'primary')
            session['user_id'] = user.id
            return redirect('/tweets')
        else: 
            form.username.errors = ['Invalid username/password'] 

    return render_template('login.html', form=form)

# logout route (GET) -> prefer to use POST request
@app.route('/logout')
def logout_user():
    # remove user session
    session.pop('user_id')
    flash('Successfully Logged Out', 'info')
    return redirect('/')

# delete route (POST) 
@app.route('/tweets/<int:id>', methods=["POST"]) 
def delete_tweet(id):
    """Delete Tweet"""
    # Could add another layer of security to protect log-in first
    if 'user_id' not in session: 
        flash('Please Log In First', 'danger')
        return redirect('/login')
    # Get Tweet from Flask SQLAlchemy
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('Tweet Deleted', 'info')
        return redirect('/tweets')
    flash("You don't have permission to do that!", 'danger')
    return redirect('/tweet') 