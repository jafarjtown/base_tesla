
import tesla
from tesla.auth.decorators import login_required
from tesla.auth.views import login as user_login, logout as user_logout, authenticate
from tesla.functions import url
from tesla.response import HttpResponse, Redirect, Render, JsonResponse
from tesla.pyhtml import CT
from .models import User
from .forms import AdminForm
from tesla.database.jsondb import JsonDB
# from tesla.views import View, DetailView, RetriveAllView
from tesla.pagination import Paginator
from tesla.search import Search

from . import collections_manage

# your views


@login_required(path='admin:login')
def collections(request):
    context = {}
    context['names'] = collections_manage.colls()

    return Render(request, 'admin/colls.html', context)


@login_required(path='admin:login')
def collection(request):
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    model = model_db.model()
    context = {}
    search_for = request.query.get('search')
    if search_for:
        models = Search(model.all(models=True), search_for,
                        model.__meta__()).result()
        context['search_for'] = search_for
    else:
        models = model_db.all(models=True)
    page = request.query.get('page')
    if not page:
        page = 1
    paginator = Paginator(models, page=int(page))
    # print(models)
    context['objs'] = paginator.current()
    context['next'] = paginator.next()
    context['previous'] = paginator.previous()
    context['pages'] = paginator.pages_lists()
    context['page'] = paginator.page
    # print(paginator.pages_lists())
    # context['objs'] = models
    context['info'] = model.__meta__()
    context['collection'] = collection
    return Render(request, 'admin/col.html', context)


@login_required(path='admin:login')
def collection_obj(request):
    # print(request.user.is_super_user)
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
        # print(data)
        obj.update(**data)
        obj = obj.save()

        return Redirect(request, 'admin:collection_obj', lookup=lookup, collection=collection)
    context = {}
    context['lookup'] = lookup
    context['collection'] = collection
    context['form'] = form
    return Render(request, 'admin/obj.html', context)


@login_required(path='admin:login')
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


@login_required(path='admin:login')
def collection_del(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    obj = model_db.model().get(id=lookup)
    obj.delete()
    return Redirect(request, 'admin:collection', collection=collection)


@login_required(path='admin:login')
def collection_del_all(request):
    lookup = request.params.get('lookup')
    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    objs = model_db.model().all(models=True)
    for obj in objs:
        obj.delete()
    return Redirect(request, 'admin:collection', collection=collection)


@login_required(path='admin:login')
def collection_download(request):

    collection = request.params.get('collection')
    model_db = JsonDB(collection + '/')
    objs = model_db.model().all(models=False)
    return JsonResponse(request, objs)


@login_required(path='admin:login')
def admin_account(request):
    obj = tesla.TeslaApp.auth_model.get(id=request.user.id)
    if 'json' in request.query:
        return JsonResponse(request, obj.json())
    # print(obj)
    form = AdminForm(obj)
    form.model = tesla.TeslaApp.auth_model
    form.fields = '__all__'
    if request.method == 'POST':
        data = request.post.data
        del data['csrfmiddleware']
        obj.update(**data)
        obj.save()
    context = {}
    context['form'] = form
    return Render(request, 'admin/account.html', context)


@login_required(path='admin:login')
def admin_settings(request):
    ...


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
        user = User.get(username=u)
        if authenticate(user, p):
            user_login(request, user)
            return Redirect(request, 'admin:index')
    return Render(request, 'admin/login.html')


def register(request):
    if request.method == 'POST':
        u = request.post.get('username')
        e = request.post.get('email')
        p = request.post.get('password')
        User.create(username=u, email=e, password=p)
        return Redirect(request, 'admin:login')
    return Render(request, 'admin/register.html')


def reset_password(request):
    if request.method == 'POST':
        # print('es')
        pass
    return Render(request, 'admin/reset-password.html')


def logout(request):
    user_logout(request)
    return Redirect(request, 'admin:login')
