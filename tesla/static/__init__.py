from tesla.router import Path
from tesla.response import HttpResponse
from dataclasses import dataclass
import os

@dataclass
class StaticFiles:
    paths = ['./static/']
    request = None
    url = '/static/'



    def __post_init__(self):
        self.urls =  [
                Path('/<filename>/', self.file)     
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
                with open(filename) as file:
                    return HttpResponse(request, file.read(), content_type=f'text/{filename.split(".")[-1]}')
            
        return HttpResponse(request, f"invalidd address\n {filename}")


 
staticfiles = StaticFiles()
