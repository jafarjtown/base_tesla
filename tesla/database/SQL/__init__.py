
import sqlite3, inspect
# from tesla.modal import CharField, NumberField, BooleanField, FileField

# class

DB_ADDR = 'database.db'

class DB:
    
    def __init__(self, table_name, objs) -> None:
        self.table_name = table_name
        self.db = DB_ADDR
        self.cursor = None
        self.is_connected = False
        self.__obj__ = objs
        
        self.__init_db__() 
        
    def __init_db__(self):
        self.db = sqlite3.connect(DB_ADDR)
        self.cursor = self.db.cursor()
        
        # print(self.__obj__)
        columns = []
        for name,t in self.__obj__:
            if type(t) == str:
                return
            
            q = ''
            # print(f'{t.value_type=}')
            if not inspect.isclass(type(t)):
                continue
            elif issubclass(type(t.value_type), str):
                q = f'VARCHR({t.max})'
            elif issubclass(type(t.value_type), int):
                q = 'INTEGER'
            elif issubclass(type(t.value_type), bool):
                q = 'BOOL'
                
            columns.append(f'{name} {q}')
        # print(f'{columns=}')
        if columns:
            QUERY = ', '.join(columns)
            command = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (__id INTEGER PRIMARY KEY, {QUERY})
                                '''
            self.cursor.execute(command)
        
    
    def all(self, json = False,**kwargs):
        self.cursor.execute(f'''
        SELECT * FROM {self.table_name}
                            ''')
        rows = self.cursor.fetchall()
        self.db.commit()
        # print(rows)
        if json:
            l = []
            # print(dict())
            keys = ['id'] + list(dict(self.__obj__).keys())
            for r in rows:
                obj = {}
                for k, v in zip(keys, r):
                    obj[k] = v
                l.append(obj)
            return l    
        return rows
    
    def get(self, **kwargs):
        QUERY = ', '.join([f'"{k}" == "{v}"' for k, v in kwargs.items()])
        # print(QUERY)
        self.cursor.execute(f'''
        SELECT * FROM {self.table_name}
        WHERE ({QUERY})
                            ''')
        row = self.cursor.fetchone()
        self.db.commit()
        return row
    
    def create(self, json):
        # del json['id']
        objs = ''
        keys = []
        values = list()
        VR = []
        for k, v in json.items():
            keys.append(k)
            values.append(v)
            VR.append('?')
        k = ','.join(keys)    
        v = tuple(values)
        vr = ','.join(VR)
        command = f'''
        INSERT INTO {self.table_name} ({k})
        VALUES ({vr})
        '''
        self.cursor.execute(command, v)
        self.db.commit()
        self.db.close()