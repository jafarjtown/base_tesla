import os
import random
import string

def csrf_check(check=True):
    # print(args, kwargs)
    def inner(request, *args, **kwargs):
        request.csrf_check = check
    return inner
