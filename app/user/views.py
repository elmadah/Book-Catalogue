from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import user
from .. import db
from ..models import User, UserBooks
from .forms import LoginForm, RegistrationForm, EditProfileForm
from .. import photos



@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.profile_image.has_file():
            filename = photos.save(request.files['profile_image'])
            current_user.profile_image = filename
        current_user.name = form.name.data
        current_user.about = form.about.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.about.data = current_user.about
    form.profile_image.data = current_user.profile_image
    return render_template('user/edit_profile.html', form=form)

@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.explore'))
        flash('Invalid username or password.')
    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.explore'))


@user.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User has been created.')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)


@user.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    books = UserBooks.query.filter_by(user_id=user.get_id()).all()

    user_books = UserBooks.query.filter_by(user_id=user.get_id()).order_by(UserBooks.timestamp.desc()).all()

    return render_template('user/user.html', user=user, books=books, user_books=user_books)