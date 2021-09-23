from . import sqlite3, QPixmap, QFileDialog, QMessageBox, QFont


class MessageSuccessUpdated(QMessageBox):
    """ Show successful editing message """

    def __init__(self, parent, text):
        super().__init__(parent)
        font = QFont('Verdana Pro Cond', 12)
        self.setFont(font)
        self.setWindowTitle('Successfully')
        self.setText(text)
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)
        self.show()


class DialogFileName(QFileDialog):
    """ Browse File """

    def __init__(self, path):
        super().__init__()
        self.path = path

    def browse_file(self, parent):
        file_name = self.getOpenFileName(
            parent,
            'Browse Picture',
            self.path,
            'Image File (*.png, *jpg)'
        )
        return file_name[0]


class DataBase:
    """ Connect to DataBase """

    def __init__(self):
        self.connection = sqlite3.connect('library.db')
        self.cursor = self.connection.cursor()


class BlobImage(DataBase):
    """ The Methods For Storing Image """

    def __init__(self):
        super().__init__()

    @staticmethod
    def read_image(image):
        """ Read The Image File to Save in Database """
        if not image:
            return None
        with open(str(image), 'rb') as image_file:
            blobImage = image_file.read()
        return blobImage

    @staticmethod
    def browse_picture_file(parent):
        """ Browse and set Picture of Book """
        dialog_file_name = DialogFileName(parent.path)
        picture_book_file = dialog_file_name.browse_file(parent)
        if picture_book_file:
            parent.picture_book_file = picture_book_file
            pixmap = QPixmap(parent.picture_book_file)
            parent.picture_book.setPixmap(pixmap)

    @staticmethod
    def browse_profile_picture_file(parent, only_return=False):
        """ Browse and set Author's Profile Picture """
        dialog_file_name = DialogFileName(parent.path)
        profile_picture_file = dialog_file_name.browse_file(parent)
        if profile_picture_file:
            if only_return:
                return profile_picture_file
            else:
                parent.profile_picture_file = profile_picture_file
                pixmap = QPixmap(parent.profile_picture_file)
                parent.profile_picture.setPixmap(pixmap)


class QueryAuthor(DataBase):
    """ SQL Query For Author """

    def __init__(self):
        super().__init__()

    def all_authors(self):
        """ Fetch all Authors """
        query = 'SELECT * FROM Author ORDER BY id DESC'
        self.cursor.execute(query)
        authors = self.cursor.fetchall()
        return authors

    def insert_author(self, *data):
        """ Insert Author to Table """
        query = 'INSERT INTO Author(id,full_name,age,profile_picture) VALUES (NULL,?,?,?)'
        self.cursor.execute(query, data)
        self.connection.commit()
        return self.cursor.lastrowid

    def delete_author(self, pk):
        query = f'DELETE FROM Author WHERE id={pk}'
        self.cursor.execute(query)
        self.connection.commit()
        return self.cursor.lastrowid

    def get_author(self, pk):
        query = f'SELECT * FROM Author WHERE id={pk}'
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def update_author(self, primary_key, fields, profile_picture):
        res = False
        if profile_picture:
            self.update_profile_picture(primary_key, profile_picture)
            res = True
            fields.pop('profile_picture')
        params = QueryAuthor.to_sql_parameters(fields)
        if params:
            query = f'UPDATE Author SET {params} WHERE id={primary_key}'
            self.cursor.execute(query)
            self.connection.commit()
            res = True
        return res

    def update_profile_picture(self, pk, profile_picture):
        query = f'UPDATE Author SET profile_picture=? WHERE id={pk}'
        self.cursor.execute(query, (profile_picture,))
        self.connection.commit()
        return True

    @staticmethod
    def to_sql_parameters(dictionary: dict) -> str:
        info = {
            'full_name': QueryAuthor.set_quote,
            'age': int,
            'profile_picture': str,
        }
        data = map(lambda k: f'{k}={info[k](dictionary[k])}', dictionary)
        final_data = ','.join(list(data))
        return final_data

    @staticmethod
    def set_quote(value):
        return f"'{value}'"


class QueryBook(DataBase):
    """ SQL Query For Book """

    def __init__(self):
        super().__init__()

    def all_books(self):
        """ Fetch All Book """
        query = 'SELECT * FROM Book ORDER BY id DESC'
        self.cursor.execute(query)
        books = self.cursor.fetchall()
        return books

    def get_book(self, pk):
        """ Get the data of Book """
        query = f'SELECT * FROM BOOK WHERE id={pk}'
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def insert_book(self, *data):
        """ Insert Book to Table """
        query = 'INSERT INTO Book VALUES (NULL,?,?,?,?,?)'
        self.cursor.execute(query, data)
        self.connection.commit()
        return self.cursor.lastrowid

    def delete_book(self, pk):
        """ Delete the Book from DataBase """
        query = f'DELETE FROM Book WHERE id={pk}'
        self.cursor.execute(query)
        self.connection.commit()
        return self.cursor.lastrowid

    def update_book(self, primary_key, fields, cover_picture):
        res = False
        if cover_picture:
            self.update_cover_picture(primary_key, cover_picture)
            res = True
            fields.pop('cover_picture')
        params = QueryBook.to_sql_parameters(fields)
        if params:
            query = f'UPDATE Book SET {params} WHERE id={primary_key}'
            self.cursor.execute(query)
            self.connection.commit()
            res = True
        return res

    def update_cover_picture(self, pk, cover_picture):
        query = f'UPDATE Book SET cover_picture=? WHERE id={pk}'
        self.cursor.execute(query, (cover_picture,))
        self.connection.commit()
        return True

    @staticmethod
    def set_quote(value):
        return f"'{value}'"

    @staticmethod
    def to_sql_parameters(dictionary: dict) -> str:
        info = {
            'title': QueryBook.set_quote,
            'price': float,
            'date_published': QueryBook.set_quote,
            'author': int,
            'cover_picture': str,
        }
        data = map(lambda k: f'{k}={info[k](dictionary[k])}', dictionary)
        final_data = ','.join(list(data))
        return final_data


class AuthorBooks(DataBase):
    """ Get All books for specific author """

    def __init__(self, pk):
        super().__init__()
        self.pk = pk
        self.books = {}
        if self.pk:
            self.append_title()

    def all_books(self):
        query = f'SELECT title,id FROM Book WHERE author={self.pk} ORDER BY id DESC'
        self.cursor.execute(query)
        self.records = self.cursor.fetchall()
        return self.records

    def append_title(self):
        self.all_books()
        for title, pk in self.records:
            self.books[title] = pk

    def delete_author_books(self, pk):
        try:
            query = f'DELETE FROM Book WHERE author={pk}'
            self.cursor.execute(query)
            self.connection.commit()
        except Exception:
            return False
        return True
