

from tesla.functions import redirect
from tesla.messages import messages_broker


def login_required(path = 'login'):
    # print(args, kwargs)
    def decorator(func):
        def innder(request, *args, **kwargs):
            if request.is_authenticated:
                return func(request, *args, **kwargs)
            messages_broker.add_message(request,'You must login')
            return redirect(request, f'{path}')
        
        return innder
    return decorator