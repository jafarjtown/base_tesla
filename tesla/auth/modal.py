from dataclasses import dataclass
from tesla.exceptions import DatabaseException
from tesla.modal import Model



@dataclass
class UserBaseModal(Model):
    # def __init__(self, username, password, email='', *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    username : str
    email : str
    password : str

    def save(self):
        # check if no User with this username
        # exis
        if not self.get(username = self.username, id = self.id):
            raise DatabaseException('User with this username already exists')
        # hashes the password
        return super().save()