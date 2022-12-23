
from tesla.auth.decorators import login_required
from tesla.auth.views import login as user_login
from tesla.functions import url
from tesla.response import HttpResponse, Redirect, Render, JsonResponse
from tesla.pyhtml import CT
from .models import User
from .forms import AdminForm
from tesla.database.jsondb import JsonDB


from . import collections_manage

# your views


def collections(request):
    context = {}
    context['names'] = collections_manage.colls()
    return Render(request, 'admin/colls.html', context)

def collection(request):
    collection = request.params.get('collection') 
    model_db = JsonDB(collection + '/')
    models = model_db.all(models=True)
    model = model_db.model()
    # print(models)
    context = {}
    context['objs'] = models
    context['info'] = model.__meta__()
    context['collection'] = collection
    return Render(request, 'admin/col.html', context)

def collection_obj(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    obj = model_db.model().get(id=lookup)
    if 'json' in request.query:
        return JsonResponse(request, obj.json())
     
    form = AdminForm(obj)
    form.model = model_db.model
    form.fields = '__all__'
    if request.method == 'POST':
        data = request.post.data
        del data['csrfmiddleware']
        obj.update(**data)
        obj.save()
    context = {}
    context['lookup'] = lookup
    context['collection'] = collection
    context['form'] = form
    return Render(request, 'admin/obj.html', context)

def collection_new(request):
    context = {}
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    model = model_db.model()
    form = AdminForm()
    form.model = model_db.model
    form.fields = '__all__'
    context['form'] = form
    if request.method == 'POST':
        data = request.post.data
        del data['csrfmiddleware']
        f = form.validate(**data) 
        f.save()
        return Redirect(request, 'admin:collection_obj', collection=collection, lookup=f.id)
    return Render(request, 'admin/col_n.html', context)    
    
def collection_del(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    obj = model_db.model().get(id=lookup)
    obj.delete()
    return Redirect(request, 'admin:collection', collection=collection)


def collection_del_all(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    objs = model_db.model().all(model=True)
    for obj in objs:
        obj.delete()
    return Redirect(request, 'admin:collection', collection=collection)


def collection_download(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    objs = model_db.model().all(model=False)
    print(objs)
    return JsonResponse(request, objs)

@login_required(path='admin:login')
def index(request):
    context = {}
    context['names'] = collections_manage.colls()
    # print(context)
    return Render(request, 'admin/base_admin.html', context)


def login(request):
    
    if request.method == 'POST':
        u = request.post.get('username')
        p = request.post.get('password')
        user = User.get(username=u, password=p)
        if isinstance(user, User):
            user_login(request , user)
            return Redirect(request, 'admin:index')
    return Render(request, 'admin/login.html')



def register(request):
    if request.method == 'POST':
        u = request.post.get('username')
        e = request.post.get('email')
        p = request.post.get('password')
        user = User.create(username=u, email=e, password=p)
        user.save()
    return Render(request, 'admin/register.html')


def reset_password(request):
    if request.method == 'POST':
        print('es')
    return Render(request, 'admin/reset-password.html')


def logout(request):
    request.clear_cookie()
    return Redirect(request, 'admin:register')