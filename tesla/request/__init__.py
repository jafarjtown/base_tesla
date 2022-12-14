import cgi
import cgitb; cgitb.enable()
from dataclasses import dataclass
import os
import tempfile
import string 
import random as r
# from Cookie import SimpleCookie
from datetime import datetime, timedelta
# from time import t

@dataclass
class TemporaryFile:
    
    
    def __init__(self, file, filename,path, *args, **kwargs) -> None:
        self.file = file
        self.filename = filename
        self.path = path 
        
        # print(self.filename, self.file)
    
    def save(self):
        # print('file obj',self.file)
        path = self.path + '/' + self.file.type
        def fbuffer(f, chunk_size=10000):
            while True:
                chunk = f.read(chunk_size)
                if not chunk: break
                yield chunk
        fn = os.path.basename(self.filename)
        if not os.path.isdir(path):
            os.makedirs(path)
        if os.path.isfile(path + '/' + fn):
            name, ex = fn.split('.')
            fn = name + str(int(datetime.now().timestamp())) + '.'  + ex 
        with open(path + '/' + fn , 'wb+') as f:
            for chunk in fbuffer(self.file.file):
                f.write(chunk)
        return path +'/'+fn + f'>{self.file.type}'

class PostBody:
    def __init__(self, data):
        self.data = data 
    
    def get(self, key):
        value = self.data.get(key)
        # if type(value) == str:
        #     print(dir(cgi))
        #     value = cgi.escape(value)

        return value
    
    def set(self, key, value):
        self.data[key] = value

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value
            
    # def __dict__(self):
    #     o = {}
    #     for k,v in self:
    #         o[k] = v
    #     return o        

    

class Request:
    def __init__(self, environ, start_response, app, csrf, authentication, context, session, auth_model):
        self.app = app
        self.csrf = csrf
        self.environ = environ
        self.start_response = start_response
        self.cookie = []
        self.context = context
        self.session = session
        self.auth_model = auth_model
        
        # self.headers = [*self.cookie]

        self.http_host = environ['HTTP_HOST']
        self.http_user_agent = environ['HTTP_USER_AGENT']
        self.http_cookie = environ.get("HTTP_COOKIE")
        self.lang = environ.get('LANG')
        self.method = environ.get('REQUEST_METHOD')
        self.path = environ.get('PATH_INFO')
        self.host_address = environ.get('HTTP_HOST')
        self.gateway_interface = environ.get('GATEWAY_INTERFACE')
        self.server_port = environ.get('SERVER_PORT')
        self.remote_host = environ.get('REMOTE_HOST')
        self.content_type = environ.get('CONTENT_TYPE')
        self.content_length = environ.get('CONTENT_LENGTH')
        self.body = environ.get('BODY')
        self.query_string = environ.get('QUERY_STRING')
        self.server_protocol = environ.get('SERVER_PROTOCOL')
        self.server_software = environ.get('SERVER_SOFTWARE')

        # auth request's
        authentication.authenticate(self.http_cookie, self.session)

        self.user = authentication.get_user()
        self.is_authenticated = self.user != authentication.ANONYMOUS 
        self.session_id = authentication.session_id
        self.parse_qs()
        self.pass_csrf()
        self.set_session_id()
        pass
    
    def set_session_id(self):
        found = False
        for c in self.http_cookie.split(';'):
            key, value, *_ = c.split('=')
            # print(2)
            if key.strip() == 'usersession':
                self.session_id = value.strip()
                found = True
                break
        if found != True:    
            session = ''.join(r.sample(string.ascii_letters, 50))

            self.set_cookie('usersession', session)    
            
    def pass_csrf(self):
        
        if self.method == 'POST':
         
            csrf = self.post.get('csrfmiddleware')
            if csrf is not None:
                if csrf in self.app.csrf_tokens:
                    
                    self.app.csrf_tokens.remove(csrf)
                    self.csrf = self.app.csrf_tokens[r.randint(0, len(self.app.csrf_tokens)-1)]
                    
                    self.app.csrf_tokens.append(''.join(r.sample([*string.ascii_letters,  *string.hexdigits],55)))
                    return None
                # self.csrf = self.app.csrf_tokens[r.randint(0, len(self.app.csrf_tokens)-1)]
            # print(self.csrf)
            
            raise Exception('csrf is not provided')    
 
    def parse_qs(self):
        # print(self.environ)
        if self.method != 'POST':
            # self.
            return
        
        self.post = PostBody({})
        environ = self.environ
        field_storage = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values = True 
        )
         
        for item in field_storage.list:
            if not item.filename:
                self.post.set(item.name, item.value)
            else:
                # print((item.type))
                self.post.set(item.name, TemporaryFile(file=item, filename=item.filename, path=self.app.media_file))
                
    def get_cookie(self):
        return ','.join(self.cookie)  

    def set_cookie(self, k, v):
        today = datetime.today()
        a = datetime(today.year, today.month, today.day).timestamp() + 5000000
        # print(a)
        self.cookie.append(f'{k}={v};max-age={int(a)};path=/')
            
