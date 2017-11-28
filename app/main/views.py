from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import requests
from . import main
from .. import db
from .forms import SearchBook, EditProfileForm
from ..models import Book, UserBooks, User, Permission
import re

@main.route('/books/search/', methods=['GET', 'POST'])
def books_search():
    form = SearchBook()

    if form.validate_on_submit():
        isbn = form.isbn.data

        isbn = re.sub(r'\D', "", isbn)
        url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)

        request = requests.get(url)

        books = request.json()

        isbnB = books['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
        titleB = books['items'][0]['volumeInfo']['title']
        subtitleB = books['items'][0]['volumeInfo']['subtitle']
        authorB = books['items'][0]['volumeInfo']['authors'][0]
        publisherB = books['items'][0]['volumeInfo']['publisher']
        publishedDateB = books['items'][0]['volumeInfo']['publishedDate']
        descriptionB = books['items'][0]['volumeInfo']['description']
        pageCountB = books['items'][0]['volumeInfo']['pageCount']
        categoriesB = books['items'][0]['volumeInfo']['categories'][0]
        averageRatingB = books['items'][0]['volumeInfo']['averageRating']
        thumbnailB = books['items'][0]['volumeInfo']['imageLinks']['thumbnail']

        if Book.query.filter_by(isbn=isbnB).first() is not None:
            return redirect(url_for('.books', id=id))
        else:
            book = Book(isbn=isbnB,
                        title=titleB,
                        subtitle = subtitleB,
                        author=authorB,
                        publisher=publisherB,
                        publishedDate=publishedDateB,
                        description=descriptionB,
                        pageCount=pageCountB,
                        categories=categoriesB,
                        averageRating=averageRatingB,
                        thumbnail=thumbnailB)
            db.session.add(book)
            db.session.commit()
            flash('You have successfully added a new Book.')

    return render_template('index.html',
                           form=form)

@main.route('/books/test/', methods=['GET', 'POST'])
def books_test():
    form = SearchBook()

    books = 0
    _title = 0
    _subtitle = 0

    if form.validate_on_submit():
        isbn = form.isbn.data

        url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)

        request = requests.get(url)

        books = request.json()

        _title = books.get('items')[0]['volumeInfo']['title']
        _subtitle = books.get('items')[0]['volumeInfo']['subtitle']

    return render_template('test.html',
                           form=form, books=books, title=_title, subtitle=_subtitle)

@main.route('/books/save/<int:id>/')
@login_required
def books_save(id):
    save = UserBooks(user_id=current_user.get_id(),
                     book_id=id,
                     timestamp=datetime.now())
    db.session.add(save)
    db.session.commit()
    flash('You saved %s.' % id)
    return redirect(url_for('.books', id=id))

@main.route('/books/<int:id>', methods=['GET', 'POST'])
def book(id):
    book = Book.query.get_or_404(id)
    books = Book.query.order_by(Book.publishedDate.desc()).all()
    return render_template('books/book.html', book=book, books=books
                           )

@main.route('/books/', methods=['GET', 'POST'])
@login_required
def books():
    books = Book.query.order_by(Book.publishedDate.desc()).all()

    return render_template('books/books.html', books=books)

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    books = Book.query.order_by(Book.publishedDate.desc()).all()

    return render_template('index.html', books=books)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    books = UserBooks.query.filter_by(user_id=current_user.get_id()).all()

    return render_template('user/user.html', user=user, books=books)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)