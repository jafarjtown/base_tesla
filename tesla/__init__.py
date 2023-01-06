from tesla.context import global_context
from tesla.media import mediafiles
from tesla.request import Request
from tesla.response import Http404Response, Http500Response
from tesla.router import router
from tesla.auth import Authentication
from tesla.session import Session
from tesla.static import staticfiles
from tesla.middleware import middlewares
from tesla.auth.modal import UserBaseModal

import string
import random as r



def csrf():
    ls = []
    for i in range(10):
        s = ''.join(r.sample([*string.ascii_letters,  *string.hexdigits],55))
        ls.append(s)
    return ls
        

class _App: 
    def __init__(self):
        self.debug = True
        self.router = router
        self.context = global_context
        self.templates_folders = []
        self.registered_models = []
       
        self.auth_model = UserBaseModal
        self.csrf_tokens = csrf()
        self.middlewares = middlewares
        self.media_file = 'media'

        self.mount('/static', staticfiles.urls, app_name='static')
        self.mount('/media', mediafiles.urls, app_name='static')
        
        pass
    
    def set_auth_model(self, model):
        self.auth_model = model
    def set_routes(self, routes: list):
        for path in routes:
            self.router.add_route(path)

    def mount(self, path, urls, app_name):
        # print(path)
        for p in urls:
            # print(p)
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
        
        request = Request(environ, start_response,self, self.csrf_tokens[r.randint(0, len(self.csrf_tokens)-1)], self.authentication, self.context, self.session, self.auth_model)
        staticfiles.request = request
        
        try:
            request.pass_csrf()
            for mid in self.middlewares.middlewares():
                err = mid(request) 
                if err:
                    return Http500Response(request, err, self.debug).make_response()
            
            func = self.router.get_route(request.path)
            if func is not None:
                
                response = func(request)
                # response.templates_folders.extend(self.template_folders)
                # print(type(response))
                return response.make_response()
 
            else:
                return Http404Response(request, self.debug, self.router.routes).make_response()
        except Exception:
            import traceback
            # print('jjujujuju')
            # raise Exception(e)
            print(traceback.format_exc())
            return Http500Response(request, traceback.format_exc(), self.debug).make_response()
    

TeslaApp = _App()    
    
    