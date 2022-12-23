 
from tesla import router





# 
def get_dynamic_url(url, path, o={}): 
    if (path.startswith('/static') and url.startswith('/static')) or (path.startswith('/media') and url.startswith('/media')):
        filename = url[7:]
        o['filename'] = filename
        # print('saaa') 
        return o
    # splitting the urls into a list
    sp_u = url.split('/')
    sp_p = path.split('/')
    
    # checking if the their length is not same
    if len(sp_u) != len(sp_p):
        return None     
    # print(sp_p, sp_u)    
    # getting the variables
    for i,p in enumerate(sp_p):
        if "{" and "}" in p:
            v = p[1:-1]
            o[v] = sp_u[i]
        elif p != sp_u[i]:
            return None
    return o



def Mount(ent, urls, app_name=None):
    for p in urls:
        if app_name != None:
            p.name += f'_{app_name}'
        p.path = ent + p.path
        # print(p.path)
        router.router.add_routes([p])           