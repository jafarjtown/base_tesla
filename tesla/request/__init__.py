from datetime import datetime
import random as r
import string
import os
from dataclasses import dataclass
import cgi
import cgitb
cgitb.enable()

# from tesla import TeslaApp
# from Cookie import SimpleCookie
# from time import t


@dataclass
class TemporaryFile:

    def __init__(self, file, filename, path, *args, **kwargs) -> None:
        self.file = file

        self.filename = filename
        self.path = path

        # print(self.filename, self.file)

    def save(self, upload_to=''):
        # print('file obj',self.file)
        if not upload_to.startswith('/') and upload_to != '':
            upload_to = '/' + upload_to

        path = self.path + upload_to + '/' + self.file.type

        def fbuffer(f, chunk_size=10000):
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        fn = os.path.basename(self.filename)
        if not os.path.isdir(path):
            os.makedirs(path)
        if os.path.isfile(path + '/' + fn):
            name, ex = fn.split('.')
            fn = name + str(int(datetime.now().timestamp())) + '.' + ex
        with open(path + '/' + fn, 'wb+') as f:
            for chunk in fbuffer(self.file.file):
                f.write(chunk)
        return '/' + path + '/'+fn + f'>{self.file.type}'


class PostBody:
    def __init__(self, data):
        self.data = data

    def get(self, key):
        value = self.data.get(key)
        # if type(value) == str:
        #     print(dir(cgi))
        #     value = cgi.escape(value)

        return value

    def addlist(self, key, value):
        if type(self.get(key)) == str or type(self.get(key)) == int:
            fs = self.get(key)
            self.set(key, [fs])
        lst = self.get(key)
        lst.append(value)
        self.set(key, lst)

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


def parse_cookies(environ):
    cookies = {}
    cookie_string = environ.get('HTTP_COOKIE', '')
    for chunk in cookie_string.split(';'):
        if '=' in chunk:
            key, value = chunk.split('=', 1)
            key, value = key.strip(), value.strip()
            cookies[key] = value
    return cookies


def parse_query_string(query_string):
    query = {}
    for param in query_string.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            key, value = key.strip(), value.strip()
            query[key] = value
    return query


def parse_form_data(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    form_data = {}
    for param in request_body.decode().split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            key, value = key.strip(), value.strip()
            form_data[key] = value
    return form_data


def parse_file_upload(environ):
    files = {}
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    boundary = environ.get('CONTENT_TYPE', '').split('=')[-1]
    if not boundary:
        return files
    parts = request_body.split(boundary.encode())[1:-1]
    for part in parts:
        lines = part.decode().split('\r\n')
        name = None
        filename = None
        content_type = None
        data = b''
        for line in lines:
            if line.startswith('Content-Disposition:'):
                name = line.split(';')[-1].split('=')[-1][1:-1]
                filename = line.split(';')[-2].split('=')[-1][1]
            elif line.startswith('Content-Type:'):
                content_type = line.split(':')[-1].strip()
            elif line == '':
                data = b''.join(lines[lines.index(line)+1:])
        if name and data:
            files[name] = {
                'filename': filename,
                'content_type': content_type,
                'data': data,
            }
    return files


class _Request:
    def __init__(self, environ, start_response, app, authentication, context, session, auth_model):
        self.environ = environ
        self.start_response = start_response
        self.app = app
        # self.csrf_token = csrf_token
        self.authentication = authentication
        self.context = context
        self.session = session
        self.auth_model = auth_model
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.headers = {k[5:]: v for k,
                        v in environ.items() if k.startswith('HTTP_')}
        self.cookies = parse_cookies(environ)
        self.query_string = environ.get('QUERY_STRING', '')
        self.GET = parse_query_string(self.query_string)
        self.POST = parse_form_data(environ)
        self.FILES = parse_file_upload(environ)

    def pass_csrf(self):
        if self.method == 'POST':
            csrf_token = self.headers.get('X-CSRF-TOKEN', '')
            if not csrf_token:
                raise Exception('Missing CSRF token')
            if csrf_token != self.csrf_token:
                raise Exception('Invalid CSRF token')


class Request:
    def __init__(self, environ, start_response, app, authentication, context, session, auth_model):
        self.app = app
        # self.csrf = csrf
        self.csrf_check = False
        self.params = {}
        self.environ = environ
        self.start_response = start_response
        self.cookies = {}
        self.context = context
        self.session = session
        self.auth_model = auth_model

        self.headers = []

        self.http_host = environ.get('HTTP_HOST')
        self.http_user_agent = environ.get('HTTP_USER_AGENT')
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

        self.parse_cookie()
        self.set_session_id()
        # auth request's
        # print(f'{self.session_id=}')
        authentication.authenticate(self.session_id, self.session)

        self.user = authentication.get_user()
        self.is_authenticated = self.user != authentication.ANONYMOUS
        self.session_id = authentication.session_id
        self.parse_qs()

        self.GET = parse_query_string(self.query_string)
        self.POST = parse_form_data(environ)
        self.FILES = parse_file_upload(environ)
        # self.pass_csrf()
        # self.csrf_middleware()
        # pass

    def set_session_id(self):
        # found = False
        session = self.get_cookie('user_session')
        if session:
            if ';' in session:
                session = session.replace(';', '')
            self.session_id = session
            # print(session)
            return
        session = ''.join(r.sample(string.ascii_letters, 50))
        self.session_id = session
        self.set_cookie('user_session', session,  {'max-age': 1296000})
        
    def pass_csrf(self):

        if self.method in ['POST', 'PUT', 'DELETE']:
            # print(self.csrf_check)
            if self.csrf_check == False:
                return
            
            # self.x_csrf_token = environ.get('HTTP_X_CSRF_TOKEN')
            csrf_token = self.post.data.get(
                'csrfmiddleware', None) or self.environ.get('HTTP_X_CSRF_TOKEN') or self.get_cookie('csrf_middleware_token')
            
            if csrf_token is not None:
                if csrf_token in self.app.csrf_tokens:
                    # print(self.dynamic_csrf)
                    if self.dynamic_csrf:
                        self.app.csrf_tokens.remove(csrf_token)
                        self.csrf_token = self.app.csrf_tokens[r.randint(
                            0, len(self.app.csrf_tokens)-1)]

                        self.app.csrf_tokens.append(
                            ''.join(r.sample([*string.ascii_letters,  *string.hexdigits], 55)))
                    return None
                # self.csrf = self.app.csrf_tokens[r.randint(0, len(self.app.csrf_tokens)-1)]
            # print(self.csrf)

            if not csrf_token:
                raise Exception('Missing CSRF token')
            elif csrf_token not in self.app.csrf_tokens:
                raise Exception('Invalid CSRF token')
        else:
            # elif csrf_token == None:
            # if self.dynamic_csrf:
            csrf_token = self.app.csrf_tokens[r.randint(
                0, len(self.app.csrf_tokens)-1)]
            self.csrf_token = csrf_token
            # self.csrf_token = self.app.csrf_tokens    
            self.set_header('Set-cookie', f'csrf_middleware_token={self.csrf_token}')

    def csrf_middleware(self):
        # print(self.environ.get('wsgi.csrf_token'))
        print(self.FILES, self.POST)
        # return
        csrf_token = self.cookies.get('csrf_middleware')
        if self.method == 'POST':
            print(csrf_token)
            if not csrf_token:
                raise Exception('Missing CSRF token')
            elif csrf_token not in self.app.csrf_tokens:
                raise Exception('Invalid CSRF token')
            # self.csrf_token = csrf_token
            # else:
            #     csrf_token = self.app.csrf_tokens[r.randint(0, len(self.app.csrf_tokens)-1)]
            #     self.csrf_token = csrf_token
            #     self.set_header('Set-Cookie', f'csrf_middleware={csrf_token};max-age=300;path=/')
        elif csrf_token == None:
            csrf_token = self.app.csrf_tokens[r.randint(
                0, len(self.app.csrf_tokens)-1)]
            self.csrf_token = csrf_token
            self.set_header('Set-Session', f'csrf_middleware={csrf_token}')

    def parse_qs(self):
        # print(self.environ)
        qs = self.query_string.split('&')
        self.query = {}
        for q in qs:
            v = ''
            k = q
            if '=' in q:
                k, v = q.split('=')
            self.query[k] = v.replace('+', ' ')

        if self.method not in ['POST', 'PUT']:

            return

        self.post = PostBody({})
        environ = self.environ
        field_storage = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )

        for item in field_storage.list:
            if not item.filename:
                if type(item.value) not in [str, int, float]:
                    continue

                if self.post.get(item.name):
                    self.post.addlist(item.name, item.value)
                    continue
                self.post.set(item.name, item.value)
            else:
                # print((item.type))
                self.post.set(item.name, TemporaryFile(
                    file=item, filename=item.filename, path=self.app.media_file))

    def clear_cookie(self):
        self.cookie = []

    def set_cookie(self, k, v, kwargs={}):
        default = {
            'path': '/',
            'max-age': 1296000,
        }
        kwargs = {**default, **kwargs}
        # print(kwargs)
        p = ';'.join([f'{k}={v}' for k, v in kwargs.items()])
        self.cookies[k] = v
        # print(p)
        self.set_header('Set-Cookie', f'{k}={v};{p}')

    def parse_cookie(self):
        if self.http_cookie == None:
            return
        cookies = self.http_cookie.split(' ')
        for cookie in cookies:
            k, v = cookie.split('=')
            self.set_cookie(k, v, {})

    def set_header(self, key, value):
        self.headers += [(key, value)]

    def get_cookie(self, key):
        return self.cookies.get(key)
