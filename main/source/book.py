from source import QFileDialog, QWidget, QDialog, loadUi, datetime, QPixmap, QMessageBox, QFont, QIcon
from source.query import QueryBook, QueryAuthor, BlobImage, MessageSuccessUpdated
from source.author import AuthorDetail

def get_author(pk):
    return QueryAuthor().get_author(pk)


def delete_book(pk):
    return QueryBook().delete_book(pk)


class MessageDeleteBook(QMessageBox):
    """ Message box to delete the book """

    def __init__(self, parent, text):
        super().__init__(parent)
        font = QFont('Verdana Pro Cond', 12)
        self.setFont(font)
        self.setText(text)
        self.setWindowTitle('Deleting')
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        # signals
        self.buttonClicked.connect(self.clicked_button)

        self.show()

    def clicked_button(self, button):
        self.button_clicked = button.text()
        if self.button_clicked == '&Yes':
            self.delete = True
        else:
            self.delete = False


class BookField:
    """ Settings Book Field """

    def __init__(self, parent):
        self.parent = parent

    def raise_error(self, msg=''):
        self.parent.error_book.setText(msg)

    def set_null_field(self):
        self.parent.title_book.setText('')
        self.parent.price_book.setValue(0)
        self.parent.author_book.setCurrentIndex(0)
        self.parent.set_date()
        self.parent.picture_book.clear()
        if hasattr(self, 'picture_book_file'):
            delattr(self, 'picture_book_file')


class BookWidget(QWidget):
    def __init__(self, parent, *data):
        super().__init__()
        loadUi('../user_interface/ui_book.ui', self)
        # Attrs
        self.parent = parent
        self.id = data[0]
        self.val_title = data[1]
        self.val_price = data[2]
        self.val_date = data[3]
        self.val_image = data[4]
        self.val_author = get_author(data[5])
        # calling important method
        self.settings()
        self.initUi()

        self.delete_book.clicked.connect(self.delete_book_clicked)
        self.book_detail.clicked.connect(self.book_detail_clicked)
        self.author_detail.clicked.connect(self.author_detail_clicked)

    def format_date(self):
        date = datetime.datetime.strptime(self.val_date, '%Y-%m-%d')
        return date.strftime('%d/%m/%Y')

    def delete_book_clicked(self):
        """ popup message to delete book """
        text = 'Are you sure to delete \'{}\' book'.format(self.val_title)
        message = MessageDeleteBook(self, text)
        message.exec_()
        # conditions
        if message.delete:
            delete_action = delete_book(self.id)
            self.parent.set_books()
            self.parent.set_authors()
        else:
            pass

    def initUi(self):
        self.author.adjustSize()
        self.title.adjustSize()
        self.adjustSize()

    def set_pixmap(self):
        if self.val_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.val_image)
        else:
            pixmap = QPixmap('../images/null-icon.jpg')
        self.picture.setPixmap(pixmap)
        self.picture.setScaledContents(True)

    def settings(self):
        self.title.setText(self.val_title)
        self.price.setText('$' + str(self.val_price))
        self.date.setText(self.format_date())
        self.author.setText(self.val_author[1])
        self.set_pixmap()

    def book_detail_clicked(self):
        data = (self.id, self.val_title, self.val_price, self.val_date, self.val_image, self.val_author)
        book_detail = BookDetail(self.parent, *data)
        book_detail.settings()
        self.parent.program.insertWidget(1, book_detail)
        self.parent.program.setCurrentIndex(1)

    def author_detail_clicked(self):
        """ display author detail page """
        data = self.val_author
        author_detail = AuthorDetail(self.parent, *data)
        author_detail.settings()
        self.parent.program.insertWidget(2, author_detail)
        self.parent.program.setCurrentIndex(2)

class BookDetail(QWidget):
    def __init__(self, parent, *data):
        super().__init__()
        loadUi('../user_interface/ui_book_detail.ui', self)
        self.setWindowIcon(QIcon('../images/book.png'))
        # Class Attrs
        self.query_author = QueryAuthor()
        self.query_book = QueryBook()

        # Attributes
        self.parent = parent
        data_ = data or (None, None, None, None, None, None)
        self.val_title = data_[1]
        self.val_price = data_[2]
        self.val_date = data_[3]
        self.val_image = data_[4]
        self.val_author = data_[5]
        self.id = data_[0]

        # Signals
        self.back_btn.clicked.connect(self.back)
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.update_btn.clicked.connect(self.update)
        self.browse_picture.clicked.connect(self.browse_picture_file)

        # set data
        self.set_combo_authors()
        self.setWindowTitle(self.val_title)

    def get_date(self, date):
        """ Convert date string to date class """
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date.date()

    def set_image(self):
        """ Get the image blob and set pixmap to label """
        if self.val_image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.val_image)
        else:
            pixmap = QPixmap('../images/author_profile_picture.jpg')
        self.profile_picture.setPixmap(pixmap)

    def settings(self):
        """ Set the configurations """
        self.title.setText(self.val_title)
        self.price_book.setValue(self.val_price)
        self.date_book.setDate(self.get_date(self.val_date))
        self.select_author()
        self.set_image()

    def select_author(self):
        """ Select the current Author  """
        full_name = self.val_author[1]
        return self.author_book.setCurrentText(full_name)

    def set_combo_authors(self):
        """ Insert authors to item list """
        if self.author_book.count() > 0:
            self.author_book.clear()
            self.author_book.addItem('-- author --')

        authors = self.query_author.all_authors()
        for author in authors:
            self.author_book.addItem(author[1], author[0])

    def back(self):
        """ Back to the main page """
        self.parent.program.setCurrentIndex(0)

    def update(self):
        """ Send request to update the book """
        blob_new_image = getattr(self, 'updated_val_image', None)
        new_date_str = str(self.date_book.date().toPyDate())

        current_values = (
            {'title': self.val_title},
            {'price': self.val_price},
            {'date_published': self.val_date},
            {'author': self.val_author[0]},
            {'cover_picture': self.val_image}
        )

        new_values = (
            {'title': self.title.text()},
            {'price': self.price_book.value()},
            {'date_published': new_date_str},
            {'author': self.author_book.currentData()},
            {'cover_picture': blob_new_image}
        )
        filter_data = FilterDataBook(self, current_values, new_values)
        filtered_fields = filter_data.filtering()
        data = filter_data.to_dictionary(filtered_fields)
        cover_picture = data.get('cover_picture',None)
        is_updated = self.query_book.update_book(self.id, data,cover_picture)
        if is_updated:
            # set attrs
            if cover_picture:
                data['cover_picture'] = cover_picture
            for name, value in data.items():
                self.set_new_attr(name, value)
            self.settings()
            self.parent.set_books()
            self.parent.set_authors()
            # show message box to display successfully message
            text = f'The \'{self.val_title}\' book was successfully edited'
            success_message = MessageSuccessUpdated(self, text)

    def delete_btn_clicked(self):
        """ popup message to delete book """
        text = 'Are you sure to delete \'{}\' book'.format(self.val_title)
        message = MessageDeleteBook(self, text)
        message.exec_()
        # conditions
        if message.delete:
            delete_action = self.query_book.delete_book(self.id)
            self.parent.set_books()
            self.parent.set_authors()
            self.back()
        else:
            pass

    def set_new_attr(self, attr, value):
        info = {
            'title': 'val_title',
            'price': 'val_price',
            'date_published': 'val_date',
            'author': 'val_author',
            'cover_picture': 'val_image',
        }
        setattr(self, info[attr], value)

    def browse_picture_file(self):  # OK
        """ Browse book's picture file """
        image_file = BlobImage().browse_profile_picture_file(self.parent, only_return=True)
        self.updated_val_image = BlobImage().read_image(image_file)
        self.set_updated_image()

    def set_updated_image(self):  # OK
        """ set the book's picture """
        blob_image = getattr(self, 'updated_val_image', None)
        if blob_image:
            pixmap = QPixmap()
            pixmap.loadFromData(blob_image)
            self.profile_picture.setPixmap(pixmap)


class FilterDataBook:
    """ Filtering Data """

    def __init__(self, parent, current_data, new_data):
        self.current_data = current_data
        self.new_data = new_data
        self.parent = parent

    def filtering(self):
        """ Filtering the new values """
        merge_data = zip(self.new_data, self.current_data)
        final_data = []
        for new, org in merge_data:
            if list(new.values())[0] != list(org.values())[0]:
                if list(new.values())[0] != None:
                    attr_name = list(new.keys())[0]
                    attr_value = list(new.values())[0]
                    if list(new.keys())[0] == 'author':
                        attr_value = self.parent.query_author.get_author(attr_value)
                    final_data.append(new)
        return final_data

    @staticmethod
    def to_dictionary(data: list):
        """ Convert list class that contained with dictionary to a dict class """
        assert isinstance(data, list)
        final_dict = {}
        for field in data:
            final_dict.update(field)
        return final_dict

