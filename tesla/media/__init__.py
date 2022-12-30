from tesla.router import Path
from tesla.response import HttpResponse
from dataclasses import dataclass
import os


media_types = {
    'video': ['mp4'],
    'audio': ['mp3'],
    'image': ['png, jpg, jpeg'],
    
}

def get_media_type(ex):
    for t, es in media_types.items():
        if ex in es:
            return t 

@dataclass
class MediaFiles:
    path = './media/'
    request = None
    url = '/media/'



    def __post_init__(self):
        self.urls =  [
                Path('/<filename>/', self.file)     
            ]


    def file(self, request):
        # print(request.params)
         
        filename = request.params['filename']
        filename, filetype = filename.split('>')
        filename = self.path + filename
        if not os.path.isfile(filename):
             
            return HttpResponse(request, f"invalidd address\n {filename}")
        with open(filename, 'rb') as file:
            return HttpResponse(request, file.read(), content_type=filetype)


 
mediafiles = MediaFiles()
