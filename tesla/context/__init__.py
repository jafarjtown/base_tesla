from dataclasses import dataclass
from tesla.functions import media_file, static_url, url



@dataclass
class Context:
    objs : dict

    def get_objs(self):
        return self.objs

    def add(self,key, value):
        self.objs[key] = value


global_context = Context({})
global_context.add('static_url', static_url)
# global_context.add('messages', messages_broker)
global_context.add('url', url)
global_context.add('media_file', media_file)