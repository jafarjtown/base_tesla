
class BaseException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    ...
    

class FileException(BaseException, FileNotFoundError):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class TemplateException(FileException):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)            

class MediaException(FileException):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)    

class DatabaseException(BaseException):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        

class KeyValueErrorException(DatabaseException, ValueError):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)            
        
        
        

# raise KeyValueErrorException('hello')        