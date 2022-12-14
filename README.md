# tesla-web

Under construction! Not ready for use yet! Currently experimenting and planning!

Developed by Jafar Idris.

### Examples of How To Use (Buggy Alpha Version)

## Creating a project

```cmd
tesla startproject
```

it will prompt you to enter your project name, a folder will be created with that name navigate to the project folder.

## project structure 
```
[project_name]
     - core
         - settings.py
         - urls.py
     - manage.py
    
```
- ### settings.py
```python
from tesla.static import staticfiles
from tesla import TeslaApp

from tesla.admin.models import User
from tesla.admin import abs_path, register_collections
import os
from pathlib import Path as Pa

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Pa(__file__).resolve().parent.parent 

TeslaApp.middlewares.set_middlewares([])

TeslaApp.auth_model = User

TeslaApp.templates_folders = [
    os.path.join(abs_path, 'templates'),    os.path.join(BASE_DIR, 'templates')
]

# Register models to Admin panel
register_collections(User)

staticfiles.paths = [ os.path.join(BASE_DIR, 'static'), os.path.join(abs_path, 'statics')]
        

```

- ### urls.py
```python

from tesla.router.url import Mount

from tesla.admin.urls import patterns as admin_urls

# map admin urls with the project 
Mount('/admin/', admin_urls, app_name='admin')

```


- Start server

to start Tesla web server, open your command prompt and run Belo code
```cmd
tesla serve [port]
```
port = 8000 by default

open your browser and navigate to the address display on your command line, you will see a 404 page because no route is specified

## Creating an Application

```cmd
tesla startapp
```

it will prompt you to enter your Application name, a folder will be created with that name navigate to the Application folder.

## Application structure
```
[app_name]
    - models.py
    - urls.py
    - views.py

```

- ### models.py
```python
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
```

- ### urls.py
```python
from tesla.router import Path
from . import views

# your urls path should be here
patterns = [
    Path('', views.index, name='index'),
    Path('login', views.login, name='login'),
    Path('logout', views.logout, name='logout'),
    Path('register', views.register, name='register'),
    Path('reset-password', views.reset_password, name='reset-password'),
    Path('collections', views.collections, name='collections'),
    Path('collections/{collection}/', views.collection, name='collection'),
    Path('collections/{collection}/new/', views.collection_new, name='collection_new'),
    Path('collections/{collection}/delete/', views.collection_del_all, name='collection_del_all'),
    Path('collections/{collection}/json/', views.collection_download, name='collection_download'),
    Path('collections/{collection}/{lookup}/', views.collection_obj, name='collection_obj'),
    Path('collections/{collection}/{lookup}/delete/', views.collection_del, name='collection_del')
]

```
---

- ### views.py
a view is a function that return instance of Response
example
```python
def login(request):
    
    if request.method == 'POST':
        u = request.post.get('username')
        p = request.post.get('password')
        user = User.get(username=u, password=p)
        if isinstance(user, User):
            user_login(request , user)
            return Redirect(request, 'admin:index')
    return Render(request, 'admin/login.html')

```
## What Tesla Web will consist

- [x] build-in Admin panel
- [x] build-in API provider ( for registered models )
- [ ] build-in Authentication mechanism 
- [ ] Documentation website 
- [ ] community 