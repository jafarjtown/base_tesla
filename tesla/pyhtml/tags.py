from uuid import uuid4
from tesla.pyhtml.formater import format
from tesla.pyhtml.js import document

import os


def get_children(elem, rec=False):
    children = []
    for child in elem.args:
        children.append(child)
        
        if rec:
            if type(child) != str and len(child.args) != 0:
                children.extend(get_children(child, rec))
    return children


def get_tag_style_attr(child):
     inline_css = []
     if child.kwargs.get("style"):
              styles = "[pyid='" + child.kwargs.get("pyid") + "']{" + child.kwargs.get('style') + "}"
              #print(child.kwargs.get("style")
            
              del (child.kwargs["style"])
              #delattr(child.kwargs, 'style')
              #print(child.kawrgs)
              inline_css.append(styles)
     if len(child.args) > 0:
        for c in child.args:
            if type(c) != str:
                inline_css.extend(get_tag_style_attr(c))
     return inline_css

class CSS:
    def __init__(self, target= None, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.target =target
        
    def css(self):
        return self.interprete()
    def interprete(self):
        css = ""
        for p, a in self.kwargs.items():
            property = self.tran(p)
            attribute = self.tran(a)
            css += f"{property}: {attribute};"
        if self.target != None:
            css = self.target + "{" + css + "}"
        return css
    def tran(self, txt):
        r = ""
        for i,l in enumerate(txt):
            if l.isupper():
                if i != 0:
                    l = f'-{l}'
                l = l.lower()
            r += l
        return r

class CSSGroup:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.assignClass()
    def assignClass(self):
        for arg in self.args:
            arg.kwargs["class"] = self.name
    def __str__(self):
        return CSS(f".{self.name}", **self.kwargs).css()
    def __repr__(self):
        return self.__str__()

 
     
     
class CT:
    def __init__(self, tag, *args, params='', **kwargs ):
        self.tag = tag
        self.args = args
        self.kwargs = kwargs
        self.params = params
        # self.kwargs["pyid"] = "pyhtml_" + str(uuid4()).split("-")[0]
        # self.doc = document.get('[pyid="'+self.kwargs.get('pyid')+'"]')
    def __repr__(self):
        return f"<{self.tag} children={get_children(self, False)} />" 
    def html(self):
        # pr
        r = " ".join(map(lambda elem: str(elem), self.args))
        # print(self.args)
        kwargs = ''
        for k, v in self.kwargs.items():
            kwargs += f" {k}='{v}'"
        # print(self.params)   
        
        return f"<{self.tag}{kwargs}{self.params}>{r}</{self.tag}>"


    def __str__(self):
        return self.html()    
    def append(self, *tags):
        self.args = list(self.args)
        for tag in tags:
            self.args.append(tag)
        return None
    def removeSelf(self,tag =None, *args, **kwargs):
        self.args = []
        self.kwargs = kwargs
        if tag:
            self.tag = tag
        return None

    def onClick(self, event):
        return self.doc.onClick(event)
        
    def value(self):
        return self.doc.getValue()

    def setattr(self, key, value):
        self.kwargs[key] = value
        return None

class SCT(CT):
    def __init__(self, tag,  *args, **kwargs):
        super().__init__(tag,  *args, **kwargs)
    def html(self):
        r = " ".join(self.args)
        kwargs = ''
        for k, v in self.kwargs.items():
            kwargs += f" {k}='{v}'"
        return f"<{self.tag}{kwargs} />"
 
     
    

        
        
class TextNode:
  def __init__(self, text):
      self.text = text
  def html(self):
      return self.text
  