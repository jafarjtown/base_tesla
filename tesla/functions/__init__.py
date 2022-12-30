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
    if f == 'video':
            return CT('video',*args, **kwargs,  src=url)
    elif f == 'audio':
            return CT('audio',*args, **kwargs, src=url)
    elif f == 'image':
            return CT('img',*args, **kwargs, src=url)
            
            


def include():
    ...

def static_url(file_path):
   
    complete_url = staticfiles.url + file_path
    return complete_url    


def url(addr, *args, **kwargs):
    for route in router.routes:
        if ':' in addr:
            # print(addr)
            *_, ap, ur = addr.split(':')
            addr = f'{ur}_{ap}'
        if route.name == addr:
            sp_u = route.path.split('/')
            for i,p in enumerate(sp_u):
                
                if "{" and "}" in p:
                    v = p[1:-1]
                    param = kwargs.get(v)
                    if not param:

                        raise Exception(f'''
    {v} can"t be None.
    it suppose to be url('{addr.replace('_', ':')}', {v}=*something* ...)

                            ''')
                    sp_u[i] = param
                    
            return f'http://{staticfiles.request.http_host}' + '/'.join(sp_u)
   
    return None



def redirect(request, path):
    return Redirect(request, path)