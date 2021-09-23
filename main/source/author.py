from . import QWidget, DataBase, loadUi, QPixmap, QMessageBox, QFont, QIcon
from .query import AuthorBooks, QueryAuthor, BlobImage, MessageSuccessUpdated


class MessageDeleteAuthor(QMessageBox):
    """ Message box to delete the author """

    def __init__(self, parent, text):
        super().__init__(parent)
        font = QFont('Verdana Pro Cond', 12)
        self.setFont(font)
        self.setText(text)
        self.setInformativeText('it will delete all Books of this author')
        self.setIcon(QMessageBox.Question)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # signals
        self.buttonClicked.connect(self.clicked_button)

        self.show()

    def clicked_button(self, button):
        self.button_clicked = button.text()
        if self.button_clicked == '&Yes':
            self.delete = True
        else:
            self.delete = False


class AuthorField:
    """ Settings Author Field """

    def __init__(self, parent):
        self.parent = parent

    def raise_error(self, msg=''):
        self.parent.error_author.setText(msg)

    def set_null_field(self):
        self.parent.full_name.setText('')
        self.parent.age.setValue(0)
        self.parent.profile_picture.clear()
        if hasattr(self, 'profile_picture_file'):
            delattr(self, 'profile_picture_file')


class AuthorWidget(QWidget, DataBase):
    def __init__(self, parent, *data):
        super().__init__()
        loadUi('../user_interface/ui_author.ui', self)
        # attrs
        self.val_full_name = data[0]
        self.val_age = data[1]
        self.image = data[2]
        self.id = data[3]
        self.parent = parent
        self.author_book = AuthorBooks(self.id)

        # class Attrs
        self.query_author = QueryAuthor()

        # Signals
        self.delete_author.clicked.connect(self.delete_author_clicked)
        self.author_detail_btn.clicked.connect(self.author_detail_clicked)

        # call methods
        self.settings()

    def author_detail_clicked(self):
        """ display author detail page """
        data = (self.id, self.val_full_name, self.image,self.val_age)
        author_detail = AuthorDetail(self.parent, *data)
        author_detail.settings()
        self.parent.program.insertWidget(2, author_detail)
        self.parent.program.setCurrentIndex(2)

    def delete_author_clicked(self):
        """ popup message to delete author """
        text = 'Are you sure to delete \'{}\' Author'.format(self.val_full_name)
        message = MessageDeleteAuthor(self, text)
        message.exec_()
        # conditions
        if message.delete:
            if self.author_book.books:
                # deleting author's books
                self.author_book.delete_author_books(self.id)
            self.query_author.delete_author(self.id)
            self.parent.set_books()
            self.parent.set_authors()
            self.parent.set_combo_authors()

    def set_image(self):
        if self.image:
            pixmap = QPixmap()
            pixmap.loadFromData(self.image)
        else:
            pixmap = QPixmap('../images/author_profile_picture.png')
        self.profile_picture.setPixmap(pixmap)

    def settings(self):
        self.full_name.setText(self.val_full_name)
        self.age.setText(str(self.val_age))
        self.set_image()
        # set books
        if self.author_book.books:
            for title, pk in self.author_book.books.items():
                self.books.addItem(title, pk)
        else:
            self.label_3.hide()
            self.books.hide()


class AuthorDetail(QWidget):
    def __init__(self, parent, *data):
        super().__init__()
        loadUi('../user_interface/ui_author_detail.ui', self)
        self.setWindowIcon(QIcon('../images/author_profile_picture.png'))

        # Attrs
        data_ = data or (None, None, None, None)
        self.pk = data_[0]
        self.val_full_name = data_[1]
        self.val_age = data_[3]
        self.val_profile_picture = data_[2]
        # Class Attrs
        self.query_author = QueryAuthor()
        self.parent = parent
        self.author_book = AuthorBooks(self.pk)

        # calling important methods
        self.setWindowTitle(self.val_full_name)

        # Signals
        self.back_btn.clicked.connect(self.back)
        self.delete_btn.clicked.connect(self.delete_author_clicked)
        self.update_btn.clicked.connect(self.update)
        self.browse_picture.clicked.connect(self.browse_picture_file)

    def set_profile_picture(self):
        """ Get the image blob and set pixmap to label """
        if self.val_profile_picture:
            pixmap = QPixmap()
            pixmap.loadFromData(self.val_profile_picture)
        else:
            pixmap = QPixmap('../images/author_profile_picture.jpg')
        self.profile_picture.setPixmap(pixmap)

    def settings(self):
        self.full_name.setText(self.val_full_name)
        self.age.setValue(float(self.val_age))
        self.set_profile_picture()

    def back(self):
        self.parent.program.setCurrentIndex(0)

    def delete_author_clicked(self):
        """ popup message to delete author """
        text = 'Are you sure to delete \'{}\' Author'.format(self.val_full_name)
        message = MessageDeleteAuthor(self, text)
        message.exec_()
        # conditions
        if message.delete:
            if self.author_book.books:
                # deleting author's books
                self.author_book.delete_author_books(self.pk)
            self.query_author.delete_author(self.pk)
            self.parent.set_books()
            self.parent.set_authors()
            self.parent.set_combo_authors()
            self.back()

    def browse_picture_file(self):  # OK
        """ Browse author's picture file """
        image_file = BlobImage().browse_profile_picture_file(self.parent, only_return=True)
        self.new_profile_picture = BlobImage().read_image(image_file)
        self.set_updated_picture_file()

    def set_updated_picture_file(self):  # OK
        """ set the book's picture """
        blob_image = getattr(self, 'new_profile_picture', None)
        if blob_image:
            pixmap = QPixmap()
            pixmap.loadFromData(blob_image)
            self.profile_picture.setPixmap(pixmap)

    def update(self):
        blob_new_profile_picture = getattr(self, 'new_profile_picture', None)
        current_data = (
            {'full_name': self.val_full_name},
            {'age': self.val_age},
            {'profile_picture': self.val_profile_picture},
        )
        new_data = (
            {'full_name': self.full_name.text()},
            {'age': self.age.value()},
            {'profile_picture': blob_new_profile_picture},
        )

        filter_data = FilterDataAuthor(self, current_data, new_data)
        filter_fields = filter_data.filtering()
        data = filter_data.to_dictionary(filter_fields)
        print(data.keys())
        profile_picture = data.get('profile_picture', None)
        print(data.keys())
        is_updated = self.query_author.update_author(self.pk, data,profile_picture)
        if is_updated:
            if profile_picture:
                data['profile_picture'] = profile_picture
            for name, value in data.items():
                print(name)
                self.set_new_attr(name, value)
            self.settings()
            self.parent.set_books()
            self.parent.set_authors()
            self.parent.set_combo_authors()
            # show message box to display successfully message
            text = f'The \'{self.val_full_name}\' author was successfully edited'
            success_message = MessageSuccessUpdated(self, text)

    def set_new_attr(self, name, value):
        info = {
            'full_name': 'val_full_name',
            'age': 'val_age',
            'profile_picture': 'val_profile_picture',
        }
        setattr(self, info[name], value)


class FilterDataAuthor:
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

    @staticmethod
    def set_quote(value):
        return f"'{value}'"
