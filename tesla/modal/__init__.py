from copy import deepcopy
from dataclasses import InitVar, asdict, dataclass, field

from datetime import datetime
# from tempfile import TemporaryFile
from tesla.database.jsondb import JsonDB
import uuid

from tesla.request import TemporaryFile

_no_default_object = object()
def property_obj(arr):
    a = []
    for l in arr:
        if not l.startswith('__'):
            a.append(l)
            
    return a        

def ModalId():
    cache = {}
    def generate(modal):
         
        if modal in cache.keys():
             
            cache[modal] += 1
            return  cache[modal]
        cache[modal] = 1
        return 1
    return generate

id_gener = ModalId()

class ModalObject:
    def __init__(self, obj):
        self.obj = obj


    def filter(self, **kwargs):
        pass

    def get(self, **kwargs):
        return self.obj.get(**kwargs)
        


@dataclass
class bModel:
    id : str
    timestamp : str

    @classmethod
    def get(cls,  **kwargs):
        # print(dir(cls))
        db = JsonDB(collection = cls.__name__ + "/") 
        js = db.get(kwargs)
        # print(js)
        
        return type(cls.__name__, (), js)
        # for k, v in js.items():
        #     setattr(cls, k, v)
        print(cls.__init__(**js))
        return cls.__init__(cls, **js)

    @classmethod
    def filter(cls, **kwargs):
        # print(dir(cls))
        db = JsonDB(collection = cls.__name__ + "/") 
        return db.filter(kwargs)   

    @classmethod
    def all(cls, **kwargs):
        # print(dir(cls))
        db = JsonDB(collection = cls.__name__ + "/") 
        return db.all()       
    
    @property
    def db(self):
        return JsonDB(collection = self.modal_name() + "/") 

    def modal_name(self):
        return (self.__class__.__name__)



    def save(self):
        js = self.json() 
        print(js)
        for k, v in js.items():
            if isinstance(v, TemporaryFile):
                # print(v.save())
                js[k] = v.save() 
        if not hasattr(self, 'id'):
            self.id = str(uuid.uuid4())
            js['id'] = self.id
        js['timestamp'] = str(datetime.now())
        self.db.create_column(model = js, table_name = str(self.id))
        return self
    
    def json(self):
        return self.__dict__


@dataclass
class Model:
    
    id : str 
    timestamp : str 
    
    def __init__(self) -> None:
        self.assign_foreign()
        print('here')
        # pass
    
    @classmethod
    def get_collection(cls, model, dept):
        
        return JsonDB(collection = cls.__name__ + "/") .get_collection(model)
    
    @classmethod
    def create(cls, *args, **kwargs):
        kwargs['id'] = str(uuid.uuid4())
        kwargs['timestamp'] = str(datetime.now())
        c = cls(**kwargs)
        # c.assign_foreign()
        return c
    
    @classmethod
    def filter(cls, **kwargs):
        # print(dir(cls))
        db = JsonDB(collection = cls.__name__ + "/") 
        return db.filter(kwargs)   

    @classmethod
    def all(cls, **kwargs):
        # print(dir(cls))
        db = JsonDB(collection = cls.__name__ + "/") 
        l = []
        for m in db.all():
            c = cls(**m)
            c.assign_foreign()
            l.append(c)
        return  l
     
    @classmethod
    def get(cls, **kwargs):
      
        db = JsonDB(collection = cls.__name__ + "/") 
        js = db.get(kwargs)
        c = None
        if js != None:
            c = cls(**js)
        # c.assign_foreign()
        return c
        pass
    
    
    @classmethod
    def __subclasses(cls):
        l = cls.__subclasses__()
        r = []
        for i in l:
            r.append(i.__name__.capitalize())
        return r
    @property
    def db(self):
        return JsonDB(collection = self.modal_name() + "/") 

    def modal_name(self):
        return (self.__class__.__name__)

    
    def save(self):
        
        js = self.json() 
        # print(js)
        for k, v in js.items():
            if isinstance(v, TemporaryFile):
                # print(v.save())
                js[k] = v.save() 
        if not bool(self.id):
            self.id = str(uuid.uuid4())
            js['id'] = self.id
            self.timestamp = str(datetime.now())    
            js['timestamp'] = self.timestamp
        self.db.create_column(model = js, table_name = str(self.id))
        # self.db.g    
        return self
    
    def json(self):
        return self.__dict__
    
    def assign_foreign(self):
        # print(self)
        js = deepcopy(list(self.json().items()))
        for k, v in js:
            if '__' in k:
                
                kwg = {}
                cl, p = k.split('__')
                kwg[p] = v
                c = None
                for cls in Model.__subclasses__():
                    
                    if cls.__name__ == cl.capitalize():
                        
                        c = cls.get(**kwg)
                        break
                    if cl.capitalize() in cls.__subclasses(): 
                        for cls in cls.__subclasses__():
                            if cls.__name__ == cl.capitalize():
                            
                                c = cls.get(**kwg)
                                break     
                setattr(self, cl, c)        
