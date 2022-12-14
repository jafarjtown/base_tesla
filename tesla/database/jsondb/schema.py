
def settype(type, default = None, onerror = ""):
    return {"type": type, "default": default, 'onerror': onerror}
    
    
User =  {
    "age" : settype(int, 0),
    "name" : settype(str, "default"),
    "hobbies" : settype(list,[2,2,3]),
    "is_admin" : settype(bool, True),
}

