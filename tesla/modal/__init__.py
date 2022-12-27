# from __future__ import annotations
from copy import deepcopy
from dataclasses import InitVar, asdict, dataclass, field, astuple

from tesla.pyhtml.tags import CT, CSS


from datetime import datetime
# from tempfile import TemporaryFile
from tesla.database.jsondb import JsonDB
import uuid
import copy

from tesla.request import TemporaryFile

_no_default_object = object()


def property_obj(arr):
    a = []
    for l in arr.__dict__:
        if not l.startswith('__'):
            if l != 'id' and l != 'timestamp':
                a.append(l)

    return a


def ModalId():
    cache = {}

    def generate(modal):

        if modal in cache.keys():

            cache[modal] += 1
            return cache[modal]
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


class Field:

    def __init__(self, required=False, label=None) -> None:
        self.input_type = 'text'
        self.type = 'input'
        self.required = required
        self.css = CSS()
        self.name = ''
        self.params = ''
        self.default = ''
        self.label = None
        self.value_type = str

        pass

    def __pre_show__(self):
        pass

    def input(self, name, **kwargs):
        k = ' '.join([f'{a}={b}' for a, b in kwargs.items()])
        self.params += ' ' + k
        self.name = name
        if self.required:
            self.params += ' required'
        if self.type == 'textarea':
            self.css.kwargs['height'] = '200px'      # s
            self.css.kwargs['resize'] = 'none'      # s
        return self

    def html(self) -> str:
        self.input(self.name)

        self.tag = CT(self.type, **{'class': "form-control"},  style=self.css.css(
        ), type=self.input_type, name=self.name, value=self.default, params=self.params)
        if self.type != 'input':
            self.tag.append(self.default)
            del self.tag.kwargs['value']
        if self.label == None:
            self.label = self.name

        self.__pre_show__()
        return self.tag.html()

    def __str__(self):
        self.html()
        return self.tag.html()

    def __repr__(self):
        return self.__class__.__name__

    def validate(self, value):
        try:
            v = self.value_type(value)
            if isinstance(v, self.value_type):
                return True
            return False
        except Exception:
            raise Exception(f'{value} is not valid type for {self.__repr__()}')


class CharField(Field):

    def __init__(self, default='', min=0, max=120, *args, **kwargs) -> None:
        self.default = default
        self.min = min
        self.max = max
        super().__init__(*args, **kwargs)

    def input(self, *args):
        kwargs = {}
        kwargs['minlength'] = self.min
        kwargs['maxlength'] = self.max
        return super().input(*args, **kwargs)


class PasswordField(CharField):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.input_type = 'password'


class ListField(Field, list):

    def __init__(self, default=[], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default = default
        self.type = 'select'


class TextField(Field):

    def __init__(self, default='', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default = default
        self.type = 'textarea'


class EmailField(Field):

    def __init__(self, default='', *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default = default
        self.input_type = 'email'


class DateField(CharField):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.input_type = 'date'


class DictField(Field, dict):

    def __init__(self, default={}, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default = default


class ForeignKey(Field):

    def __init__(self, related_model, required=False, label=None) -> None:
        super().__init__(required, label)
        self.related_model = related_model
        self.option_models = related_model.all()
        self.related_model_id = None
        self.type = 'select'

    def __pre_show__(self):
        for obj in self.option_models:

            opt = CT('option', str(obj), value=obj.id)
            if self.related_model_id == obj.id:

                opt.params += ' selected'
            self.tag.append(opt)
            ...

    def input(self, name, **kwargs):
        name += '__id'

        return super().input(name, **kwargs)

class ManyToManyField(Field):
    
    def __init__(self, related_model, required=False, label=None) -> None:
        super().__init__(required, label)
        # self.default = []
        self.related_model = related_model
        self.option_models = related_model.all()
        self.related_model_ids = []
        self.type = 'select'
        
    
    def __pre_show__(self):
          self.tag.params += 'multiple'
          for obj in self.option_models:

            opt = CT('option', str(obj), value=obj.id)
            if obj.id in self.related_model_ids:

                opt.params += ' selected'
            self.tag.append(opt)
          return super().__pre_show__()
      
      
    def input(self, name, **kwargs):
        name += '__ids'

        return super().input(name, **kwargs)
    
    
    def related_models(self):
        return [self.related_model.get(id = id) for id in self.related_model_ids]
              
class Model:

    id = CharField()
    timestamp = CharField()

    def __init__(self) -> None:
        self.assign_foreign()

        # pass

    @classmethod
    def get_collection(cls, model, dept):

        return JsonDB(collection=cls.__name__ + "/") .get_collection(model)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs['id'] = str(uuid.uuid4())
        kwargs['timestamp'] = str(datetime.now())
        c = cls()
        for k, v in kwargs.items():
             
            setattr(c, k, v)
            
        return c

    @classmethod
    def filter(cls, **kwargs):

        db = JsonDB(collection=cls.__name__ + "/")
        return db.filter(kwargs)

    @classmethod
    def all(cls, models=True):

        db = JsonDB(collection=cls.__name__ + "/")
        if not models:
            return list(db.all())
        l = []
        for m in db.all():
            c = cls()
            for k, v in m.items():

                if '__' in k:
                    mn = k.split('__')[0]
                    tt = getattr(c, mn)

                    if isinstance(type(tt), ForeignKey):
                        tt.related_model_id = v
                        setattr(c, mn, tt.related_model.get(id=v))
                    if isinstance(type(tt), ManyToManyField):
                        tt.related_model_ids = []
                        for i in v:
                            tt.related_model_ids.append(i)
                        setattr(c, mn, tt.related_models())    
                        # print(v)
                        # setattr(c, mn, tt.related_model.get(id=v))    

                setattr(c, k, v)
            # c.assign_foreign()
            l.append(c)
        return l

    @classmethod
    def size(cls):
        db = JsonDB(collection=cls.__name__ + "/")
        return db.size()

    @classmethod
    def get(cls, *args, **kwargs):

        db = JsonDB(collection=cls.__name__ + "/")
        js = db.get(kwargs)

        c = None
        if js != None:
            c = cls()
            for k, v in js.items():
                if '__' in k:
                    mn = k.split('__')[0]
                    tt = getattr(c, mn)
                    if issubclass(type(tt), ForeignKey):
                        tt.related_model_id = v
                        setattr(c, mn, tt.related_model.get(id=v))
                    if issubclass(type(tt), ManyToManyField):
                        tt.related_model_ids = []
                        for i in v:
                            tt.related_model_ids.append(i)
                        setattr(c, mn, tt.related_models())        
                setattr(c, k, v)
        return c

    @classmethod
    def __subclasses(cls):
        l = cls.__subclasses__()
        r = []
        for i in l:
            r.append(i.__name__.capitalize())
        return r

    @property
    def db(self):
        return JsonDB(collection=self.modal_name() + "/")

    def modal_name(self):
        return (self.__class__.__name__)

    def save(self):
        cls_copy = self.__class__

        js = self.json()
        j = copy.deepcopy(js)
        for k, v in js.items():
            print(k, v)
            if isinstance(v, TemporaryFile):

                j[k] = v.save()
            if issubclass(type(v), Model):
                del j[k]
            if issubclass(type(v), (ForeignKey, ManyToManyField)):
                    if j.get(k):
                        del j[k]
                    k = k + '__id'
                    if isinstance(getattr(cls_copy, kk), ManyToManyField):
                        k += 's'
                    j[k] = v  
            if type(v) == list and len(v) > 0 and  issubclass(type(v[0]), Model):    
                del j[k]          
            if '__' in k:  
                kk = k.split('__')[0]
                if issubclass(type(getattr(cls_copy, kk)), (ForeignKey, ManyToManyField)):
                    # del j[k]
                    # if j.get(k):
                    #     del j[k]
                    # kk = k
                    # k = k + '__id'
                    if isinstance(getattr(cls_copy, kk), ManyToManyField):
                        # k += 's'
                        if type(v) == str:
                            v = [v]
                        
                    # j[k] = v
                    # setattr(self, k, v)          

        if not bool(self.id):
            self.id = str(uuid.uuid4())
            j['id'] = self.id
            self.timestamp = str(datetime.now())
            j['timestamp'] = self.timestamp
        # print(j)    
        self.db.create_column(model=j, table_name=str(self.id))
        # self.db.g
        return self

    def update(self, **kwargs):

        for k, v in kwargs.items():
            if '__' in k:
                kk = k.split('__')[0]
                tt = getattr(self, kk)
                # old_ref = ge

                if issubclass(type(tt), Model):
                    new_ref = tt.__class__.get(id=v)
                    setattr(self, kk, new_ref)
                if issubclass(type(tt), ForeignKey):

                    tt.related_model_id = v
                if issubclass(type(tt), ManyToManyField):
                    tt.related_model_ids = []
                    if type(v) == str:
                        v = [v]
                    # print(v)    
                    for i in v:
                        tt.related_model_ids.append(i)
                       
            setattr(self, k, v)
        return self

    def json(self):
        # print(self.__annotations__)
        return self.__dict__

    def delete(self):
        self.db.delete(self.id)
        return None

    def assign_foreign(self):

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

    @classmethod
    def __meta__(cls):
        return ('id',)

    @classmethod
    def property_cls(cls):
        ls = property_obj(cls)

        return ls

    # @property
    def admin_dis(self):
        tp = self.__meta__()
        f = []
        for t in tp:
            f.append(getattr(self, t))

        return f
