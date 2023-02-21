from tesla.context import global_context
from tesla.media import mediafiles
from tesla.request import Request
from tesla.response import Http404Response, Http500Response, Response
from tesla.router import router
from tesla.auth import Authentication
from tesla.session import Session
from tesla.static import staticfiles
from tesla.middleware import middlewares
from tesla.auth.modal import User

import string
import random as r



def csrf():
    ls = []
    for i in range(10):
        s = ''.join(r.sample([*string.ascii_letters,  *string.hexdigits],55))
        ls.append(s)
    return ls
        

import random
import string

class _App:
    def __init__(self):
        self.debug = True
        self.dynamic_csrf = True
        self.router = router
        self.context = global_context
        self.templates_folders = []
        self.registered_models = []
        self.auth_model = User
        self.csrf_tokens = csrf()
        self.middlewares = middlewares
        self.media_file = 'media'
        self.base_dir = None
        self.db = 'tesla.database.SQL'
        

        self.mount('/static', staticfiles.urls, app_name='static')
        self.mount('/media', mediafiles.urls, app_name='static')

    def set_auth_model(self, model):
        self.auth_model = model
        
    def set_routes(self, routes: list):
        for path in routes:
            self.router.add_route(path)

    def mount(self, path, urls, app_name):
        for p in urls:
            if app_name != None:
                if p.name:
                    p.name += f'_{app_name}'
                p.path = path + p.path
            self.router.add_routes([p])           

    def __call__(self, environ, start_response):

        self.authentication = Authentication()
        self.session = Session({})
        if self.auth_model is not None:
            self.authentication.model = self.auth_model
        
        request = Request(environ, start_response, self, self.authentication, self.context, self.session, self.auth_model)
        request.dynamic_csrf = self.dynamic_csrf
        staticfiles.request = request
        
        try:
            for mid in self.middlewares.middlewares():
                # print(request.csrf_check)
                err = mid(request) 
                if err:
                    return Http500Response(request, err, self.debug).make_response()
            request.pass_csrf()
            # print(request.csrf_check)
            
            func = self.router.get_route(request.path)
            if func is not None:
                # print(func)
                response = func(request)
                return response.make_response()


            else:
                if self.debug == False:
                    func =  self.router.get_404()
                
                    if func is not None:
                        r = func(request)
                        return r.make_response()
                    else:
                        return Http404Response(request, self.debug, self.router.routes).make_response()
                return Http404Response(request, self.debug, self.router.routes).make_response()    
        except Exception:
            import traceback
            print(traceback.format_exc())
            return Http500Response(request, traceback.format_exc(), self.debug).make_response()










TeslaApp = _App()    
    
    