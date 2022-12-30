from dataclasses import dataclass
from tesla.exceptions import DatabaseException
from tesla.modal import Model
from argon2 import PasswordHasher 



class UserBaseModal(Model):
 
    def save(self):
        
        # check if no User with this username
        # exis
        
        existing_user = self.get(username = self.username)
        # print(existing_user.id != self.id)
        ph = PasswordHasher()
        if existing_user and existing_user.id != self.id :
            raise DatabaseException('User with this username already exists')
        # hashes the password
        elif existing_user == None:
            password = ph.hash(self.password)
            self.password = password
        elif ph.check_needs_rehash(self.password):
            password = ph.hash(self.password)
            self.password = password
        # elif ph.    
        return super().save()