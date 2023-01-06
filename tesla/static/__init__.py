from tesla.router import Path
from tesla.response import HttpResponse
from dataclasses import dataclass
import os


media_types = {
    'video': ['mp4'],
    'audio': ['mp3'],
    'image': ['png', 'jpg', 'jpeg'],
    'text': ['css', 'js', 'txt','json']
    
}

def get_media_type(ex):
    r = 'text/txt'
    
    for t, es in media_types.items():
        
        if ex.lower() in es:
            r = f'{t}/{ex}'
            
            break
    return r    
@dataclass
class StaticFiles:
    paths = ['./static/']
    request = None
    url = '/static/'



    def __post_init__(self):
        self.urls =  [
                Path('/{filename}/', self.file)     
            ]


    def file(self, request):
        # print(request.params)
         
        filename = request.params['filename']
        # print(self.paths)
        for path in self.paths:
            # print(path + filename)
            if os.path.isfile(path + filename):
                # print(path)
                filename = path + filename
                with open(filename, 'rb') as file:
                    # print(file.)
                    request.headers += [('cache-control', 'public, max-age=3256926')]
                    return HttpResponse(request, file.read(), content_type=get_media_type(filename.split(".")[-1]))
            
        return HttpResponse(request, f"invalidd address\n {filename}")


 
staticfiles = StaticFiles()
