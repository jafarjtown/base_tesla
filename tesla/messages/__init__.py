from dataclasses import dataclass, field


@dataclass    
class Message:
    seen : bool = False
    message : str = ''
    level : int = 1
      
    def __str__(self) -> str:
        self.seen = True
        return self.message
 
@dataclass    
class MessageBroker:
    messages : list = field(default_factory=list) 
    
    def add_message(self,req, message, level=1):
        
        m = Message(message=message, level=level)
        b = self.get_messages(req)
        b.add_message(m)
        
    def get_messages(self, req):
        for m in self.messages:
            if m._req_s == req.session_id:
                return m
        m = Messages()
        m._req_s = req.session_id  
        self.messages.append(m)
         
        return m        
    
    
        
        
messages_broker = MessageBroker()
        

@dataclass
class Messages:
    __messages : list = field(default_factory=list)      
    _req_s : str = None  
    def add_message(self,m):

        self.__messages.append(m)
    def remove_seen(self):
        self.__messages = list(filter(lambda x: x.seen == False, self.__messages))     
    def __iter__(self):
        self.remove_seen()
        self.current_index = 0
          
        return self
    
    def __next__(self):
        if self.current_index < len(self.__messages):
            # ls = [x for x in self.messages if x.req_s == self.req_s]
            self.remove_seen()
            x = self.__messages[self.current_index]
            self.current_index += 1
            return x
        else:
            raise StopIteration
        
        
        
          