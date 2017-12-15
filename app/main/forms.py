from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from .. import photos

class SearchBook(FlaskForm):
    isbn = StringField('ISBN', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

class EditBook(FlaskForm):
    isbn = StringField('ISBN', validators=[Length(0, 64)])
    title = StringField('Title', validators=[Length(0, 64)])
    subtitle = TextAreaField('Subtitle', validators=[Length(0, 200)])
    author = StringField('Author', validators=[Length(0, 64)])
    publisher = StringField('Publisher', validators=[Length(0, 160)])
    description = TextAreaField('Description')
    categories = StringField('Categories', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    profile_image = FileField('Profile Image', validators=[FileRequired(), FileAllowed(photos, 'Images only!')])
    name = StringField('User Full Name', validators=[Length(0, 64)])
    about = TextAreaField('About me')
    submit = SubmitField('Submit')