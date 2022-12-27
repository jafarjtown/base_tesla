from dataclasses import dataclass, field

@dataclass
class Collection:
    models : dict = field(default_factory=dict)
    
    
    def add(self, model):
         if model.__name__ in self.models:
             return self.models[model.__name__]
         self.models[model.__name__] = {
             'name': model.__name__,
             'counts': model.size()[0],
             'size': model.size()[1]
         }
         return model
     
    def remove(self, model):
        if model.__name__ in self.models:
            del self.models[model.__name__] 
            return None
        return None
    
    def colls(self):
        return [m for m in self.models.values()]