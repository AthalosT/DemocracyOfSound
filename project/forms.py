from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, HiddenField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from project.models import User, Song, Room, List

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Enter input:', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class RoomLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter')

class CreateRoomForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Room')

# Figure out whether this should route to roomlogin 
class FindRoomForm(FlaskForm):
    roomid = StringField('Room Code', validators=[DataRequired()])
    #password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Find Room')

class SongQueryForm(FlaskForm):
    user_query = StringField('Song Name', validators=[DataRequired()])
    #number_shown = StringField('Number of Suggestions', validators=[DataRequired()])
    submit1 = SubmitField('Find Song')

class SongSelectForm(FlaskForm):
    choices = RadioField('Select Song', coerce=str)
    submit2 = SubmitField('Enter')  
