from tesla.router import Path
from tesla.response import HttpResponse, Redirect
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
                Path('/{filename}/', self.file, name='file'),     
                Path('/{filename}/delete', self.delete, name='delete'),     
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
    
    def delete(self, request):
        filename = request.params['filename']
        next = request.query.get('next')
        filename, filetype = filename.split('>')
        filename = self.path + filename
        if not os.path.isfile(filename):  
            os.remove(filename)
        return Redirect(request, next)    


 
mediafiles = MediaFiles()
