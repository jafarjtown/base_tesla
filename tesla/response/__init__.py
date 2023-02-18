# from tesla import TeslaApp
import tesla
from tesla.pages import ErrorPage
from tesla.request import Request
from tesla.messages import messages_broker


import os

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape, ChoiceLoader


class Response:
    def __init__(self, request: Request, status_code: str, content_type: str):

        self.status_code = status_code
        self.start_response = request.start_response
        self.content_type = content_type
        # print(request.get_cookie())
        self.headers = [('Content-type', self.content_type)]
        self.headers += request.headers

        self.response_content = []
        self.templates_folders = ['./']
        self.templates_folders.extend(tesla.TeslaApp.templates_folders)

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

    def __init__(self, request: Request, content, context={},  status_code='200 OK', content_type='text/html'):

        # request.cookie = self.parse_cookie(request.http_cookie)
        request.headers += [('cache-control', 'private, no-cache')]
        super().__init__(request, status_code, content_type)
        # env = Environment(loader=PackageLoader('jinja2', '/'))

        # if self.is_available(content) is not None:
        # template = env.get_template(self.is_available(content))
        file_loader = FileSystemLoader(self.templates_folders)
        loader = ChoiceLoader([
            # PackageLoader("tesla.admin", 'templates'),
            FileSystemLoader(self.templates_folders)
        ])
        # env = Environment(loader=file_loader)
        env = Environment(loader=loader,
                          autoescape=select_autoescape())
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        globals_obj = request.context.get_objs()
        for k, v in globals_obj.items():
            env.globals[k] = v
        template = env.get_template(content)
        # print(**request.context.get_objs())
        content = template.render(
            **{'user': request.user, 'messages': messages_broker.get_messages(request), **request.params, **context})
        # else:
        #     content = f'Template {content} not found.'
        # content = template.render(*context)
        self.response_content.append(content.encode())

    # def is_available(self, filename):
    #     for path in self.templates_folders:
    #         if not path.endswith('/'):
    #             path = path + '/'
    #         if os.path.isfile(path + filename):
    #             return filename
        # return None


class HttpResponse(Response):

    def __init__(self, request: Request, content,  status_code='200 OK', content_type='text/html'):
        super().__init__(request, status_code, content_type)
        if type(content) == str:
            content = f'{content}'.encode()
        self.response_content.append(content)


class JsonResponse(Response):

    def __init__(self, request: Request, content: str,  status_code='200 OK', content_type='application/json'):
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
        logs = []
        for p in routes:
            r = p.path
            if p.name:
                r += ' ' + p.name
            logs.append(r)
        doc = ErrorPage(request, logs, '404 page not found',
                        'available paths', '', debug)
        self.response_content.append(str(doc).encode())


class Http500Response(ErrorResponse):
    def __init__(self, request: Request, message, debug):
        super().__init__(request, '500 Server Error')
        doc = ErrorPage(request, [], '500 Server Error', message, '', debug)
        self.response_content.append(str(doc).encode())
        # self.response_content.append(f'500 Server Error \n {message}'.encode())


class Redirect(Response):
    def __init__(self, request: Request, route,  status_code='302 Found', content_type='text/html', *args, **kwargs):
        super().__init__(request, status_code, content_type)
        self.headers += [('Location', tesla.functions.url(route, **kwargs))]
        # print(self.headers)
