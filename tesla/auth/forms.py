from dataclasses import dataclass
from tesla.form import Field, Form


@dataclass
class LoginForm(Form):
    username : str = Field(placeholder = 'Enter username', name='username', label_text='Username',data_type = str)
    password : str = Field(placeholder = 'Enter password', name= 'password', type = 'password', label_text='Password', data_type = str)
    remember_me : bool = Field(placeholder='Remember Me', type='checkbox', name='rmb', label_text='Remember Me', label_id='rmb', data_type = bool)

@dataclass
class RegisterForm(Form):
    username : str = Field(placeholder = 'Enter username', name='username', label_text='Username', data_type = str)
    password : str = Field(placeholder = 'Enter password', name= 'password', type = 'password', label_text='Password', data_type = str)
    confirm_password : str = Field(placeholder = 'Enter password', name= 'confirm_password', type = 'password', label_text='Confirm Password', data_type = str)
    remember_me : bool = Field(placeholder='Remember Me', type='checkbox', name='remember_me', label_text='Remember Me', label_id='rmb', data_type = bool)

