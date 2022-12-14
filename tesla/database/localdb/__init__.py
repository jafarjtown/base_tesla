
from typing import Any, Dict, List, AnyStr, Set

class __Localdb:
    
    def __init__(self) -> None:
        self.__db = {}
        
    # def save(self):
    def get(self, key : AnyStr, ps=True) -> Any:
        if key in self.__db or ps:
            return self.__db.get(key)
        raise KeyError(f'{key} not found.') 
    
    def clear(self, key : AnyStr):
        if key in self.__db:
            delattr(self.__db, key)
            return None
        raise KeyError(f'{key} not found.') 
    
    def add(self, key : AnyStr, value : Any, ps=True):
        if key in self.__db and not ps:
            raise Exception(f'{key} already exists.')
        self.__db[key] = value
        return self.get(key)
    
    def exists(self, key : AnyStr) -> bool:
        if key in self.__db:
            return True
        return False
    
    

global_db = __Localdb()    