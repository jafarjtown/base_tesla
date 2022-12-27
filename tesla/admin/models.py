
from tesla.auth.modal import UserBaseModal
from tesla.modal import Model, CharField, ListField, TextField, EmailField, PasswordField,DateField

from dataclasses import dataclass
            
            

class User(UserBaseModal):
    
    username = CharField(min=4, max=10)
    email = EmailField(required=True)
    password = PasswordField(min=8, max=16, required=True)
    
    dob = DateField()
    bio = TextField()
    
    
    @classmethod
    def __meta__(self):
        
        return ('id', 'username', 'email')
    
    
    def __str__(self) -> str:
        return self.username