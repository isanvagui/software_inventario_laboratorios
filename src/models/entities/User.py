from werkzeug.security import check_password_hash
from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, username, password, fullname="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

# print(generate_password_hash ("suscribete")) //esta linea se utiliza para crear nuevos usuarios y esta (,generate_password_hash) porción de codigo lo pego en la primer linea
