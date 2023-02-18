from tesla.response import Render
from tesla.pagination import Paginator

class View:
    model = None
    lookup = None
    template = None
    pagination = False
    pagination_count = 20
    response = Render
    

    def as_view(cls, **kwargs):
        
        def wrapper(request, *args, **kwargs):
            method = request.method
            if hasattr(cls, method.lower()):
                func = getattr(cls, method.lower())
                return func(request, *args, **kwargs)
            else:
                raise Exception(f'{method} Method is not allowed or provided')
            
        return wrapper
    

class DetailView(View):
    
    def get(self, request, *args, **kwargs):
        
        lk = request.params.get(self.lookup)
        all = self.model.all(models=True)
        obj = None
        for o in all:
            if getattr(o, self.lookup) == lk:
                obj = o
                break
        if issubclass(self.response, Render):
            context = {}
            context['obj'] = obj
            return self.response(request, self.template, context)
        if obj == None:
            json_obj = {}
        else:
            json_obj = obj.json()    
        return self.response(request, json_obj)

class RetrieveAllView(View):
    
    def get(self, request, *args, **kwargs):
        all = self.model.all(models=True)

        if issubclass(self.response, Render):
            context = {}
            context['objs'] = all
            return self.response(request, self.template, context)
        json_obj = []
        for o in all:
            json_obj.append(o.json())
        if self.pagination:
            page = request.query.get('page')
            if not page:
                page = 1
            paginator = Paginator(all,json=True, page=int(page), limit=1)
            json_obj = {
                'page': 1,
                'next': paginator.next(),
                'previous': paginator.previous(),
                'data': paginator.current()
            } 
        
   
        return self.response(request, json_obj)  