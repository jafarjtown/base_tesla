
from tesla.auth.modal import UserBaseModal
from tesla.modal import Model, CharField, FileField, TextField, EmailField, PasswordField,DateField, BooleanField, ImageField, NumberField, PositiveNumberField, NegativeNumberField

from dataclasses import dataclass

# class Permission(Model):
#     can_edit = BooleanField()
#     can_create = 
            

class User(UserBaseModal):
    
    username = CharField(min=4, max=10)
    email = EmailField(required=True)
    password = PasswordField(min=8, max=16, required=True)
    
    dob = DateField()
    bio = TextField()
    age = PositiveNumberField()
    dept = NegativeNumberField()
    account = NumberField()
    profile_pic = ImageField(upload_to='users_files')
    profile_doc = FileField(upload_to='users_files')
    
    is_super_user = BooleanField()
    
    
    @classmethod
    def __meta__(self):
        
        return ('id', 'username', 'email')
    
    
    def __str__(self) -> str:
        return self.username