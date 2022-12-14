from tesla.database.localdb import global_db
from .modal import UserBaseModal
# from http.cookiejar import Cookie


class Anonymous:
    pass

    def __str__(self):
        return 'Anonymous User'
    
    
    def get(self, key):
        return self.__str__()

class Authentication:
    def __init__(self):
        self.ANONYMOUS = Anonymous()
        self.user = None
        self.model = UserBaseModal
        self.session_id = ''
        
        pass
    
    def get_user(self):
        if self.user is None:
            return self.ANONYMOUS
        return self.user
    def set_user(self, obj):
        self.user = obj
        return self.user

    def authenticate(self, cookie:str, session):
        
        if cookie == None:
            return False
        for c in cookie.split(';'):
            key, value, *_ = c.split('=')
            # print(2)
            if key.strip() == 'usersession':
                user_session = session.get(value.strip())
                # print(user_session)
                self.session_id = value.strip()
                if not user_session:
                    return False
                user = self.model.get(id=user_session.get('__id'))
                self.set_user(user)

     
        
