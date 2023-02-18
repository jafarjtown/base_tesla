from dataclasses import dataclass, field, asdict, astuple
# from .auth import csrf_middleware

@dataclass
class Middlewares:
    _middlewares : list = field(default_factory=list, init=False, repr=False)
    
    
    def set_middlewares(self, middlewares):
        for middleware in middlewares:
            self.register_middleware(middleware) 
            
    def register_middleware(self, middleware):
        if middleware not in self._middlewares:
            self._middlewares.append(middleware) 
            
            
    def middlewares(self):
        return self._middlewares
    

    
    
    
middlewares = Middlewares()    

# middlewares.register_middleware(csrf_middleware)