from dataclasses import dataclass, field
import os
import json
import random as rn
from uuid import uuid4 as v4
import copy
# sorted
from tesla.database.jsondb.schema import User, settype

ABS_PATH = './db/'

def Contains(column, obj):
    r = {}
    #print(obj)
    for k in obj.keys():
        r[k] = False
        if column[k] == obj[k]:
            r[k] = True
    for c in list(r.values()):
        if c == False:
            return False
    return True

def GreaterThan(columns, obj, k, op):
    key = k.find(f"__{op}t")
    #print(k)
   # print(columns["age"] > obj[k], columns)
    if op == 'g':
         statement = columns[k[:key]] > obj[k]
    else:
        statement = columns[k[:key]] < obj[k]
    #print(statement)
    if statement:
        
        o = {}
        for ky, v in obj.items():
           
            if ky.find(f"__{op}t") != -1:
                o[ky[:key]] = columns[k[:key]]
            else:
              o[ky] = v
             
            #print(o)
        return columns, o, True
        pass
    return columns, obj, False

@dataclass
class ColCache:
    db : dict = field(default_factory=dict)
    def update(self,collection , key, value):
        if self.db.get(collection):
            self.db[collection][key] = value
        raise Exception(f'No collection with name {collection}')   
    
    def get(self, collection, key=None):
        if key:
            return self.db.get(collection).get(key)
        return self.db.get(collection) 
    def set(self, key, json):
        if self.get(key) ==  None:
            self.db[key] = dict()
        self.db[key] = (json) 
    def delete(self, key):
        del self.db[key]
        # print(key)
        # print(self.db)
local_c_db = ColCache({})


@dataclass
class DBCache:
    db : dict = field(default_factory=dict)
    def update(self,collection , key, value):
        if self.db.get(collection):
            self.db[collection][key] = value
        raise Exception(f'No collection with name {collection}')   
    
    def get(self, collection, key=None):
        if key:
            return self.db.get(collection).get(key)
        return self.db.get(collection) 
    
    def set(self, key, col):
        if self.db.get(key) ==  None:
            self.db[key] = list()
        self.db[key].append(col) 
        # print(self.db[key])
        
    def remove(self, collection, id):
        for c in self.db[collection]:
            if c.get('id') == id:
                self.db[collection].remove(c)
                break

        

local_db = DBCache({})

# @dataclass
class Column:
    
    def __init__(self, file):
        self.file = file
        self.__one_2_many = {}
        # self.many_2_many = []
        
        *_, self.cls, id = file.split('/')
        self.id = id.split('.')[0]
        
        
        
    def __post_init__(self):
        for k , v in self.readAll().items():
            # print(k, v)
            if '__' in k:
                m, k = k.split('__')
                self.__one_2_many[m] = {k: v}
        ...    
            
    def update(self, **obj):
        obj = dict(obj)
        json_db = local_c_db.get(self.id)
        if not json_db:   
            with open(self.file) as f:
                json_db = json.load(f)
        for key, value in obj.items():
            json_db[key] = value
        with open(self.file, 'w+') as f:
            json.dump(json_db, f, indent=4)
            local_c_db.set(self.id, json_db)
            
    def readAll(self, dept=1):
        json_db = {}
        if local_c_db.get(self.id):
            json_db = local_c_db.get(self.id)
            
        else:
            with open(self.file) as f:
                json_db = json.load(f)
            
                local_c_db.set(self.id, json_db) 
        if dept > 1:
            # print(dept)
            self.__post_init__()
            for key in self.__one_2_many:
                obj = self.__one_2_many[key]
                json_db[key] = self.get_foreign_obj(key, **obj).readAll()         
        return json_db
  
    def get(self,key):
        # print(key)
        # print(self.one_2_many)
        if self.__one_2_many == {}:
            self.__post_init__()
        
        if key in self.__one_2_many:
            obj = self.__one_2_many[key]
            return self.get_foreign_obj(key+'/', **obj)
        if local_c_db.get(self.id):
            return local_c_db.get(self.id, key)
        
        
        with open(self.file) as f:
            json_db = json.load(f)
            local_c_db.set(self.id, json_db)
        return json_db.get(key)
    def clear(self, key):
        if local_c_db.get(self.id):
            local_c_db.delete(self.id)
        with open(self.file, 'r+') as file:
           json_db = json.load(file)
           if type(key) == list:
               for k in key:
                   del (json_db[k])
           else:
               del (json_db[key])
        return None
              
    def delete(self):
        local_db.remove(self.cls, self.id)
        if local_c_db.get(self.id):
            local_c_db.delete(self.id)
        os.remove(self.file)
    def clearAll(self):
        if local_c_db.get(self.id):
            local_c_db.set(self.id, {}) 
        with open(self.file, 'w+') as file:
           json.dump({}, file, indent=4)
        return None

    def __repr__(self):
        return f"Column {self.get('id')}"
    
    def get_foreign_obj(self, key, **args):
        return JsonDB(key.title()).get(args)
  
       
class JsonDB:
    # db = {}
    abs_path = ''
    def __init__(self, collection, path = './db/'):
        self.collection = collection
        self.abs_path = path
        self.path = path + 'collections/'
        ABS_PATH = self.abs_path
        
         
        if os.path.isdir(self.path  + self.collection) == False:
            os.makedirs(self.path + self.collection)
            self.init_json_db()
                
    def init_json_db(self):
            if not os.path.isfile(self.abs_path + 'db.json'):
                with open(self.abs_path + 'db.json', 'w+') as f:
                    json.dump({}, f) 
            with open(self.abs_path + 'db.json', 'r+') as f:
                js = json.load(f) 
                if 'collections' not in js:
                    js['collections'] = {}
                if self.collection[:-1] not in js['collections']:    
                    js['collections'][self.collection[:-1]] = {}
                js['collections'][self.collection[:-1]]['count'] = len(self.all())
                js['collections'][self.collection[:-1]]['link'] = ''    
            with open(self.abs_path + 'db.json', 'w+') as f:
                json.dump(js, f, indent=4)   

    
    @classmethod
    def get_collection(cls, model, dept=1):
        if model.title() not in cls.db()['collections']:
            return {
                'Error': f'No such collection {model}'
            }
        # return type(model, (), )    
        return JsonDB(model.title() + '/').all()
        
           
    @classmethod         
    def db(cls):
        js = {}
        return json.load(open(ABS_PATH + 'db.json'))            
    def create_column(self, model, table_name):
           
           with open(self.path + self.collection + table_name + '.json', 'w+') as file:
            #    self.dump_db(model, self.collection) 
               json.dump(model, file, indent=4)
            #    c = Column(self.path + self.collection + table_name + '.json')
            #    if local_db.get(self.collection[:-1])
            #    local_db.set(self.collection[:-1], model)
               self.init_json_db()
            #    print(c)
            #    raise Exception('b')
            #    local_c_db.set(c.get('id'), c)
               return None
    
    def all(self):
        # print(local_db)
        if local_db.get(self.collection.split('/')[0]):
           return local_db.get(self.collection.split('/')[0])
        
        all = os.listdir(self.path + self.collection)
        for i in all:
            # c = Column(self.path + self.collection + i)
            with open(self.path + self.collection + i) as fl:
                c = json.load(fl)
            # print(c.get('id'))
            local_db.set(self.collection.split('/')[0], c)
            # local_c_db.set(c.get('id'), c)
        # print('here 3')
        return  local_db.get(self.collection.split('/')[0]) if local_db.get(self.collection.split('/')[0]) else []
        
    def get(self,obj):
        all = self.all()
        # print(all)
        for i in all:
            # print(i, obj)
            o = i
            keys = set(o.keys())
            keys2 = set(obj.keys())
            
            t = (keys2 & keys)
             
            if list(t) == list(keys2):
               
               contains = Contains(o, obj)
               if contains:
                   colle = self.collection
                   if '/' not in colle:
                       colle += '/'
                    #    print(self.collection)
                #    return Column(self.path + colle +  i.get('id') + '.json').readAll()
                   return o
        return None
    def filter(self, ob):
        all = self.all()
        result = []
        
        for i in all:
            obj = copy.deepcopy(ob)
            o = i.readAll() 
            #print(obj)
            keys = set(o.keys())
            keys2 = set(obj.keys())
            gt = None
            for k in keys2:
                if k.find("__") != -1 :
                    op = 'g' if k.find("__gt") != -1 else 'l' 
                    #print(op)
                    o, obj, gt = GreaterThan(o, obj ,k, op)
                    keys2 = set(obj.keys())
                    #print(obj)
            if gt == False:
                   #print(gt)
                   continue
            t = (keys2 & keys)
   
            if list(t) == list(keys2):
               contains = Contains(o, obj)
               #print(contains)
               if contains:
                   result.append(i)
        return result
  
        
# db = DB("users/", User)
# products = DB("products/", Product)
# pr1 = products.create_column("watch")
# pr1.update({"name": "US watch", "rate": 5})
#jafar = db.create_column('jafar')
#nura = db.create_column('nura')
#jafar.update({'name':'Jafar Idris','age':50, 'nura': nura.read('id')})
#nura.update({'name':'Nura Idris','age':50, 'nura': nura.read('id')})
#json_db = jafar.readAll()
#name = jafar.read('age')
#jafar.clear(['name','age', 'nura'])
#jafar.clearAll()
#json_db = jafar.readAll()
#print(json_db)
# all = db.filter({'age__gt':5, 'age__lt':59})
#pr1 = db.get({"id":"a58b1227-a97d-4705-a630-460604fdebf7"})
#print(pr1)
#print(all)
# for c in all:
#    print(c.read("name"), c.read('age'))
    