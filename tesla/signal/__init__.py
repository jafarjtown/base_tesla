

class Signal:
    __signals = {}
    
    
    def connect(self, sender, receiver, signal='pre'):
        sign = sender.__name__ + signal
        rs = self.__signals.get(sign)
        if rs:
            self.__signals[sign] += [receiver]
            return
        self.__signals[sign] = [receiver]
    
    def send(self, sender, instance, created,signal, **kwargs):
        sign = sender.__name__ + signal
        rs = self.__signals.get(sign, [])
        for r in rs:
            r(sender, instance, created,**kwargs)         
            
signal = Signal()

def connect_pre_save(sender, receiver):
    signal.connect(sender=sender, receiver=receiver, signal='pre-save')

def connect_post_save(sender, receiver):
    signal.connect(sender=sender, receiver=receiver, signal='post-save')    