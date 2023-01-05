# from __future__ import annotations
import uuid
from copy import deepcopy
from datetime import datetime

# from tempfile import TemporaryFile
from tesla.database.jsondb import JsonDB
from tesla.functions import truncate, url
from tesla.pyhtml.tags import CSS, CT
from tesla.request import TemporaryFile
from tesla.signal import signal


def property_obj(arr, d=None):
    a = []
    for l, v in arr.__dict__.items():
        if not l.startswith('__'):
            if l != 'id' and l != 'timestamp':
                if d:
                    l = (l, v)
                a.append(l)

    return a


def to_dict(arr):
    a = {}
    for k, v in arr:
        a[k] = v
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

    def html(self, **kwargs) -> str:
        self.input(self.name)

        self.tag = CT(self.type, **kwargs, style=self.css.css(
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
        self.default = str(datetime.now())


class DictField(Field, dict):

    def __init__(self, default={}, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default = default


class ForeignKey(Field):

    def __init__(self, related_model, required=False, label=None) -> None:
        super().__init__(required, label)
        self.default = None
        self.related_model = related_model
        self.related_model_id = None
        self.type = 'select'

    @property
    def option_models(self):
        return self.related_model.all()

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
        self.default = []
        self.related_model = related_model
        # self.option_models = related_model.all()
        self.related_model_ids = []
        self.type = 'select'

    @property
    def option_models(self):
        return self.related_model.all()

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
        return [self.related_model.get(id=id) for id in self.related_model_ids]

class BooleanField(Field):
    
    def __init__(self, required=False, label=None) -> None:
        super().__init__(required, label)
        self.input_type = 'checkbox'
        self.default = False
    
    def html(self, **kwargs) -> str:
        self.input(self.name)
        if self.default:
            self.params += ' checked'
        self.tag = CT('input', type='checkbox', name=self.name, params=self.params)
        # return super().html(**kwargs)
        self.__pre_show__()
        return self.tag.html()

class NumberField(Field):
    
    def __init__(self, required=False, label=None) -> None:
        
        super().__init__(required, label)
        self.input_type = 'number'
        self.default = 0 
        self.min = -9999999999
        self.max = 99999999999
    
        
    def input(self, *args):
        kwargs = {}
        kwargs['min'] = self.min
        kwargs['max'] = self.max
        return super().input(*args, **kwargs)    

class PositiveNumberField(NumberField):
    
    def __init__(self, required=False, label=None) -> None:
        super().__init__(required, label)
        self.default = 0 
        self.min = 0
        self.max = 9999999999
    

class NegativeNumberField(NumberField):
    
    def __init__(self, required=False, label=None) -> None:
        super().__init__(required, label)
        self.default = -1 
        self.min = -999999999
        self.max = 0
    
        

class FileField(Field):
    
    def __init__(self,upload_to = '' , required=False, label=None) -> None:
        super().__init__(required, label)
        self.upload_to = upload_to
        self.accept = '*'
    
    def html(self, **kwargs) -> str:
        self.input(self.name)
        self.tag = CT('input', type='file', accept=self.accept, name=self.name, params=self.params)
        if self.default:
            p = CT('p', 'current file : ')
            old_file = CT('a',  truncate(self.default), href=self.default)
            delete_old_file = CT('a',  'remove', href=self.default + '?next={{request.path}}')
            
            p.append(old_file)
            p.append(' | ')
            p.append(delete_old_file)
            self.tag = CT('span', self.tag, p)
        # return super().html(**kwargs)
        self.__pre_show__()
        return self.tag.html()    
    def validate_file(self, file, name):
        if self.accept == '*':
            return
        file_type = self.accept[:-2]
        if file.type.split('/')[0] != file_type:
            raise Exception(f'{file.type} is not accepted for {name}') 
class ImageField(FileField):
    
    def __init__(self, upload_to='', required=False, label=None) -> None:
        super().__init__(upload_to, required, label)
        self.accept = 'image/*'

class AudioField(FileField):
    
    def __init__(self, upload_to='', required=False, label=None) -> None:
        super().__init__(upload_to, required, label)
        self.accept = 'audio/*'

class VideoField(FileField):
    
    def __init__(self, upload_to='', required=False, label=None) -> None:
        super().__init__(upload_to, required, label)
        self.accept = 'video/*'

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
        c = c.save()
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
        created = not bool(self.get(id = self.id))
        signal.send(self.__class__, self, created, 'pre-save')
        cls_copy = self.__class__

        j = {**self.json()}
        cls_props = to_dict(property_obj(cls_copy, True))
        props = {**cls_props, **j}


        for k, v in props.items():
            
            if '__' in k:
                ref_k = k.split('__')[0]
                if ref_k in j:
                    del j[ref_k]
            if type(v) == str and '__ids' in k:
                j[k] = [v]
            if issubclass(type(v), (ForeignKey, ManyToManyField)):
                is_m2m = issubclass(type(v), ManyToManyField)
                # is_1t1 = issubclass(type(v), ForeignKey)
                kk = k + '__id'
                if is_m2m:
                    kk += 's'
                if kk in j.keys():
                    if k in j.keys():
                        del j[k]
                else:
                    j[kk] = v.default
                continue
            elif issubclass(type(v), (BooleanField, DateField)):
                j[k] = v.default
                
            elif issubclass(type(cls_props.get(k)), BooleanField):
                if v == 'on':
                    j[k] = True  
                else:
                    j[k] = False        
            elif issubclass(type(v), TemporaryFile):
                _model_field = cls_props.get(k)
                _model_field.validate_file(v.file, k)
                j[k] = v.save(_model_field.upload_to)
            elif type(v) == str and v.isnumeric():
                j[k] = int(v)    
            setattr(self, k, v)

        # if not bool(self.id):
        #     self.id = str(uuid.uuid4())
        #     j['id'] = self.id
        #     self.timestamp = str(datetime.now())
        #     j['timestamp'] = self.timestamp

        self.db.create_column(model=j, table_name=str(self.id))
        # self.db.g
        signal.send(self.__class__, self, created,'post-save')
        
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

    def admin_dis(self):
        tp = self.__meta__()
        cls_dis = self.get(id=self.id)
        f = []
        for t in tp:

            tt = getattr(cls_dis, t)

            if issubclass(type(tt), list):
                tt = ', '.join([str(m) for m in tt])
            f.append(tt)

        return f

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'
