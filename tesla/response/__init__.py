from turtle import width
from tesla.request import Request
from tesla.pyhtml.tags import CSS, CT, CSSGroup
from tesla.pyhtml import PYHTML
from tesla.messages import messages_broker

import os

from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader('.')



# from jinja2 import Environment, PackageLoader


class Response:
    def __init__(self, request: Request, status_code: str, content_type: str):
        
        self.status_code = status_code
        self.start_response = request.start_response
        self.content_type = content_type
        # print(request.get_cookie())
        self.headers = [('Content-type', self.content_type), ('Set-cookie', request.get_cookie())]
        self.response_content = []
        self.templates_folders = ['./']

        
        ...

    def make_response(self):
        self.start_response(self.status_code, self.headers)
        return self.response_content

    def parse_cookie(self, cookie):
        cookie = cookie.split(';')
        obj = {}
        for c in cookie:
            c = c.split('=')
            obj[c[0]] = c[1]
        cookie = obj
        return obj.items()

class Render(Response):
    
    def __init__(self, request: Request, content, context = {},  status_code = '200 OK', content_type = 'text/html'):
        
        # request.cookie = self.parse_cookie(request.http_cookie)
        super().__init__(request, status_code, content_type)
        # env = Environment(loader=PackageLoader('jinja2', '/'))

        if self.is_available(content) is not None:
            # template = env.get_template(self.is_available(content))
            env = Environment(loader = file_loader)
            env.trim_blocks = True
            env.lstrip_blocks = True
            env.rstrip_blocks = True
            globals_obj= request.context.get_objs()
            for k, v in globals_obj.items():
                env.globals[k] = v
            template = env.get_template(self.is_available(content))
            # print(**request.context.get_objs())
            content = template.render(**{'csrf' : request.csrf, 'messages': messages_broker.get_messages(request), **request.params, **context})
        else:
            content = f'Template {content} not found.'
        # content = template.render(*context)
        self.response_content.append(content.encode()) 

    def is_available(self, filename):
        for path in self.templates_folders:
            if os.path.isfile(path + filename):
                return path + filename
        return None


class HttpResponse(Response):
    
    def __init__(self, request: Request,content,  status_code = '200 OK', content_type = 'text/html'):
        super().__init__(request, status_code, content_type)
        if type(content) == str:
            content = content.encode()
        self.response_content.append(content) 

    
class JsonResponse(Response):
    
    def __init__(self, request: Request,content : str,  status_code = '200 OK', content_type = 'application/json'):
        super().__init__(request, status_code, content_type)
        import json
        content = json.dumps(content).encode()
        self.response_content.append(content) 
    

class ErrorResponse(Response):
    def __init__(self, request: Request, error_code: str):
        super().__init__(request, '404 Not Found', 'text/html')
        # self.response_content.append('Server Error'.encode())


class Http404Response(ErrorResponse):
    def __init__(self, request: Request, debug, routes):
        super().__init__(request, '404 Not Found')
        doc = PYHTML()
        head, body = doc.create_doc()
        # css
        style = CT('style', CSS('*', margin='0', boxSizing='border-box').css(),CSS('body', backgroundColor='floralwhite').css() ) 
        h1_s = CSS('h1', 
                   backgroundColor='blue', 
                   padding='15px',
                   color='white',
                   borderBottom='10px solid black'
                   
                   )
        li_s = CSS('li',
                   backgroundColor='lightblue',
                   listStyle='none',
                   padding='5px 10px',
                   width='260px',
                   margin='2px 0'
                   )
        
        req_s = CSS('#req_body', 
                    borderTop='10px solid black',
                    margin='10px 0'
                    )
        style.append(h1_s.css(), li_s.css(), req_s.css())
        # head
        head.append(style ,CT('title', '404 page not found'))
        
        # body
        h1 = CT('h1', '404 page not found')
        p = CT('p', 'Available routes in the application.',  style=CSS(
            margin='10px',
            marginLeft='40px',
            fontSize='x-large'
        ).css())
        
        ul = CT('ul')
        
        req_p = CT('p', 'Request body',  style=CSS(
            margin='10px',
            marginLeft='40px',
            fontSize='x-large'
        ).css())
        ul_req = CT('ul') 
        req_b = CT('div',req_p, ul_req, id='req_body')
        for k, v in request.environ.items():
            x = CT('xmp', f'{k} = {v}')
            ul_req.append(CT('li', x, style=CSS(
                width='fit-content'
            ).css()))
        
        for route in routes:
            # print(route)
            x = CT('xmp', route.path)
            if route.name:
                x.append(f'[name={route.name}]')
            ul.append(CT('li', x))
        
        if debug:
            body.append(h1,p, ul, req_b)
        else:
            body.append('404 Not Found')    
        self.response_content.append(str(doc).encode())
        
class Http500Response(ErrorResponse):
    def __init__(self, request: Request, message):
        super().__init__(request, '500 Server Error')
        self.response_content.append(f'500 Server Error \n {message}'.encode())        
      
      
class Redirect(Response):
    def __init__(self, request: Request, route,  status_code = '302 Found', content_type = 'text/html'):
        super().__init__(request, status_code, content_type)
        self.headers += [('Location', route)]
        # print(self.headers)
         