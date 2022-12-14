from tesla.pyhtml.tags import CT, get_children, get_tag_style_attr
from tesla.pyhtml.watcher import Watcher
from tesla.pyhtml.server import server


import socketserver
import http.server

import os
import threading
class PYHTML:
    def __init__(self,html = True,css = False,js = False, path='./'
    ):
        self.html = html
        self.css = css
        self.js = js     
        self._path = path
        self.tag = CT("html")
        if not os.path.isdir(path):
            os.mkdir(path)
        
        
    def generate_files(self):
        if self.css:
            elems = self.tag.args
            
            inline_css = []
            
            for elem in elems:
               for child in get_children(elem):
                   if child.tag == "style":
                       inline_css.extend(child.args[:])
                       child.removeSelf("link", rel="stylesheet", href=f"./style.css")
               inline_css.extend(get_tag_style_attr(elem))
            with open(f"{self._path}/style.css", "w") as file:
                for css in inline_css:
                    
                    file.write(str(css))

        if self.html:
            with open(f'{self._path}/index.html', 'w') as file:
                file.write(format(self.tag.html()))
                
    def __str__(self):
        return format(self.tag.html())
    def allElems(self):
        elems = []
        head = self.tag
        for elem in head.args:
            elems.extend(get_children(elem))
        return elems

    def create_doc(self):
       
        body = CT("body")
        head = CT("head")
        self.tag.append(head, body)
        
        return head, body
        
    def preview(self):
        #self.generate_files()
        path = self._path
        print(f"{'':.^40}")
        print(f":{'PyHtml preview':^38}:")
        print(f"{'':.^40}")
       
        
        #watcher = Watcher("./")
        
        handler_object = server(path)
        PORT = 1234
        with socketserver.TCPServer(("", PORT),handler_object) as my_server:
            socketserver.TCPServer.allow_reuse_address = True
            print(f"Server started at http://localhost:{PORT}")
        # Star the server
            t1 = threading.Thread(target=Watcher, args=["./",self.generate_files, my_server])
            t1.start()
        #my_server.allow_reuse_address = True
            my_server.serve_forever()
    
