from dataclasses import dataclass, field
from datetime import datetime
import json
import os



@dataclass
class Session:
    values : dict = field(default_factory=dict)
    
    
    def __post_init__(self):
        if os.path.isfile('session.db'):
            with open('session.db') as file:
                obj = json.load(file)
                self.values = {**self.values, **obj}

    def add_to_session(self, key, value):
        today = datetime.today()
        expires = datetime(today.year, today.month, today.day).timestamp() + 5000000
        for k, v in self.values.items():
            if v == value:
                del self.values[k]
                break
        self.values[key] = {**value, 'expire_at':expires}
        self.save()

    def get_values(self):
        return self.values.values()
    
    def get(self, key):
        # print(key)
        if key not in self.values:
            return None
        if self.values.get(key)['expire_at'] <= datetime.today().timestamp():
            delattr(self.values, key)
            return None
        return self.values.get(key)
    
    
    def save(self):
        with open('session.db', 'w') as file:
            json.dump(self.values, file, indent=4)


        