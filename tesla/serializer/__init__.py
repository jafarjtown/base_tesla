
from tesla.response import JsonResponse
from tesla.pagination import Paginator


class Serializer:
    
    model = None
    
    dept = 1
    
    
    # def __init__(self) -> None:
    #     self.models = self.model.all()
    
    
    def serialize(self):
        return self.model.all(models=False)
        ...
    
class APIView:
    model = None
    lookup = None
    pagination = False
    pagination_count = 20
    response = JsonResponse
    

    def as_view(cls, **kwargs):
        
        def wrapper(request, *args, **kwargs):
            method = request.method
            if hasattr(cls, method.lower()):
                func = getattr(cls, method.lower())
                return func(request, *args, **kwargs)
            else:
                raise Exception(f'{method} Method is not allowed or provided')
            
        return wrapper
    

class RetrieveAPIView(APIView):

    def get(self, request, *args, **kwargs):
        all = self.model.all(models=True)

        
        json_obj = []
        for o in all:
            json_obj.append(o.json())
        if self.pagination:
            page = request.query.get('page')
            if not page:
                page = 1
            paginator = Paginator(all ,json=True, page=int(page), limit=self.pagination_count)
            data = paginator.current()
            json_obj = {
                'count': len(data),
                'all': len(all),
                'next': paginator.next(),
                'previous': paginator.previous(),
                'data': data
            } 
        
   
        return self.response(request, json_obj)  
    
class CreateRetrieveAPIView(RetrieveAPIView):
    
    def post(self, request, *args, **kwargs):
        
        self.model.create(**request.post.data)
        
        return self.get(request, *args, **kwargs) 
    

class UpdateDelete(APIView):
    
    def get(self, request, *args, **kwargs):
        lookup = request.params.get(self.lookup)
        all = self.model.all()
        model = None
        # print(lookup)
        for i in all:
            js = i.json()
            if js[self.lookup] == lookup:
                # print(js.get(self.lookup) == lookup)
                model = i.json()
                break
        return self.response(request, model) 
    
    def put(self, request, *args, **kwargs):
        lookup = request.params.get(self.lookup)
        all = self.model.all()
        model = None
        # print(lookup)
        for i in all:
            js = i.json()
            if js[self.lookup] == lookup:
                # print(js.get(self.lookup) == lookup)
                i.update(**request.post.data)
                i.save()
                model = i.json()
                break
        return self.response(request, model)
    
    def delete(self, request, *args, **kwargs):
        lookup = request.params.get(self.lookup)
        all = self.model.all()
        model = None
        # print(lookup)
        for i in all:
            js = i.json()
            if js[self.lookup] == lookup:
                # print(js.get(self.lookup) == lookup)
                i.delete()
                break
        return self.response(request, None)  