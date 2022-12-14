
import http.server
import socketserver


def server(path):
    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler, ):
    #def __init_
       
            def do_GET(self):
                if self.path == '/':
                   self.path = path
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
               
    return MyHttpRequestHandler
        

