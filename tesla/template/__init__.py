import re
from dataclasses import dataclass, field

from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader('./templates')
env = Environment(loader = file_loader)


class UnusedTemplateVariable(Exception):
    pass

@dataclass
class Template:
    string : str
    obj : dict
    used_args : set = field(default_factory=set, init=False)
    
    
    def render(self):
        self.result = self.string
        self.parse_str()
        self.parse_func()
        return self.result.strip()
        
        
    def parse_func(self):
        words_list = self.result.split(" ")
        self.result = ""
        for word in words_list:
            if "{%" and "%}" in word:
                if "}" != word[-1]:
                    v = word.split("%}")[0].split("{%")[1]
                else:
                    v = word[2:-2]
                f_n, b = v.split("(")
                args = b.split(")")[0]
                va = self.obj.get(f_n)
                r = va(args)
                word = word.replace(v, str(r)).replace("%}", "").replace("{%", "")
            self.result += " " + word
                
    def parse_str(self):
        words_list = self.result.split(" ")
        self.result = ""
        for word in words_list:
            if "{{" and "}}" in word:
                if "}" != word[-1]:
                    v = word.split("}}")[0].split("{{")[1]
                    
                else:
                    
                    v = word[2:-2]
             
                va = self.obj.get(v)
                word = word.replace((v), str(va)).replace("}}", "").replace("{{","")
                if va != None:
                    self.used_args.add(v)
            
            self.result += " " + word
        
        return None


# obj = {"name": "jafar", "age": 18}
        
# def add(str):
#     n, m = str.split(",")
#     print(n)
#     return int(n) + int(m)
    
    
# def up(str):
#     return str.upper()
# txt = "hello {%up({{name}})%}\n, am {{age}} years, hmmm {{name}}, 5 + 4 = {%add(5,4)%} {%add(100,5)%}"    
# obj["add"] = add
# obj["up"] = up
# doc = Template(txt, obj)   
#doc.render()     
# print(doc.render().encode())
#output
#b'hello jafar\n, am 18 years, hmmm jafar, 5 + 4 = 9'

