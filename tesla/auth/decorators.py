

from tesla.functions import redirect
from tesla.messages import messages_broker


def login_required(func):
    
    def innder(request, *args, **kwargs):
        if request.is_authenticated:
            return func(request, *args, **kwargs)
        messages_broker.add_message(request,'You must login')
        return redirect(request, '/login/',)
    
    return innder