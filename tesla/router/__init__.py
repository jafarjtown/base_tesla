from tesla.router.url import get_dynamic_url

class Path:
    def __init__(self, path, func, name=None):
        self.path = path 
        self._func = func
        self.name = name
        
        
    
    def func(self, request):
        request.params = self.obj
        return self._func(request)
    def match(self, path):
        self.obj = {}
        self.obj = get_dynamic_url(path, self.path)
        # print(self.obj)
        if self.path == path:
            # print('....')
            # print(self.path, self.obj, path)
            # print('.....')
            return True
         
        elif self.obj:
            # print('....')
            # print(self.path, self.obj, path)
            # print('.....')
            # print(path, self.path)
            return True 
        return False

class Router:
    def __init__(self, routes=None):
        self.routes = list(routes) if routes else []
        self.current = None
        self.request = None


    def add_routes(self, paths):
        self.routes.append(*paths)
        # for r in self.routes:
            # print(r.path)

    def get_route(self, path):
        self.current = path
        for route in self.routes:
            # print(route.path) 
            if route.match(self.current):
                
                return route.func
        return None
    
    

router = Router() 