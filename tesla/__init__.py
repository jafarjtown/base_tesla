import imp
from tesla.context import global_context
from tesla.media import mediafiles
from tesla.request import Request
from tesla.response import Http404Response, HttpResponse, Http500Response
from tesla.router import router
from tesla.auth import Authentication
from tesla.session import Session
from tesla.static import staticfiles
from tesla.middleware import middlewares


import string
import numbers
import random as r

def csrf():
    ls = []
    for i in range(10):
        s = ''.join(r.sample([*string.ascii_letters,  *string.hexdigits],55))
        ls.append(s)
    return ls
        

class App: 
    def __init__(self, auth_model,debug=False):
        self.debug = debug
        self.router = router
        self.context = global_context
       
        self.auth_model = auth_model
        self.csrf_tokens = csrf()
        self.middlewares = middlewares
        self.media_file = 'media'

        self.mount('/static', staticfiles.urls)
        self.mount('/media', mediafiles.urls)
        
        pass
    
    def set_auth_model(self, model):
        self.auth_model = model
    def set_routes(self, routes: list):
        for path in routes:
            self.router.add_route(path)

    def mount(self, path, urls):
        # print(path)
        for p in urls:
            p.path = path + p.path
            # print(p.path)
            self.router.add_routes([p])           

    def __call__(self, environ, start_response):
        
        self.authentication = Authentication()
        self.session = Session({})
        self.authentication.model = self.auth_model
        
        request = Request(environ, start_response,self, self.csrf_tokens[r.randint(0, len(self.csrf_tokens)-1)], self.authentication, self.context, self.session, self.auth_model)
        staticfiles.request = request
        
        try:
           
            for mid in self.middlewares.middlewares():
                err = mid(request) 
                if err:
                    return Http500Response(request, err).make_response()
            
            func = self.router.get_route(request.path)
            if func is not None:
                
                response = func(request)
                return response.make_response()
 
            else:
                return Http404Response(request, self.debug, self.router.routes).make_response()
        except Exception as e:
            raise Exception(e)
            # return Http500Response(request, e).make_response()
    
    
    
    