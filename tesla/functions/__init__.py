from tesla.response import Redirect
from tesla.static import staticfiles
from tesla.router import router

from tesla.pyhtml import CT
# from

# path = f'http://{staticfiles.request.http_host}'


def media_file(url, *args, **kwargs):
    # print(url)
    if url == None:
        return ''
    _, filetype = url.split('>')
    f, _ = filetype.split('/')
    url = '/' + url
    match f:
        case 'video':
            return CT('video',*args, **kwargs,  src=url)
        case 'audio':
            return CT('audio',*args, **kwargs, src=url)
        case 'image':
            return CT('img',*args, **kwargs, src=url)
            
            


def include():
    ...

def static_url(file_path):
   
    complete_url = f'http://{staticfiles.request.http_host}' + staticfiles.url + file_path
    return complete_url    


def url(addr):
    for route in router.routes:
        if ':' in addr:
            ap, ur = addr.split(':')
            addr = f'{ur}_{ap}'
        if route.name == addr:
            return f'http://{staticfiles.request.http_host}'+ route.path 
    return None



def redirect(request, path):
    return Redirect(request, path)