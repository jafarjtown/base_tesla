
from tesla.router import Path
from tesla.response import Render, JsonResponse,Response

from tesla import TeslaApp
import os
import sys
import ast


def join_path(paths):
    count = 0
    r = ''
    for p in paths:
        r += p


def wrapper(pg, backends=[], context={}):
    # TeslaApp.backend
    pth = os.path.join(TeslaApp.backend)
    sys.path.append(pth)
    import views

    def req(request):
        b = {}
        redirect = False
        for v in backends:
            func = getattr(views, v)
            obj = func(request)
            if type(obj) != dict:
                if issubclass(type(obj), Response):
                    redirect = obj
                    break
            b = {**context, **b, **obj}
        # print(redirect)
        if redirect:
            
            return redirect
        return Render(request, pg, b)
    return req


def get_pages(address) -> list:
    routes = []
    pgs = os.listdir(address)

    for pg in pgs:
        if os.path.isdir(address / pg):
            pass
        else:
            name, *views_file, _ = pg.split('.')
            context = {}

            if name.startswith('index'):
                name = name.replace('index', '')
            if '_' in name:
                n = ''
                for p in name.split('_'):
                    if '[' and ']' in p:
                        n = os.path.join(n, '{' + p[1:-1] + '}')
                    else:
                        n = os.path.join(n, p)
                name = n.replace('\\', '/')
            p = Path(name, wrapper(pg, context=context,
                     backends=views_file), name=name)
            routes.append(p)

    return routes


def config_api_route(route):
    pth = os.path.join(TeslaApp.base_dir, 'api')
    sys.path.append(pth)
    try:
        import api
        apis = [a for a in dir(api) if not a.startswith('__')]

        def wrapper(api):
            def req(request):
                b = api(request)
                return JsonResponse(request, b)
            return req
        routes = [Path(a, wrapper(getattr(api, a)), name=a) for a in apis]
        TeslaApp.mount('/'+route+'/', routes, route)
    except Exception as e:
        raise Exception(e)
