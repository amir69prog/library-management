from source import (
    QMessageBox,
    BlobImage,
    QDialog,
    DataBase,
    QApplication,
    sys,
    loadUi,
    os,
    QStackedLayout,
    datetime,
    QIcon,
)

from source.book import BookWidget, BookField, BookDetail
from source.query import QueryBook, QueryAuthor
from source.author import AuthorWidget, AuthorField, AuthorDetail

"""
Todo: 
	1. books tabs:
		1.1: display all book in the list ...DONE
			1.1.1: create and set image ...DONE
		1.2: create book page to delete/update/read...DONE
	2. author tabs:
		2.1: display all authors in list
			2.1.1: create and set profile picture
		2.2: author page to read/delete/update 
	3. clean the code:
		creat class for each object
"""


# Main
class MainApp(QDialog, DataBase):
    def __init__(self, program):
        super().__init__()
        loadUi('../user_interface/ui_main.ui', self)
        self.setWindowTitle('Library Management')
        self.setWindowIcon(QIcon('../images/window_icon.png'))
        # class Attrs
        self.blob_image = BlobImage()
        self.query_book = QueryBook()
        self.query_author = QueryAuthor()
        self.book_field = BookField(self)
        self.author_field = AuthorField(self)
        self.program = program

        # Attrs
        self.path = str(os.getcwd())
        # Signals
        self.browse_picture.clicked.connect(lambda: self.blob_image.browse_picture_file(self))
        self.browse_profile_picture.clicked.connect(lambda: self.blob_image.browse_profile_picture_file(self))
        self.insert_book.clicked.connect(self.insert_book_method)
        self.insert_author.clicked.connect(self.insert_author_method)
        self.add_author.clicked.connect(self.add_author_clicked)

        # call important methods
        self.set_books()
        self.set_combo_authors()
        self.set_authors()
        self.set_date()

    ''' Methods '''

    def set_date(self):
        date = datetime.datetime.now().date()
        self.date_book.setDate(date)

    ''' Book Methods '''

    def set_books(self):  # OK
        if self.list_book.count() > 0:
            self.clear_book_list()
        books = self.query_book.all_books()
        for book in books:
            # create widget and add item to list
            widget = self.create_book_widget(book)
            self.list_book.addWidget(widget)
        self.countBook.setText(str(self.list_book.count()))  # set count of book

    def create_book_widget(self, data):  # OK
        """ Create Book Widget -> book item """
        widget = BookWidget(self, *data)
        return widget

    def insert_book_method(self):  # OK
        """ Get the values fields """
        self.book_field.raise_error()
        title = self.title_book.text()
        date_published = self.date_book.date().toPyDate()
        author = self.author_book.currentData()
        price = self.price_book.value()
        image = getattr(self, 'picture_book_file', None)
        blob_image = self.blob_image.read_image(image)
        if title and author:
            # insert to table book
            row_id = self.query_book.insert_book(title, price, date_published, blob_image, author)
            # insert to list
            self.set_books()
            self.set_authors()
            self.book_field.set_null_field()
        else:
            message = 'Please Fill out the Required Fields'
            self.book_field.raise_error(message)

    def clear_book_list(self):  # OK
        for i in reversed(range(self.list_book.count())):
            self.list_book.itemAt(i).widget().setParent(None)

    ''' Author Methods '''

    def set_combo_authors(self):  # OK
        if self.author_book.count() > 0:
            self.author_book.clear()
            self.author_book.addItem('-- author --')

        authors = self.query_author.all_authors()
        for author in authors:
            self.author_book.addItem(author[1], author[0])

    def set_authors(self):  # Ok
        if self.list_author.count() > 0:
            self.clear_author_list()
        authors = self.query_author.all_authors()
        for author in authors:
            widget = self.create_author_widget(author)
            self.list_author.addWidget(widget)
        self.countAuthor.setText(str(self.list_author.count()))  # set count of author

    def create_author_widget(self, author):  # OK
        id_ = author[0]
        full_name = author[1]
        age = author[3]
        profile_picture = author[2]
        widget = AuthorWidget(self, full_name, age, profile_picture, id_)
        return widget

    def insert_author_method(self):
        self.author_field.raise_error()
        full_name = self.full_name.text()
        age = self.age.value()
        profile_picture = getattr(self, 'profile_picture_file', None)
        blob_profile_picture = self.blob_image.read_image(profile_picture)

        if full_name and age:
            row_id = self.query_author.insert_author(full_name, age, blob_profile_picture)
            self.author_field.set_null_field()
            self.set_combo_authors()
            self.set_authors()
        else:
            message = 'Please Fill out the Required Fields'
            self.author_field.raise_error(message)

    def clear_author_list(self):
        for author in reversed(range(self.list_author.count())):
            self.list_author.itemAt(author).widget().setParent(None)

    """ Signals Methods """

    def add_author_clicked(self):
        self.tabs.setCurrentIndex(1)


# Run App
if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = QStackedLayout()
    main_app = MainApp(program)
    book_detail = BookDetail(main_app)
    author_detail = AuthorDetail(main_app)
    program.insertWidget(0, main_app)
    program.insertWidget(1, book_detail)
    program.insertWidget(2, author_detail)
    app.exec_()
