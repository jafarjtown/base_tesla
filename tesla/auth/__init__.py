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

    def authenticate(self, session_id, session):
        user_session = session.get(session_id)
        # print(user_session)
        # print(user_session)
        self.session_id = session_id
        if not user_session:
            return False
        user = self.model.get(id=user_session.get('__id'))
        self.set_user(user)

     
        
