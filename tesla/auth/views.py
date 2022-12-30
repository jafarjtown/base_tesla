from tesla import TeslaApp
from tesla.functions import redirect
from tesla.pyhtml import PYHTML
from tesla.pyhtml.tags import CT, CSS, CSSGroup
from tesla.response import HttpResponse
from tesla.auth.forms import LoginForm, RegisterForm
from tesla.database.localdb import global_db


import random as r
import string
from datetime import datetime
# LoginForm().save()


def login(request, user):
    session = ''.join(r.sample(string.ascii_letters, 50))

    request.set_cookie('user_session', session)
    global_db.add(session, user)

    request.session.add_to_session(
        session, {'__id': user.id, 'session': str(session)})


def logout(request):
    request.headers += [('Set-Cookie',
                        'user_session=null;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/')]


def LoginView(request):

    if request.is_authenticated:
        return redirect(request, '/')
    form_data = LoginForm()

    if request.method == 'POST':
        username = request.post.get('username')
        password = request.post.get('password')
        user = TeslaApp.auth_model.get(username=username, password=password)
        # print(user)
        if user:
            login(request, user)
            return redirect(request, '/')
        # print(username, password)
    doc = PYHTML()
    head, body = doc.create_doc()

    # head
    title = CT('title', 'Tesla | Authentication View')
    style = CT('style', '''
               *{
    box-sizing: border-box;
    margin: 0;
}

form{
    width: 320px;
    height: fit-content;
    border: 1px solid;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 15px;
    font-size: large;
    margin: 20px auto;
    
    background-color: #2196F3;
    color: white;
}
input{
    width: 100%;
    padding: 10px;
    border: 1px solid lightgray ;
    border-radius: 5px;
    outline: none;
    
    background-color: #fafafa;
}
#rmb{
    display: flex;
    align-items: center;
    width: 100%;
    gap: 10px;
}
#rmb > input{
    width: fit-content;
}
button{
    padding: 10px;
    border-radius: 5px;
    border: none;
    background-color: #26ff00;
    cursor: pointer;
}

               ''')
    p = CT('p', '*This is default Tesla login page')
    form_style = CSS(
        display='flex',
        flexDirection='column',
        alignItems='center',
        padding='10px',
        margin='auto',
        marginTop='30px',
        width='250px',
        gap='10px',
        backgroundColor='lightgray',
        borderRadius='5px'
    )

    head.append(title, style)
    # form
    form = CT('form', method='POST')
    csrf = CT('input', value=request.csrf, name='csrfmiddleware', hidden=1)
    h2 = CT('h2', 'User login view')

    login_btn = CT('button', 'login')
    form.append(h2, csrf, form_data, login_btn, p)
    body.append(form)
    return HttpResponse(request, str(doc))


def RegisterView(request):

    if request.is_authenticated:
        return redirect(request, '/')
    form_data = RegisterForm()

    if request.method == 'POST':
        username = request.post.get('username')
        password = request.post.get('password')
        user = form_data.validate(request.post, TeslaApp.auth_model)
        # print(request.post.get('rmb'))
        # user = User(username=username, password=password).save()
        # print(user)
        if user:
            login(request, user)
            return redirect(request, '/')
        # print(username, password)
    doc = PYHTML()
    head, body = doc.create_doc()

    # head
    title = CT('title', 'Tesla | Authentication View')
    style = CT('style', '''
               *{
    box-sizing: border-box;
    margin: 0;
}

form{
    width: 320px;
    height: fit-content;
    border: 1px solid;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 15px;
    font-size: large;
    margin: 20px auto;
    
    background-color: #2196F3;
    color: white;
}
input{
    width: 100%;
    padding: 10px;
    border: 1px solid lightgray ;
    border-radius: 5px;
    outline: none;
    
    background-color: #fafafa;
}
#rmb{
    display: flex;
    align-items: center;
    width: 100%;
    gap: 10px;
}
#rmb > input{
    width: fit-content;
}
button{
    padding: 10px;
    border-radius: 5px;
    border: none;
    background-color: #26ff00;
    cursor: pointer;
}

               ''')
    p = CT('p', '*This is default Tesla Register page')

    head.append(title, style)
    # form
    form = CT('form', method='POST', enctype="multipart/form-data")
    csrf = CT('input', value=request.csrf, name='csrfmiddleware', hidden=1)
    h2 = CT('h2', 'User Register view')

    login_btn = CT('button', 'login')
    form.append(h2, csrf, form_data, login_btn, p)
    body.append(form)
    return HttpResponse(request, str(doc))


def authenticate(user, en_password):
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    try:
        ph.verify(user.password, en_password)
        if ph.check_needs_rehash(user.password):
            user.password = ph.hash(password)
            user.save()

            ...
        return True
    except:
        return False
