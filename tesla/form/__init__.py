from dataclasses import dataclass
from tesla.pyhtml.tags import CT
from tesla.modal import ForeignKey, ManyToManyField
from tesla.request import TemporaryFile
import copy


class Form:
    def validate(self, obj, model=None):
        data = dict(obj)
        del data['csrfmiddleware']
        for key, value in data.items():
            print(key, value)
            b = self.fields()[key].validate(value)
            if not b:
                ...
        if model:
            return model(**data).save()        
        return True    
             
        # print(self.fields())
    def save(self):
        fields = self.fields()
        # print(self.html())
    
    def fields(self):

        return self.__dict__

    def html(self):
        return ''.join(map(lambda f: f.field(), self.fields().values()))

    def __repr__(self):
        return self.html()

    def __str__(self):
        return (self.html())
        
class ModelForm:
    
    def __init__(self, instance = None) -> None:
        self.instance = instance
        
    
    def html(self):
        html = []
        model = self.model()
        if isinstance(self.fields, list):
            fields = self.fields
        else:
            fields = self.model.property_cls()   
        for field in fields:
            value = copy.deepcopy(getattr(model, field))
            value.name = field
            
            if self.instance:
                obj = self.instance
                # print(value.default)
                default = (getattr(obj, field))
                if type(default) in [int, bool, float, str]:
                    value.default = default
            else:
                if issubclass(type(value), (ForeignKey)):
                    
                        value.related_model_id = None
                    
                if issubclass(type(value), (ManyToManyField)):
                    value.related_model_ids = []            
            #     value.default = ''        
            html.append(value)
            ...
        # print('passs......')    
        return html    
            
    def __str__(self) -> str:
        return f'{self.html()}'   

    def validate(self, **kwargs):
        
        new_model = copy.deepcopy(self.model)

        if type(self.fields) == list:
            if self.fields != list(kwargs.keys()):
                not_kwargs = ', '.join([a for a in set(self.fields) if a not in set(kwargs.keys())])
                raise Exception(f'{not_kwargs} are not valid fields for {self.model.__name__}')
            for field in self.fields:
                f = getattr(new_model, field)
                v = f.validate(kwargs.get(field))
                
            return new_model.create(**kwargs) 

        for field, value in kwargs.items():
            if '__' in field:
                field = field.split('__')[0]
                tt = type(getattr(new_model, field))
                if not issubclass(tt, (ForeignKey, ManyToManyField)):
                    field += '__' + field[1]
                    
            f = getattr(new_model, field)
            v = f.validate(value)
        # print(kwargs)  
        # print('123')  
        return new_model.create(**kwargs) 

    def save(self):


        ...             
    
    

 



@dataclass
class Field:
    placeholder : str = 'Input'
    type : str = 'text'
    data_type : str = 'text'
    name : str = 'name'
    label: bool = True
    label_text : str = ''
    label_id : str = ''
    

    def __str__(self):
        return  self.field()

    def __repr__(self):
        return self.__str__()
    
    def field(self):
        input = CT('input', type=self.type, placeholder = self.placeholder, name=self.name)
        if self.label:
            if self.label_text == '':
                self.label_text = self.name
            input = CT('label', self.label_text , input, id=self.label_id)
        return (input.html())
    
    def validate(self, value):
        return isinstance(value, self.data_type)
