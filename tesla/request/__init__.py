from datetime import datetime
import random as r
import string
import os
from dataclasses import dataclass
import cgi
import cgitb
cgitb.enable()
# from Cookie import SimpleCookie
# from time import t


@dataclass
class TemporaryFile:

    def __init__(self, file, filename, path, *args, **kwargs) -> None:
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
        return path + '/'+fn + f'>{self.file.type}'


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


class Request:
    def __init__(self, environ, start_response, app, csrf, authentication, context, session, auth_model):
        self.app = app
        self.csrf = csrf
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
        authentication.authenticate(self.session_id, self.session)

        self.user = authentication.get_user()
        self.is_authenticated = self.user != authentication.ANONYMOUS
        self.session_id = authentication.session_id
        self.parse_qs()
        # self.pass_csrf()
        pass

    def set_session_id(self):
        found = False
        session = self.get_cookie('user_session')
        if session:
            self.session_id = session
            return
        session = ''.join(r.sample(string.ascii_letters, 50))
        self.session_id = session
        self.set_cookie('user_session', session)
        # if self.cookies:

        #     for c in self.http_cookie.split(';'):
        #         key, value, *_ = c.split('=')
        #         # print(2)
        #         if key.strip() == 'usersession':
        #             self.session_id = value.strip()
        #             found = True
        #             break
        # if found != True:
        #     session = ''.join(r.sample(string.ascii_letters, 50))
        #     self.session_id = session
        #     self.set_cookie('usersession', session)

    def pass_csrf(self):

        if self.method == 'POST':

            csrf = self.post.get('csrfmiddleware')
            if csrf is not None:
                if csrf in self.app.csrf_tokens:

                    self.app.csrf_tokens.remove(csrf)
                    self.csrf = self.app.csrf_tokens[r.randint(
                        0, len(self.app.csrf_tokens)-1)]

                    self.app.csrf_tokens.append(
                        ''.join(r.sample([*string.ascii_letters,  *string.hexdigits], 55)))
                    return None
                # self.csrf = self.app.csrf_tokens[r.randint(0, len(self.app.csrf_tokens)-1)]
            # print(self.csrf)

            raise Exception('csrf is not provided')

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

        if self.method != 'POST':

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

    def set_cookie(self, k, v, **kwargs):
        default = {
            'path': '/',
            'max-age': 1296000,
        }
        kwargs = {**default, **kwargs}
        p = ';'.join([f'{k}={v}' for k, v in kwargs.items()])
        self.cookies[k] = v
        self.set_header('Set-Cookie', f'{k}={v};{p}')

    def parse_cookie(self):
        if self.http_cookie == None:
            return
        cookies = self.http_cookie.split(' ')
        for cookie in cookies:
            k, v = cookie.split('=')
            self.set_cookie(k, v)

    def set_header(self, key, value):
        self.headers += [(key, value)]

    def get_cookie(self, key):
        return self.cookies.get(key)
