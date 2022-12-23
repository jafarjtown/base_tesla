from dataclasses import dataclass, field
from typing import Any
import os
import json
# from uuid import uuid4 as v4
import copy
# sorted
from tesla.database.jsondb.schema import User, settype
import tesla

ABS_PATH = './db/'


def Contains(column, obj):
    r = {}
    # print(obj)
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
    # print(k)
   # print(columns["age"] > obj[k], columns)
    if op == 'g':
        statement = columns[k[:key]] > obj[k]
    else:
        statement = columns[k[:key]] < obj[k]
    # print(statement)
    if statement:

        o = {}
        for ky, v in obj.items():

            if ky.find(f"__{op}t") != -1:
                o[ky[:key]] = columns[k[:key]]
            else:
                o[ky] = v

            # print(o)
        return columns, o, True
        pass
    return columns, obj, False


@dataclass
class ColCache:
    obj: Any
    db: dict = field(default_factory=dict)

    def update(self, collection, key, value):
        if self.db.get(collection):
            self.db[collection][key] = value
        raise Exception(f'No collection with name {collection}')

    def get(self, collection, key=None):
        if key:
            return self.db.get(collection).get(key)
        return self.db.get(collection)

    def set(self, key, json):
        if self.get(key) == None:
            self.db[key] = dict()
        self.db[key] = (json)

    def delete(self, key):
        del self.db[key]

        # print(key)
        # print(self.db)
local_c_db = ColCache({})


@dataclass
class DBCache:
    db: dict = field(default_factory=dict)

    def update(self, collection, key, value):
        if self.db.get(collection):
            self.db[collection][key] = value
        else:
            self.db[collection] = dict()
            self.db[collection][key] = value

    def get(self, collection, key=None):
        if key:
            o = self.db.get(collection)
            if o:
                j = o.get(key)
                if j:
                    return j.values()
                return o.values()
        o = self.db.get(collection)
        return o.values() if o else []

    def remove(self, collection, key):
        del self.db[collection][key]
        
        

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
        for k, v in self.readAll().items():
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

    def get(self, key):
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

    def __init__(self, collection, path='./db/'):
        self.collection = collection
        self.abs_path = path
        self.path = path + 'collections/'
        self.model = None
        ABS_PATH = self.abs_path
        self.__metas = None

        if os.path.isdir(self.path + self.collection) == False:
            os.makedirs(self.path + self.collection)

        self.__model__()

    def __model__(self):
        model_n = self.collection[:-1]
        for m in tesla.TeslaApp.registered_models:

            if m.__name__ == model_n:
                self.model = m

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
            json.dump(model, file, indent=4)
            local_db.update(self.collection.split(
                '/')[0], model.get('id'), model)
            return None

    def delete(self, table_name):
        os.remove(self.path + self.collection + table_name + '.json')
        local_db.remove(self.collection[:-1], table_name)
        return None
        
        
        
    def all(self, models=False):
        # print(local_db)

        lookup = self.collection.split('/')[0]
        if local_db.get(lookup):
            if models:
                ls = []
                for js in local_db.get(lookup):

                    c = self.model()
                    for k, v in js.items():
                        setattr(c, k, v)
                    ls.append(c)

                return ls
            # print(local_db.get(lookup))

            return local_db.get(lookup)

        all = os.listdir(self.path + self.collection)
        for i in all:

            with open(self.path + self.collection + i) as fl:
                js_ = json.load(fl)

                local_db.update(lookup, js_.get('id'), js_)
        if models:
            ls = []
            for js in local_db.get(lookup):
                c = self.model()
                for k, v in js.items():
                    setattr(c, k, v)
                ls.append(c)
            return ls
        # print(local_db.get(lookup))
        return local_db.get(lookup)

    def get(self, obj):
        all = self.all()
        user = None
        for i in all:
            a = 0
            b = len(obj)

            for k, v in obj.items():

                if i.get(k) == v:
                    a += 1
            if a == b:
                user = i
                break
        return user

    def filter(self, ob):
        all = self.all()
        result = []

        for i in all:
            obj = copy.deepcopy(ob)
            o = i.readAll()
            # print(obj)
            keys = set(o.keys())
            keys2 = set(obj.keys())
            gt = None
            for k in keys2:
                if k.find("__") != -1:
                    op = 'g' if k.find("__gt") != -1 else 'l'
                    # print(op)
                    o, obj, gt = GreaterThan(o, obj, k, op)
                    keys2 = set(obj.keys())
                    # print(obj)
            if gt == False:
                # print(gt)
                continue
            t = (keys2 & keys)

            if list(t) == list(keys2):
                contains = Contains(o, obj)
                # print(contains)
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
# jafar.clearAll()
#json_db = jafar.readAll()
# print(json_db)
# all = db.filter({'age__gt':5, 'age__lt':59})
#pr1 = db.get({"id":"a58b1227-a97d-4705-a630-460604fdebf7"})
# print(pr1)
# print(all)
# for c in all:
#    print(c.read("name"), c.read('age'))
