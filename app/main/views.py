from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_user, logout_user, login_required, \
    current_user
from datetime import datetime
import requests
from . import main
from .. import db
from .forms import SearchBook, EditProfileForm, EditBook
from ..models import Book, UserBooks, User, Permission
import re
from .. import photos
from ..user.decorators import admin_required
from ..user.forms import LoginForm
from  sqlalchemy.sql.expression import func

@main.route('/books/search/', methods=['GET', 'POST'])
def books_search():
    form = SearchBook()
    if form.validate_on_submit():
        isbn = form.isbn.data

        isbn = re.sub(r'\D', "", isbn)
        url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{}'.format(isbn)

        request = requests.get(url)

        request_json = request.json()
        try:
            books = request_json['items'][0]['volumeInfo']
            isbnB = books['industryIdentifiers'][1]['identifier']
            titleB = books['title']

            _subtitle = books.get('subtitle', '')

            authorB = books['authors'][0]
            _publisher = books.get('publisher', '')
            _publishedDate = books.get('publishedDate', '')
            _description = books.get('description', '')
            _pageCount = books.get('pageCount', '')
            _categories = books['categories'][0]
            # _categories = books.get('categories', '')
            _averageRating = books.get('averageRating', '')
            thumbnailB = books['imageLinks']['thumbnail']

            Book_filter = Book.query.filter_by(isbn=isbnB).first()

            # 1781109605

            if Book_filter is not None:
                return redirect(url_for('.book', id=Book_filter.id))
            else:
                book = Book(isbn=isbnB,
                            title=titleB,
                            subtitle=_subtitle,
                            author=authorB,
                            publisher=_publisher,
                            publishedDate=_publishedDate,
                            description=_description,
                            pageCount=_pageCount,
                            categories=_categories,
                            averageRating=_averageRating,
                            thumbnail=thumbnailB)
                db.session.add(book)
                db.session.commit()

                return redirect(url_for('.index'))
                flash('You have successfully added a new Book.')

        except:
            abort(404)
            flash("Can't lookup the book")




    return render_template('books/books_search.html',
                           form=form)

@main.route('/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def books_edit(id):
    book = Book.query.get_or_404(id)
    form = EditBook(obj=book)
    if form.validate_on_submit():
        book.isbn=form.isbn.data
        book.title=form.title.data
        book.subtitle=form.subtitle.data
        book.author=form.author.data
        book.publisher=form.publisher.data
        book.description=form.description.data
        book.categories=form.categories.data

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('.admin'))
        flash('Saved!')

    return render_template('books/edit_book.html', form=form, book=book)




@main.route('/books/save/<int:id>/')
@login_required
def books_save(id):
    save = UserBooks(user_id=current_user.get_id(),
                     book_id=id,
                     timestamp=datetime.now())
    db.session.add(save)
    db.session.commit()
    flash('You saved to your library')
    return redirect(url_for('.books', id=id))

@main.route('/books/save/remove/<int:id>/')
@login_required
def books_remove_save(id):
    delete_userbooks = UserBooks.query.filter_by(book_id=id).delete()

    db.session.commit()
    flash('Book is removed from your library')
    return redirect(url_for('.books', id=id))


@main.route('/books/<int:id>', methods=['GET', 'POST'])
def book(id):
    book = Book.query.get_or_404(id)
    books = Book.query.order_by(func.random()).limit(6).all()
    return render_template('books/book.html', book=book, books=books
                           )

@main.route('/books/', methods=['GET', 'POST'])
def books():
    books = Book.query.order_by(Book.publishedDate.desc()).all()

    return render_template('books/books.html', books=books)

@main.route('/book/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def book_delete(id):
    delete_book = Book.query.filter_by(id=id).delete()
    delete_userbooks = UserBooks.query.filter_by(book_id=id).delete()


    db.session.commit()
    flash('Book is deleted')
    return redirect(url_for('.admin'))
# 9781495057540

@main.route('/explore/', methods=['GET', 'POST'])
@login_required
def explore():
    user_books = UserBooks.query.order_by(UserBooks.timestamp.desc()).all()
    users = User.query.order_by(User.member_since.desc()).all()


    return render_template('books/explore.html',
                           user_books=user_books,
                           users=users)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.explore'))
        flash('Invalid username or password.')
    books = Book.query.order_by(Book.timestamp.desc()).all()

    return render_template('index.html', books=books, form=form)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    books = UserBooks.query.filter_by(user_id=user.get_id()).all()

    user_books = UserBooks.query.filter_by(user_id=user.get_id()).order_by(UserBooks.timestamp.desc()).all()

    return render_template('user/user.html', user=user, books=books, user_books=user_books)


@main.route('/edit-profile', methods=['GET', 'POST'])
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

@main.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    user = User.query.order_by(User.member_since.desc()).all()
    books = Book.query.order_by(Book.timestamp.desc()).all()

    return render_template('admin/admin.html', user=user, books=books)

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404