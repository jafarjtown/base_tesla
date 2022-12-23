from dataclasses import dataclass
from tesla.exceptions import DatabaseException
from tesla.modal import Model
import bcrypt



class UserBaseModal(Model):
 
    def save(self):
        # check if no User with this username
        # exis
        
        existing_user = self.get(username = self.username)
        # print(existing_user.id != self.id)
        if existing_user and existing_user.id != self.id :
            raise DatabaseException('User with this username already exists')
        # hashes the password
        elif existing_user == None:
            password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt(prefix=b'2a')).decode()
            self.password = password
        return super().save()