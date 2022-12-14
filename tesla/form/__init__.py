from dataclasses import dataclass
from tesla.pyhtml.tags import CT
from tesla.request import TemporaryFile


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
        print(self.html())
    
    def fields(self):

        return self.__dict__

    def html(self):
        return ''.join(map(lambda f: f.field(), self.fields().values()))

    def __repr__(self):
        return self.html()

    def __str__(self):
        return (self.html())
        
    

 



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
