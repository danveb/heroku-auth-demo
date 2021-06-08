from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired 

# separate RegisterForm and UserForm if needed
class UserForm(FlaskForm):
    # fields
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

# TweetForm; inherits from FlaskForm
class TweetForm(FlaskForm):
    # fields 
    text = StringField('Tweet Text', validators=[InputRequired()]) 