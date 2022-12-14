
import os

import time
class Watcher:
    def __init__(self, dir, generate_files, server):
        self.dir = dir
        self.files = os.listdir(dir)
        self.generate_files = generate_files
        self.server = server
        self.start_watching()
    def start_watching(self):
        files = {}
        while True:
            
            
            for i, file in enumerate(self.files):
               
                if os.path.isdir(file):
                    continue
                with open(self.dir + file, "r") as f1:
                     if files.get(file):
                        f2 = files.get(file)
                     else:
                       
                        files[file] = f1.read()
                        f2 = f1.read()
                     
                     
                     if f1.read() != f2:
                            files[file] = f1.read()
                            print(f"{file} changed")
                            print('reloading the server...')
                            self.generate_files()
                            self.server.server_close()
                            self.server.shutdown()
                            os.system( 'python main.py' )
                            
                            