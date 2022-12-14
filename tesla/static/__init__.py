from tesla.router import Path
from tesla.response import HttpResponse
from dataclasses import dataclass
import os

@dataclass
class StaticFiles:
    path = './static/'
    request = None
    url = '/static/'



    def __post_init__(self):
        self.urls =  [
                Path('/<filename>/', self.file)     
            ]


    def file(self, request):
        # print(request.params)
         
        filename = request.params['filename']
        filename = self.path + filename
        if not os.path.isfile(filename):
             
            return HttpResponse(request, f"invalidd address\n {filename}")
        with open(filename) as file:
            return HttpResponse(request, file.read(), content_type=f'text/{filename.split(".")[-1]}')


 
staticfiles = StaticFiles()
