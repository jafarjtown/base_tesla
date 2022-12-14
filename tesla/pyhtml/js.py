class JavaScript:
    def document(self):
        pass

class Document:
    def get(self, target):
        return Event(f"document.querySelector('{target}')")
    
    def alert(self, obj):
        return f"alert('{obj}')"
    
    def log(self, obj):
        return f"console.log('{obj}')"

    

document = Document()


class Event:
    def __init__(self, target):
        self.target = target
    def addEventListener(self, event, func = None):
        return f"{self.target}.addEventListener('{event}', ()=>{func});" 
        
    def innerElem(self, elem):
        return f"{self.target}.innerHTML = '{elem}'" 

    def onClick(self, event):
        return self.addEventListener('click', event)
    
    def remove(self, target):
        return f"{self.target}.removeChild({self.target}.querySelector('{target}'))"

    def append(self, child):
        return f"{self.target}.append('{child}')"
    
    
